import os
import random
from typing import List
from .config import config

def _pick_images_from_pool(pool, count, allow_duplicate):
    """
    从全局可用池 pool 里选 count 张图片，选完后从 pool 里移除。
    allow_duplicate=True 时 pool 用完自动补充，False 时用完报错。
    返回选中的图片路径列表。
    """
    paths = []
    while len(paths) < count:
        if not pool['available']:
            if allow_duplicate:
                # 允许重复则补充池
                pool['available'] = pool['all'][:]
            else:
                # 不允许重复则报错
                raise RuntimeError('Not enough unique images to pick!')
        need = count - len(paths)
        if len(pool['available']) >= need:
            chosen = random.sample(pool['available'], need)
        else:
            chosen = pool['available'][:]
        for p in chosen:
            paths.append(p)
            pool['available'].remove(p)
    return paths

def calculate_building_image_paths(
    user_data: List[List[float]],
    num_layers: int,
    region: str,
    allow_duplicate: bool = False,
    verbose: bool = False
) -> List[List[str]]:
    """
    返回: [前景(3张图片), layer1, layer2, ...] (len(result) == num_layers+1)
    前景始终存在，不计入num_layers。
    allow_duplicate为True时，所有layer全局均匀使用图片。
    verbose=True 时，打印每个建筑的 user data、htype、选中的图片路径。
    """
    img_root = config['img_root']
    height_types = config['height_types']
    height_boundaries = config['height_boundaries']
    buildings_per_layer = config['buildings_per_layer']
    categories = config['categories']
    generic = 'generic'
    result = []

    # 为每个 htype 维护一个 pool
    pools = {}
    for htype in height_types:
        region_files = config['image_paths'][region][htype]
        generic_files = config['image_paths'][generic][htype]
        all_files = region_files + generic_files
        if not all_files:
            raise RuntimeError(f'No images found for {region}/{htype} and fallback generic/{htype}!')
        pools[htype] = {
            'all': all_files[:],  # 全部图片路径
            'available': all_files[:],  # 当前可用图片路径
        }
    # 前景：始终3张图片，使用h0
    foreground_paths = _pick_images_from_pool(pools['h0'], 3, allow_duplicate)
    if verbose:
        for i, p in enumerate(foreground_paths):
            print(f"[前景] idx={i}, htype=h0, path={p}")
    result.append(foreground_paths)
    for layer_idx in range(num_layers):
        layer_paths = []
        layer_data = user_data[layer_idx]
        for b in range(buildings_per_layer):
            idx = int(b / (buildings_per_layer - 1) * (len(layer_data) - 1))
            val = layer_data[idx]
            htype = None
            for i, boundary in enumerate(height_boundaries):
                if val < boundary:
                    htype = height_types[i]
                    break
            if htype is None:
                htype = height_types[-1]
            picked = _pick_images_from_pool(pools[htype], 1, allow_duplicate)
            layer_paths.append(picked[0])
            if verbose:
                print(f"[第{layer_idx+1}层] building={b}, user_data={val:.2f}, htype={htype}, path={picked[0]}")
        result.append(layer_paths)
    return result 
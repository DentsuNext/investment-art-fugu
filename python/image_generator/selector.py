import os
import random
from typing import List
from typing import Optional
from .config import config

def _pick_images_from_pool(pool, count, allow_duplicate):
    """
    优先从region池选，region用完后再从generic池选。
    allow_duplicate=True时，两个池都用完后自动补充。
    返回选中的图片路径列表。
    """
    paths = []
    while len(paths) < count:
        # 优先从region池选
        if pool['region']:
            need = count - len(paths)
            chosen = random.sample(pool['region'], min(need, len(pool['region'])))
            for p in chosen:
                paths.append(p)
                pool['region'].remove(p)
        # region用完后再从generic池选
        elif pool['generic']:
            need = count - len(paths)
            chosen = random.sample(pool['generic'], min(need, len(pool['generic'])))
            for p in chosen:
                paths.append(p)
                pool['generic'].remove(p)
        # 两个池都用完
        else:
            if allow_duplicate:
                pool['region'] = pool['region_all'][:]
                pool['generic'] = pool['generic_all'][:]
            else:
                raise RuntimeError('Not enough unique images to pick!')
    return paths

def calculate_building_image_paths(
    user_data: List[List[float]],
    num_layers: int,
    region: str,
    allow_duplicate: bool = False,
    verbose: bool = False
) -> List[List[str]]:
    """
    返回: [前景(3张图片), layer1, ..., layerN] (len(result) == num_layers+1)
    前景始终为第一项，后面依次为各层（顺序为从前到后，layer1最前，layerN最后）。
    先挑选前景3张图片，再为各层挑选图片，确保前景和各层图片不重复（当allow_duplicate=False时）。
    总是优先从region文件夹选，region用完后才会用generic。
    allow_duplicate为True时，两个池都用完后自动补充。
    verbose=True 时，打印每个建筑的 user data、htype、选中的图片路径。
    """    
    img_root = config['img_root']
    height_types = config['height_types']
    height_boundaries = config['height_boundaries']
    buildings_per_layer = config['buildings_per_layer']
    categories = config['categories']
    generic = 'generic'
    layer_results = []

    # 为每个 htype 维护一个 pool，region/generic分开
    pools = {}
    for htype in height_types:
        region_files = config['image_paths'][region][htype]
        generic_files = config['image_paths'][generic][htype]
        pools[htype] = {
            'region': region_files[:],
            'region_all': region_files[:],
            'generic': generic_files[:],
            'generic_all': generic_files[:],
        }
    # 先挑选前景3张图片（h0），从池中移除
    foreground_paths = _pick_images_from_pool(pools['h0'], 3, allow_duplicate)
    if verbose:
        for i, p in enumerate(foreground_paths):
            print(f"[前景] idx={i}, htype=h0, path={p}")
    # 再为各层挑选图片
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
        layer_results.append(layer_paths)
    # 返回顺序: [前景, layer1, ..., layerN]
    return [foreground_paths] + layer_results 
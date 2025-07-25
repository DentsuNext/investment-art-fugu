import os
import random
from typing import List
from typing import Optional
from .config import config
from .utils import getShiftedUserDataID
from .utils import getForegroundUserDataID

def _pick_images_from_lists(region_list, generic_list, count):
    """
    从 region_list 里优先选，选完后从 generic_list 里补足。每次选中后会从原列表中删除，保证全局唯一。
    """
    paths = []
    # region_list 先选
    need = min(count, len(region_list))
    if need > 0:
        chosen = random.sample(region_list, need)
        for p in chosen:
            paths.append(p)
            region_list.remove(p)
    # 不够再从 generic_list 选
    if len(paths) < count:
        need2 = count - len(paths)
        if len(generic_list) < need2:
            raise RuntimeError('Not enough unique images to pick!')
        chosen2 = random.sample(generic_list, need2)
        for p in chosen2:
            paths.append(p)
            generic_list.remove(p)
    return paths

def _calculate_htype_from_value(value, height_types, height_threshold, height_boundaries):
    if value <= height_threshold:
        return None

    for i, boundary in enumerate(height_boundaries):
        if value < boundary:
            return height_types[i]

    return height_types[-1]

def _pick_images_for_layer(user_data, layer_idx, is_foreground, available_images, layer_regions, layer_folders, generic_folder, verbose= False):
    """
    挑选一层（或前景）的图片路径列表。
    参数：
        user_data: 所有层的用户数据（二维数组）
        layer_idx: 当前层索引（前景为0）
        is_foreground: 是否为前景层（True/False）
        available_images: 可用图片池（每次选中后会从中删除，保证全局唯一）
        layer_regions: 层地区名列表
        layer_folders: 层图片文件夹名列表
        generic_folder: generic 文件夹名
        verbose: 是否打印详细日志
    返回：
        当前层的图片路径列表（遇到低于阈值的点返回空字符串）
    """
    layer_data = user_data[layer_idx]   
    if not layer_data:
        # 如果该层 user_data 为空，直接返回空列表
        if verbose:
            if is_foreground:
                print(f"[前景层] user_data[0] 为空，跳过")
            else:
                print(f"[第{layer_idx+1}层] user_data 为空，跳过")
        return []


    height_types = config['height_types']
    height_boundaries = config['height_boundaries']
    height_threshold = config['height_threshold']
    num_layers = len(layer_regions)
    folder = layer_folders[layer_idx]

    # 前景和普通层的建筑数量不同
    if is_foreground:
        buildings_per_layer = config['extra_building_count']
    else:
        buildings_per_layer = config['buildings_per_layer']
    
    
    layer_results = []
    for b in range(buildings_per_layer):
        # 计算 user_data 的索引
        if is_foreground:
            idx = getForegroundUserDataID(user_data, b, buildings_per_layer)
        else:
            idx = getShiftedUserDataID(user_data, num_layers, buildings_per_layer, layer_idx, b)
        idx = max(0, min(idx, len(layer_data) - 1))
        val = layer_data[idx]
        # 计算高度类型
        htype = _calculate_htype_from_value(val, height_types, height_threshold, height_boundaries)
        if htype is None:
            layer_results.append("")
            if verbose:
                if is_foreground:
                    print(f"[前景层] building={b}, idx = {idx}, user_data={val:.2f}, skip picking")
                else:
                    print(f"[第{layer_idx+1}层] building={b}, idx = {idx}, user_data={val:.2f}, skip picking")
            continue
        # 前景强制用 h0
        if is_foreground:
            htype = height_types[0]
        
        # 选图片
        region_list = available_images.get(folder, {}).get(htype, [])
        generic_list = available_images.get(generic_folder, {}).get(htype, [])
        picked = _pick_images_from_lists(region_list, generic_list, 1)
        layer_results.append(picked[0])
        if verbose:
            if is_foreground:
                print(f"[前景层] building={b}, idx = {idx}, user_data={val:.2f}, htype={htype}, path={picked[0]}")
            else:
                print(f"[第{layer_idx+1}层] building={b}, idx = {idx}, user_data={val:.2f}, htype={htype}, path={picked[0]}")
    return layer_results

def calculate_building_image_paths(
    user_data: List[List[float]],
    verbose: bool = False
) -> List[List[str]]:
    """
    返回: [前景(3张图片), layer1, ..., layerN] (len(result) == num_layers+1)
    前景始终为第一项，后面依次为各层（顺序为从前到后，layer1最前，layerN最后）。
    先挑选前景3张图片，再为各层挑选图片，确保所有图片都不重复。
    每层优先从对应文件夹选，用完后用generic，用完报错。
    verbose=True 时，打印每个建筑的 user data、htype、选中的图片路径。
    """
    img_root = config['img_root']
    layer_regions = config['layer_regions']
    layer_folders = config['layer_folders']
    generic_folder = 'generic'
    num_layers = len(layer_regions)
    layer_results = []

    # 校验 user_data 长度
    if len(user_data) != num_layers:
        raise ValueError(f'user_data 长度 {len(user_data)} 与 layer 数量 {num_layers} 不一致!')

    # 只为 layer_folders 里出现过的目录（去重）和 generic 目录准备可用图片列表副本
    needed_folders = list(set(layer_folders + [generic_folder]))
    available_images = {}
    for folder in needed_folders:
        if folder not in config['image_paths']:
            # 如果配置中没有该文件夹，抛出异常
            raise ValueError(f'文件夹 "{folder}" 不在 {img_root} 中，请检查配置和图片目录结构！')
        available_images[folder] = {}
        for htype, imglist in config['image_paths'][folder].items():
            available_images[folder][htype] = imglist.copy()

    if verbose:
        print(f"=========挑选: 开始=========")
    # 先挑选前景3张图片（h0），从layer_folders[0]文件夹选，用完后用generic
    foreground_paths = _pick_images_for_layer(user_data, 0, True, available_images, layer_regions, layer_folders, generic_folder, verbose=verbose)
    
    # 再为各层挑选图片
    for layer_idx in range(num_layers):
        layer_paths = _pick_images_for_layer(user_data, layer_idx, False, available_images, layer_regions, layer_folders, generic_folder, verbose=verbose)
        layer_results.append(layer_paths)
    if verbose:
        print(f"=========挑选: 结束=========")
    
    # 返回顺序: [前景, layer1, ..., layerN]
    return [foreground_paths] + layer_results 
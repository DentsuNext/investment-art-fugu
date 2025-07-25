import os
import json

config = {
    # 图片库地址
    "img_root": "imgset",    
    # 每层建筑所来自的地区
    "layer_regions": ["china", "global", "overseas", "others"],
    # 每层建筑图片所来自的文件夹名称
    "layer_folders": ["china", "global", "global", "generic"],
    # 每个地区内, 根据高度划分的子文件夹
    "height_types": ["h0", "h1", "h2", "h3", "h4"],
    # 生成图片的分辨率
    "resolution": (956, 671),
    # 线条宽度
    "line_width": 2,
    # 每个图层包含的建筑数量
    "buildings_per_layer": 13,  
    # 高度分割: 用户数据小于0.2的将选择h0文件夹内的建筑, 大于等于0.2小于0.4的选择h1内的建筑, 依次类推
    "height_boundaries": [0.3, 0.4, 0.6, 0.8],
    # 用户数据若小于这个值, 则不会为这个点绘制建筑
    "height_threshold": 0.15,
    # 建筑可以叠加的颜色
    "overlay_colors": {
        "gold": "assets/gold.png",    # 金色
        "silver": "assets/silver.png",  # 银色
        "copper": "assets/copper.png"    # 铜色
    },
    # 每层建筑后面, 折线下方的背景颜色
    "layer_colors": [
        (206, 114, 114, 255),   #第一层
        (252, 200, 85, 255),    #第二层
        (206, 155, 82, 255),    #第三层
        (168, 144, 110, 255)    #第四层       
    ],
    # 第一层前再额外显示的建筑数量
    "extra_building_count": 3,    
}

def build_image_paths(config):
    img_root = config["img_root"]
    height_types = config["height_types"]
    layer_folders = config["layer_folders"]
    layer_regions = config["layer_regions"]
    # 检查 layer_folders 和 layer_regions 数量是否一致
    if len(layer_folders) != len(layer_regions):
        raise ValueError(f'layer_folders 和 layer_regions 数量不一致: {len(layer_folders)} vs {len(layer_regions)}，请检查配置！')
    # 检查 layer_folders 是否都存在
    subfolders = [f for f in os.listdir(img_root) if os.path.isdir(os.path.join(img_root, f))]
    for folder in set(layer_folders):
        if folder not in subfolders:
            raise ValueError(f'layer_folders 中的文件夹 "{folder}" 不存在于 {img_root} 目录下，请检查配置和目录结构！')
    # 读取所有子文件夹
    image_paths = {}
    for folder in subfolders:
        image_paths[folder] = {}
        for htype in height_types:
            subdir = os.path.join(img_root, folder, htype)
            if not os.path.isdir(subdir):
                continue
            files = [f for f in os.listdir(subdir) if f.lower().endswith('.png') and not f.startswith('._')]
            image_paths[folder][htype] = [os.path.join(subdir, f) for f in files]
    return image_paths

config["image_paths"] = build_image_paths(config)

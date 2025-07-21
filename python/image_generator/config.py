import os
import json

img_root = "imgset"

categories = ["asia", "us", "china", "generic"]
height_types = ["h0", "h1", "h2", "h3", "h4"]

# Precompute all image paths for each region/height_type
image_paths = {}
for region in categories:
    image_paths[region] = {}
    for htype in height_types:
        folder = os.path.join(img_root, region, htype)
        if not os.path.isdir(folder):
            continue
        files = [f for f in os.listdir(folder) if f.lower().endswith('.png') and not f.startswith('._')]
        # Store full paths
        image_paths[region][htype] = [os.path.join(folder, f) for f in files]

config = {
    "img_root": img_root,
    "categories": categories,
    "height_types": height_types,
    "image_paths": image_paths,
      
    # 生成图片的分辨率
    "resolution": (956, 671),
    # 线条宽度
    "line_width": 2,
    # 每个图层包含的建筑数量
    "buildings_per_layer": 13,  
    # 高度分割: 用户数据小于0.2的将选择h0文件夹内的建筑, 大于等于0.2小于0.4的选择h1内的建筑, 依次类推
    "height_boundaries": [0.2, 0.4, 0.6, 0.8],
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
    "extra_building_count": 3
}

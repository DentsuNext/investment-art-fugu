import os
import json

def count_images(folder: str, output_file: str = "__imagecount__.json"):
    """统计主文件夹下各region的h0-h4子文件夹图片数量，并写入JSON到同级目录"""
    result = {}
    # 遍历每个region（一级子文件夹）
    for region in [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]:
        region_path = os.path.join(folder, region)
        counts = []
        # 统计h0-h4子文件夹下的png图片数量
        for sub in ['h0', 'h1', 'h2', 'h3', 'h4']:
            sub_path = os.path.join(region_path, sub)
            if os.path.isdir(sub_path):
                count = len([f for f in os.listdir(sub_path) if f.lower().endswith('.png') and not f.startswith('._')])
            else:
                count = 0
            counts.append(str(count))
        # 用逗号拼接
        result[region] = ','.join(counts)
    # 输出文件始终写到folder目录下
    output_path = os.path.join(folder, os.path.basename(output_file))
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Image counts written to {output_path}") 
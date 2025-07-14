import os
import sys
import argparse
import json
import random
from typing import List, Dict
from PIL import Image

# 将文件夹（及可选的所有子文件夹）下的所有png图片重命名为0.png, 1.png, ...
def rename_images(folder: str, include_subfolder=False):
    """将指定文件夹及其所有子文件夹下的图片按序号重命名为0.png, 1.png..."""
    def all_dirs(root):
        # 生成器，遍历所有需要处理的文件夹
        for dirpath, dirnames, _ in os.walk(root):
            yield dirpath
            if not include_subfolder:
                break  # 如果不递归，仅处理根目录
    for current_folder in all_dirs(folder):
        if not os.path.isdir(current_folder):
            continue
        # 找到当前文件夹下所有png图片
        files = [f for f in os.listdir(current_folder) if f.lower().endswith('.png') and os.path.isfile(os.path.join(current_folder, f))]
        files.sort()
        # 第一步，先重命名为临时名，避免覆盖
        for idx, fname in enumerate(files):
            src = os.path.join(current_folder, fname)
            tmp_dst = os.path.join(current_folder, f"tmp_{idx}.png")
            os.rename(src, tmp_dst)
        # 第二步，将临时名统一改为最终序号名
        tmp_files = [f for f in os.listdir(current_folder) if f.startswith('tmp_') and f.endswith('.png')]
        tmp_files.sort()
        for idx, fname in enumerate(tmp_files):
            src = os.path.join(current_folder, fname)
            dst = os.path.join(current_folder, f"{idx}.png")
            os.rename(src, dst)
        print(f"Renamed {len(tmp_files)} images in {current_folder}")

# 统计每个region（如china, asia, us, generic）下各h0-h4子文件夹的图片数量，并写入JSON到同级目录
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
                count = len([f for f in os.listdir(sub_path) if f.lower().endswith('.png')])
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

# 自动裁剪文件夹下所有png图片的透明边界
def auto_crop_images(folder: str):
    """自动裁剪文件夹下所有png图片的透明边界"""
    files = [f for f in os.listdir(folder) if f.lower().endswith('.png')]
    for fname in files:
        path = os.path.join(folder, fname)
        print(f"Auto-cropping {fname}")
        img = Image.open(path)
        # 有alpha通道则裁剪透明边界
        if img.mode in ("RGBA", "LA"):
            bbox = img.getbbox()
            if bbox:
                cropped = img.crop(bbox)
                cropped.save(path)
        else:
            # 非透明图片可扩展裁剪纯色边界
            pass
    print(f"-----------------------------------------------")
    print(f"Auto-cropped {len(files)} images in {folder}")

# 按图片宽高比分箱，将图片移动到对应子文件夹下
def split_images_by_ratio(folder: str, out_folder=None, ratios=None, subfolders=None):
    """
    按图片宽高比分箱，将图片移动到对应子文件夹：
    - out_folder: 输出根目录（默认与folder相同）
    - ratios: 分箱阈值（默认[0.2, 0.4, 0.7, 1]）
    - subfolders: 分箱子文件夹名（默认['h0', 'h1', 'h2', 'h3', 'h4']）
    每张图片根据宽高比分配到对应子文件夹
    """
    if ratios is None:
        ratios = [0.2, 0.4, 0.7, 1]
    if subfolders is None:
        subfolders = ['h0', 'h1', 'h2', 'h3', 'h4']
    if out_folder is None:
        out_folder = folder
    files = [f for f in os.listdir(folder) if f.lower().endswith('.png')]
    assignments = []
    for fname in files:
        path = os.path.join(folder, fname)
        try:
            img = Image.open(path)
            width, height = img.size
            r = width / height if height != 0 else 0
        except Exception as e:
            print(f"Error reading {fname}: {e}")
            r = 0
        # 根据宽高比分箱
        if r > ratios[3]:
            bin_idx = 0
        elif r > ratios[2]:
            bin_idx = 1
        elif r > ratios[1]:
            bin_idx = 2
        elif r > ratios[0]:
            bin_idx = 3
        else:
            bin_idx = 4
        assignments.append((fname, bin_idx))
        print(f"ratio of {fname} is {r:.2f}, moving to {subfolders[bin_idx]}")
    # 移动图片到对应输出文件夹
    for fname, bin_idx in assignments:
        target_dir = os.path.join(out_folder, subfolders[bin_idx])
        os.makedirs(target_dir, exist_ok=True)
        src = os.path.join(folder, fname)
        dst = os.path.join(target_dir, fname)
        os.rename(src, dst)
    print(f"Split {len(files)} images into {subfolders} under {out_folder} by ratio bins {ratios}")

# 交互式菜单，供用户选择图片管理功能
def interactive_menu(folder):
    print("Image Management Toolkit")
    print("1. Rename images")
    print("2. Count images and write to file")
    print("3. Auto-crop images")
    print("4. Split images by ratio")
    choice = input("Select function (1-4): ").strip()
    if choice == '1':
        include_subfolder = input("Include subfolders for renaming? (y/n): ").strip().lower() == 'y'
        rename_images(folder, include_subfolder)
    elif choice == '2':
        output_file = input("Enter output JSON file [default: __imagecount__.json]: ").strip() or "__imagecount__.json"
        count_images(folder, output_file)
    elif choice == '3':
        auto_crop_images(folder)
    elif choice == '4':
        ratio_str = input("Enter ratios (comma separated, e.g. 0.7,0.2,0.1): ").strip()
        out_folders = input("Enter output folders (comma separated): ").strip().split(',')
        ratios = [float(r) for r in ratio_str.split(',')]
        split_images_by_ratio(folder, out_folders, ratios)
    else:
        print("Invalid choice.")

# 主入口，命令行参数解析和分发
def main():
    parser = argparse.ArgumentParser(description="Image Management Toolkit")
    parser.add_argument('folder', nargs='?', default=None, help='Source folder for interactive menu')
    parser.add_argument('--rename', type=str, help='Rename images in the specified folder')
    parser.add_argument('--count', nargs='*', metavar=('FOLDER', 'OUTFILE'), help='Count images and write to OUTFILE (default: __imagecount__.json)')
    parser.add_argument('--crop', type=str, help='Auto-crop images in the specified folder')
    parser.add_argument('--split', nargs='+', metavar='ARGS', help='Split images by ratio. Usage: --split FOLDER [OUTFOLDER] [RATIOS] [SUBFOLDERS] (OUTFOLDER, RATIOS, and SUBFOLDERS are optional; RATIOS and SUBFOLDERS are comma separated, OUTFOLDER is root output dir). Example: --split ./imgset ./output "0.2,0.4,0.7,1" "h0,h1,h2,h3,h4"')
    args = parser.parse_args()

    # 仅提供folder参数时进入交互菜单
    if (len(sys.argv) == 2 and args.folder and not (args.rename or args.count or args.crop or args.split)):
        interactive_menu(args.folder)
        return
    if len(sys.argv) == 1:
        print("Error: You must specify the source folder as a positional argument.")
        print("Usage: python image_manager.py <folder>")
        return
    if args.rename:
        include_subfolder = input("Include subfolders for renaming? (y/n): ").strip().lower() == 'y'
        rename_images(args.rename, include_subfolder)
    if args.count:
        if len(args.count) == 0:
            count_images(args.folder, "__imagecount__.json")
        elif len(args.count) == 1:
            count_images(args.count[0], "__imagecount__.json")
        else:
            count_images(args.count[0], args.count[1])
    if args.crop:
        auto_crop_images(args.crop)
    if args.split:
        # 解析split_images_by_ratio的参数
        split_args = args.split
        folder = split_args[0]
        out_folder = folder  # 默认输出根目录
        ratios = None
        subfolders = None
        if len(split_args) > 1:
            # 第二个参数如果像ratio或子文件夹列表，则跳过，否则视为out_folder
            if ',' in split_args[1] or split_args[1].replace('.', '', 1).isdigit():
                pass
            else:
                out_folder = split_args[1]
        if len(split_args) > 1:
            if out_folder == folder and (',' in split_args[1] or split_args[1].replace('.', '', 1).isdigit()):
                ratios = [float(r) for r in split_args[1].split(',')]
        if len(split_args) > 2:
            if out_folder != folder:
                ratios = [float(r) for r in split_args[2].split(',')]
            else:
                subfolders = split_args[2].split(',')
        if len(split_args) > 3:
            subfolders = split_args[3].split(',')
        split_images_by_ratio(folder, out_folder, ratios, subfolders)

if __name__ == "__main__":
    main() 
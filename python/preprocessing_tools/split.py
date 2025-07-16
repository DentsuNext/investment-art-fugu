import os
from PIL import Image

def split_images(folder: str, out_folder=None, ratios=None, subfolders=None):
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
    files = [f for f in os.listdir(folder) if f.lower().endswith('.png') and not f.startswith('._')]
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
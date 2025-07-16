import os

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
        files = [f for f in os.listdir(current_folder) if f.lower().endswith('.png') and os.path.isfile(os.path.join(current_folder, f)) and not f.startswith('._')]
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
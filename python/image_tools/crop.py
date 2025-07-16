import os
from PIL import Image

def crop_images(folder: str, include_subfolders=False):
    """
    自动裁剪文件夹下所有png图片的透明边界。
    如果 include_subfolders=True，则递归处理所有子文件夹。
    """
    def all_dirs(root):
        for dirpath, dirnames, _ in os.walk(root):
            yield dirpath
            if not include_subfolders:
                break
    for current_folder in all_dirs(folder):
        files = [f for f in os.listdir(current_folder) if f.lower().endswith('.png') and not f.startswith('._')]
        for fname in files:
            path = os.path.join(current_folder, fname)
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
        print(f"-------")
        print(f"Auto-cropped {len(files)} images in {current_folder}")
        print(f"-----------------------------------------------") 
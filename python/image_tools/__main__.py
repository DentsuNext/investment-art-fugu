import argparse
from .rename import rename_images
from .count import count_images
from .crop import crop_images
from .split import split_images

def main():
    parser = argparse.ArgumentParser(description="Image Management Toolkit")
    parser.add_argument('--rename', type=str, help='Rename images in the specified folder')
    parser.add_argument('--rename-subfolders', action='store_true', help='Include subfolders when renaming')
    parser.add_argument('--count', nargs=2, metavar=('FOLDER', 'OUTFILE'), help='Count images and write to OUTFILE')
    parser.add_argument('--crop', type=str, help='Auto-crop images in the specified folder')
    parser.add_argument('--crop-subfolders', action='store_true', help='Include subfolders when cropping')
    parser.add_argument('--split', nargs='+', metavar='ARGS', help='Split images by ratio. Usage: --split FOLDER [OUTFOLDER] [RATIOS] [SUBFOLDERS] (OUTFOLDER, RATIOS, and SUBFOLDERS are optional; RATIOS and SUBFOLDERS are comma separated, OUTFOLDER is root output dir).')
    args = parser.parse_args()

    if not any(vars(args).values()):
        # 交互式菜单
        print("Image Management Toolkit")
        print("1. Auto-crop images")
        print("2. Split images by ratio")
        print("3. Rename images")
        print("4. Count images and write to file")
        choice = input("Select function (1-4): ").strip()
        if choice == '1':
            folder = input("Enter folder path: ").strip()
            include_subfolder = input("Include subfolders for cropping? (y/n): ").strip().lower() == 'y'
            crop_images(folder, include_subfolder)
        elif choice == '2':
            folder = input("Enter source folder path: ").strip()
            out_folder = input("Enter output root folder (leave blank to use source folder): ").strip() or None
            ratio_str = input("Enter ratios (comma separated, e.g. 0.2,0.4,0.7,1): ").strip()
            ratios = [float(r) for r in ratio_str.split(',')] if ratio_str else None
            subfolders_str = input("Enter subfolder names (comma separated, e.g. h0,h1,h2,h3,h4): ").strip()
            subfolders = subfolders_str.split(',') if subfolders_str else None
            split_images(folder, out_folder, ratios, subfolders)
        elif choice == '3':
            folder = input("Enter folder path: ").strip()
            include_subfolder = input("Include subfolders for renaming? (y/n): ").strip().lower() == 'y'
            rename_images(folder, include_subfolder)
        elif choice == '4':
            folder = input("Enter folder path: ").strip()
            output_file = input("Enter output JSON file [default: __imagecount__.json]: ").strip() or "__imagecount__.json"
            count_images(folder, output_file)
        else:
            print("Invalid choice.")
    else:
        if args.rename:
            rename_images(args.rename, args.rename_subfolders)
        if args.count:
            count_images(args.count[0], args.count[1])
        if args.crop:
            crop_images(args.crop, args.crop_subfolders)
        if args.split:
            # Flexible parsing for split: FOLDER [OUTFOLDER] [RATIOS] [SUBFOLDERS]
            split_args = args.split
            folder = split_args[0]
            out_folder = None
            ratios = None
            subfolders = None
            if len(split_args) > 1:
                out_folder = split_args[1]
            if len(split_args) > 2:
                ratios = [float(r) for r in split_args[2].split(',')]
            if len(split_args) > 3:
                subfolders = split_args[3].split(',')
            split_images(folder, out_folder, ratios, subfolders)

if __name__ == "__main__":
    main() 
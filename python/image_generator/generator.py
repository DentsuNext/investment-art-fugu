import os
import random
from typing import List, Optional
from PIL import Image, ImageDraw
from .config import config
from .utils import getShiftedUserDataID

# 生成最终图片的主函数
def generate_final_image(
    user_data: List[List[float]],  # 每层的用户数据，二维数组。前面的数据会被绘制在前排, 后面的数据会被绘制在后排
    building_image_paths: List[List[str]],  # selector输出的图片路径，[前景, layer1, ..., layerN]
    color_name: str = 'gold',  # 建筑叠加色名称，可选 'gold', 'silver', 'copper'
    output_path: str = 'output.png',  # 输出图片路径
    verbose: bool = False,
    guides: bool = False
):
    """
    根据用户数据和已选图片路径生成最终图片。
    user_data: 每层的用户数据，二维数组。前面的数据会被绘制在前排, 后面的数据会被绘制在后排
    building_image_paths: selector输出的图片路径，[前景, layer1, ..., layerN]
    output_path: 输出图片路径
    color_name: 建筑叠加色名称，可选 'gold', 'silver', 'copper'
    verbose: 是否输出print信息（默认读取config）
    guides: 是否显示辅助线（边框、蓝点等，默认读取config）
    """
    
    # 配置参数
    size = config['resolution']
    line_width = config['line_width']
    overlay_colors = config['overlay_colors']
    layer_colors = config['layer_colors']
    num_layers = len(user_data)
    buildings_per_layer = config['buildings_per_layer']
    points_per_line = [len(layer_data) for layer_data in user_data]
    extra_building_count = config['extra_building_count']


    # 本地资源路径
    bg_gradient_path = 'assets/bg-gradient.png'
    line_gradient_path = 'assets/line-gradient.jpg'
    overall_bg_path = 'assets/bg.png'

    # 加载背景和渐变图片
    bg_gradient = Image.open(bg_gradient_path).convert('RGBA')
    line_gradient = Image.open(line_gradient_path).convert('RGBA')
    overall_bg = Image.open(overall_bg_path).convert('RGBA').resize(size)

    # 读取金银铜渐变图并resize到画布大小（路径从config获取）
    gradient_img = Image.open(overlay_colors[color_name]).convert('RGBA').resize(size)

    if verbose:
        print(f"=========绘制: 开始=========")
    # 1. 生成每层背景（折线下方区域，渐变+色块）
    backgrounds = []
    for i in range(num_layers):
        line_data = user_data[i]
        points = [(int(x*size[0]/(points_per_line[i]-1)), int(size[1] - y*size[1])) for x, y in enumerate(line_data)]
        poly = points + [(size[0], size[1]), (0, size[1])]
        mask = Image.new('L', size, 0)
        ImageDraw.Draw(mask).polygon(poly, fill=255)
        color_bg = Image.new('RGBA', size, layer_colors[i % len(layer_colors)])
        grad_bg = bg_gradient.resize(size)
        color_with_grad = color_bg.copy()
        color_with_grad.putalpha(grad_bg.split()[-1])
        layer_bg = Image.new('RGBA', size, (0,0,0,0))
        layer_bg.paste(color_with_grad, (0,0), mask)
        backgrounds.append(layer_bg)

    # 2. 生成每层建筑（横向依次排开，底部对齐，等比缩放）
    buildings = []
    debug_point_list = []  # 存储每个建筑对应的折线点坐标
    # building_image_paths: [前景, layer1, ..., layerN]
    # user_data: [layer1, layer2, ..., layerN](layer1最前，layerN最后)
    # building_image_paths[1]对应user_data[0], ..., building_image_paths[num_layers]对应user_data[num_layers-1]
    for i in range(num_layers):
        layer = Image.new('RGBA', size, (0,0,0,0))  # 全透明
        chosen_imgs = building_image_paths[i+1]  # i=0对应layer1, i=num_layers-1对应layerN
        line_data = user_data[i]

        # 绘制常规层. 为避免完全遮挡, 每层会有一个水平偏移
        for j, img_path in enumerate(chosen_imgs):   
            if img_path == "":
                if verbose:
                    print(f"[第{i+1}层] building={j}, skip drawing")
                continue

            idx = getShiftedUserDataID(user_data, num_layers, buildings_per_layer, i, j)
            x_center = int(idx / (points_per_line[i]-1) * size[0])   
            
            strict_idx = max(0, min(idx, points_per_line[i]-1))
            h_ratio = line_data[strict_idx]
            h = int(size[1] * h_ratio)
            if verbose:
                print(f"[第{i+1}层] building={j}, idx = {idx}, x_center = {x_center}")

            draw_building(layer, img_path, x_center, h, gradient_img, verbose, guides, debug_point_list)              

        # 如果是最前层（layer1），同时绘制3个前景建筑
        if i == 0 and extra_building_count > 0:
            fg_imgs = building_image_paths[0]
            for j, img_path in enumerate(fg_imgs):
                x_center = int((j+0.5) / extra_building_count * size[0])
                h_ratio = 0.2 + (random.random()-0.5) * 2 * 0.1
                h = int(size[1] * h_ratio)
                draw_building(layer, img_path, x_center, h, gradient_img, verbose, guides, debug_point_list)

        buildings.append(layer)

    # 3. 生成每层折线图
    lines = []
    for i in range(num_layers):
        layer = Image.new('RGBA', size, (0,0,0,0))  # 全透明
        line_data = user_data[i]
        points = [(int(x*size[0]/(points_per_line[i]-1)), int(size[1] - y*size[1])) for x, y in enumerate(line_data)]
        layer = draw_gradient_line(layer, points, line_gradient, width=line_width)
        lines.append(layer)

    # 4. 输出单层的建筑图    
    layer_output_name, layer_output_ext = os.path.splitext(output_path)
    for i in range(num_layers):
        layer = Image.new('RGBA', size, (0,0,0,0))  # 全透明
        layer = Image.alpha_composite(layer, buildings[i])
        layer = Image.alpha_composite(layer, lines[i])
        layer_output_path = layer_output_name+str(i+1)+layer_output_ext
        layer.save(layer_output_path)
        if verbose:
            print(f'单层图片已保存到 {layer_output_path}')

    # 5. 合成最终海报：白色底+assets/bg.png+每层内容
    base = Image.new('RGBA', size, (255,255,255,255))
    base = Image.alpha_composite(base, overall_bg)
    # 合成时要反向叠加, user_data中前面的数据会被绘制在前排, 后面的数据会被绘制在后排
    # Draw from back to front: layerN (back) ... layer1 (front)
    for i in range(num_layers-1, -1, -1):
        base = Image.alpha_composite(base, backgrounds[i])
        base = Image.alpha_composite(base, buildings[i])
        base = Image.alpha_composite(base, lines[i])
    
    # guides控制辅助线: 在折线点上画蓝色小圆点（建筑画完后再画，避免被遮挡）
    if guides:
        draw = ImageDraw.Draw(base)
        for pt_x, pt_y in debug_point_list:
            r = 5
            draw.ellipse([pt_x-r, pt_y-r, pt_x+r, pt_y+r], fill=(0,0,255,255))

    # 保存图片
    base.save(output_path)
    if verbose:
        print(f"=========绘制: 结束=========")
    if verbose:
        print(f'最终图片已保存到 {output_path}')


def draw_building(layer:Image, img_path, img_center_x, img_dst_height, gradient_img, verbose, guides, debug_point_list):
    """
    在指定的图层上绘制单个建筑。

    函数会根据目标高度等比缩放建筑图片，并将其水平居中放置在指定位置，然后应用渐变色，
    最终将处理后的建筑合成到图层上。

    :param layer: PIL.Image, 目标图层，建筑将被绘制在这上面。
    :param img_path: str, 建筑图片的路径。
    :param img_center_x: int, 建筑在图层上的目标水平中心点 x 坐标。
    :param img_dst_height: int, 建筑的目标高度（会等比缩放）。
    :param gradient_img: PIL.Image, 用于色彩映射的渐变图。
    :param guides: bool, 是否记录调试信息（建筑的落点坐标）。
    :param debug_point_list: list, 用于存储调试点的列表。
     """ 
    img = Image.open(img_path).convert('RGBA')
    orig_w, orig_h = img.size
    scale = img_dst_height / orig_h
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    img = img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)
    paste_x = img_center_x - (new_w // 2) 
    paste_y = layer.size[1] - img_dst_height
    # 使用ColorMap方式混合
    blended = blend_building_with_gradient(img, gradient_img)
    layer.alpha_composite(blended, (paste_x, paste_y))

    if verbose:
        print(f"left = {paste_x}, top = {paste_y}, width = {new_w}, height = {new_h}")

    if guides:
        # 中文注释: 记录每个建筑对应的折线点坐标
        debug_point_list.append((img_center_x, paste_y))
        # 中文注释: 同时画出img的边框用来debug
        draw = ImageDraw.Draw(layer)
        rect_coords = (paste_x, paste_y, paste_x + new_w, paste_y + new_h)
        draw.rectangle(rect_coords, outline="red", width=1)



def blend_building_with_gradient(img, gradient_img, vmin=0.0, vmax=1.0, amount=1.0):
    """
    按HLSL ColorMap方式，将建筑图片img的亮度映射到渐变图gradient_img的横坐标，实现色彩映射。
    amount=1时完全使用映射色，amount=0时返回原图，介于0-1时线性混合。
    vmin/vmax用于裁剪RGB后再计算亮度。
    :param img: 单个建筑图片，RGBA
    :param gradient_img: 整体渐变图，RGBA，已resize到画布大小
    :param vmin: RGB下界，默认0
    :param vmax: RGB上界，默认1
    :param amount: 映射色占比，0-1
    :return: 叠加后的RGBA图片，尺寸与img一致
    """
    from PIL import Image
    import numpy as np
    # 1. 获取原图像素并归一化到[0,1]
    arr = np.array(img).astype(np.float32) / 255.0  # [0,1]
    # 2. 对RGB进行clip，防止极端值影响亮度映射
    arr[..., :3] = np.clip(arr[..., :3], vmin, vmax)
    # 3. 计算亮度（luminance），采用ITU-R BT.709标准
    lumi = 0.2126 * arr[...,0] + 0.7152 * arr[...,1] + 0.0722 * arr[...,2]
    lumi = np.clip(lumi, 0, 1)
    # 4. 采样渐变图（横坐标为lumi，纵坐标为0.5），即用亮度查表获得目标色
    grad_w, grad_h = gradient_img.size
    grad_arr = np.array(gradient_img).astype(np.float32) / 255.0
    y_idx = int(grad_h * 0.5)
    color = np.zeros(arr.shape)
    for i in range(img.height):
        for j in range(img.width):
            x_idx = int(lumi[i,j] * (grad_w-1))
            color[i,j,:3] = grad_arr[y_idx, x_idx, :3]
            color[i,j,3] = arr[i,j,3]  # alpha保持原值
    # 5. 按amount参数与原色线性混合
    if amount < 1.0:
        color[..., :3] = arr[..., :3] * (1-amount) + color[..., :3] * amount
    # 6. 转回PIL图片输出
    out = (color * 255).astype(np.uint8)
    blended = Image.fromarray(out, mode='RGBA')
    return blended

# 折线绘制函数（抗锯齿渐变线条）
def draw_gradient_line(img, points, gradient_img, width=8, scale=4):
    """
    在图片上绘制带抗锯齿效果的渐变折线。

    该函数通过先在放大尺寸的画布上绘制线条，然后再缩小的方式来实现抗锯齿。
    线条的颜色来自于传入的渐变图。

    :param img: PIL.Image, 需要绘制线条的图片。
    :param points: list, 折线所有顶点的坐标列表，格式为 [(x1, y1), (x2, y2), ...]。
    :param gradient_img: PIL.Image, 作为线条颜色的渐变图。
    :param width: int, 线条的宽度。
    :param scale: int, 抗锯齿效果的上采样倍数，值越大效果越好但计算量越大。
    :return: PIL.Image, 绘制了渐变线条后的图片。
    """
    big_size = (img.size[0]*scale, img.size[1]*scale)
    mask = Image.new('L', big_size, 0)
    draw = ImageDraw.Draw(mask)
    big_points = [(x*scale, y*scale) for x, y in points]
    big_width = width * scale
    draw.line(big_points, fill=255, width=big_width)
    for pt in big_points:
        x, y = pt
        r = big_width // 2
        draw.ellipse([x - r, y - r, x + r, y + r], fill=255)
    mask = mask.resize(img.size, resample=Image.Resampling.LANCZOS)
    grad = gradient_img.resize(img.size)
    img.paste(grad, (0,0), mask)
    return img
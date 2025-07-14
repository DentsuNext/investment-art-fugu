import os
import glob
import random
from PIL import Image, ImageDraw
import numpy as np

# 线条数据
api_data = [0.6384532879572101,0.6722419265351831,0.7150069025046927,0.7950014287474461,0.7947472945790489,0.7401317673768544,0.722553607379248,0.710701473808543,0.7486681462855103,0.8164330856107183,0.8681893211318872,0.8817548877567277,0.9349614485890521,0.964264007668949,0.9190144637729916,0.8897349483646959,0.8271815423739173,0.7643971036758967,0.7279158765564631,0.6979542578586894,0.7233332713748055,0.7747760093414968,0.7853260643053066,0.8180706957387998,0.8012979895544359,0.7803295857794137,0.7741721301053544,0.8194357198485236,0.8123604227389977,0.7609153840702542,0.7184480029064213,0.6879150533424416,0.7401742771372042,0.7759490865669978,0.7706585181576572,0.7193308153776672,0.6562197847270008,0.6374215237935422,0.5711044458527876,0.5336893307666897,0.5230385777263182,0.5697626660827446,0.5886864215912023,0.6511636997489193,0.6707873544093793,0.6600810577997347,0.6374397917523359,0.6120722429801783,0.5389905525865505,0.5009884389941488,0.45042327309431557,0.45090859577782777,0.5918579389934034,0.5629251234054288,0.497865775042301,0.5001521970745436,0.41577803883284,0.37752034651258365,0.40986274240789383,0.41811184467158874,0.4726907428326413,0.5414148488621398,0.5521786297677965,0.623958433820216,0.6544862013609147,0.6848326296745111,0.7293415403705625,0.6702789533707362,0.6582040232212212,0.6022059353973668,0.5715271380167248,0.48669858342531136,0.4531680642775446,0.5089018854148528,0.5441697000018825,0.6251733733314658,0.6617058227369321,0.6940778733701741,0.7305809435481159,0.7872230015697701,0.8050480002628514,0.8418668435205406,0.8791737552246597,0.9249181478204946,0.9845238855330636,0.9480950577209271,0.9291779962699995,0.8926954211272546,0.8517785219149219,0.8415764467823856,0.8025490472194202,0.7491707500795712,0.7057606746875817,0.6864074510438387,0.6387986170078879,0.6218962538596626,0.6753289643510407,0.683565638606696,0.7262985457541202,0.7687455425527066,0.8084329136479802,0.9001022525759521,0.896870036591346,0.9314359444180033,0.22067398735878385,0.24421171078981718,0.32285387561587225,0.377905455539321,0.41692685632079884,0.4592217941418426,0.47988594762676595,0.5623327018024877,0.5847484810950987,0.5807032999409543,0.5599501894897138,0.5070985201347548,0.4890037584718692,0.41918153007628906,0.39732864461851597,0.3574562565028583,0.2699494449094151,0.27579268577915844,0.26218049477765915,0.3181582712139383,0.38674888351763204,0.42448353727753874,0.41053788276720615,0.33720608897402204,0.3086945978816694,0.28679893387347777,0.20892099170190098,0.17899732024001325,0.1691904837122556,0.18013218904548634,0.18916595669284858,0.2304593378447073,0.30870087216678094,0.31178989639951116,0.402564400280286,0.4196688859999991,0.4627838162544641,0.4592056626484451,0.4471180056212264,0.4379109744442666,0.4744614655142857,0.43264060983080616,0.4127432245511649,0.42448751683518143,0.46744307019141196,0.5457799667350131,0.5606282911952337,0.6268052869160807,0.6500317671217357,0.7150099458820296,0.7638030197741442,0.7985705733091052]

# 配置
size = (956, 671)
num_layers = 3
num_lines = 3
imgs_per_layer = 8
random.seed(42)
def rand_rgba(alpha=128):
    return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255), alpha)

imgset_paths = sorted(glob.glob('imgset/*'))
bg_gradient = Image.open('assets/bg-gradient.png').convert('RGBA')
line_gradient = Image.open('assets/line-gradient.jpg').convert('RGBA')
overall_bg = Image.open('assets/bg.png').convert('RGBA').resize(size)

points_per_line = len(api_data) // num_lines

# 1. 生成每层背景（折线下方区域，渐变+色块）
backgrounds = []
for i in range(num_layers):
    line_data = api_data[i*points_per_line:(i+1)*points_per_line]
    points = [(int(x*size[0]/(points_per_line-1)), int(size[1] - y*size[1])) for x, y in enumerate(line_data)]
    poly = points + [(size[0], size[1]), (0, size[1])]
    mask = Image.new('L', size, 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    color_bg = Image.new('RGBA', size, rand_rgba(180))
    grad_bg = bg_gradient.resize(size)
    color_with_grad = color_bg.copy()
    color_with_grad.putalpha(grad_bg.split()[-1])
    layer_bg = Image.new('RGBA', size, (0,0,0,0))
    layer_bg.paste(color_with_grad, (0,0), mask)
    backgrounds.append(layer_bg)

# 2. 生成每层建筑（横向依次排开，底部对齐，等比缩放）
buildings = []
for i in range(num_layers):
    layer = Image.new('RGBA', size, (0,0,0,0))  # 全透明
    chosen_imgs = [random.choice(imgset_paths) for _ in range(imgs_per_layer)]
    line_data = api_data[i*points_per_line:(i+1)*points_per_line]
    for j, img_path in enumerate(chosen_imgs):
        x0 = int(j * size[0] / imgs_per_layer)
        x1 = int((j+1) * size[0] / imgs_per_layer)
        w = x1 - x0
        center_idx = int((j + 0.5) * points_per_line / imgs_per_layer)
        h_ratio = line_data[min(center_idx, points_per_line-1)]
        h = int(size[1] * h_ratio)
        img = Image.open(img_path).convert('RGBA')
        orig_w, orig_h = img.size
        scale = h / orig_h
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        img = img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)
        paste_x = x0 + (w - new_w) // 2
        paste_y = size[1] - new_h
        layer.alpha_composite(img, (paste_x, paste_y))
    color_overlay = Image.new('RGBA', size, rand_rgba(40))  # 更低透明度
    layer = Image.alpha_composite(layer, color_overlay)
    buildings.append(layer)

# 3. 抗锯齿渐变线条函数
def draw_gradient_line(img, points, gradient_img, width=8, scale=4):
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

# 4. 合成：白色底+assets/bg.png+每层内容
base = Image.new('RGBA', size, (255,255,255,255))
base = Image.alpha_composite(base, overall_bg)
for i in range(num_layers):
    base = Image.alpha_composite(base, backgrounds[i])
    base = Image.alpha_composite(base, buildings[i])
    line_data = api_data[i*points_per_line:(i+1)*points_per_line]
    points = [(int(x*size[0]/(points_per_line-1)), int(size[1] - y*size[1])) for x, y in enumerate(line_data)]
    base = draw_gradient_line(base, points, line_gradient, width=2)

base.save('output.png')
print('output.png generated.') 
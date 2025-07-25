import random
from image_generator import generate_image
from tests.test_user_data import get_test_user_data



if __name__ == '__main__':
    # 选择要测试的场景编号（0~6）
    """
    根据 case 生成不同类型的 user_data 测试数据：
    0. 手写的数据
    1. 正常的随机数据
    2. 某一层为空
    3. 某层中前面一部分的值为0
    4. 第一层中前面一部分的值为0
    5. 某层中, 有些值是为0的
    6. 某层中, 有些值是低于height_threshold的
    """
    case = 0
    user_data = get_test_user_data(case)


    # 生成图片
    generate_image(
        user_data=user_data,           # 二维数组，每层数据为一个数组。 即使层数据为空， 也需要传入空数组
        color_name='copper',             # 金/银/铜渐变，可选: 'gold', 'silver', 'copper'
        output_path='output.png',      # 输出图片的路径名称。单层图片会以文件名加序号的方式保存
        verbose=False,                 # 是否输出详细信息
        guides=False                   # 是否显示辅助线（边框、蓝点等）
    )
    print(f'测试图片已生成: output.png') 



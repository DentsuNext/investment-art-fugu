from typing import Optional
from .selector import calculate_building_image_paths
from .generator import generate_final_image

def generate_image(
    user_data,
    color_name='gold',
    output_path='output.png',
    verbose:bool = False,
    guides:bool = False
):
    """
    一步生成最终合成图片：先选图，再合成。
    :param user_data: 用户数据，二维数组
    :param color_name: "gold", "silver", "copper"三色可选
    :param output_path: 输出图片路径。单层图片会以文件名加序号的方式保存
    :param verbose: 是否输出详细信息
    :param guides: 是否显示辅助线（边框、蓝点等）
    """
    building_image_paths = calculate_building_image_paths(
        user_data=user_data,
        verbose=verbose
    )
    generate_final_image(
        user_data=user_data,
        building_image_paths=building_image_paths,
        color_name=color_name,
        output_path=output_path,
        verbose=verbose,
        guides=guides
    )

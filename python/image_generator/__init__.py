from typing import Optional
from .selector import calculate_building_image_paths
from .generator import generate_final_image

def generate_image(
    user_data,
    num_layers,
    region,
    color_name='gold',
    output_path='output.png',
    allow_duplicate=False,
    verbose:Optional[bool] = None
):
    """
    一步生成最终合成图片：先选图，再合成。
    :param user_data: 用户数据，二维数组
    :param num_layers: 层数
    :param region: 区域
    :param color_name: 金/银/铜
    :param output_path: 输出图片路径
    :param allow_duplicate: 是否允许图片重复
    :param verbose: 是否输出详细信息
    """
    building_image_paths = calculate_building_image_paths(
        user_data=user_data,
        num_layers=num_layers,
        region=region,
        allow_duplicate=allow_duplicate,
        verbose=verbose
    )
    generate_final_image(
        user_data=user_data,
        building_image_paths=building_image_paths,
        color_name=color_name,
        output_path=output_path,
        verbose=verbose
    )

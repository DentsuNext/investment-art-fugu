import random
import pytest
from image_generator.selector import calculate_building_image_paths
from image_generator import config as global_config_mod

def test_normal_case():
    # 正常情况：4层，每层有数据
    num_layers = len(global_config_mod.config["layer_regions"])
    buildings_per_layer = global_config_mod.config["buildings_per_layer"]
    extra_building_count = global_config_mod.config["extra_building_count"]
    user_data = [[random.random() for _ in range(buildings_per_layer)] for _ in range(num_layers)]
    # 前景数据用第一层的前 extra_building_count 个
    user_data[0] = [random.random() for _ in range(buildings_per_layer)]
    result = calculate_building_image_paths(user_data, verbose=True)
    # 检查返回结构
    assert len(result) == num_layers + 1  # 1前景+4层
    assert len(result[0]) == extra_building_count  # 前景图片数量
    for i, layer in enumerate(result[1:], 1):
        assert len(layer) == buildings_per_layer
    # 检查全局唯一性
    all_selected = [img_path for layer in result for img_path in layer if img_path]
    assert len(all_selected) == len(set(all_selected)), "Some images were selected more than once across all layers!"

def test_empty_layer():
    # 某层为空数组
    num_layers = len(global_config_mod.config["layer_regions"])
    buildings_per_layer = global_config_mod.config["buildings_per_layer"]
    extra_building_count = global_config_mod.config["extra_building_count"]
    user_data = [[random.random() for _ in range(buildings_per_layer)] for _ in range(num_layers)]
    user_data[2] = []  # 第三层为空
    result = calculate_building_image_paths(user_data, verbose=True)
    assert len(result) == num_layers + 1
    assert result[3] == []  # 第三层应为空

def test_user_data_length_mismatch():
    # user_data 长度不符应报错
    num_layers = len(global_config_mod.config["layer_regions"])
    buildings_per_layer = global_config_mod.config["buildings_per_layer"]
    user_data = [[random.random() for _ in range(buildings_per_layer)] for _ in range(num_layers + 1)]
    with pytest.raises(ValueError):
        calculate_building_image_paths(user_data)

def test_all_layers_empty():
    # 所有层都为空
    num_layers = len(global_config_mod.config["layer_regions"])
    extra_building_count = global_config_mod.config["extra_building_count"]
    user_data = [[] for _ in range(num_layers)]
    result = calculate_building_image_paths(user_data)
    # 前景有图，其余全空
    assert len(result) == num_layers + 1
    assert result[0] == [] or len(result[0]) == extra_building_count
    for layer in result[1:]:
        assert layer == []

if __name__ == "__main__":
    test_normal_case()
    test_empty_layer()
    test_user_data_length_mismatch()
    test_all_layers_empty()
    print("All tests passed.") 
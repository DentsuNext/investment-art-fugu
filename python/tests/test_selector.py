import random
from building_generator.selector import calculate_building_image_paths
from building_generator import config as global_config_mod

def test_calculate_building_image_paths():
    # Generate random user_data: 4 layers, each with 52 floats in [0, 1]
    user_data = [[random.random() for _ in range(52)] for _ in range(4)]
    num_layers = 4
    region = "china"
    result = calculate_building_image_paths(user_data, num_layers, region)
    print("Result shape:", [[len(layer) for layer in result]])
    # Check result shape
    assert len(result) == 5  # 1 foreground + 4 layers
    assert len(result[0]) == 3  # Foreground always 3 images
    for i, layer in enumerate(result[1:], 1):
        assert len(layer) == global_config_mod.config["buildings_per_layer"]

if __name__ == "__main__":
    test_calculate_building_image_paths()
    print("Test passed.") 
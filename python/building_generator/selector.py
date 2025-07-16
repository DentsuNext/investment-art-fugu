import os
import random
from typing import List
from .config import config

def _pick_images(region, htype, count, chosen, img_root, generic='generic'):
    """
    Pick 'count' images from region/htype, fallback to generic/htype, avoiding duplicates in 'chosen'.
    Returns a list of image paths.
    """
    paths = []
    # Try region first
    region_files = config['image_paths'][region][htype]
    candidates = [i for i in range(len(region_files)) if i not in chosen]
    while len(paths) < count and candidates:
        idx = random.choice(candidates)
        chosen.add(idx)
        paths.append(region_files[idx])
        candidates.remove(idx)
    # Fallback to generic
    if len(paths) < count:
        generic_files = config['image_paths'][generic][htype]
        candidates = [i for i in range(len(generic_files)) if i not in chosen]
        while len(paths) < count and candidates:
            idx = random.choice(candidates)
            chosen.add(idx)
            paths.append(generic_files[idx])
            candidates.remove(idx)
    if len(paths) < count:
        raise RuntimeError(f'Not enough images for {region}/{htype} and fallback generic/{htype}!')
    return paths

def calculate_building_image_paths(
    user_data: List[List[float]],
    num_layers: int,
    region: str
) -> List[List[str]]:
    """
    Returns: [foreground (3 images), layer1, layer2, ...] (len(result) == num_layers+1)
    Foreground is always present and not included in num_layers.
    """
    img_root = config['img_root']
    height_types = config['height_types']
    height_boundaries = config['height_boundaries']
    buildings_per_layer = config['buildings_per_layer']
    categories = config['categories']
    generic = 'generic'
    result = []

    # Use a global chosen set to avoid duplicates across all layers
    chosen_global = set()

    # Foreground: always 3 images, use h0
    foreground_paths = _pick_images(region, 'h0', 3, chosen_global, img_root, generic)
    result.append(foreground_paths)

    # For each layer (not including foreground)
    for layer_idx in range(num_layers):
        layer_paths = []
        layer_data = user_data[layer_idx]
        for b in range(buildings_per_layer):
            # Evenly pick user data point for each building
            idx = int(b / (buildings_per_layer - 1) * (len(layer_data) - 1))
            val = layer_data[idx]
            # Map user data to height type
            htype = None
            for i, boundary in enumerate(height_boundaries):
                if val < boundary:
                    htype = height_types[i]
                    break
            if htype is None:
                htype = height_types[-1]
            # Pick 1 image for this building
            picked = _pick_images(region, htype, 1, chosen_global, img_root, generic)
            layer_paths.append(picked[0])
        result.append(layer_paths)
    return result 
import os
import json

img_root = "imgset"

categories = ["asia", "us", "china", "generic"]
height_types = ["h0", "h1", "h2", "h3", "h4"]

# Precompute all image paths for each region/height_type
image_paths = {}
for region in categories:
    image_paths[region] = {}
    for htype in height_types:
        folder = os.path.join(img_root, region, htype)
        if not os.path.isdir(folder):
            continue
        files = [f for f in os.listdir(folder) if f.lower().endswith('.png') and not f.startswith('._')]
        # Store full paths
        image_paths[region][htype] = [os.path.join(folder, f) for f in files]

config = {
    "img_root": img_root,
    "categories": categories,
    "height_types": height_types,
    "height_boundaries": [0.2, 0.4, 0.6, 0.8],
    "buildings_per_layer": 13,
    "image_paths": image_paths
}

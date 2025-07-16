import os
import json

img_root = "imgset"
imagecount_path = os.path.join(img_root, "__imagecount__.json")

categories = ["asia", "us", "china", "generic"]
height_types = ["h0", "h1", "h2", "h3", "h4"]

try:
    with open(imagecount_path, "r", encoding="utf-8") as f:
        raw_img_count = json.load(f)
except FileNotFoundError:
    raise RuntimeError(f"Required image count file not found: {imagecount_path}")

# Parse the string format into the expected dict format
img_count = {}
for region in categories:
    if region not in raw_img_count:
        raise RuntimeError(f"Region '{region}' missing in {imagecount_path}")
    counts_str = raw_img_count[region]
    counts = [int(x) for x in counts_str.split(",")]
    if len(counts) != len(height_types):
        raise RuntimeError(f"Region '{region}' in {imagecount_path} does not have 5 height type counts")
    img_count[region] = {htype: count for htype, count in zip(height_types, counts)}

config = {
    "img_root": img_root,
    "categories": categories,
    "height_types": height_types,
    "height_boundaries": [0.2, 0.4, 0.6, 0.8],
    "buildings_per_layer": 13,
    "img_count": img_count,
    "random_seed": 42
}

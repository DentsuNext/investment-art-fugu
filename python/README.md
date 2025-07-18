# Investment Art Fugu Python Project

---

## Project Structure

```
python/
├── image_generator/        # Main module for image generation
├── line_generator/         # Module for line generation
├── preprocessing_tools/    # Tools for image preparation and management
├── assets/                 # Static resources (backgrounds, gradients, etc.)
├── imgset/                 # Image library (buildings by region/height)
├── tests/                  # Unit and integration tests
├── README.md
├── requirements.txt
```

---

## How to use

- **Install dependencies**
  ```bash
  pip install -r requirements.txt
  ```

- **One-line image generation:**
  ```python
  from image_generator import generate_image
  # user_data: list of lists, each sublist is one layer's data
  generate_image(
      user_data=user_data,           # 二维数组，每层一个长度为points_per_line的数组
      num_layers=3,                  # 层数
      region='china',                # 区域，可选: 'asia', 'us', 'china'
      color_name='gold',             # 金/银/铜渐变
      output_path='output.png',      # 输出图片的路径名称
      allow_duplicate=False,         # 是否允许图片重复
      verbose=False,                 # 是否输出详细信息
      guides=False                   # 是否显示辅助线（边框、蓝点等）
  )
  ```
  > `user_data` 示例：`[[0.1, 0.2, ...], [0.3, 0.4, ...], ...]`，每层一个数组。

- **Demo:**
运行 `python example.py` 查看完整流程。

---

## Configuration

所有主要参数均在 `image_generator/config.py` 中配置，也可在调用API时临时覆盖。

```python
# 生成图片的分辨率
"resolution": (956, 671),
# 线条宽度
"line_width": 2,
# 每个图层包含的建筑数量
"buildings_per_layer": 13,  
# 高度分割: 用户数据小于0.2的将选择h0文件夹内的建筑, 大于等于0.2小于0.4的选择h1内的建筑, 依次类推
"height_boundaries": [0.2, 0.4, 0.6, 0.8],
# 建筑可以叠加的颜色（渐变图路径）
"overlay_colors": {
    "gold": "assets/gold.png",    # 金色
    "silver": "assets/silver.png",  # 银色
    "copper": "assets/copper.png"   # 铜色
},
# 每层建筑后面, 折线下方的背景颜色
"layer_colors": [
    (206, 114, 114, 255),   # 第一层
    (252, 200, 85, 255),    # 第二层
    (206, 155, 82, 255),    # 第三层
    (168, 144, 110, 255)    # 第四层       
]
```
若需要修改叠加的金银铜三种颜色，请至`/assets`文件夹替换相应图片
> `gold.png`, `silver.png`, `copper.png`（横向渐变，供建筑叠加）

---

## Image preparation

- **图片库结构**
  - 根目录`imgset`可在 `image_generator/config.py` 修改。
  - `imgset/asia/`, `imgset/us/`, `imgset/china/`, `imgset/generic/`：区域建筑图片
  - 每个区域下有 `h0` ~ `h4` 文件夹，分别存放不同高度的建筑
  - **图片格式必须为 `.png`**，文件名可自定义
  - 图片底部不能留有空白

- **辅助工具**
  - `preprocessing_tools` 目录下有 crop, split, rename 工具
  - 用法：
    ```bash
    python -m preprocessing_tools
    ```

---

## Order of layers

- `user_data`: `[layer1, layer2, ..., layerN]`  # layer1为最前排，layerN为最远背景
- `building_image_paths`: `[foreground, layer1, ..., layerN]`
- **绘制顺序**
  - 从后往前绘制：layerN → ... → layer1
  - 每层包含13栋建筑（可在`image_generator/config.py`中调整）
  - 除了用户数据生成的Layer, 还会额外显示一个3张建筑图组成的前景层，建筑图会在对应区域的`h0`文件夹中选择
---
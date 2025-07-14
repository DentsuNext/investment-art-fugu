# Python 图片生成工程

本工程用于生成多层建筑、折线、渐变背景叠加的图片。

## 目录结构

- generate_image.py         主程序
- requirements.txt         Python 依赖
- Dockerfile               Docker 构建文件
- assets/                  素材图片（bg.png, bg-gradient.png, line-gradient.jpg）
- imgset/                  建筑图片素材

---

## 运行方式一：直接用 Python 运行

1. 安装 Python 3.10+（推荐 3.10/3.11）
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行生成图片：
   ```bash
   python generate_image.py
   ```
4. 生成的图片为 `output.png`

---

## 运行方式二：用 Docker 运行（推荐跨平台复现）

1. 安装 Docker
2. 构建镜像：
   ```bash
   docker build -t python-imggen .
   ```
3. 运行生成图片（挂载当前目录，输出文件可直接访问）：
   - Linux/Mac:
     ```bash
     docker run -v $(pwd):/app python-imggen
     ```
   - Windows PowerShell:
     ```powershell
     docker run -v ${PWD}:/app python-imggen
     ```
   - Windows CMD:
     ```cmd
     docker run -v %cd%:/app python-imggen
     ```
4. 生成的图片为 `output.png`

---

## 说明
- 所有素材图片需放在 `assets/` 和 `imgset/` 文件夹下。
- 运行后会在当前目录生成 `output.png`。
- 可根据 `generate_image.py` 修改参数自定义效果。 
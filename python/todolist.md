

# 背景:
这是一个供服务器程序调用的Python模块, 通过传入一系列设置参数和用户数据, 生成建筑图片拼接而成的静态图.
![Reference](assets/ref.png)

--- 

# 算法过程: 
为了更方便的修改和调用模块, 将模块的算法分为两个步骤
1. 通过传入图片设置和用户数据, 计算出应该显示哪些建筑图片
2. 通过传入图片设置, 用户数据, 以及在第一步得出的应该显示的建筑图片列表, 生成最终图片

--- 

## 步骤一: 计算建筑图片列表

### 基本参数: 作为模块的参数, 一经修改, 对之后每次模块调用都生效
- 每层内建筑的个数: int. 所有层内数量一致, 因此需要1个参数.    
- 建筑图片的根目录地址: string. 
- 建筑图片在每个分类下的图片数量: array.
- 用来判断用户数据应该对应哪种高度类型(h0/h1/h2/h3/h4)的分界数组: array.
- 是否打开Verbose模式: bool
### 传入参数: 每次调用模块时动态传入的参数
- 显示几层画面: int
- 每层画面里, 用来生成折线点的用户数据的数组: array. 数据格式说明见下方"用户数据格式"
- 所有层内的建筑, 应从"asia", "us", "china"中的哪个大区中进行选择: int. 选择的具体逻辑见下方"建筑图片挑选逻辑"

### 返回值:
所有图片地址的数组: array.

### 用户数据格式
数据类型为float, 数据范围是[0, 1]. 数字代表占整张图片的高度比例.

### 图片库的组织方式
1. 建筑分为"asia", "us", "china"三个大类, 代表存储着来自asia, us, china三个地区的建筑图片. 还有一个"generic"分类, 代表一般建筑图片, 可以出现在任何地区. 因此, 图片库根目录下一共4个文件夹
2. 每个分类下有h0, h1, h2, h3, h4一共5个文件夹, 按高度存放5种高度的建筑图片

### 建筑图片挑选逻辑
1. 传入的用户数据, 每层会有52个点横向排开, 但建筑只会有13个横向排开, 因此先获取到每个建筑显示位置处, 对应的用户数据点
2. 从对应的地区库中的h0文件夹内, 随机挑选3张图片作为第0层的前景层. 如果图片数量不够了, 就从generic分类下的h0文件夹中选择图片. 
3. 对于第1层到第4层的每个建筑
    1. 将对应的用户数据点转化为应该显示的高度类型(h0/h1/h2/h3/h4)
    2. 从对应的地区库中, 对应的高度类型文件夹中, 随机挑选一张图片, 并且这张图片不能和之前选择的图片重复. 如果图片数量不够了, 就从generic分类下的高度类型文件夹中选择图片. 
4. 将选择的图片地址, 从第0层到第4层, 组成数组, 作为函数返回值

---

## 步骤二: 生成最终图片
### 基本参数:作为模块的参数, 一经修改, 对之后每次模块调用都生效
- 最终图片的分辨率: array
- 每层内折线上的点的个数: int. 所有层内数量一致, 因此需要1个参数.
- 折线的宽度: float. 
- 每层内折线下方的背景要叠加的颜色: array. 由于每层叠加的颜色不同, 一共需要4个颜色参数.
- 每层内建筑的个数: int. 所有层内数量一致, 因此需要1个参数.
- 建筑可以叠加的颜色: array. 一共有金, 银, 铜三种颜色, 因此需要3个颜色参数
- 是否打开Verbose模式: bool.

### 传入参数: 每次调用模块时动态传入的参数
- 显示几层画面: int.
- 每层画面里, 用来生成折线点的用户数据的数组: array. 数据格式说明见下方"用户数据格式"
- 所有层内的建筑图片, 需要和金, 银, 铜三种颜色中的哪种颜色进行叠加: int.

### 返回值:
无

### 用户数据格式
数据类型为float, 数据范围是[0, 1]. 数字代表占整张图片的高度比例.

### 图层绘制顺序(从背景到前景)
1. 总背景(assets/bg.png)
2. 第4层画面
    1. 折线下的背景.  只存在于折线下方, 将layer-bg.png与一个特定颜色叠加后显示. 每层指定的叠加颜色不同, 在基本参数中设置.
    2. 建筑图片. 最左侧的在最下层, 往右依次排开, 共13栋建筑. 
        1. 建筑底部与生成图片的底部对齐, 高度与建筑所在位置的折线图上的点的高度一致, 宽度按图片自身的原比例缩放. 建筑数量可在基本参数中设置. 
        2. 建筑和指定的金, 银, 铜三种颜色中的一种进行叠加显示. 所有层内建筑叠加的颜色为同一种. 与哪种颜色叠加为传入的参数. 
    3. 折线. 由52个点组成, 横向平均分布, 高度来自传入的用户数据(范围[0,1], 数字代表占整张图片的高度比例). 折线和line-gradient.jpg叠加后显示. 折线的宽度可在基本参数中设置. 
3. 第3层画面. 与第4层一致
4. 第2层画面. 与第4层一致
5. 第1层画面. 与第4层一致
6. 第0层画面
    1. 将3张图片作为最前景的建筑, 横向均匀的显示在最前方. 
        1. 高度按照0.2来显示, 宽度按图片自身的原比例缩放. 
        2. 和指定的金, 银, 铜三种颜色中的一种进行叠加显示. 

---

# 开发阶段
1. 可行性验证. 使用随机图片, 开发验证基本的生成图片功能. (已完成)
2. 制作辅助功能, 可以实现自动裁切图片, 分类图片, 统计各个子文件夹中的图片数量, 自动重命名图片. 为之后功能的开发做准备. (已完成)
3. 制作计算建筑图片列表的功能并测试.(已完成)
4. 制作生成最终图片的功能并测试.(已完成)
5. 制作测试例程和撰写使用说明.(已完成)

# ArcSVGTool
 
## 简介

本项目是一个用于将 SVG 路径转换为黑线的工具  
方便谱师在写谱时可以做一些黑线艺术  
可在[`此视频`](https://www.bilibili.com/video/BV1Uz4y1c7hw/)查看使用效果

## 注意事项

__本项目只在 Python 3.12.0 测试过，其他版本的 Python 请自行测试__

---

本项目发布的 exe 程序是由 [`pyinstaller`](https://pypi.org/project/pyinstaller/) 打包的

---

如果你只想要 SVG 路径转换黑线的方法那可以直接使用 [`svg2aff.py`](https://github.com/LAM0578/ArcSVGTool/blob/main/svg2aff.py)  
如果你需要图形化界面需要安装以下几个依赖包：
- [`PyQt5`](https://pypi.org/project/PyQt5/)
    - 用于可视化界面界面
- [`qt_material`](https://pypi.org/project/qt_material/)
    - 用于界面主题
- [`BlurWindow`](https://pypi.org/project/BlurWindow/)
    - 用于毛玻璃窗体效果

---

如果您觉得上面的方法比较麻烦可以到 [`release`](https://github.com/LAM0578/ArcSVGTool/releases) 查看并下载

## 更新日志

### 2023 / 12 / 15 - 上传
- 上传到 GitHub

### 2023 / 12 / 15 - 添加窗体毛玻璃效果
- 增加窗体毛玻璃效果
- ~~删了一些多余的空格~~

### 2023 / 12 / 23 - 修复问题及新增功能
- svg2aff.py 新增 svgPath2Lines 方法
    - 用于预览
- 修复了 svgPath 输入部分可输入 richText 的问题
- 增加预览功能
- 新增自动语言设置功能
    - 根据系统语言, 默认为 en

### 2023 / 12 / 23 - 修复按钮边界尺寸问题
- 修复了按钮边界不正常的问题

### 2023 / 12 / 24 - 增加自适应以及 AFF 预览
- 增加自适应功能
    - 根据屏幕大小和设计大小 `2560x1600` 计算缩放
- 增加 AFF 预览功能

### 2023 / 12 / 24 - 修复问题以及增加限制曲线数量
- 将尺寸数量限制在了 128 以内
- 修复了弹窗没有 OK 按钮的问题
- 修复了曲线数量为 1 的情况下会有 `ZeroDivisionError` 的问题

### 2024 / 1 / 15 - 移除了对 pyautogui 的依赖
- 移除了对 `pyautogui` 的依赖, 现在可以不使用 `pyautogui` 来自适应缩放了

### 2024 / 9 / 6 - 添加一些新功能
- 添加了曲线间隔
    - 曲线间隔用于计算曲线分割数量，当分割数量小于 3 时则分割数量为 3
- 添加自动计算曲线分割数量 (实验性) 功能

### 2024 / 9 / 7 - 尝试支持其他平台
- 将获取分辨率的方法修改为 `QApplication.primaryScreen().geometry()`
- 将获取系统语言的方法修改为 `locale.getlocale()`
- 限制屏幕缩放最小为 0.6 (尝试修复在低分辨率下文字过小的问题)

### 2025 / 3 / 29 - 添加精度调整
- 添加精度调整, 示例 `f2`
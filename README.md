# ArcSVGTool
 
## 简介

本项目是一个用于将 SVG 路径转换为黑线的工具  
方便谱师在写谱时可以做一些黑线艺术  
可在[此视频](https://www.bilibili.com/video/BV1Uz4y1c7hw/)查看使用效果

## 注意事项

如果你只想要 SVG 路径转换黑线的方法那可以直接使用 svg2aff.py  
如果你需要图形化界面那么有以下几个依赖包：
- [PyQt5](https://pypi.org/project/PyQt5/)
    - 用于可视化界面界面
- [qt_material](https://pypi.org/project/qt_material/)
    - 用于界面主题
- [BlurWindow](https://pypi.org/project/BlurWindow/)
    - 用于毛玻璃窗体效果

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
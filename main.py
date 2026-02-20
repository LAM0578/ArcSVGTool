import sys
import os
import json
from svg2aff import (
    svgPath2Aff,
    svgPath2Lines,
    point
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QTextEdit,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtGui import (
    QIcon,
    QColor,
    QPainter,
    QPen,
    QFont
)
from math import (
    floor,
    ceil
)
from PyQt5.QtCore import QFileInfo, Qt
from qt_material import apply_stylesheet
from BlurWindow.blurWindow import GlobalBlur
import sys
import ctypes
import locale

# NCat 2026-01-27
# **Please build in venv**
# pyinstaller --noconsole --onedir --add-data "Icon.ico;." --workpath="" --icon="Icon.ico" --name="ArcSVGTool" "main.py" -y

STYLE_SHEET = '''
* {
    font-size: {fontSize}px;
    font-family: "Microsoft YaHei", sans-serif;
    text-transform: none;
}
QLineEdit, QTextEdit {
    color: #f6f6f6;
    font-family: "consolas", "Microsoft YaHei", monospace;
}
QPushButton#mainWindowButton {
    padding-left: {padding}px;
    padding-right: {padding}px;
}
'''

_LANG_EN = 'en_US'
_LANG_ZH_HANS = 'Chinese (Simplified)_China'

I18N_TEXTS = {
    'title':
    {
        _LANG_EN: 'SVG Path to AFF',
        _LANG_ZH_HANS: 'SVG 路径转 AFF'
    },
    'affPreview': {
        _LANG_EN: 'AFF Preview',
        _LANG_ZH_HANS: 'AFF 预览',
    },
    'svgRaw':
    {
        _LANG_EN: 'SVG Path Raw',
        _LANG_ZH_HANS: 'SVG 路径原始数据'
    },
    'tick':
    {
        _LANG_EN: 'Generate Time',
        _LANG_ZH_HANS: '生成时间'
    },
    'endTick':
    {
        _LANG_EN: 'Generate End Time',
        _LANG_ZH_HANS: '生成的结束时间'
    },
    'offset':
    {
        _LANG_EN: 'Result Offset',
        _LANG_ZH_HANS: '结果偏移'
    },
    'deltaOffsetEnd':
    {
        _LANG_EN: 'End Result Delta Offset',
        _LANG_ZH_HANS: '结束结果叠加偏移'
    },
    'scale':
    {
        _LANG_EN: 'Result Scale',
        _LANG_ZH_HANS: '结果缩放'
    },
    'scaleFirst':
    {
        _LANG_EN: 'Scale First',
        _LANG_ZH_HANS: '缩放优先'
    },
    'curveUseInterval':
    {
        _LANG_EN: 'Curve split by interval',
        _LANG_ZH_HANS: '曲线使用间隔分割'
    },
    'autoCurveCount': {
        _LANG_EN: 'Auto Calc Curve Split Count',
        _LANG_ZH_HANS: '自动计算曲线分割数量'
    },
    'curveInterval':
    {
        _LANG_EN: 'Curve Split Interval',
        _LANG_ZH_HANS: '曲线分割间隔'
    },
    'curveCount':
    {
        _LANG_EN: 'Curve Split Count',
        _LANG_ZH_HANS: '曲线分割数量'
    },
    'generateAndSave':
    {
        _LANG_EN: 'Generate And Save',
        _LANG_ZH_HANS: '生成并保存'
    },
    'error':
    {
        _LANG_EN: 'Error',
        _LANG_ZH_HANS: '错误'
    },
    'invalidInt':
    {
        _LANG_EN: 'invalid int value: {}\nat {}',
        _LANG_ZH_HANS: '无效的 int 值: {}\n位于 {}'
    },
    'invalidFloat':
    {
        _LANG_EN: 'invalid float value: {}\nat {}',
        _LANG_ZH_HANS: '无效的 float 值: {}\n位于 {}'
    },
    'saveAs':
    {
        _LANG_EN: 'Save As',
        _LANG_ZH_HANS: '储存为'
    },
    'fileFilter' :
    {
        _LANG_EN: 'All Files (*);;Arcaea Chart File (*.aff);;Text File (*.txt)',
        _LANG_ZH_HANS: '所有文件 (*);;Arcaea 谱面文件 (*.aff);;文本文件 (*.txt)'
    },
    'svgRawToolTip':
    {
        _LANG_EN: 'Please use https://yqnn.github.io/svg-path-editor/ to format your SVG Path\r\nPlease do not use Minify output', 
        _LANG_ZH_HANS: '使用时请到 https://yqnn.github.io/svg-path-editor/ 格式化你的 SVG 路径\r\n请不要使用 Minify output 输出'
    },
    'scaleFirstToolTip':
    {
        _LANG_EN: 'True: p * scale + offset\r\nFalse: (p + offset) * scale',
        _LANG_ZH_HANS: '勾选后按照此公式进行缩放: p * scale + offset\r\n否则按照此公式进行缩放: (p + offset) * scale'
    },
    'curveUseIntervalToolTip':
    {
        _LANG_EN: 'When this option is selected, the number of curves will be calculated by the interval and the length of the curve',
        _LANG_ZH_HANS: '勾选后曲线分割数量将根据曲线间隔与曲线长度进行计算'
    },
    'preview':
    {
        _LANG_EN: 'Preview',
        _LANG_ZH_HANS: '预览'
    },
    'zeroPreviewSize':
    {
        _LANG_EN: 'Preview Size is 0',
        _LANG_ZH_HANS: '预览尺寸为 0'
    },
    'invalidCurveInterval':
    {
        _LANG_EN: 'Curve Interval is too small',
        _LANG_ZH_HANS: '曲线间隔过小'
    },
    'invalidCurveCount':
    {
        _LANG_EN: 'Curve Count is too large',
        _LANG_ZH_HANS: '曲线数量过大'
    },
    'format': {
        _LANG_EN: 'Format',
        _LANG_ZH_HANS: '格式'
    },
    'invalidFormat': {
        _LANG_EN: 'Invaild format, must be start with \'f\'',
        _LANG_ZH_HANS: '非法格式, 必须以 \'f\' 开头'
    },
    'useZPosMode': {
        _LANG_EN: 'Use Z Position Mode',
        _LANG_ZH_HANS: '使用 Z 位置模式'
    },
    'useZPosModeToolTip': {
        _LANG_EN: 'When enabled, the minimum/maximum Y of the shape and the start/end Y of each segment will be interpolated between the start and end time to determine Z position',
        _LANG_ZH_HANS: '勾选后将使用图形的最小 / 最大 Y 和线段的起始 / 结束 Y 位置在开始 / 结束时间之间进行插值'
    },
    'info': {
        _LANG_EN: 'Info',
        _LANG_ZH_HANS: '信息'
    }
}

DESIGN_SIZE = point(2560, 1600)
SCREEN_SCALE = 1

# x2world(x) = (x * 850) - 425
# y2world(y) = (y * 450) + 100
# (y2world(1) - y2world(0)) / (x2world(1) - x2world(0)) = 0.529411
Y_SCALE = 0.529411
DESIGN_SIZE_Y_SCALE = Y_SCALE + 0.5

GRID_X_LIMIT = 150
GRID_Y_LIMIT = GRID_X_LIMIT // Y_SCALE

def calculateScreenScale():
    global SCREEN_SCALE
    screenRect = QApplication.primaryScreen().geometry()
    scrWidth = screenRect.width()
    scrHeight = screenRect.height()
    widthScale = scrWidth / DESIGN_SIZE.x
    heightScale = scrHeight / DESIGN_SIZE.y
    SCREEN_SCALE = max(min(widthScale, heightScale), .6)

def fixScale(x):
    return int(x * SCREEN_SCALE)

def fixScales(*n):
    return list(map(fixScale, n))

def isVSCode():
    try:
        if sys.ps1:
            return True
        return False
    except:
        return False

LANG = _LANG_EN

def autoSetLanguage():
    global LANG

    language = locale.getlocale()[0]
    if language != _LANG_ZH_HANS:
        LANG = _LANG_EN
        return
    LANG = language

def applyBlur(window):
    window.setAttribute(Qt.WA_TranslucentBackground)
    hWnd = window.winId()
    GlobalBlur(hWnd,Acrylic=True,Dark=True,QWidget=window)

def applyIcon(window):
    fileinfo = QFileInfo(__file__).absolutePath()
    window.setWindowIcon(QIcon(fileinfo + '/Icon.ico'))

class previewWindow(QWidget):
    def __init__(self, lines):
        super().__init__()

        applyBlur(self)
        applyIcon(self)

        self.setWindowTitle(I18N_TEXTS["preview"][LANG])
        self.setGeometry(*fixScales(900, 100, 800, 800))
        self.setFixedSize(*fixScales(800, 800))

        self.lines = lines
        self.mnw = float('inf')
        self.mnh = float('inf')
        self.mxw = -float('inf')
        self.mxh = -float('inf')
        for line in lines:
            p0 = line[0]
            p1 = line[1]
            # min
            self.mnw = min(self.mnw, p0.x, p1.x)
            self.mnh = min(self.mnh, p0.y, p1.y)
            # max
            self.mxw = max(self.mxw, p0.x, p1.x)
            self.mxh = max(self.mxh, p0.y, p1.y)

        mnw = self.mnw
        mnh = self.mnh
        mxw = self.mxw
        mxh = self.mxh
        
        designSize = 800
        border = 50
        designSize -= border * 2
        wdif = mxw - mnw
        hdif = mxh - mnh
        if wdif == 0 and hdif == 0:
            raise Exception(I18N_TEXTS["zeroPreviewSize"][LANG])
        scale = designSize / max(wdif, hdif / 2.)

        self.windowSize = int(800 * SCREEN_SCALE)
        self.designSize = designSize
        self.border = border
        self.scale = scale

    def transPoint(self, p):
        _p = (p - point(self.mnw, self.mnh)) * self.scale
        _p *= point(1, Y_SCALE)
        _p = point(_p.x, (self.designSize * DESIGN_SIZE_Y_SCALE - _p.y))
        return ((_p + point(self.border)) * SCREEN_SCALE).toIntPoint()
    
    def resetPoint(self, p):
        _p = (p / SCREEN_SCALE - point(self.border))
        _p = point(_p.x, (self.designSize * DESIGN_SIZE_Y_SCALE - _p.y))
        _p /= point(1, Y_SCALE)
        _p /= self.scale
        _p += point(self.mnw, self.mnh)
        return _p

    def drawText(self, painter, pen, x, y, text, shadow=True, color=QColor(255, 255, 255, 255)):

        if shadow:
            pen.setColor(QColor(0, 0, 0, 200))
            painter.setPen(pen)
            painter.drawText(x + 2, y + 2, text)

        pen.setColor(color)
        painter.setPen(pen)
        painter.drawText(x, y, text)

    def paintEvent(self, event):

        painter = QPainter(self)
        pen = QPen()
        lastPenColor = None
        
        def cSetPenColor(c):
            pen.setColor(c)
            painter.setPen(pen)

        def drawText(x, y, text, shadow=True, color=QColor(255, 255, 255, 255)):
            self.drawText(painter, pen, x, y, text, shadow, color)
            if lastPenColor != None:
                cSetPenColor(lastPenColor)

        def drawTextMultiLine(ofs, text: str):
            lines = text.splitlines()
            lines.reverse()
            x = ofs
            y = self.windowSize - ofs
            for line in lines:
                drawText(x, y, line)
                y -= ofs
        
        def setPenColor(r, g, b, a=255):
            nonlocal lastPenColor
            c = QColor(r, g, b, a)
            pen.setColor(c)
            painter.setPen(pen)
            lastPenColor = c

        def setPenWidth(w, mx=1):
            w = max(fixScale(int(w)), mx)
            pen.setWidth(w)
            painter.setPen(pen)

        def drawYLines(y):
            p0 = self.transPoint(point(0, y))
            p0.x = 0
            p1 = point(self.windowSize, p0.y)
            painter.drawLine(p0.x, p0.y, p1.x, p1.y)
        
        def drawXLines(x):
            p0 = self.transPoint(point(x, 0))
            p0.y = 0
            p1 = point(p0.x, self.windowSize)
            painter.drawLine(p0.x, p0.y, p1.x, p1.y)

        def drawPointLines(ps):
            ls = []
            for i in range(len(ps) - 1):
                p0 = self.transPoint(ps[i])
                p1 = self.transPoint(ps[i + 1])
                ls.append((p0, p1))
            ls.append((
                self.transPoint(ps[-1]),
                self.transPoint(ps[0])
            ))
            for l in ls:
                painter.drawLine(l[0].x, l[0].y, l[1].x, l[1].y)
        
        def lerp(a, b, t):
            return a + (b - a) * t
    
        _fontSize = int(10 * SCREEN_SCALE)
        painter.setFont(QFont("Consolas", _fontSize))

        _textOffsetX = _fontSize
        _textOffsetY = _fontSize * 2

        # draw grid
        
        setPenWidth(2)
        
        _border2 = self.border * 2
        mnp = self.resetPoint(point(0))
        mxp = self.resetPoint(point(self.designSize + _border2))

        setPenColor(255, 255, 255, 32)
        textColor = QColor(255, 255, 255, 128)

        mnx = min(mnp.x, mxp.x)
        mxx = max(mnp.x, mxp.x)
        i = floor(mnx)
        count = ceil(mxx - i)
        # print('x count: ', count)
        if count <= GRID_X_LIMIT:
            allowDrawText = count < 20
            for j in range(count):
                drawXLines(i)
                if allowDrawText and j > 0:
                    textPos = self.transPoint(point(i, 0))
                    drawText(textPos.x, _textOffsetY, str(i), False, textColor)
                i += 1

        mny = min(mnp.y, mxp.y)
        mxy = max(mnp.y, mxp.y)
        i = floor(mny)
        count = ceil((mxy - i))
        # print('y count: ', count)
        if count <= GRID_Y_LIMIT:
            allowDrawText = count < 35
            for j in range(count):
                drawYLines(i)
                if allowDrawText and j > 0:
                    textPos = self.transPoint(point(0, i))
                    drawText(_textOffsetX, textPos.y, str(i), False, textColor)
                i += 1

        # mnx = min(mnp.x, mxp.x)
        # mxx = max(mnp.x, mxp.x)
        # i = floor(mnx)
        # while i <= mxx:
        #     drawXLines(i)
        #     i += 1

        # mny = min(mnp.y, mxp.y)
        # mxy = max(mnp.y, mxp.y)
        # i = floor(mny)
        # while i <= mxy:
        #     drawYLines(i)
        #     i += 1

        # draw 0 / 1 lines (x & y)

        setPenColor(255, 0, 0, 64) # y

        drawYLines(0)
        drawYLines(1)

        setPenColor(0, 255, 0, 64) # x
        
        drawXLines(0)
        drawXLines(1)

        # draw ftr border

        setPenColor(0xff, 0x4b, 0x0f, 175)

        drawPointLines([
            point(-.5, 0),
            point(1.5, 0),
            point(1, 1),
            point(0, 1)
        ])

        # draw lines

        setPenColor(0x91, 0x78, 0xaa, 200)
        setPenWidth(.02 * self.scale, 2)
        
        for line in self.lines:
            p0 = self.transPoint(line[0])
            p1 = self.transPoint(line[1])
            
            painter.drawLine(p0.x, p0.y, p1.x, p1.y)

        # draw info

        setPenColor(0, 0, 0)
        
        ofs = int(25 * SCREEN_SCALE)

        drawTextMultiLine(
            ofs,
            '\n'.join([
                f'min x: {self.mnw}',
                f'min y: {self.mnh}',
                '',
                f'max x: {self.mxw}',
                f'max y: {self.mxh}',
                '',
                f'cnt x: {lerp(self.mnw, self.mxw, .5)}',
                f'cnt y: {lerp(self.mnh, self.mxh, .5)}',
                '',
                f'scl w: {self.mxw - self.mnw}',
                f'scl h: {self.mxh - self.mnh}',
            ]))
        
class previewAffWindow(QWidget):
    def __init__(self, content):
        super().__init__()

        applyBlur(self)
        applyIcon(self)

        self.setWindowTitle(I18N_TEXTS["affPreview"][LANG])
        self.setGeometry(*fixScales(900, 100, 800, 600))
        self.setFixedSize(*fixScales(800, 800))
        
        self.affRawEdit = mainWindow._mainWindow__createTextEdit(
            self, 25, 25, 750, 750)
        self.affRawEdit.setText(content)

class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # screenRect = QApplication.desktop().screenGeometry()

        calculateScreenScale()

        widthOffset = 155
        height = 25

        if LANG == _LANG_ZH_HANS:
            widthOffset = 105

        applyBlur(self)
        applyIcon(self)

        self.setWindowTitle(I18N_TEXTS["title"][LANG])
        self.setGeometry(*fixScales(100, 100, 800, 950))
        self.setFixedSize(*fixScales(800, 950))

        # create components

        self.svgRawLabel = self.__createLabel(
            I18N_TEXTS["svgRaw"][LANG], 50, height, I18N_TEXTS["svgRawToolTip"][LANG])

        height += 45

        self.svgRawEdit = self.__createTextEdit(50, height, 700, 135)

        height += 170

        self.tickLabel = self.__createLabel(
            I18N_TEXTS["tick"][LANG], 50, height)
        self.tickEdit = self.__createLineEdit(200 + widthOffset, height)

        height += 50

        self.endTickLabel = self.__createLabel(
            I18N_TEXTS["endTick"][LANG], 50, height)
        self.endTickEdit = self.__createLineEdit(200 + widthOffset, height)

        height += 50

        self.offsetLabel = self.__createLabel(
            I18N_TEXTS["offset"][LANG], 50, height)

        self.offsetXEdit = self.__createLineEdit(200 + widthOffset, height)
        self.offsetYEdit = self.__createLineEdit(325 + widthOffset, height)

        height += 50

        self.offsetEndLabel = self.__createLabel(
            I18N_TEXTS["deltaOffsetEnd"][LANG], 50, height)

        self.offsetEndXEdit = self.__createLineEdit(200 + widthOffset, height)
        self.offsetEndYEdit = self.__createLineEdit(325 + widthOffset, height)

        height += 50

        self.scaleLabel = self.__createLabel(
            I18N_TEXTS["scale"][LANG], 50, height)

        self.scaleXEdit = self.__createLineEdit(200 + widthOffset, height)
        self.scaleYEdit = self.__createLineEdit(325 + widthOffset, height)

        height += 50

        self.scaleFirstLabel = self.__createLabel(
            I18N_TEXTS["scaleFirst"][LANG], 50, height, I18N_TEXTS["scaleFirstToolTip"][LANG])
        self.scaleFirstCheckBox = self.__createCheckBox(200 + widthOffset, height)

        height += 50

        self.autoCurveCountLabel = self.__createLabel(
            I18N_TEXTS["autoCurveCount"][LANG], 50, height, None)
        self.autoCurveCountCheckBox = self.__createCheckBox(200 + widthOffset, height)

        height += 50

        self.curveUseIntervalLabel = self.__createLabel(
            I18N_TEXTS["curveUseInterval"][LANG], 50, height, I18N_TEXTS["curveUseIntervalToolTip"][LANG])
        self.curveUseIntervalCheckBox = self.__createCheckBox(200 + widthOffset, height)

        height += 50

        self.curveCountLabel = self.__createLabel(I18N_TEXTS["curveCount"][LANG], 50, height)
        self.curveCountEdit = self.__createLineEdit(200 + widthOffset, height)

        height += 50

        self.curveIntervalLabel = self.__createLabel(I18N_TEXTS["curveInterval"][LANG], 50, height)
        self.curveIntervalEdit = self.__createLineEdit(200 + widthOffset, height)

        height += 50

        self.formatLabel = self.__createLabel(I18N_TEXTS["format"][LANG], 50, height)
        self.formatEdit = self.__createLineEdit(200 + widthOffset, height)

        height += 50

        self.useZPosModeLabel = self.__createLabel(
            I18N_TEXTS["useZPosMode"][LANG], 50, height, I18N_TEXTS["useZPosModeToolTip"][LANG])
        self.useZPosModeCheckBox = self.__createCheckBox(200 + widthOffset, height)

        height += 70

        self.generateButton = self.__createButton(
            I18N_TEXTS["generateAndSave"][LANG],
            50,
            height,
            self.generate)
        
        width = self.generateButton.width() / SCREEN_SCALE

        self.previewButton = self.__createButton(
            I18N_TEXTS["preview"][LANG],
            50 + width + 30,
            height,
            self.openPreview)
        
        width += self.previewButton.width() / SCREEN_SCALE

        self.previewAffButton = self.__createButton(
            I18N_TEXTS["affPreview"][LANG],
            50 + width + 60,
            height,
            self.openAffPreview)

        self.__setDefaultComponentValues()
        self.importConfig()

    @staticmethod
    def __getDirPath():
        path = __file__
        if not os.path.exists(path): # is pyinstaller exe
            path = os.path.abspath(sys.executable)
        return os.path.dirname(path)
    
    @staticmethod
    def __getConfigPath():
        dirPath = mainWindow.__getDirPath()
        return os.path.join(dirPath, "config.json")
    
    def __createLabel(self, content, x, y, tooltip=None):
        label = QLabel(self)
        label.setText(content)
        label.move(*fixScales(x, y))
        label.resize(*fixScales(1000, 35))
        if tooltip is not None:
            label.setToolTip(tooltip)
        return label

    def __createLineEdit(self, x, y):
        lineEdit = QLineEdit(self)
        lineEdit.move(*fixScales(x, y))
        lineEdit.resize(*fixScales(100, 35))
        return lineEdit
    
    def __createCheckBox(self, x, y):
        checkBox = QCheckBox(self)
        checkBox.move(*fixScales(x, y))
        return checkBox
    
    def __createTextEdit(self, x, y, width, height):
        textEdit = QTextEdit(self)
        textEdit.setAcceptRichText(False)
        textEdit.move(*fixScales(x, y))
        textEdit.resize(*fixScales(width, height))
        return textEdit
    
    def __createButton(self, text, x, y, onClicked):
        button = QPushButton(self)
        button.setText(text)
        button.move(*fixScales(x, y))
        button.adjustSize()
        button.resize(*fixScales(button.width() + 50, 35))
        button.clicked.connect(onClicked)
        button.setObjectName('mainWindowButton')
        return button
    
    def __setDefaultComponentValues(self):
        self.svgRawEdit.setText('M 0 0 l 1 0 l 0 1 l -1 0 Z')
        self.tickEdit.setText('0')
        self.endTickEdit.setText('0')
        self.offsetXEdit.setText('0')
        self.offsetYEdit.setText('0')
        self.offsetEndXEdit.setText('0')
        self.offsetEndYEdit.setText('0')
        self.scaleXEdit.setText('1')
        self.scaleYEdit.setText('-2')
        self.scaleFirstCheckBox.setChecked(True)
        self.curveCountEdit.setText('7')
        self.curveIntervalEdit.setText('0.1')
        self.formatEdit.setText('f2')

    def messageBox(self, funcNameOrContent, exc):
        if exc == None:
            QMessageBox.information(
                self,
                I18N_TEXTS['info'][LANG],
                funcNameOrContent
            )
            return
        if isVSCode():
            raise exc
        QMessageBox.critical(
            self,
            I18N_TEXTS["error"][LANG],
            funcNameOrContent + '\n\n' +
            exc.__str__()
        )

    @staticmethod
    def __tryParseInt(s, n):
        try:
            return int(s)
        except:
            raise ValueError(
                I18N_TEXTS["invalidInt"][LANG].format(
                    s,
                    n
                )
            )
        
    @staticmethod
    def __tryParseFloat(s, n):
        try:
            return float(s)
        except:
            raise ValueError(
                I18N_TEXTS["invalidFloat"][LANG].format(
                    s,
                    n
                )
            )
        
    def __parseConfig(self, dic=None):
        svgRaw = self.svgRawEdit.toPlainText()
        tick = self.__tryParseInt(
            self.tickEdit.text(),
            self.tickLabel.text()
        )
        endTick = self.__tryParseInt(
            self.endTickEdit.text(),
            self.endTickLabel.text()
        )
        offset = point(
            self.__tryParseFloat(
                self.offsetXEdit.text(),
                self.offsetLabel.text() + ' x'
            ),
            self.__tryParseFloat(
                self.offsetYEdit.text(),
                self.offsetLabel.text() + ' y'
            )
        )
        deltaOffsetEnd = point(
            self.__tryParseFloat(
                self.offsetEndXEdit.text(),
                self.offsetEndLabel.text() + ' x'
            ),
            self.__tryParseFloat(
                self.offsetEndYEdit.text(),
                self.offsetEndLabel.text() + ' y'
            )
        )
        scale = point(
            self.__tryParseFloat(
                self.scaleXEdit.text(),
                self.scaleLabel.text() + ' x'
            ),
            self.__tryParseFloat(
                self.scaleYEdit.text(),
                self.scaleLabel.text() + ' y'
            )
        )
        scaleFirst = self.scaleFirstCheckBox.isChecked()
        curveUseInterval = self.curveUseIntervalCheckBox.isChecked()
        curveInterval = self.__tryParseFloat(
            self.curveIntervalEdit.text(),
            self.curveIntervalLabel.text()
        )
        curveCount = self.__tryParseInt(
            self.curveCountEdit.text(),
            self.curveCountLabel.text()
        )
        autoCurveCount = self.autoCurveCountCheckBox.isChecked()
        format_ = self.formatEdit.text().strip()
        if format_ == '' or format_[0].lower() != 'f':
            raise ValueError(I18N_TEXTS["invalidFormat"][LANG])
        if not autoCurveCount:
            if curveUseInterval:
                if curveInterval < 0.01:
                    raise ValueError(I18N_TEXTS['invalidCurveInterval'][LANG])
            else:
                if curveCount > 128:
                    raise OverflowError(I18N_TEXTS['invalidCurveCount'][LANG])
        useZPosMode = self.useZPosModeCheckBox.isChecked()
        if dic != None:
            dic['svgRaw'] = svgRaw
            dic['tick'] = tick
            dic['endTick'] = endTick
            dic['offset'] = offset.toArray()
            dic['deltaOffsetEnd'] = deltaOffsetEnd.toArray()
            dic['scale'] = scale.toArray()
            dic['scaleFirst'] = scaleFirst
            dic['curveCount'] = curveCount
            dic['curveInterval'] = curveInterval
            dic['curveUseInterval'] = curveUseInterval
            dic['autoCurveCount'] = autoCurveCount
            dic['format'] = format_
            dic['useZPosMode'] = useZPosMode
        return (
            svgRaw,
            tick,
            endTick,
            offset,
            deltaOffsetEnd,
            scale,
            scaleFirst,
            curveCount,
            curveInterval,
            curveUseInterval,
            autoCurveCount,
            format_,
            useZPosMode
        )
    
    def exportConfig(self):
        configPath = self.__getConfigPath()
        dic = {}
        self.__parseConfig(dic)
        with open(configPath, 'w', encoding='utf-8') as f:
            json.dump(dic, f, indent=2, ensure_ascii=False)

    def importConfig(self):
        configPath = self.__getConfigPath()
        if not os.path.exists(configPath):
            return
        with open(configPath, 'r', encoding='utf-8') as f:
            try:
                dic = json.load(f)
                self.svgRawEdit.setText(dic['svgRaw'])
                self.tickEdit.setText(str(dic['tick']))
                self.endTickEdit.setText(str(dic['endTick']))
                self.offsetXEdit.setText(str(dic['offset'][0]))
                self.offsetYEdit.setText(str(dic['offset'][1]))
                self.offsetEndXEdit.setText(str(dic['deltaOffsetEnd'][0]))
                self.offsetEndYEdit.setText(str(dic['deltaOffsetEnd'][1]))
                self.scaleXEdit.setText(str(dic['scale'][0]))
                self.scaleYEdit.setText(str(dic['scale'][1]))
                self.scaleFirstCheckBox.setChecked(dic['scaleFirst'])
                self.curveCountEdit.setText(str(dic['curveCount']))
                self.curveIntervalEdit.setText(str(dic['curveInterval']))
                self.curveUseIntervalCheckBox.setChecked(dic['curveUseInterval'])
                self.autoCurveCountCheckBox.setChecked(dic['autoCurveCount'])
                self.formatEdit.setText(dic['format'])
                self.useZPosModeCheckBox.setChecked(dic['useZPosMode'])
            except:
                return
            
    def closeEvent(self, event):
        self.exportConfig()
        event.accept()

    def generate(self):
        try:
            
            affRaw = svgPath2Aff(
                *self.__parseConfig()
            )

            # save aff file

            options = QFileDialog.Options()
            filePath, _ = QFileDialog.getSaveFileName(
                self,
                I18N_TEXTS["saveAs"][LANG],
                "",
                I18N_TEXTS["fileFilter"][LANG],
                options=options
            )
            
            if filePath:
                outputPath = filePath
                with open(outputPath, 'w') as f:
                    f.write(affRaw)

        except Exception as ex:
            self.messageBox('mainWindow.generate', ex)
            return
        
    def openAffPreview(self):
        try:
            affRaw = svgPath2Aff(
                *self.__parseConfig()
            )
            self.previewAffWin = previewAffWindow(affRaw)
            self.previewAffWin.setStyleSheet(self.styleSheet())
            self.previewAffWin.show()

        except Exception as ex:
            self.messageBox('mainWindow.openAffPreview', ex)
            return
        
    def openPreview(self):
        try:
            (
                svgRaw,
                _,
                _,
                offset,
                _,
                scale,
                scaleFirst,
                curveCount,
                curveInterval,
                curveUseInterval,
                autoCurveCount,
                format_,
                _
            ) = self.__parseConfig()
            # self.messageBox(config[-1], None)
            ndigits = int(format_[1:])
            lines = svgPath2Lines(
                svgRaw,
                offset,
                scale,
                scaleFirst,
                curveCount,
                curveInterval,
                curveUseInterval,
                autoCurveCount,
                ndigits
            )
            self.previewWin = previewWindow(lines)
            self.previewWin.show()

        except Exception as ex:
            self.messageBox('mainWindow.openPreview', ex)
            return

if __name__ == "__main__":
    try:
        autoSetLanguage()
    except:
        pass
    # ctypes.windll.user32.SetProcessDPIAware()
    # calcScreenScale()
    app = QApplication(sys.argv)
    window = mainWindow()
    apply_stylesheet(app, theme='default_dark.xml')
    styleSheet = (
        STYLE_SHEET
        .replace('{fontSize}', str(fixScale(20)))
        .replace('{padding}', str(fixScale(-50)))
    )
    window.setStyleSheet(styleSheet)
    window.show()
    app.exec_()

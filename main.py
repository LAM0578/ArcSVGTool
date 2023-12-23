import sys
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
from PyQt5.QtCore import QFileInfo, Qt
from qt_material import apply_stylesheet
from BlurWindow.blurWindow import GlobalBlur

# NCat 2023-12-23
# pyinstaller --noconsole --onefile --add-data "Icon.ico;." --icon="Icon.ico" --name="ArcSVGTool" "main.py"

STYLE_SHEET = '''
* {
    font-size: 20px;
    font-family: "Microsoft YaHei", sans-serif;
}
QLineEdit, QTextEdit {
    color: #f6f6f6;
    font-family: "consolas", "Microsoft YaHei", monospace;
}
'''

I18N_TEXTS = {
    'title':
    {
        'en': 'SVG Path to AFF',
        'zh-Hans': 'SVG 路径转 AFF'
    },
    'svgRaw':
    {
        'en': 'SVG Path Raw',
        'zh-Hans': 'SVG 路径原始数据'
    },
    'tick':
    {
        'en': 'Generate Tick',
        'zh-Hans': '生成时间'
    },
    'offset':
    {
        'en': 'Result Offset',
        'zh-Hans': '结果偏移'
    },
    'scale':
    {
        'en': 'Result Scale',
        'zh-Hans': '结果缩放'
    },
    'scaleFirst':
    {
        'en': 'Scale First',
        'zh-Hans': '缩放优先'
    },
    'curveCount':
    {
        'en': 'Curve Count',
        'zh-Hans': '曲线数量'
    },
    'generateAndSave':
    {
        'en': 'Generate And Save',
        'zh-Hans': '生成并保存'
    },
    'error':
    {
        'en': 'Error',
        'zh-Hans': '错误'
    },
    'invalidInt':
    {
        'en': 'invalid int value: {}\nat {}',
        'zh-Hans': '无效的 int 值: {}\n位于 {}'
    },
    'invalidFloat':
    {
        'en': 'invalid float value: {}\nat {}',
        'zh-Hans': '无效的 float 值: {}\n位于 {}'
    },
    'saveAs':
    {
        'en': 'Save As',
        'zh-Hans': '储存为'
    },
    'fileFilter' :
    {
        'en': 'All Files (*);;Arcaea Chart File (*.aff);;Text File (*.txt)',
        'zh-Hans': '所有文件 (*);;Arcaea 谱面文件 (*.aff);;文本文件 (*.txt)'
    },
    'svgRawToolTip':
    {
        'en': 'Please use https://yqnn.github.io/svg-path-editor/ to format your SVG Path\r\nPlease do not use Minify output', 
        'zh-Hans': '使用时请到 https://yqnn.github.io/svg-path-editor/ 格式化你的 SVG 路径\r\n请不要使用 Minify output 输出'
    },
    'scaleFirstToolTip':
    {
        'en': 'True: p * scale + offset\r\nFalse: (p + offset) * scale',
        'zh-Hans': '勾选后按照此公式进行缩放: p * scale + offset\r\n否则按照此公式进行缩放: (p + offset) * scale'
    },
    'preview':
    {
        'en': 'Preview',
        'zh-Hans': '预览'
    },
    'zeroPreviewSize':
    {
        'en': 'Preview Size is 0',
        'zh-Hans': '预览尺寸为 0'
    }
}

LANG = 'en'

def autoSetLang():
    import sys
    import ctypes
    global LANG

    if sys.platform == 'win32':
        dll = ctypes.windll.kernel32
        code = dll.GetUserDefaultUILanguage()
        if (code == 0x804 or
            code == 0xc04 or
            code == 0x404):
            LANG = 'zh-Hans'

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
        self.setGeometry(900, 100, 800, 800)
        self.setFixedSize(800, 800)

        self.lines = lines
        self.mnw = float('inf')
        self.mnh = float('inf')
        self.mxw = -float('inf')
        self.mxh = -float('inf')
        for line in lines:
            p0 = line[0]
            p1 = line[1]
            # min
            if p0.x < self.mnw:
                self.mnw = p0.x
            if p0.y < self.mnh:
                self.mnh = p0.y
            if p1.x < self.mnw:
                self.mnw = p1.x
            if p1.y < self.mnh:
                self.mnh = p1.y
            # max
            if p0.x > self.mxw:
                self.mxw = p0.x
            if p0.y > self.mxh:
                self.mxh = p0.y
            if p1.x > self.mxw:
                self.mxw = p1.x
            if p1.y > self.mxh:
                self.mxh = p1.y

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

        self.designSize = designSize
        self.border = border
        self.scale = scale

    def transPoint(self, p):
        _p = (p - point(self.mnw, self.mnh)) * self.scale
        _p *= point(1, .5)
        _p = point(_p.x, self.designSize - _p.y)
        return (_p + point(self.border)).toIntPoint()

    def drawText(self, painter, pen, x, y, text):

        pen.setColor(QColor(0, 0, 0, 200))
        painter.setPen(pen)
        painter.drawText(x + 2, y + 2, text)

        pen.setColor(QColor(255, 255, 255, 255))
        painter.setPen(pen)
        painter.drawText(x, y, text)

    def paintEvent(self, event):

        painter = QPainter(self)
        pen = QPen()

        def drawText(x, y, text):
            self.drawText(painter, pen,x, y, text)

        def drawTextMultiLine(ofs, text: str):
            lines = text.splitlines()
            lines.reverse()
            x = ofs
            y = 800 - ofs
            for line in lines:
                drawText(x, y, line)
                y -= ofs
        
        def setPenColor(r, g, b, a=255):
            pen.setColor(QColor(r, g, b, a))
            painter.setPen(pen)

        def setPenWidth(w):
            w = max(int(w), 4)
            pen.setWidth(w)
            painter.setPen(pen)

        def drawYLines(y):
            p0 = self.transPoint(point(0, y))
            p0.x = 0
            p1 = point(800, p0.y)
            painter.drawLine(p0.x, p0.y, p1.x, p1.y)
        
        def drawXLines(x):
            p0 = self.transPoint(point(x, 0))
            p0.y = 0
            p1 = point(p0.x, 800)
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

        setPenWidth(2)

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

        setPenColor(0x91, 0x78, 0xaa, 200)
        setPenWidth(.005 * self.scale)
        
        for line in self.lines:
            p0 = self.transPoint(line[0])
            p1 = self.transPoint(line[1])
            
            painter.drawLine(p0.x, p0.y, p1.x, p1.y)

        setPenColor(0, 0, 0)
    
        painter.setFont(QFont("Consolas", 10))
        
        ofs = 25

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
            ]))

class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        def getButtonTextWidth(btn: QPushButton):
            text = btn.text()
            fontMetrics = btn.fontMetrics()
            fontMetrics.horizontalAdvance(text)
            return fontMetrics.width(text) + 50

        widthOffset = 45
        height = 25

        applyBlur(self)
        applyIcon(self)

        self.setWindowTitle(I18N_TEXTS["title"][LANG])
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)

        # create components

        self.svgRawLabel = QLabel(self)
        self.svgRawLabel.setText(I18N_TEXTS["svgRaw"][LANG])
        self.svgRawLabel.move(50, height)
        self.svgRawLabel.resize(1000, 35)
        self.svgRawLabel.setToolTip(I18N_TEXTS["svgRawToolTip"][LANG])

        height += 45

        self.svgRawEdit = QTextEdit(self)
        self.svgRawEdit.setAcceptRichText(False)
        self.svgRawEdit.move(50, height)
        self.svgRawEdit.resize(700, 135)

        height += 170

        self.tickLabel = QLabel(self)
        self.tickLabel.setText(I18N_TEXTS["tick"][LANG])
        self.tickLabel.move(50, height)
        self.tickLabel.resize(1000, 35)

        self.tickEdit = QLineEdit(self)
        self.tickEdit.move(200 + widthOffset, height)
        self.tickEdit.resize(100, 35)

        height += 50

        self.offsetLabel = QLabel(self)
        self.offsetLabel.setText(I18N_TEXTS["offset"][LANG])
        self.offsetLabel.move(50, height)
        self.offsetLabel.resize(1000, 35)

        self.offsetXEdit = QLineEdit(self)
        self.offsetXEdit.move(200 + widthOffset, height)
        self.offsetXEdit.resize(100, 35)

        self.offsetYEdit = QLineEdit(self)
        self.offsetYEdit.move(325 + widthOffset, height)
        self.offsetYEdit.resize(100, 35)

        height += 50

        self.scaleLabel = QLabel(self)
        self.scaleLabel.setText(I18N_TEXTS["scale"][LANG])
        self.scaleLabel.move(50, height)
        self.scaleLabel.resize(1000, 35)

        self.scaleXEdit = QLineEdit(self)
        self.scaleXEdit.move(200 + widthOffset, height)
        self.scaleXEdit.resize(100, 35)

        self.scaleYEdit = QLineEdit(self)
        self.scaleYEdit.move(325 + widthOffset, height)
        self.scaleYEdit.resize(100, 35)

        height += 50

        self.scaleFirstLabel = QLabel(self)
        self.scaleFirstLabel.setText(I18N_TEXTS["scaleFirst"][LANG])
        self.scaleFirstLabel.move(50, height)
        self.scaleFirstLabel.resize(1000, 35)
        self.scaleFirstLabel.setToolTip(I18N_TEXTS["scaleFirstToolTip"][LANG])

        self.scaleFirstCheckBox = QCheckBox(self)
        self.scaleFirstCheckBox.move(200 + widthOffset, height)

        height += 50

        self.curveCountLabel = QLabel(self)
        self.curveCountLabel.setText(I18N_TEXTS["curveCount"][LANG])
        self.curveCountLabel.move(50, height)
        self.curveCountLabel.resize(1000, 35)

        self.curveCountEdit = QLineEdit(self)
        self.curveCountEdit.move(200 + widthOffset, height)
        self.curveCountEdit.resize(100, 35)

        height += 70

        self.generateButton = QPushButton(self)
        self.generateButton.setText(I18N_TEXTS["generateAndSave"][LANG])
        self.generateButton.move(200 + widthOffset, height)
        generateButtonWidth = getButtonTextWidth(self.generateButton)
        self.generateButton.resize(generateButtonWidth, 35)
        self.generateButton.clicked.connect(self.generate)

        self.generateButton = QPushButton(self)
        self.generateButton.setText(I18N_TEXTS["preview"][LANG])
        self.generateButton.move(200 + widthOffset + generateButtonWidth + 30, height)
        self.generateButton.resize(getButtonTextWidth(self.generateButton), 35)
        self.generateButton.clicked.connect(self.openPreview)

        self.__setDefaultComponentValues()
        # self.openPreview()

    def __setDefaultComponentValues(self):
        self.svgRawEdit.setText('M 0 0 l 1 0 l 0 1 l -1 0 Z')
        self.tickEdit.setText('0')
        self.offsetXEdit.setText('0')
        self.offsetYEdit.setText('0')
        self.scaleXEdit.setText('1')
        self.scaleYEdit.setText('-2')
        self.scaleFirstCheckBox.setChecked(True)
        self.curveCountEdit.setText('7')

    def messageBox(self, funcName, exc):
        QMessageBox.critical(
            self,
            I18N_TEXTS["error"][LANG],
            funcName + '\n\n' +
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
        
    def __parseConfig(self):
        try:
            svgRaw = self.svgRawEdit.toPlainText()
            tick = self.__tryParseInt(
                self.tickEdit.text(),
                self.tickLabel.text()
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
            curveCount = self.__tryParseInt(
                self.curveCountEdit.text(),
                self.curveCountLabel.text()
            )
            return svgRaw, tick, offset, scale, scaleFirst, curveCount
        except Exception as ex:
            self.messageBox('mainWindow.__parseConfig', ex)
            return

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
        
    def openPreview(self):
        try:
            config = self.__parseConfig()
            lines = svgPath2Lines(config[0], *config[2:])
            self.previewWin = previewWindow(lines)
            self.previewWin.show()

        except Exception as ex:
            self.messageBox('mainWindow.openPreview', ex)
            return

if __name__ == "__main__":
    try:
        autoSetLang()
    except:
        pass
    app = QApplication(sys.argv)
    window = mainWindow()
    apply_stylesheet(app, theme='default_dark.xml')
    window.setStyleSheet(STYLE_SHEET)
    window.show()
    app.exec_()

import sys
from svg2aff import svgPath2Aff, point
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QTextEdit,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QFileInfo, Qt
from qt_material import apply_stylesheet
from BlurWindow.blurWindow import GlobalBlur

# NCat 2023-12-14
# pyinstaller --onefile --add-data "Icon.ico;." --icon="Icon.ico" --name="ArcSVGTool" "main.py"
    
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
    }
}

LANG = 'zh-Hans'
# LANG = 'en'

class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        def getButtonTextWidth(btn: QPushButton):
            text = btn.text()
            fontMetrics = btn.fontMetrics()
            fontMetrics.horizontalAdvance(text)
            return fontMetrics.width(text) * 2

        widthOffset = 45
        height = 25

        self.setAttribute(Qt.WA_TranslucentBackground)
        hWnd = self.winId()
        GlobalBlur(hWnd,Acrylic=True,Dark=True,QWidget=self)

        fileinfo = QFileInfo(__file__).absolutePath()

        self.setWindowTitle(I18N_TEXTS["title"][LANG])
        self.setWindowIcon(QIcon(fileinfo + '/Icon.ico'))
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
        self.generateButton.resize(getButtonTextWidth(self.generateButton), 35)
        self.generateButton.clicked.connect(self.generate)

        self.__setDefaultComponentValues()

    def __setDefaultComponentValues(self):
        self.svgRawEdit.setText('M 0 0 l 1 0 l 0 1 l -1 0 Z')
        self.tickEdit.setText('0')
        self.offsetXEdit.setText('0')
        self.offsetYEdit.setText('0')
        self.scaleXEdit.setText('1')
        self.scaleYEdit.setText('-2')
        self.scaleFirstCheckBox.setChecked(True)
        self.curveCountEdit.setText('7')

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

    def generate(self):
        try:
            # parse arguments

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
            
            affRaw = svgPath2Aff(
                svgRaw,
                tick,
                offset,
                scale,
                scaleFirst,
                curveCount
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

        except ValueError as vex:
            QMessageBox.critical(self, I18N_TEXTS["error"][LANG], vex.__str__())
            return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainWindow()
    apply_stylesheet(app, theme='default_dark.xml')
    stylesheet = '''
    * {
        font-size: 20px;
        font-family: "Microsoft YaHei", sans-serif;
    }
    QLineEdit, QTextEdit {
        color: #f6f6f6;
        font-family: "consolas", "Microsoft YaHei", monospace;
    }
    '''
    window.setStyleSheet(stylesheet)
    window.show()
    sys.exit(app.exec_())

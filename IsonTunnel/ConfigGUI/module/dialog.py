from PyQt5.QtWidgets import QTextBrowser, QDialog, QVBoxLayout
import yaml
from IsonTunnel.ConfigGUI.utils import ROOT

class Dialog:
    def __init__(self):
        with open(ROOT/'config/qt_maual.yaml', 'r') as file:
            self.qt_text = yaml.safe_load(file)
            self.window = QDialog()
            self.window.setMinimumSize(1400, 800)
            self.window.setMaximumSize(1800, 1300)

    def help_message(self, type='calibration'):
        self.window.setWindowTitle(self.qt_text[type]['title'])
        layout = QVBoxLayout()
        self.text_browser = QTextBrowser(self.window)
        self.text_browser.append(self.qt_text[type]['content'])

        layout.addWidget(self.text_browser)

        self.window.setLayout(layout)
        self.window.setModal(False)

        # Dialog을 띄우는 버튼 생성
        self.window.resize(300, 200)
        self.window.show()
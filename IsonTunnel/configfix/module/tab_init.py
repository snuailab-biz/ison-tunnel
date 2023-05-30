import cv2
import os

from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, QLineEdit, QGridLayout
from PyQt5.QtCore import QSize
from IsonTunnel import CONFIG_ROOT
from IsonTunnel.configfix import COMMON_CFG

from PyQt5.uic import loadUi
from IsonTunnel.configfix.utils import ROOT
from IsonTunnel.configfix.utils import save_config, check_variable_type

class TabInit(QWidget):
    def __init__(self):
        super().__init__()

        uifile = ROOT / 'ui/init.ui' 
        loadUi(uifile, self)

        # self.cams = QPushButton("SAVE URL IMAGE", self)
        self.load_button.setText("SAVE URL IMAGE")
        self.load_button.setMinimumSize(QSize(500, 500))
        self.load_button.clicked.connect(self.rtsp_load)
        self.label_list = []
        self.textbox_list = []

        self.label = QLabel('camera_url')
        self.textbox = QLineEdit(str(COMMON_CFG.camera_url))

        # layout_confing = QGridLayout()
        self.value_layout.addWidget(self.label, 0)
        self.value_layout.addLayout(self.get_cameraUrl_edits(self.textbox), 0)



    def get_cameraUrl_edits(self, text):
        layout_edit_cameraUrl = QGridLayout()
        self.line_cameraUrl = []
        for t in eval(text.text()):
            line = QLineEdit(text=t)
            layout_edit_cameraUrl.addWidget(line)
            self.line_cameraUrl.append(line.text())
        return layout_edit_cameraUrl
        
    def rtsp_load(self):
        # for i, s in enumerate(self.line_cameraUrl):
        #     cap = cv2.VideoCapture(s)
        #     assert cap.isOpened(), f'Failed to open {s}'
        #     w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        #     h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #     success, img = cap.read()  # guarantee first frame
        #     cv2.imshow("img", img)
        #     cv2.waitKey(0)
        #     cv2.destroyAllWindows()
        #     os.makedirs(f"{CONFIG_ROOT}/field/cam{i+1}", exist_ok=True)
        #     cv2.imwrite(f"{CONFIG_ROOT}/field/cam{i+1}/lanes.jpg", img)
        #     if success:
        #         print(f' Success ✅ ({i}: frame of shape {w}x{h})')
        #     else:
        #         print(f" Failed Image")
        
        save_config(self.line_cameraUrl)


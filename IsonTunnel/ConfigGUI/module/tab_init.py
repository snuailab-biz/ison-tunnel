from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import QSize
from IsonTunnel.ConfigGUI.config import COMMON_CFG
import cv2
import os
from IsonTunnel.configure import CONFIG_ROOT

class TabInit(QWidget):
    def __init__(self):
        super().__init__()
        self.cams = QPushButton("SAVE URL IMAGE", self)
        self.cams.setMinimumSize(QSize(500, 500))
        self.cams.clicked.connect(self.save_img)

        self.images = [None] * len(COMMON_CFG.camera_url)

        layout_cam = QHBoxLayout()
        layout_cam.addWidget(self.cams)
        layout = QVBoxLayout()
        layout.addLayout(layout_cam)
        self.setLayout(layout)
        

    def save_img(self):
        self.rtsp_load()
        for i, img in enumerate(self.images):
            cv2.imshow("img", img)
            cv2.waitKey(0)
            os.makedirs(f"{CONFIG_ROOT}/field/cam{i+1}", exist_ok=True)
            cv2.imwrite(f"{CONFIG_ROOT}/field/cam{i+1}/lanes.jpg", img)
        
        cv2.destroyAllWindows()
    
    def rtsp_load(self):
        sources = COMMON_CFG.camera_url
        for i, s in enumerate(sources):
            cap = cv2.VideoCapture(s)
            assert cap.isOpened(), f'Failed to open {s}'
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            success, self.images[i] = cap.read()  # guarantee first frame
            if success:
                print(f' Success ✅ ({i}: frame of shape {w}x{h})')
            else:
                print(f" Failed Image")


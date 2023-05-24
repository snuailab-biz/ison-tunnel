import numpy as np
import cv2
from PyQt5.QtWidgets import QMessageBox, QLineEdit, QTextBrowser, QWidget, QPushButton, QLabel, QGridLayout, QDialog, QVBoxLayout
from PyQt5.QtCore import QSize, Qt
from IsonTunnel.ConfigGUI.config import EVENT_CFG
from PyQt5.uic import loadUi
from IsonTunnel.ConfigGUI.configSaver import save_config
from .dialog import Dialog

from IsonTunnel.ConfigGUI.module.camera.camera import Camera
from IsonTunnel.ConfigGUI.utils import ROOT

class TabEvent(QWidget, Dialog):
    def __init__(self):
        super().__init__()

        uifile = ROOT / 'ui/event.ui' 
        loadUi(uifile, self)
        # params
        self.img = [None]+[]*4
        self.cams = [None]*4
        self.load_button.setText("Load Camera (OFF)")
        
        # cams
        self.cam1.setMinimumSize(QSize(300, 300))
        self.cam2.setMinimumSize(QSize(300, 300))
        self.cam3.setMinimumSize(QSize(300, 300))
        self.cam4.setMinimumSize(QSize(300, 300))

        self.help_button.setMaximumSize(QSize(300, 720))
        self.help_button.clicked.connect(lambda: self.help_message('event'))

        self.cam1.clicked.connect(lambda: self.call_img(0))
        self.cam2.clicked.connect(lambda: self.call_img(1))
        self.cam3.clicked.connect(lambda: self.call_img(2))
        self.cam4.clicked.connect(lambda: self.call_img(3))

        # Create labels and text boxes for each key-value pair in the YAML data
        self.label_list = []
        self.textbox_list = []
        for key, value in  EVENT_CFG:
            label = QLabel(key)
            label.setFixedWidth(150)
            textbox = QLineEdit(str(value))
            self.label_list.append(label)
            self.textbox_list.append(textbox)

        # save btn about config
        save_button = QPushButton('Save')
        save_button.setMinimumSize(QSize(200, 200))
        save_button.clicked.connect(self.save_data)

        
        layout_confing = QGridLayout()
        for idx, (label, textbox) in enumerate(zip(self.label_list, self.textbox_list)):
            if label.text()== 'camera_url':
                layout_confing.addWidget(label, idx, 0, 4, -1)
                layout_confing.addLayout(self.get_cameraUrl_edits(textbox), idx, 1,  4, -1)
            else:
                layout_confing.addWidget(label, idx+3, 0)
                layout_confing.addWidget(textbox, idx+3, 1)

        # self.load_button = QPushButton('Load Camera (OFF)')
        self.load_button.setMinimumSize(QSize(100, 100))
        self.load_button.clicked.connect(self.load_camera)

        self.layout.addLayout(layout_confing)
        self.layout.addWidget(save_button)
        # self.setLayout(self.layout)
        self.cam_check = False

    def get_cameraUrl_edits(self, text):
        layout_edit_cameraUrl = QGridLayout()
        self.line_cameraUrl = []
        for t in eval(text.text()):
            line = QLineEdit(text=t)
            layout_edit_cameraUrl.addWidget(line)
            self.line_cameraUrl.append(line)
        return layout_edit_cameraUrl
    
    def load_camera(self):
        try:
            cam1 = Camera(1, mode = "event")
            cam2 = Camera(2, mode = "event")
            cam3 = Camera(3, mode = "event")
            cam4 = Camera(4, mode = "event")
            self.cams = [cam1, cam2, cam3, cam4]
            self.load_button.setText("Load Camera (ON)")
            self.cam_check = True
        except:
            pass


    def find_pixel(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:                      # 마우스를 누른 상태
            self.x1, self.y1 = x,y
            print(self.x1, self.y1)
            print(self.window[self.y1,self.x1])
            cv2.imshow("image", self.window)
            self.points.append([x,y])
            self.draw_space()

    def draw_space(self):
        cv2.fillPoly(self.window, [np.concatenate((self.points, self.pre[::-1]),axis=0)], (0,255/self.lane,0))
        cv2.imshow("image", self.window)

    def save_mask(self):
        mask = cv2.inRange(self.window, (0,255/self.lane,0), (0,255/self.lane,0))
        cv2.imshow("mask1", mask)
        cv2.imwrite(f"configure/field/cam{self.number}/test_lane{self.lane}.jpg", mask)
    
    def reset(self):
        # check cam number
        btn = self.sender()
        self.number = int(btn.text()[-1])
        
        # set img
        self.window = self.img[self.number].copy()
        self.origin = self.img[self.number].copy()
        self.width = self.window.shape[1]
        self.height = self.window.shape[0]        
        
        # reset param
        self.x1,self.y1 = -1,-1
        self.lane = 1
        self.num = 1
        self.points = []
        self.pre = np.array([[0, 0], [self.width, 0]])

    def call_img(self, ind):
        if self.cam_check:
            cam = self.cams[ind]
            cam.event_image()
        
    def save_data(self):
        data = {}
        
        # Get Key, Value from GUI
        for label, textbox in zip(self.label_list, self.textbox_list):
            if label.text() == 'camera_url':
                continue
            data[label.text()] = textbox.text()
        
        # get camera_url texts
        data['camera_url'] = []
        for textbox in self.line_cameraUrl:
            data['camera_url'].append(textbox.text())
        
        save_config(data, mode='event')
        
        # Inform the user that the data has been saved
        QMessageBox.information(self, 'info', '저장되었습니다.')



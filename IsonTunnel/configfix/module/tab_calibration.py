from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QSize
from PyQt5.uic import loadUi

from IsonTunnel.configfix.module.camera import Camera
from .dialog import Dialog
from IsonTunnel.configfix.utils import ROOT

class TabCalibration(QWidget, Dialog):
    def __init__(self):
        super().__init__()
        uifile = ROOT/ 'ui/calibration.ui' 
        self.cams = [None]*4
        loadUi(uifile, self)
        self.set_button()
        self.load_camera()
        self.fn_button()

    def set_button(self):
        self.cam_o_show_1.setText("Cam1 : Origin Image")
        self.cam_t_show_1.setText("Cam1 : Undist Image")

        self.cam_o_show_2.setText("Cam2 : Origin Image")
        self.cam_t_show_2.setText("Cam2 : Undist Image")

        self.cam_o_show_3.setText("Cam3 : Origin Image")
        self.cam_t_show_3.setText("Cam3 : Undist Image")

        self.cam_o_show_4.setText("Cam4 : Origin Image")
        self.cam_t_show_4.setText("Cam4 : Undist Image")

        self.push_load.setText("Load Camera (OFF)")
        self.push_load.setMinimumSize(QSize(100, 100))
        self.push_load.clicked.connect(self.load_camera)

        self.cam_o_show_1.setMinimumSize(QSize(300, 200))
        self.cam_o_show_1.setMaximumSize(QSize(500, 300))
        self.cam_t_show_1.setMinimumSize(QSize(300, 200))
        self.cam_t_show_1.setMaximumSize(QSize(500, 300))
        # self.help_button.setMinimumSize(QSize(win_size_w, win_size_h))
        self.help_button.setMaximumSize(QSize(300, 720))
        self.help_button.clicked.connect(lambda: self.help_message('calibration'))

        self.cam_o_show_2.setMinimumSize(QSize(300, 200))
        self.cam_o_show_2.setMaximumSize(QSize(500, 300))
        self.cam_t_show_2.setMinimumSize(QSize(300, 200))
        self.cam_t_show_2.setMaximumSize(QSize(500, 300))

        self.cam_o_show_3.setMinimumSize(QSize(300, 200))
        self.cam_o_show_3.setMaximumSize(QSize(500, 300))
        self.cam_t_show_3.setMinimumSize(QSize(300, 200))
        self.cam_t_show_3.setMaximumSize(QSize(500, 300))

        self.cam_o_show_4.setMinimumSize(QSize(300, 200))
        self.cam_o_show_4.setMaximumSize(QSize(500, 300))
        self.cam_t_show_4.setMinimumSize(QSize(300, 200))
        self.cam_t_show_4.setMaximumSize(QSize(500, 300))


    def load_camera(self):
        try:
            cam1 = Camera(1, mode='calib')
            cam2 = Camera(2, mode='calib')
            cam3 = Camera(3, mode='calib')
            cam4 = Camera(4, mode='calib')
            self.cams = [cam1, cam2, cam3, cam4]
            self.push_load.setText("Load Camera (ON)")
            self.init_parameter()
        except:
            print("Camera None")

    def init_parameter(self):
        self.cam_k00_1.setText(str(self.cams[0].K[0][0]))
        self.cam_k01_1.setText(str(self.cams[0].K[0][1]))
        self.cam_k02_1.setText(str(self.cams[0].K[0][2]))
        self.cam_k10_1.setText(str(self.cams[0].K[1][0]))
        self.cam_k11_1.setText(str(self.cams[0].K[1][1]))
        self.cam_k12_1.setText(str(self.cams[0].K[1][2]))
        self.cam_k20_1.setText(str(self.cams[0].K[2][0]))
        self.cam_k21_1.setText(str(self.cams[0].K[2][1]))
        self.cam_k22_1.setText(str(self.cams[0].K[2][2]))
        self.cam_k00_2.setText(str(self.cams[1].K[0][0]))
        self.cam_k01_2.setText(str(self.cams[1].K[0][1]))
        self.cam_k02_2.setText(str(self.cams[1].K[0][2]))
        self.cam_k10_2.setText(str(self.cams[1].K[1][0]))
        self.cam_k11_2.setText(str(self.cams[1].K[1][1]))
        self.cam_k12_2.setText(str(self.cams[1].K[1][2]))
        self.cam_k20_2.setText(str(self.cams[1].K[2][0]))
        self.cam_k21_2.setText(str(self.cams[1].K[2][1]))
        self.cam_k22_2.setText(str(self.cams[1].K[2][2]))
        self.cam_k00_3.setText(str(self.cams[2].K[0][0]))
        self.cam_k01_3.setText(str(self.cams[2].K[0][1]))
        self.cam_k02_3.setText(str(self.cams[2].K[0][2]))
        self.cam_k10_3.setText(str(self.cams[2].K[1][0]))
        self.cam_k11_3.setText(str(self.cams[2].K[1][1]))
        self.cam_k12_3.setText(str(self.cams[2].K[1][2]))
        self.cam_k20_3.setText(str(self.cams[2].K[2][0]))
        self.cam_k21_3.setText(str(self.cams[2].K[2][1]))
        self.cam_k22_3.setText(str(self.cams[2].K[2][2]))
        self.cam_k00_4.setText(str(self.cams[3].K[0][0]))
        self.cam_k01_4.setText(str(self.cams[3].K[0][1]))
        self.cam_k02_4.setText(str(self.cams[3].K[0][2]))
        self.cam_k10_4.setText(str(self.cams[3].K[1][0]))
        self.cam_k11_4.setText(str(self.cams[3].K[1][1]))
        self.cam_k12_4.setText(str(self.cams[3].K[1][2]))
        self.cam_k20_4.setText(str(self.cams[3].K[2][0]))
        self.cam_k21_4.setText(str(self.cams[3].K[2][1]))
        self.cam_k22_4.setText(str(self.cams[3].K[2][2]))

        self.cam_d1_1.setText(str(self.cams[0].D[0]))
        self.cam_d2_1.setText(str(self.cams[0].D[1]))
        self.cam_d3_1.setText(str(self.cams[0].D[2]))
        self.cam_d4_1.setText(str(self.cams[0].D[3]))
        self.cam_d1_2.setText(str(self.cams[1].D[0]))
        self.cam_d2_2.setText(str(self.cams[1].D[1]))
        self.cam_d3_2.setText(str(self.cams[1].D[2]))
        self.cam_d4_2.setText(str(self.cams[1].D[3]))
        self.cam_d1_3.setText(str(self.cams[2].D[0]))
        self.cam_d2_3.setText(str(self.cams[2].D[1]))
        self.cam_d3_3.setText(str(self.cams[2].D[2]))
        self.cam_d4_3.setText(str(self.cams[2].D[3]))
        self.cam_d1_4.setText(str(self.cams[3].D[0]))
        self.cam_d2_4.setText(str(self.cams[3].D[1]))
        self.cam_d3_4.setText(str(self.cams[3].D[2]))
        self.cam_d4_4.setText(str(self.cams[3].D[3]))

        self.cam_t_1.setText(str(self.cams[0].theta))
        self.cam_t_2.setText(str(self.cams[1].theta))
        self.cam_t_3.setText(str(self.cams[2].theta))
        self.cam_t_4.setText(str(self.cams[3].theta))
    

    def fn_button(self):
        self.cam_o_show_1.clicked.connect(lambda: self.image_view(0))
        self.cam_t_show_1.clicked.connect(lambda: self.get_calibration(0))

        self.cam_o_show_2.clicked.connect(lambda: self.image_view(1))
        self.cam_t_show_2.clicked.connect(lambda: self.get_calibration(1))

        self.cam_o_show_3.clicked.connect(lambda: self.image_view(2))
        self.cam_t_show_3.clicked.connect(lambda: self.get_calibration(2))

        self.cam_o_show_4.clicked.connect(lambda: self.image_view(3))
        self.cam_t_show_4.clicked.connect(lambda: self.get_calibration(3))


    def image_view(self, ind):
        self.cams[ind].image_view()

    def get_calibration(self, ind):
        while True:
            k, d, theta, trigger = self.cams[ind].calibration()
            if ind == 0:
                self.cam_k02_1.setText('i ' + str(k[0][2]))
                self.cam_k12_1.setText(str(k[1][2]))
                self.cam_d1_1.setText(str(d[0]))
                self.cam_d1_1.setText(str(d[0]))
                self.cam_d2_1.setText(str(d[1]))
                self.cam_d2_1.setText(str(d[1]))
                self.cam_d3_1.setText(str(d[2]))
                self.cam_d3_1.setText(str(d[2]))
                self.cam_d4_1.setText(str(d[3]))
                self.cam_d4_1.setText(str(d[3]))
                self.cam_t_1.setText(str(theta))
            if ind == 1:
                self.cam_k02_2.setText(str(k[0][2]))
                self.cam_k12_2.setText(str(k[1][2]))
                self.cam_d1_2.setText(str(d[0]))
                self.cam_d1_2.setText(str(d[0]))
                self.cam_d2_2.setText(str(d[1]))
                self.cam_d2_2.setText(str(d[1]))
                self.cam_d3_2.setText(str(d[2]))
                self.cam_d3_2.setText(str(d[2]))
                self.cam_d4_2.setText(str(d[3]))
                self.cam_d4_2.setText(str(d[3]))
                self.cam_t_2.setText(str(theta))
            if ind == 2:
                self.cam_k02_3.setText(str(k[0][2]))
                self.cam_k12_3.setText(str(k[1][2]))
                self.cam_d1_3.setText(str(d[0]))
                self.cam_d1_3.setText(str(d[0]))
                self.cam_d2_3.setText(str(d[1]))
                self.cam_d2_3.setText(str(d[1]))
                self.cam_d3_3.setText(str(d[2]))
                self.cam_d3_3.setText(str(d[2]))
                self.cam_d4_3.setText(str(d[3]))
                self.cam_d4_3.setText(str(d[3]))
                self.cam_t_3.setText(str(theta))
            if ind == 3:
                self.cam_k02_4.setText(str(k[0][2]))
                self.cam_k12_4.setText(str(k[1][2]))
                self.cam_d1_4.setText(str(d[0]))
                self.cam_d1_4.setText(str(d[0]))
                self.cam_d2_4.setText(str(d[1]))
                self.cam_d2_4.setText(str(d[1]))
                self.cam_d3_4.setText(str(d[2]))
                self.cam_d3_4.setText(str(d[2]))
                self.cam_d4_4.setText(str(d[3]))
                self.cam_d4_4.setText(str(d[3]))
                self.cam_t_4.setText(str(theta))

            if trigger:
                break
        
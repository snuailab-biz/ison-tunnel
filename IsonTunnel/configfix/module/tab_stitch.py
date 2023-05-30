
import numpy as np
import cv2
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget
from IsonTunnel.configfix.module.camera.camera import Camera
from PyQt5.uic import loadUi
from .dialog import Dialog
from IsonTunnel.configfix.utils import ROOT


class TabStit(QWidget, Dialog):
    def __init__(self):
        super().__init__()
        uifile = ROOT / 'ui/stitch.ui' 
        loadUi(uifile, self)
        
        self.load_button.setMaximumSize(QSize(9999, 200))
        self.stitch_button.setMaximumSize(QSize(9999, 200))
        self.help_button.setMaximumSize(QSize(300, 200))
        self.help_button.clicked.connect(lambda: self.help_message('stitch'))

        # params
        self.img = [None]+[]*4
        self.cams = [None]*4
        # cams
        self.cam1.setMinimumSize(QSize(300, 300))
        self.cam2.setMinimumSize(QSize(300, 300))
        self.cam3.setMinimumSize(QSize(300, 300))
        self.cam4.setMinimumSize(QSize(300, 300))
        self.cam1.clicked.connect(lambda: self.call_img(0))
        self.cam2.clicked.connect(lambda: self.call_img(1))
        self.cam3.clicked.connect(lambda: self.call_img(2))
        self.cam4.clicked.connect(lambda: self.call_img(3))

        # self.stitch_button = QPushButton('Stitching!!')
        # self.stitch_button.setMinimumSize(QSize(300, 200))
        self.stitch_button.clicked.connect(self.stitch)

        self.load_button.setText("Load Camera (OFF)")
        self.load_button.setMinimumSize(QSize(100, 100))
        self.load_button.clicked.connect(self.load_camera)

        self.load_camera()

    def load_camera(self):
        try:
            cam1 = Camera(1, mode = "stit")
            cam2 = Camera(2, mode = "stit")
            cam3 = Camera(3, mode = "stit")
            cam4 = Camera(4, mode = "stit")
            self.cams = [cam1, cam2, cam3, cam4]
            self.load_button.setText('Load Camera (On)')
        except:
            pass
    
    def call_img(self, i):
        while True:
            trigger = self.cams[i].get_keypoint()
            if trigger:
                break

    def stitch(self):
        image_resize = (1000,448)
        stitch_offset = 100
        mask=self.create_outline_mask(image_size=image_resize, offset=stitch_offset)
        inv_mask = 1.0-mask
        stitch_imgs = [self.cams[0].stitch_img, self.cams[1].stitch_img, self.cams[2].stitch_img, self.cams[3].stitch_img]

        merge_img=self.stitch_blending(stitch_imgs, mask, inv_mask)

        cv2.imshow("merge_img",merge_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    def create_outline_mask(self, image_size=(0, 0),offset = 0):
        # 이미지 사이즈 얻기
        width,hight = image_size
        
        # 이미지 양끝으로부터 offset 크기에 맞춘 mask 생성
        mask = np.full_like(np.ones((hight,int(2*offset),3)), 255)

        # linear 세팅 : 왼쪽부터 1 ~ 0 사이 값을 가짐;
        for i in range(int(2*offset)):
            mask[:,i] = 1.0 - (1.0*(i/(2*offset)))
        
        return mask

    def stitch_blending(self, img_array,mask=None,inv_mask=None):
        blending_img = []
        _, mask_w = mask.shape[:2]
        x_offset = int(mask_w/2)
        if (mask_w>0):
            for idx_ in range(len(img_array)-1):
                    # 오른쪽 사이드 이미지 blending
                    img_array[idx_][:,-mask_w:] =  mask*img_array[idx_][:,-mask_w:] + inv_mask*img_array[idx_+1][:,:mask_w]
                    # 왼쪽 사이드 이미지 blending
                    img_array[idx_+1][:,:mask_w] =  inv_mask*img_array[idx_][:,-mask_w:] + mask*img_array[idx_+1][:,:mask_w]
                    
                    # 양(왼쪽,오른쪽) 사이드 blending 처리된 이미지 보관
                    blending_img.append(img_array[idx_][:,x_offset:-x_offset])
            # blending 처리된 마지막 이미지 보관
            blending_img.append(img_array[len(img_array)-1][:,x_offset:-x_offset])
        else:
            blending_img = img_array;
        # 가로 stitch 적업
        return np.concatenate(blending_img,axis=1)


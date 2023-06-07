from functools import lru_cache
import pprint
import numpy as np
import cv2
from IsonTunnel.eventer.IsonEvent.event_object import Car
from IsonTunnel.eventer import LOGGER, EVENTER_CFG
from IsonTunnel import CONFIG_ROOT

class IsonCamera:
    def __init__(self, camera_number, names) -> None:
        self.cam_id = camera_number
        self.names = names

        self.car_object = {}
        self.frame_locate = []

        self.root_path = CONFIG_ROOT / EVENTER_CFG.postprocess_path
        self.lane1 = None
        self.lane2 = None
        self.lane3 = None
        self.lane4 = None
        self.speed = None
        self.lane_masks = []

        path = f"{self.root_path}/cam{str(self.cam_id+1)}"
        image_lst = ['lane1.jpg', 'lane2.jpg', 'lane3.jpg', 'lane4.jpg']
        imgs = [f"{path}/{img}" for img in image_lst]
        self.lane_mask_load(imgs)
        cv2.namedWindow(str(2), cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow(str(2), 800, 448)
        cv2.moveWindow(str(2), 50, 300) 
        cv2.namedWindow(str(3), cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow(str(3), 800, 448)
        cv2.moveWindow(str(3), 850, 300) 
        cv2.namedWindow(str(4), cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow(str(4), 800, 448)
        cv2.moveWindow(str(4), 1650, 300) 
        cv2.namedWindow(str(1), cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow(str(1), 800, 448)
        cv2.moveWindow(str(1), 2400, 300) 

    def event_update(self): # 생성과 소멸
        for i, track_id in enumerate(self.id):
            track_id = 1
            if track_id in list(self.car_object.keys()):
                self.car_object[track_id].update_frame(self.xywh[i], 4, self.lane_info[i])
            else:
                self.car_object[track_id] = Car(track_id, self.xywh[i], self.cam_id, 4, self.lane_info[i])
    
    def event(self):
        for diff in self.differ:
            lost = self.car_object[diff].lost
            if lost and self.car_object[diff]._check_event_frame:
                LOGGER.info("Delete {}, Cam ID : {}, Car ID : {}".format(self.car_object[diff]._cls, self.car_object[diff].cam_id, self.car_object[diff].car_id))
                del self.car_object[diff]
        for inters in self.intersection:
            self.car_object[inters].event()

    def lane_mask_load(self, imgs):
        lane_lst = []
        for i, img in enumerate(imgs):
            img = cv2.imread(img)
            img = cv2.resize(img, dsize=(800, 448),  interpolation=cv2.INTER_LINEAR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, lane_mask = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            lane_lst.append(lane_mask)
        self.lane_masks = np.asarray(lane_lst)

    @property
    def differ(self):
        return self.car_object.keys() - self.id
        
    @property
    def intersection(self):
        return self.car_object.keys() & self.id

    def update(self, orig_img, det_info):
        self.orig_img = orig_img
        self.orig_shape = orig_img.shape[:2]
        self.det_info = det_info
        # self.draw()

    
    def show(self, winname):
        # cv2.resizeWindow(str(winname), self.orig_shape[1], self.orig_shape[0])
        self.draw()
        cv2.imshow(str(winname), self.orig_img)
        # if winname==str(3):
        #     cv2.moveWindow(winname, 3600, 100) 
        # if winname==str(4):
        #     cv2.moveWindow(winname, 4400, 100) 

    def draw(self):
        for id, xywh, cls in zip(self.id, self.xywh, self.cls):
            name = f'ID: {id} Class: {self.names[cls]}'
            x, y, w, h = xywh
            xl = np.clip(int(x-w/2), 0, self.orig_shape[1])
            yt = np.clip(int(y-h/2), 0, self.orig_shape[0])
            xr = np.clip(int(x+w/2), 0, self.orig_shape[1])
            yb = np.clip(int(y+h/2), 0, self.orig_shape[0])
            label = f'{name}'
            cv2.rectangle(self.orig_img, (xl, yt), (xr, yb), (255,255,255), 5)
            cv2.putText(self.orig_img, label, (int(x-w/2), int(y-h/2) - 5), cv2.FONT_ITALIC, 1, (255,0,0), 2)
    
    @property
    def id(self):
        if self.det_info[:,0].any():
            return np.array([1]* len(self.det_info[:,0]))

        else:
            return self.det_info[:, 0]
        # return np.array([1])

    @property
    def xywh(self):
        return self.det_info[:, 1:5]

    @property
    def cls(self):
        if self.det_info[:, 6].any():
            return np.array([4] * len(self.det_info[:, 6]))
        else:
            return self.det_info[:, 6]
        # return np.array([4])

    @property
    def lane_info(self):
        frame_array = np.asarray(self.xywh)[:, :2]
        lane_value = self.lane_masks[:,frame_array[:,1]+20, frame_array[:,0]].T
        self.lane = np.argwhere(lane_value>0)[:,1]+1
        # np.all(np.diff(np.argwhere(lane_value>0)[:,1]+1) == 0) 비교프레임수가 커지면 이 방식이 더 빠름
        return self.lane

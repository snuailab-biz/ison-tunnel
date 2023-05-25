from functools import lru_cache
import pprint
import numpy as np
import cv2
from IsonTunnel.eventer.IsonEvent.event_object import Car
from IsonTunnel.eventer.config import logger, CONFIG_ROOT, DEFAULT_CFG

class IsonCamera:
    def __init__(self, camera_number, names) -> None:
        self.cam_id = camera_number
        # self.det_info = Infos(det_infos, self.orig_shape) if det_infos is not None else None  # native size boxes
        self.names = names
        # self._keys = [k for k in (['det_info']) if getattr(self, k) is not None]

        self.car_object = {}
        self.frame_locate = []

        self.root_path = CONFIG_ROOT / DEFAULT_CFG.postprocess_path
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

    def event_update(self): # 생성과 소멸
        for i, track_id in enumerate(self.id):
            if track_id in list(self.car_object.keys()):
                self.car_object[track_id].update_frame(self.xywh[i], self.cls[i], self.lane_info[i])
            else:
                self.car_object[track_id] = Car(track_id, self.xywh[i], self.cam_id, self.cls[i], self.lane_info[i])
    
    def event(self):
        for diff in self.differ:
            lost = self.car_object[diff].lost
            if lost and self.car_object[diff]._check_event_frame:
                logger.info("Delete {}, Cam ID : {}, Car ID : {}".format(self.car_object[diff]._cls, self.car_object[diff].cam_id, self.car_object[diff].car_id))
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
        cv2.namedWindow(str(winname), cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)  # allow window resize (Linux)
        cv2.resizeWindow(str(winname), self.orig_shape[1], self.orig_shape[0])
        self.draw()
        cv2.imshow(str(winname), self.orig_img)

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
        return self.det_info[:, 0]

    @property
    def xywh(self):
        return self.det_info[:, 1:5]

    @property
    def cls(self):
        return self.det_info[:, 6]

    @property
    def lane_info(self):
        frame_array = np.asarray(self.xywh)[:, :2]
        lane_value = self.lane_masks[:,frame_array[:,1], frame_array[:,0]].T
        self.lane = np.argwhere(lane_value>0)[:,1]+1
        # np.all(np.diff(np.argwhere(lane_value>0)[:,1]+1) == 0) 비교프레임수가 커지면 이 방식이 더 빠름
        return self.lane

# class Infos:
#     def __init__(self, det_info, orig_shape) -> None:
#         if det_info.ndim == 1:
#             det_info = det_info[None, :]
#         n = det_info.shape[-1]
#         assert n in (7, 8), f'expected `n` in [7, 8], but got {n}'  # xyxy, (track_id), conf, cls
#         # TODO
#         self.det_info = det_info
#         self.orig_shape = np.asarray(orig_shape)
    
#     @property
#     def lane_info(self):
#         mask = self.lane_masks
#         frame_array = np.asarray(self.frame_bbox)[:, :2]
#         lane_value = mask[:,frame_array[:,1], frame_array[:,0]].T
#         lane = set(np.argwhere(lane_value>0)[:,1]+1)
#         # np.all(np.diff(np.argwhere(lane_value>0)[:,1]+1) == 0) 비교프레임수가 커지면 이 방식이 더 빠름
#         return lane.pop() if len(lane) ==1 else self.init_lane

#     @property
#     def id(self):
#         return self.det_info[:, 0]

#     @property
#     def xywh(self):
#         return self.det_info[:, 1:5]
        
#     @property
#     def current_time(self):
#         return self.det_info[:, 5]

#     @property
#     def cls(self):
#         return self.det_info[:, 6]
        
#     @property
#     def cam_id(self):
#         return self.det_info[:, 7]


#     @property
#     @lru_cache(maxsize=2)
#     def xyxyn(self):
#         return self.xyxy / self.orig_shape[[1, 0, 1, 0]]

#     def numpy(self):
#         return Infos(self.det_info.numpy(), self.orig_shape)

#     @property
#     def shape(self):
#         return self.det_info.shape

#     @property
#     def data(self):
#         return self.det_info

#     def __len__(self):  # override len(results)
#         return len(self.det_info)

#     def __str__(self):
#         return self.det_info.__str__()

#     def __repr__(self):
#         return (f'{self.__class__.__module__}.{self.__class__.__name__}\n'
#                 f'type:  {self.det_info.__class__.__module__}.{self.boxes.__class__.__name__}\n'
#                 f'shape: {self.det_info.shape}\n'
#                 f'dtype: {self.det_info.dtype}\n'
#                 f'{self.det_info.__repr__()}')

#     def __getitem__(self, idx):
#         return Infos(self.boxes[idx], self.orig_shape)

#     def __getattr__(self, attr):
#         name = self.__class__.__name__
#         raise AttributeError(f"'{name}' object has no attribute '{attr}'. See valid attributes below.\n{self.__doc__}")
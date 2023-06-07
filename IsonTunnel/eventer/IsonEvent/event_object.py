import numpy as np
from IsonTunnel.eventer import EVENTER_CFG as config
import datetime
from IsonTunnel.eventer import LOGGER

state_direction = {
    1: "Left",
    2: "Left",
    3: "Right",
    4: "Right",
}
class Car:
    def __init__(self, car_id, xywh, cam_id, cls, lane_info):
        self.cam_id = cam_id
        self.car_id = car_id
        x, y, w, h = xywh
        self.frame_bbox = [[x,y+int(h/5),w,h]]
        self.cls = cls

        self.speed_state = False
        self.lane_state = False
        self.stop_state = False
        self.reverse_state = False
        self.person_state = False

        self.position = None

        self.lane_infos = [lane_info]
        self.init_direction = state_direction[lane_info]

        self.cur_lane = None
        self.cur_direction = None

        self.check_delete = False
        self.life_count = 0
        self.stop_count = 0
        self.reverse_count = 0
        self.event_state = {
            1: [0, "역주행"],
            2: [0, "과속"],
            3: [0, "불법 주정차"],
            4: [0, "차선변경"],
            5: [0, "미확인 낙하물 & 사람 발견"]
        }

        LOGGER.info("Generate {}, Cam ID : {}, Car ID : {}".format(self._cls, self.cam_id, self.car_id))


    def update_frame(self, xywh, cls, lane_info):
        if len(self.frame_bbox)>=config.check_frame: del self.frame_bbox[0]
        self.cls = cls
        x, y, w, h = xywh
        self.frame_bbox.append([x,y+int(h/5),w,h])
        self.position = xywh[0], xywh[1]
        self.lane_infos.append(lane_info)
        if len(self.lane_infos) > 5:
            del self.lane_infos[0]

        # if self._check_event_frame and not self.init_lane and not self.init_direction:
        #     self.init_status(lane_masks)
    

    @property
    def _cls(self):
        return config.names[self.cls]

    @property
    def lost(self):
        self.lane_state = False
        self.reverse_state = False
        self.stop_state = False
        self.speed_state = False

        self.life_count +=1
        return True if self.life_count > config.life else False
    
    def event(self):
        self.life_count = 0
        if not self._check_event_frame:
            return False
        self.cur_direction = self._current_direction

        self.check_lane_change()
        self.check_reverse()
        self.check_stop()
        self.check_speed_over()

    @property
    def _check_event_frame(self):
        return len(self.frame_bbox) == config.check_frame

    @property
    def _current_direction(self):
        frame_array = np.asarray(self.frame_bbox)[:, :1]
        direct = frame_array[-1] - frame_array[:-1]
        dist_x = np.sum(direct)/ len(direct)
        if np.abs(dist_x)>config.dist_thr:
            d = np.clip(np.diff(frame_array[:], axis=0), -1, 1).sum()
            if d < 0:
                self.current_direction = "Left"
            elif d > 0:
                self.current_direction = "Right"
            else: 
                self.current_direction = self.current_direction
        else:
            self.current_direction = 'Stop'

        return self.current_direction

    def check_stop(self):
        if self.cur_direction == 'Stop':
            self.stop_count += 1
        else:
            self.stop_count = 0

        if self.stop_count > config.stop_life:
            self.stop_state = True
            self.send_event(3)
            self.stop_count = 0
        else:
            self.stop_state = False

    def check_reverse(self):
        if self.cur_direction in ['Stop', self.init_direction]:
            self.reverse_state = False
        else:
            self.reverse_count+=1
            if self.reverse_count > config.reverse_life:
                self.send_event(1)
                self.reverse_state = True
                self.reverse_count = 0

    def check_lane_change(self):

        if all(self.lane_infos == self.lane_infos[0]):
            self.lane_state = False
        else:
            self.lane_state = True
            self.send_event(4)

    def check_speed_over(self):
        # self.send_event(2)
        self.speed_state = False

    def check_person(self):
        self.person_state = False

    def send_event(self, event_type):
        if self.event_state[event_type][0]==0:
            now = datetime.datetime.now()
            event_body = {
                "cam": 'cam'+str(self.cam_id),
                "camHls": "cam URI",
                "date": now.strftime("%Y%m%d-%H:%M:%S.%f"),
                "laneInfo": str(self.lane_infos[-1]),
                "position": self.frame_bbox[-1][:2]
            }
            LOGGER.warning(f"ID : {self.car_id}, {self.event_state[event_type][1]}, {event_body}")
            self.event_state[event_type][0] = 50
        else:
            self.event_state[event_type][0] -= 1
        # request(http_url, event_type, event_body)
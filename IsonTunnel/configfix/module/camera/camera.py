import cv2
import json
from IsonTunnel.configfix.module.camera import EventProcess, StitchProcess, CalibrationProcess
from IsonTunnel.configure import CONFIG_ROOT

class Camera(EventProcess, StitchProcess, CalibrationProcess):
    def __init__(self, cam_id, mode):
        self.cam_id = cam_id
        self.cam_path = f'{CONFIG_ROOT}/field/cam{cam_id}'
        self.param_path = f"{self.cam_path}/params.json"
        self.params = json.load(open(self.param_path))

        self.winmask = f'mask_cam_{cam_id}'
        self.winname_o = f'cam_{cam_id}'
        self.winname_t = f'Undistort_cam_{cam_id}'
        self.winname_d = f'draw_img_{cam_id}'

        if mode == "event":
            self.set_event()

        elif mode == "calib":
            self.set_calibration()

        elif mode == "stit":
            self.set_stit()
    
    def allclean(self):
        cv2.destroyAllWindows()
        return 1

    def image_view(self):
        cv2.imshow(self.winname_o, self.img)
        while True:
            cv2.imshow(self.winname_o, self.img)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                cv2.destroyWindow(self.winname_o)
                break
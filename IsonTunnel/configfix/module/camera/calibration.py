import numpy as np 
import cv2
import json

class CalibrationProcess:
    def set_calibration(self):
        self.img = cv2.imread(f'{self.cam_path}/lanes.jpg')
        self.K = np.array(self.params['K'])
        self.D = np.array(self.params['D'])
        self.theta = self.params['theta']
        self.h, self.w = self.img.shape[:2]
        self.transform()
        self.draw_img = self.transform_img.copy()
        self.actions = {
            ord('a'): lambda: self.update_D(0, 0.001),
            ord('s'): lambda: self.update_D(0, -0.001),
            ord('d'): lambda: self.update_D(1, 0.001),
            ord('f'): lambda: self.update_D(1, -0.001),
            ord('z'): lambda: self.update_D(2, 0.001),
            ord('x'): lambda: self.update_D(2, -0.001),
            ord('c'): lambda: self.update_D(3, 0.001),
            ord('v'): lambda: self.update_D(3, -0.001),

            ord('j'): lambda: self.update_theta(0.1),
            ord('k'): lambda: self.update_theta(-0.1),

            ord('y'): lambda: self.update_K([0,2], 1.0),
            ord('u'): lambda: self.update_K([0,2], -1.0),
            ord('i'): lambda: self.update_K([1,2], 1.0),
            ord('o'): lambda: self.update_K([1,2], -1.0),

            ord('1'): self.init_camera_parameter,

            ord('2'): self.save_calib_config,

            27: self.allclean
        }

    def update_D(self, idx, delta):
        self.D[idx] += delta

    def update_K(self, idx, delta):
        self.K[idx[0], idx[1]] += delta

    def update_theta(self, delta):
        self.theta += delta
    
    def init_camera_parameter(self):
        self.K = np.array(self.params['K'])
        self.D = np.array(self.params['D'])
        self.theta = self.params['theta']

    def save_calib_config(self):
        np.save(f'{self.cam_path}/mapx.npy', self.map1)
        np.save(f'{self.cam_path}/mapy.npy', self.map2)
        save_dict = self.params
        save_dict['K'] = self.K.tolist()
        save_dict['D'] = self.D.tolist()
        save_dict['theta'] = self.theta

        with open(self.param_path, "w") as write_file:
            json.dump(save_dict, write_file, indent=3)

        cv2.imwrite(f'{self.cam_path}/transform_img.jpg', self.transform_img)
    

    def get_fisheye_map(self, image_shape:list,K_coff,D_coff,raw_view=False):
        img_height,img_width = image_shape
        DIM = [img_width,img_height]
        balance_value = 0
        if(raw_view):
            balance_value = 1

        new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K_coff, D_coff, DIM, np.eye(3), balance=balance_value)
        self.map1, self.map2 = cv2.fisheye.initUndistortRectifyMap(K_coff, D_coff, np.eye(3), new_K, DIM, cv2.CV_16SC2)
    

    def transform(self):
        self.get_fisheye_map([self.h, self.w], self.K, self.D, raw_view=0)
        undistorted_img = cv2.remap(self.img, self.map1, self.map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        matrix = cv2.getRotationMatrix2D((int(self.w/2),int(self.h/2)), float(self.theta), 1.0)
        self.transform_img = cv2.warpAffine(undistorted_img, matrix, (self.w, self.h))

    def calibration(self):
        trigger=0
        self.transform()
        cv2.imshow(self.winname_t, self.transform_img)

        key = cv2.waitKey(1) & 0xFF

        action = self.actions.get(key)
        if action: action()

        if key == ord ('q'):
            cv2.destroyWindow(self.winname_t) # return self.K, self.D, self.theta_deg
            trigger=1
        
        return self.K, self.D, self.theta, trigger
    
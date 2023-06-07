import numpy as np
import cv2
import os
import time
import json


path = '/home/ljj/data/ison/old/ison_raw/video'

class VideoSplit:
    def __init__(self, path):
        self.cap = cv2.VideoCapture(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

    def video_split(self):
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # start_time = 153  # Start time in seconds
        # end_time = 200  # End time in seconds
        start_time = 195  # Start time in seconds
        end_time = 225  # End time in seconds
        self.start_frame = int(start_time * self.fps)
        self.end_frame = int(end_time * self.fps)
        self.frame_lst = []
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        for frame_num in range(self.start_frame, self.end_frame):
            ret, img = self.cap.read()
            self.frame_lst.append(img)
            if not ret:
                break
            # cv2.imshow("img", img)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #         break
        self.cap.release()
        cv2.destroyAllWindows()
    
    def set_calibration(self, param_path):
        self.params = json.load(open(param_path))
        self.K = np.array(self.params['K'])
        self.D = np.array(self.params['D'])
        self.theta = self.params['theta']
        h, w = (1080, 1920)
        self.get_fisheye_map([h, w], self.K, self.D, raw_view=0)

    def get_fisheye_map(self, image_shape:list,K_coff,D_coff,raw_view=False):
        img_height,img_width = image_shape
        DIM = [img_width,img_height]
        balance_value = 0
        if(raw_view):
            balance_value = 1

        new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K_coff, D_coff, DIM, np.eye(3), balance=balance_value)
        self.map1, self.map2 = cv2.fisheye.initUndistortRectifyMap(K_coff, D_coff, np.eye(3), new_K, DIM, cv2.CV_16SC2)
    
    def transform(self, img):
        h, w = img.shape[:2]
        undistorted_img = cv2.remap(img, self.map1, self.map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        matrix = cv2.getRotationMatrix2D((int(w/2),int(h/2)), float(self.theta), 1.0)
        return cv2.warpAffine(undistorted_img, matrix, (w, h))

    def video_show(self):
        while True:
            ret, img = self.cap.read()
            s = time.time()
            res = self.transform(img)
            res = cv2.resize(res, (800, 448), interpolation=cv2.INTER_LINEAR)
            cv2.imshow('img', res)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            print(time.time()-s)

    
    def video_save(self, output_name):
        height, width, _ = self.frame_lst[0].shape
        output_video = cv2.VideoWriter(output_name,
                                    cv2.VideoWriter_fourcc(*'mp4v'),
                                    self.fps,
                                    (width, height))

        # Write each frame from the frame_list to the output video
        for frame in self.frame_lst:
            output_video.write(frame)

    def save_capture(self, i):
        ret, img = self.cap.read()
        cv2.imwrite(f'img{i}.png', img)


if __name__ == '__main__':


    url1 = os.path.join(path, 'url11.mp4')
    url2 = os.path.join(path, 'url22.mp4')
    url3 = os.path.join(path, 'url33.mp4')
    url4 = os.path.join(path, 'url44.mp4')

    video1 = VideoSplit(url3)
    video1.video_split()
    video1.video_save('output_video3.mp4')

    video1 = VideoSplit(url1)
    video1.video_split()
    video1.video_save('output_video1.mp4')

    video1 = VideoSplit(url2)
    video1.video_split()
    video1.video_save('output_video2.mp4')

    video1 = VideoSplit(url4)
    video1.video_split()
    video1.video_save('output_video4.mp4')
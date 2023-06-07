import numpy as np
import json
import cv2
import torch
import math
import re

from threading import Thread
from IsonTunnel.configure import CONFIG_ROOT


class Camera:
    def __init__(self, cam_id, image):
        self.cam_id = cam_id
        self.cam_path = f'{CONFIG_ROOT}/field/cam{cam_id}'
        self.params = json.load(open(f"{self.cam_path}/params.json"))
        self.K = np.array(self.params['K'])
        self.D = np.array(self.params['D'])
        self.theta_deg = self.params['theta']
        self.cross_point_left = self.params['left_point']
        self.cross_point_right = self.params['right_point']

        h, w = image.shape[:2]

        self.get_fisheye_map([h, w], self.K, self.D, raw_view=0)
        self.matrix = cv2.getRotationMatrix2D((int(w/2),int(h/2)), float(self.theta_deg), 1.0)

    def get_fisheye_map(self, image_shape:list,K_coff,D_coff,raw_view=False):
        img_height,img_width = image_shape
        DIM = [img_width,img_height]
        balance_value = 0
        if(raw_view):
            balance_value = 1

        new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K_coff, D_coff, DIM, np.eye(3), balance=balance_value)
        self.map1, self.map2 = cv2.fisheye.initUndistortRectifyMap(K_coff, D_coff, np.eye(3), new_K, DIM, cv2.CV_16SC2)

    def transform_calib(self, image):
        h, w = image.shape[:2]
        undistorted_img = cv2.remap(image, self.map1, self.map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        transform_img = cv2.warpAffine(undistorted_img, self.matrix, (w, h))
        return transform_img

class VideoStream:
    # YOLOv8 streamloader, i.e. `yolo predict source='rtsp://example.com/media.mp4'  # RTSP, RTMP, HTTP streams`
    def __init__(self, sources='file.streams', imgsz=640, stride=32, auto=True, transforms=None, vid_stride=1):
        torch.backends.cudnn.benchmark = True  # faster for fixed-size inference
        self.mode = 'video'
        self.imgsz = imgsz
        self.stride = stride
        self.vid_stride = vid_stride  # video frame-rate stride
        # sources = Path(sources).read_text().rsplit() if os.path.isfile(sources) else [sources]
        sources = ['/home/ljj/workspace/ison-tunnel/output_video1.mp4',
                    '/home/ljj/workspace/ison-tunnel/output_video2.mp4',
                    '/home/ljj/workspace/ison-tunnel/output_video3.mp4',
                    '/home/ljj/workspace/ison-tunnel/output_video4.mp4',
                   ]
        n = len(sources)
        self.sources = [clean_str(x) for x in sources]  # clean source names for later
        self.imgs, self.fps, self.frames, self.threads = [None] * n, [0] * n, [0] * n, [None] * n
        self.cams = []
        for i, s in enumerate(sources):  # index, source
            # Start thread to read frames from video stream
            st = f'{i + 1}/{n}: {s}... '
            s = eval(s) if s.isnumeric() else s  # i.e. s = '0' local webcam
            cap = cv2.VideoCapture(s)
            if not cap.isOpened():
                raise ConnectionError(f'{st}Failed to open {s}')
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)  # warning: may return 0 or nan
            self.frames[i] = max(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 0) or float('inf')  # infinite stream fallback
            self.fps[i] = max((fps if math.isfinite(fps) else 0) % 100, 0) or 30  # 30 FPS fallback
            self.cams.append(Camera(i+1, cap.read()[1]))

            success, self.imgs[i] = cap.read()  # guarantee first frame
            if not success or self.imgs[i] is None:
                raise ConnectionError(f'{st}Failed to read images from {s}')
            self.threads[i] = Thread(target=self.update, args=([i, cap, s]), daemon=True)
            # LOGGER.info(f'{st}Success ✅ ({self.frames[i]} frames of shape {w}x{h} at {self.fps[i]:.2f} FPS)')
            self.threads[i].start()
        # LOGGER.info('')  # newline

        # check for common shapes
        s = np.stack([LetterBox(imgsz, auto, stride=stride)(image=x).shape for x in self.imgs])
        self.rect = np.unique(s, axis=0).shape[0] == 1  # rect inference if all shapes equal
        self.auto = auto and self.rect
        self.transforms = transforms  # optional
        self.bs = self.__len__()
        

    def update(self, i, cap, stream):
        # Read stream `i` frames in daemon thread
        n, f = 0, self.frames[i]  # frame number, frame array
        while cap.isOpened() and n < f:
            n += 1
            cap.grab()  # .read() = .grab() followed by .retrieve()
            if n % self.vid_stride == 0:
                success, im = cap.retrieve()
                if success:
                    res =  self.cams[i].transform_calib(im)
                    res = cv2.resize(res, (800, 448), interpolation=cv2.INTER_LINEAR)
                    self.imgs[i] = res
                else:
                    self.imgs[i] = np.zeros_like(self.imgs[i])
                    cap.open(stream)  # re-open stream if signal was lost

    def __iter__(self):
        self.count = -1
        return self

    def __next__(self):
        self.count += 1
        if not all(x.is_alive() for x in self.threads) or cv2.waitKey(1) == ord('q'):  # q to quit
            cv2.destroyAllWindows()
            raise StopIteration

        im0 = self.imgs.copy()
        # cv2.imshow(f'asd', im0[0])
        # cv2.imshow(f'as', im0[1])
        # cv2.imshow(f'ad', im0[2])
        # cv2.imshow(f'sd', im0[3])
        # cv2.waitKey(1)
        
        if self.transforms:
            im = np.stack([self.transforms(x) for x in im0])  # transforms
        else:
            im = np.stack([LetterBox(self.imgsz, self.auto, stride=self.stride)(image=x) for x in im0])
            im = im[..., ::-1].transpose((0, 3, 1, 2))  # BGR to RGB, BHWC to BCHW
            im = np.ascontiguousarray(im)  # contiguous


        return self.sources, im, im0, None, ''

    def __len__(self):
        return len(self.sources)  # 1E12 frames = 32 streams at 30 FPS for 30 years

class LoadStreams:
    # YOLOv8 streamloader, i.e. `yolo predict source='rtsp://example.com/media.mp4'  # RTSP, RTMP, HTTP streams`
    def __init__(self, sources='file.streams', imgsz=640, stride=32, auto=True, transforms=None, vid_stride=1):
        torch.backends.cudnn.benchmark = True  # faster for fixed-size inference
        self.mode = 'stream'
        self.imgsz = imgsz
        self.stride = stride
        self.vid_stride = vid_stride  # video frame-rate stride
        # sources = Path(sources).read_text().rsplit() if os.path.isfile(sources) else [sources]
        n = len(sources)
        self.sources = [clean_str(x) for x in sources]  # clean source names for later
        self.imgs, self.fps, self.frames, self.threads = [None] * n, [0] * n, [0] * n, [None] * n
        self.cams = []
        for i, s in enumerate(sources):  # index, source
            # Start thread to read frames from video stream
            st = f'{i + 1}/{n}: {s}... '
            s = eval(s) if s.isnumeric() else s  # i.e. s = '0' local webcam
            cap = cv2.VideoCapture(s)
            if not cap.isOpened():
                raise ConnectionError(f'{st}Failed to open {s}')
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)  # warning: may return 0 or nan
            self.frames[i] = max(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 0) or float('inf')  # infinite stream fallback
            self.fps[i] = max((fps if math.isfinite(fps) else 0) % 100, 0) or 30  # 30 FPS fallback
            self.cams.append(Camera(i+1, cap.read()[1]))

            success, self.imgs[i] = cap.read()  # guarantee first frame
            if not success or self.imgs[i] is None:
                raise ConnectionError(f'{st}Failed to read images from {s}')
            self.threads[i] = Thread(target=self.update, args=([i, cap, s]), daemon=True)
            # LOGGER.info(f'{st}Success ✅ ({self.frames[i]} frames of shape {w}x{h} at {self.fps[i]:.2f} FPS)')
            self.threads[i].start()
        # LOGGER.info('')  # newline

        # check for common shapes
        s = np.stack([LetterBox(imgsz, auto, stride=stride)(image=x).shape for x in self.imgs])
        self.rect = np.unique(s, axis=0).shape[0] == 1  # rect inference if all shapes equal
        self.auto = auto and self.rect
        self.transforms = transforms  # optional
        self.bs = self.__len__()
        

    def update(self, i, cap, stream):
        # Read stream `i` frames in daemon thread
        n, f = 0, self.frames[i]  # frame number, frame array
        while cap.isOpened() and n < f:
            n += 1
            cap.grab()  # .read() = .grab() followed by .retrieve()
            if n % self.vid_stride == 0:
                success, im = cap.retrieve()
                if success:
                    transform_im =  self.cams[i].transform_calib(im)
                    self.imgs[i] = transform_im
                else:
                    self.imgs[i] = np.zeros_like(self.imgs[i])
                    cap.open(stream)  # re-open stream if signal was lost

    def __iter__(self):
        self.count = -1
        return self

    def __next__(self):
        self.count += 1
        if not all(x.is_alive() for x in self.threads) or cv2.waitKey(1) == ord('q'):  # q to quit
            cv2.destroyAllWindows()
            raise StopIteration

        im0 = self.imgs.copy()
        # cv2.imshow(f'asd', im0[0])
        # cv2.imshow(f'as', im0[1])
        # cv2.imshow(f'ad', im0[2])
        # cv2.imshow(f'sd', im0[3])
        # cv2.waitKey(1)
        
        if self.transforms:
            im = np.stack([self.transforms(x) for x in im0])  # transforms
        else:
            im = np.stack([LetterBox(self.imgsz, self.auto, stride=self.stride)(image=x) for x in im0])
            im = im[..., ::-1].transpose((0, 3, 1, 2))  # BGR to RGB, BHWC to BCHW
            im = np.ascontiguousarray(im)  # contiguous


        return self.sources, im, im0, None, ''

    def __len__(self):
        return len(self.sources)  # 1E12 frames = 32 streams at 30 FPS for 30 years

class LetterBox:
    """Resize image and padding for detection, instance segmentation, pose"""

    def __init__(self, new_shape=(640, 640), auto=False, scaleFill=False, scaleup=True, stride=32):
        self.new_shape = new_shape
        self.auto = auto
        self.scaleFill = scaleFill
        self.scaleup = scaleup
        self.stride = stride

    def __call__(self, labels=None, image=None):
        if labels is None:
            labels = {}
        img = labels.get('img') if image is None else image
        shape = img.shape[:2]  # current shape [height, width]
        new_shape = labels.pop('rect_shape', self.new_shape)
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not self.scaleup:  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
        if self.auto:  # minimum rectangle
            dw, dh = np.mod(dw, self.stride), np.mod(dh, self.stride)  # wh padding
        elif self.scaleFill:  # stretch
            dw, dh = 0.0, 0.0
            new_unpad = (new_shape[1], new_shape[0])
            ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

        dw /= 2  # divide padding into 2 sides
        dh /= 2
        if labels.get('ratio_pad'):
            labels['ratio_pad'] = (labels['ratio_pad'], (dw, dh))  # for evaluation

        if shape[::-1] != new_unpad:  # resize
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT,
                                 value=(114, 114, 114))  # add border

        if len(labels):
            labels = self._update_labels(labels, ratio, dw, dh)
            labels['img'] = img
            labels['resized_shape'] = new_shape
            return labels
        else:
            return img

    def _update_labels(self, labels, ratio, padw, padh):
        """Update labels"""
        labels['instances'].convert_bbox(format='xyxy')
        labels['instances'].denormalize(*labels['img'].shape[:2][::-1])
        labels['instances'].scale(*ratio)
        labels['instances'].add_padding(padw, padh)
        return labels

def clean_str(s):
    """
    Cleans a string by replacing special characters with underscore _

    Args:
      s (str): a string needing special characters replaced

    Returns:
      (str): a string with special characters replaced by an underscore _
    """
    return re.sub(pattern='[|@#!¡·$€%&()=?¿^*;:,¨´><+]', repl='_', string=s)
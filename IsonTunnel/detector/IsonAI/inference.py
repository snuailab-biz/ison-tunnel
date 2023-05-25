from pathlib import Path
import torch
import numpy as np 
import time
from ultralytics.nn.autobackend import AutoBackend
from ultralytics.yolo.cfg import get_cfg
from ultralytics.yolo.engine.results import Results
from ultralytics.yolo.utils import DEFAULT_CFG, SETTINGS, ops, IterableSimpleNamespace, yaml_load
from ultralytics.yolo.utils.checks import check_imgsz, check_yaml
from ultralytics.yolo.utils.files import increment_path
from ultralytics.yolo.utils.torch_utils import select_device, smart_inference_mode
from ultralytics.tracker import BOTSORT, BYTETracker

from IsonTunnel.detector.config import logger

logger_detector = logger.bind(detector="detector")
TRACKER_MAP = {'bytetrack': BYTETracker, 'botsort': BOTSORT}

from IsonTunnel.detector.IsonAI.streamer import LoadStreams
from IsonTunnel.configure import CONFIG_ROOT


class IsonPredictor:
    def __init__(self, cfg=DEFAULT_CFG, overrides=None):
        self.args = get_cfg(cfg, overrides)
        self.args.device=1
        project = self.args.project or Path(SETTINGS['runs_dir']) / self.args.task
        name = self.args.name or f'{self.args.mode}'
        self.save_dir = increment_path(Path(project) / name, exist_ok=self.args.exist_ok)
        self.args.conf = 0.85
        self.done_warmup = False

        # Usable if setup is done
        self.model = None 
        self.data = self.args.data  # data_dict
        self.imgsz = None
        self.device = None
        self.dataset = None
        self.vid_path, self.vid_writer = None, None
        self.annotator = None
        self.data_path = None
        self.batch = None
        self.sync = 0
        self.log_count = 0

        if self.args.verbose or self.args.save or self.args.save_txt or self.args.show:
            self.vis = True
        else:
            self.vis = False

        self.setup_model()
        self.setup_source()
        self.setup_tracker()
        self.model.warmup(imgsz=(1 if self.model.pt or self.model.triton else self.dataset.bs, 3, *self.imgsz))
    
    def setup_tracker(self):
        tracker = check_yaml(self.args.tracker)
        cfg = IterableSimpleNamespace(**yaml_load(tracker))
        assert cfg.tracker_type in ['bytetrack', 'botsort'], \
            f"Only support 'bytetrack' and 'botsort' for now, but got '{cfg.tracker_type}'"
        trackers = []
        for _ in range(self.dataset.bs):
            tracker = TRACKER_MAP['bytetrack'](args=cfg, frame_rate=30)
            trackers.append(tracker)
        self.trackers = trackers
        logger_detector.info('Setup Tracker')
        

    def setup_model(self, verbose=True):
        device = select_device(self.args.device, verbose=verbose)
        self.args.half &= device.type != 'cpu'  # half precision only supported on CUDA
        self.model = AutoBackend(CONFIG_ROOT / self.args.model,
                                 device=device,
                                 dnn=self.args.dnn,
                                 data=self.args.data,
                                 fp16=self.args.half,
                                 verbose=verbose)
        self.device = device
        self.model.eval()
        logger_detector.info('Setup model')

    def setup_source(self):
        self.imgsz = check_imgsz(self.args.imgsz, stride=self.model.stride, min_dim=2)  # check image size
        transforms = None


        logger_detector.info('Setup RTSP')
        self.dataset = LoadStreams(self.args.source,
                            imgsz=self.imgsz,
                            stride=self.model.stride,
                            auto=self.model.pt,
                            transforms=transforms,
                            vid_stride=self.args.vid_stride)

        self.vid_path, self.vid_writer = [None] * self.dataset.bs, [None] * self.dataset.bs
        



    def preprocess(self, img):
        img = (img if isinstance(img, torch.Tensor) else torch.from_numpy(img)).to(self.model.device)
        img = img.half() if self.model.fp16 else img.float()  # uint8 to fp16/32
        img /= 255  # 0 - 255 to 0.0 - 1.0
        return img

    def postprocess(self, preds, img, orig_imgs):
        preds = ops.non_max_suppression(preds,
                                        self.args.conf,
                                        self.args.iou,
                                        agnostic=self.args.agnostic_nms,
                                        max_det=self.args.max_det,
                                        classes=self.args.classes)

        results = []
        for i, pred in enumerate(preds):
            orig_img = orig_imgs[i] if isinstance(orig_imgs, list) else orig_imgs
            if not isinstance(orig_imgs, torch.Tensor):
                pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], orig_img.shape)
            path, _, _, _, _ = self.batch
            img_path = path[i] if isinstance(path, list) else path
            results.append(Results(orig_img=orig_img, path=img_path, names=self.model.names, boxes=pred))
        return results
    
    def on_predict_postprocess_end(self):
        bs = self.dataset.bs
        im0s = self.batch[2]
        im0s = im0s if isinstance(im0s, list) else [im0s]

        for i in range(bs):
            det = self.results[i].boxes.cpu().numpy()
            if len(det) == 0:
                continue
            tracks = self.trackers[i].update(det, im0s[i])
            if len(tracks) == 0:
                continue
            self.results[i].update(boxes=torch.as_tensor(tracks[:, :-1]))

    def send_server(self, data_lst):
        total_bytes = bytes()
        batch_length = len(data_lst)
        b_byte = batch_length.to_bytes(1, 'little', signed=False) # int to bytes
        total_bytes += b_byte
        for data in data_lst:
            info = data[0]
            det_len = len(info)
            det_len_byte = det_len.to_bytes(1, 'little', signed=False) # int to bytes
            det_info_byte = info.tobytes() # np to bytes
        #==================== Image ====================#
            img = data[1]

            # result, imgencode = cv2.imencode('.jpg', img, encode_param)
            # img_bytes = imgencode.tobytes()
            img_bytes = img.tobytes()
            img_len_byte = len(img_bytes).to_bytes(3, 'little', signed=False)

            # b_byte + 1.det_num + 1.det_info + 1.image_num + 1.image
            total_bytes += (det_len_byte + det_info_byte + img_len_byte + img_bytes)
        
        


        # time.sleep(0.005)
        return total_bytes

    def network(self, results):
        batch_lst = []
        for camera, result in enumerate(results):
            info_result = np.empty((0,8), int)
            det = result.boxes  # TODO: make boxes inherit from tensors
            if len(det) == 0:
                batch_lst.append([info_result, result.orig_img])
                continue
            # ------------------------------ Detect ----------------------------------- #
            for d in reversed(det):
                # print(d.cls, d.id, d.xywh.squeeze())
                cls, id, [x, y, w, h] = int(d.cls), 0 if d.id is None else int(d.id), [int(item) for item in d.xywh.squeeze()]
                info_result = np.append(info_result, np.array([[id, x, y, w, h, self.sync, cls, camera]]), axis=0)
            batch_lst.append([info_result, result.orig_img])
        
        send_bytes = self.send_server(batch_lst)
        
        return send_bytes


    def send_unity(self, results):
        batch_lst = []
        unity_bytes = bytes()
        object_num = 0
        st = time.time()
        for camera, result in enumerate(results):
            det = result.boxes
            if len(det) == 0:
                continue
            object_num += len(det)
            for d in det:
                unity_bytes += self.ison_simulator_protocol(d, camera) 

        object_byte = object_num.to_bytes(4, 'little', signed=False)
        unity_bytes = object_byte + unity_bytes
            
        return unity_bytes
    
    def ison_simulator_protocol(self, obj, camera):
        cls, id, [x, y, w, h] = int(obj.cls), 0 if obj.id is None else int(obj.id), [int(item) for item in obj.xywh.squeeze()]
        byte_id = id.to_bytes(4, 'little', signed=True)

        byte_cx = int(x).to_bytes(4, 'little', signed=True)
        byte_cy = int(y).to_bytes(4, 'little', signed=True)
        byte_w = int(w).to_bytes(4, 'little', signed=True)
        byte_h = int(h).to_bytes(4, 'little', signed=True)

        byte_time = self.sync.to_bytes(4, 'little', signed=True)
        byte_cls = cls.to_bytes(4, 'little', signed=True)
        byte_camera = camera.to_bytes(4, 'little', signed=True)

        return byte_id+byte_cx+byte_cy+byte_w+byte_h+byte_time+byte_cls+byte_camera
    

    @smart_inference_mode()
    def stream_inference(self, image_queue, unity_queue):
        self.seen, self.windows, self.dt, self.batch = 0, [], (ops.Profile(), ops.Profile(), ops.Profile(), ops.Profile()), None
        
        for batch in self.dataset:
            self.batch = batch
            _, im, im0s, _, s = batch

            # preprocess
            with self.dt[0]:
                im = self.preprocess(im)
                if len(im.shape) == 3:
                    im = im[None]  # expand for batch dim

            # inference
            with self.dt[1]:
                preds = self.model(im, augment=self.args.augment, visualize=False)

            # postprocess
            with self.dt[2]:
                self.results = self.postprocess(preds, im, im0s)
                self.on_predict_postprocess_end()
            
            with self.dt[3]:
                self.sync+=1
                image_bytes = self.network(self.results)
                if not image_queue.full():
                    image_queue.put(image_bytes)

                unity_bytes = self.send_unity(self.results)
                if not unity_queue.full():
                    unity_queue.put(unity_bytes)


        # #     # Print time (inference-only)
            # if self.args.verbose:
            self.log_count += 1
            if self.log_count % 300 == 0:
                self.log_count=1
                logger_detector.info(f'\n [Avg] Pre-processing : {(self.dt[0].dt) * 1E3:.1f}ms, Detector model : {(self.dt[1].dt) * 1E3:.1f}ms, Post-processing : {(self.dt[2].dt) * 1E3:.1f}ms, Network : {(self.dt[3].dt) * 1E3:.1f}ms, Total : {sum([t.dt for t in self.dt]) * 1E3:.1f}ms')
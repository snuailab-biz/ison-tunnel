from IsonTunnel.stitch import STITCH_CFG, LOGGER
import cv2
from threading import Thread
import time
import numpy as np
import math
import gi
from gi.repository import Gst, GstRtspServer, GLib
Gst.init(None)
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')

from IsonTunnel.stitch.IsonStitch.camera import Camera, stitch_blending, create_outline_mask

current_state = None
class IsonStitchRTSP(GstRtspServer.RTSPMediaFactory):
    def __init__(self, config, **properties):
        super(IsonStitchRTSP, self).__init__(**properties)
        self.img_width = 3200;#self.img_width = 5120
        self.img_height = 798;#self.img_height = 1080
        self.stat = True
        self.started = False
        self.number_frames = 0
        fps = 30
        self.duration = 1 / fps * Gst.SECOND  # duration of a frame in nanoseconds
        self.vid_stride = 1
        self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                             'caps=video/x-raw,format=BGR,width={},height={},framerate={}/1 ' \
                             '! videoconvert ! video/x-raw,format=I420 ' \
                             '! x264enc speed-preset=ultrafast tune=zerolatency ' \
                             '! rtph264pay config-interval=1 name=pay0 pt=96' \
                             .format(self.img_width, self.img_height, fps)
        sources = [ config.camera_url[0], config.camera_url[1], config.camera_url[2], config.camera_url[3] ]
        n = len(sources)
        self.imgs, self.fps, self.frames, self.threads = [None] * n, [0] * n, [0] * n, [None] * n
        for i, s in enumerate(sources):
            st = f'{i + 1}/{n}: {s}... '
            cap = cv2.VideoCapture(s)
            assert cap.isOpened(), f'Failed to open {s}'
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.frames[i] = max(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 0) or float('inf')  # infinite stream fallback
            self.fps[i] = max((fps if math.isfinite(fps) else 0) % 100, 0) or 30  # 30 FPS fallback

            success, self.imgs[i] = cap.read()  # guarantee first frame
            if not success or self.imgs[i] is None:
                raise ConnectionError(f'{st}Failed to read images from {s}')
            self.threads[i] = Thread(target=self.update, args=([i, cap, s]), daemon=True)
            LOGGER.info(f'{st}Success ✅ ({self.frames[i]} frames of shape {w}x{h} at {self.fps[i]:.2f} FPS)')
            self.threads[i].start()
        
        self.cam1 = Camera(1, self.imgs[0])
        self.cam2 = Camera(2, self.imgs[1])
        self.cam3 = Camera(3, self.imgs[2])
        self.cam4 = Camera(4, self.imgs[3])

        self.log_count = 0

        image_resize = (800,798)
        stitch_offset = 100
        self.mask = create_outline_mask(image_size=image_resize, offset=stitch_offset)
        self.inv_mask = 1.0-self.mask

    def update(self, i, cap, stream):
        n, f = 0, self.frames[i]
        while cap.isOpened() and n < f:
            n +=1 
            cap.grab()  # .read() = .grab() followed by .retrieve()
            if n % self.vid_stride == 0:
                success, im = cap.retrieve()
                if success:
                    self.imgs[i] = im
                else:
                    self.imgs[i] = np.zeros_like(self.imgs[i])
                    cap.open(stream)  # re-open stream if signal was lost
            #time.sleep(300.0)  # wait time

    def on_need_data(self, src, length):
        global current_state
        self.log_count += 1
        # =================================================================================
        # ==============================Image Processing===================================
        # =================================================================================
        st = time.time()
        
        frame1 = self.imgs[0].copy()
        frame2 = self.imgs[1].copy()
        frame3 = self.imgs[2].copy()
        frame4 = self.imgs[3].copy()

        trasform_img1 = self.cam1.transform_calib(frame1)
        trasform_img2 = self.cam2.transform_calib(frame2)
        trasform_img3 = self.cam3.transform_calib(frame3)
        trasform_img4 = self.cam4.transform_calib(frame4)

        undistortion_1 = self.cam1.transform_stit(trasform_img1)
        undistortion_2 = self.cam2.transform_stit(trasform_img2)
        undistortion_3 = self.cam3.transform_stit(trasform_img3)
        undistortion_4 = self.cam4.transform_stit(trasform_img4)

        stitch_imgs = [undistortion_1, undistortion_2, undistortion_3, undistortion_4]
        frame=stitch_blending(stitch_imgs, self.mask, self.inv_mask)

        buf = Gst.Buffer.new_wrapped(frame.tobytes());
        

        buf.duration = self.duration
        timestamp = self.number_frames * self.duration
        buf.pts = buf.dts = int(timestamp)
        buf.offset = timestamp
        self.number_frames += 1

        current_state = Gst.State.PLAYING
        retval = src.emit('push-buffer', buf)
        if retval != Gst.FlowReturn.OK:
            current_state = Gst.State.NULL
            LOGGER.info(retval)
            LOGGER.info('The user has ended the monitoring.')
            src.emit('end-of-stream')
        
        if self.log_count % 300 == 0:
            current_state = Gst.State.NULL
            self.log_count = 1
            LOGGER.info(f" [Avg] RTSP Process Time: {time.time() - st}ms")

    def do_create_element(self, _):
        return Gst.parse_launch(self.launch_string)
    
    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)
    
# Rtsp server implementation where we attach the factory sensor with the stream uri
class GstServer(GstRtspServer.RTSPServer):
    def __init__(self, config, **properties):
        super(GstServer, self).__init__(**properties)
        self.factory = IsonStitchRTSP(config)
        self.factory.set_shared(True)
        self.set_service(str(config.stitch_port))
        self.get_mount_points().add_factory(config.stitch_stream_uri, self.factory)
        self.attach(None)


def log_every_10s():
    if not current_state == Gst.State.PLAYING:
        LOGGER.info("The user is not monitoring the simulator.")
    return True


def run():
    while True:
        try:
            Gst.init(None)
            LOGGER.info('================================================')
            LOGGER.info(f'Ison Stitch RTSP Streaming - version {STITCH_CFG.version}' )
            LOGGER.info('------------------------------------------------')
            LOGGER.info(f'IP: {STITCH_CFG.rtsp_ip}')
            LOGGER.info(f'Port: {STITCH_CFG.stitch_port}')
            LOGGER.info('================================================')
            server = GstServer(STITCH_CFG)
            loop = GLib.MainLoop()
            LOGGER.info("RTSP Strat ! ! !")
            GLib.timeout_add_seconds(10, log_every_10s)
            loop.run()
        except Exception as e:
            LOGGER.exception(e)

if __name__ == '__main__':
    run()
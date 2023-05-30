from IsonTunnel.streamer import STREAM_CFG, LOGGER
from _thread import *
import gi
import time

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib
from IsonTunnel.streamer.IsonStreamer import IsonSimulator

current_state = None

class IsonRtsp(GstRtspServer.RTSPMediaFactory):
    def __init__(self, **properties):
        super(IsonRtsp, self).__init__(**properties)
        self.pipeline = Gst.Pipeline()
        self.img_width = 1920
        self.img_height = 1080
        self.stat = True
        self.started = False
        self.number_frames = 0
        fps = 30
        self.duration = 1 / fps * Gst.SECOND
        self.vid_stride = 1
        self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                             'caps=video/x-raw,format=BGR,width={},height={},framerate={}/1 ' \
                             '! videoconvert ! video/x-raw,format=I420 ' \
                             '! x264enc speed-preset=ultrafast tune=zerolatency ! queue ' \
                             '! rtph264pay config-interval=1 name=pay0 pt=96' \
                             .format(self.img_width, self.img_height, fps)
        self.imgs, self.fps, self.frames, self.threads = [None], [None], [None], [None]
        self.log_count = 0
        self.ison_simulator = IsonSimulator(STREAM_CFG.simulator_ip, STREAM_CFG.simulator_port, LOGGER)

	
    def on_need_data(self, src, lenght):
        try:
            global current_state
            self.log_count += 1
            st = time.time()
            data = self.ison_simulator.recv_simulator_byte()
            # delay = (0.03-(time.time()-st)) if (0.033-(time.time()-st))> 0 else 0
            # time.sleep(delay)
            buf = Gst.Buffer.new_allocate(None, len(data), None)
            buf.fill(0, data)
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
        
        except Exception as e:
            LOGGER.info(f'The connection to the simulator server has been lost. \n{e}')  # 로그 남기기
            src.emit('end-of-stream')
            self.on_error()
    
    # def on_error(self):
    #     loop.quit()
        # Gst.quit()

    def do_create_element(self, _):
        return Gst.parse_launch(self.launch_string)
    
    def do_configure(self, rtsp_media):
        self.number_frames =0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        LOGGER.info('Starting Rtsp streaming to user.')  # 로그 남기기
        appsrc.connect('need-data', self.on_need_data)
        


class GstServer(GstRtspServer.RTSPServer):
    def __init__(self, config, **properties):
        super(GstServer, self).__init__(**properties)
        # threading.Thread.__init__(self)
        self.factory = IsonRtsp()
        self.factory.set_shared(True)
        self.set_service(str(config.rtsp_port))
        self.get_mount_points().add_factory(config.stream_uri, self.factory)
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
            LOGGER.info(f'Ison Simulator RTSP Streaming' )
            LOGGER.info('------------------------------------------------')
            LOGGER.info(f'Simulator IP: {STREAM_CFG.simulator_ip}')
            LOGGER.info(f'Simulator Port: {STREAM_CFG.simulator_port}')
            LOGGER.info(f'RTSP IP: {STREAM_CFG.rtsp_ip}')
            LOGGER.info(f'RTSP Port: {STREAM_CFG.rtsp_port}')
            LOGGER.info('================================================')

            server = GstServer(STREAM_CFG)
            loop = GLib.MainLoop()
            LOGGER.info("RTSP Strat ! ! !")
            GLib.timeout_add_seconds(10, log_every_10s)
            loop.run()
        except Exception as e:
            LOGGER.exception(e)


if __name__ == '__main__':
    run()

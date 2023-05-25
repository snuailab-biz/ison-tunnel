import sys
import socket
import numpy as np
import time
from IsonTunnel.eventer.IsonEvent import IsonCamera
from IsonTunnel.eventer.config import logger, log_exception, DEFAULT_CFG
import cv2


class IsonClient:
    @log_exception(logger, level="CRITICAL", message="IP : {}, PORT : {}".format(DEFAULT_CFG.detect_ip, DEFAULT_CFG.detect_port))
    def __init__(self, config):
        self.output_imgsz = config.image_size
        self.show=config.show
        self.save=config.save
        while True:
            try:
                self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
                # self.client_socket.connect((config.detect_ip, config.detect_port)) 
                self.client_socket.connect((config.detect_ip, config.detect_port)) 
                self.client_socket.send('ISON'.encode()) 
                logger.info(f"Connection Detector Server. IP : {config.detect_ip} Port : {config.detect_port}.")
                break
            except ConnectionRefusedError:
                logger.warning(f"Connection Refused. retrying in {config.retry_time} seconds...")
                time.sleep(config.retry_time)
            
        self.setup_camera(config)
        self.log_count = 0

    def run(self):
        st = time.time()
        while True: 
            self.log_count +=1
            self.recv_detector_byte()
            self.event_process()
            # delay = (0.02992-(time.time()-st)) if (0.033-(time.time()-st))> 0 else 0
            # time.sleep(delay)
            if self.log_count % 300 == 0:
                self.log_count = 0
                logger.info(f"\n [Avg] Byte Receive and processing Time, {time.time() - st}ms")
            st = time.time()
    
    def event_process(self):
        for eventer in self.camera_dict.values():
            eventer.event_update()
            eventer.event()
    
    def recv_detector_byte(self):
        len_byte = self.recvall(1)
        batch_len = int.from_bytes(len_byte, byteorder='little')

        for i in range(batch_len):
            det_len_byte = self.recvall(1)
            det_len = int.from_bytes(det_len_byte, byteorder='little')

            det_info_byte = self.recvall(det_len*64)
            det_info = np.frombuffer(det_info_byte, int).reshape(det_len, 8)

            img_len_byte = self.recvall(3)
            img_len = int.from_bytes(img_len_byte, byteorder='little')

            img_byte = self.recvall(img_len)
            data = np.frombuffer(img_byte, np.uint8) # decimg = cv2.imdecode(data, 1)

            img = data.reshape(self.output_imgsz)

            self.camera_dict[i].update(orig_img=img, det_info=det_info)
        self.show_and_write(4)
        cv2.waitKey(1)
        
    def recvall(self, length):
        buf = b''
        while length:
            newbuf = self.client_socket.recv(length)
            if not newbuf: return None
            buf += newbuf
            length -= len(newbuf)
        return buf

    def setup_camera(self, config):
        self.camera_dict = {
            0: IsonCamera(0, config.names),
            1: IsonCamera(1, config.names),
            2: IsonCamera(2, config.names),
            3: IsonCamera(3, config.names),
        }

    def show_and_write(self, batch_len):
        for i in range(batch_len):
            if self.show: self.camera_dict[i].show(str(i+1))
            if self.save: self.vid_writer[i].write(self.camera_dict[i].orig_img)

def run():
    # try:
    client = IsonClient(config=DEFAULT_CFG)
    client.run()
    # except Exception as e:
    #     logger.exception(e)
    #     sys.exit(1)

if __name__ == '__main__':
    run()
        
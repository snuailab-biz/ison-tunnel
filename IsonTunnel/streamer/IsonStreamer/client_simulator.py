
import socket 
import numpy as np
import cv2
import time
import sys

class IsonSimulator:
    def __init__(self, ip, port, logger):
        count = 0
        while True:
            try:
                self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
                self.client_socket.connect((ip, port)) 
                self.client_socket.send((1).to_bytes(4,'little', signed=True))

                logger.info(f"Connected to the Simulation Server.")
                break
            except ConnectionRefusedError:
                logger.warning("Simulation server not connected. Retrying in 5 seconds...")
                time.sleep(5)
                count+=1
                if count ==10:
                    logger.error("\nError, Please start the Simulator\n")
                    sys.exit(1)

    def run(self):
        while True: 
            st = time.time()
            frame = self.recv_simulator_byte()
            cv2.imshow("sdffsd", frame)
            # delay = (0.03322-(time.time()-st)) if (0.03322-(time.time()-st))> 0 else 0
            # time.sleep(delay)
            print(time.time() - st)
            key=cv2.waitKey(1)
            self.vid_writer.write(frame)
            if key & 0xFF == ord('q'):
                break
        
    
    def recv_simulator_byte(self):
        msg = self.recvall(int(1920*1080*3))
        data=np.frombuffer(msg, dtype=np.uint8)
        frame = data.reshape(1080,1920,3)
        frame = frame[::-1, :, ::-1]
        data = frame.tobytes()
        return data

    def recvall(self, length):
        buf = b''
        while length:
            newbuf = self.client_socket.recv(length)
            if not newbuf: return None
            buf += newbuf
            length -= len(newbuf)
        return buf



if __name__ == '__main__':
    a = IsonSimulator('localhost', 1235)
    a.run()

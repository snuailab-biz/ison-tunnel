import socketserver
import threading
from queue import Queue
image_queue = Queue(100)
unity_queue = Queue(100)
lock = threading.Lock()

class StreamManager:
    def __init__(self):
        self.users = {}
    
    def addUser(self, username, conn, addr):
        lock.acquire()
        self.users[username] = (conn, addr)
        lock.release()

        connect_print = '[{}] 연결완료'.format(username)

        print(connect_print)

        return username

    def removeUser(self, username):
        if username not in self.users:
            return 

        lock.acquire()
        del self.users[username]
        lock.release()

        connect_print = '[{}] 연결 종료'.format(username)
        print(connect_print)
    
import time

        
class ServerHandler(socketserver.BaseRequestHandler):
    streamer = StreamManager()

    def handle(self):
        print("[{}] Connect".format(self.client_address[0]))

        try:
            username = self.registerUsername()
            if username =='ISON':
                self.send_server()
            else:
                self.send_unity()
        except Exception as e:
            print(e)
        
        print('{} 접속 종료'.format(self.client_address[0]))
        self.streamer.removeUser(username)
    

    def send_server(self): 
        while True: 
            try:
                # if not image_queue.empty():
                stringData = image_queue.get()
                self.request.send(stringData)

            except ConnectionResetError as e:
                break

    def send_unity(self): 
        while True: 
            try:
                stringData = unity_queue.get()
                self.request.send(stringData)
                

            except ConnectionResetError as e:
                break
    
    def registerUsername(self):
        while True:
            username = self.request.recv(1024)
            username = username.decode().strip()

            if self.streamer.addUser(username, self.request, self.client_address):
                return username
    
class ServerIson(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
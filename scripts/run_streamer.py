import sys
import os
sys.path.append(os.getcwd())
from IsonTunnel.streamer import app_streamer

if __name__ == '__main__':
    app_streamer.run()
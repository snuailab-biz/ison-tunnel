import sys
import os
sys.path.append(os.getcwd())
from IsonTunnel.detector import app_detect

if __name__ == '__main__':
    app_detect.run()

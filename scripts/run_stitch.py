import sys
import os
sys.path.append(os.getcwd())
from IsonTunnel.stitch import app_stitch

if __name__ == '__main__':
    app_stitch.run()
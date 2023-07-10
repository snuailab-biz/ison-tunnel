import sys
import os
sys.path.append(os.getcwd())
from IsonTunnel.eventer import app_event

if __name__ == '__main__':
    app_event.run()
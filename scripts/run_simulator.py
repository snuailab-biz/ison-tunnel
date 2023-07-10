import sys
import os
sys.path.append(os.getcwd())
from IsonTunnel.simulator import app_simulator

if __name__ == '__main__':
    app_simulator.run()
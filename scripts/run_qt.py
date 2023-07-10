import sys
import os
sys.path.append(os.getcwd())
from IsonTunnel.configfix import app_configfix

if __name__ == '__main__':
    app_configfix.run()

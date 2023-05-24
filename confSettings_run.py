
import sys
from PyQt5.QtWidgets import QApplication
from IsonTunnel import IsonWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = IsonWindow()
    window.show()
    sys.exit(app.exec_())

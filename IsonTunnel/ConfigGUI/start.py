import sys
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from IsonTunnel.ConfigGUI.module import TabInit, TabDetector, TabEvent, TabRtsp, TabSimulator, TabCalibration, TabStit
from PyQt5.QtWidgets import QApplication

class IsonWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('ISON Settings Application')
        self.setMinimumSize(2500, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.tabs = QTabWidget(self)
        self.tab_init = TabInit()
        self.tab_detector = TabDetector()
        self.tab_event = TabEvent()
        self.tab_rtsp = TabRtsp()
        self.tab_simulator = TabSimulator()
        self.tab_calibration = TabCalibration()
        self.tab_stitch = TabStit()
        self.tabs.addTab(self.tab_init, "Initialize for Settings")
        self.tabs.addTab(self.tab_detector, "Detector Config Settings")
        self.tabs.addTab(self.tab_event, "Event Config Settings")
        self.tabs.addTab(self.tab_rtsp, "RTSP Config Settings")
        self.tabs.addTab(self.tab_simulator, "Simulator Config Settings")
        self.tabs.addTab(self.tab_calibration, "Calibration Config Settings")
        self.tabs.addTab(self.tab_stitch, "Stitch Run")

        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)
        central_widget.setLayout(vbox)




def run_window():
    app = QApplication(sys.argv)
    window = IsonWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_window()

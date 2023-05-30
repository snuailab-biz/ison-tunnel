from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class TabSimulator(QWidget):
    def __init__(self):
        super().__init__()

        self.label = QLabel("This is Tab simulator")
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
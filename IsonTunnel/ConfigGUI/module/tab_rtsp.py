from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy, QTabWidget, QFileDialog
from PyQt5.QtCore import Qt
import yaml
from IsonTunnel.ConfigGUI.config import RTSP_CFG

class TabRtsp(QWidget):
    def __init__(self):
        super().__init__()

        # Create labels and text boxes for each key-value pair in the YAML data
        self.label_list = []
        self.textbox_list = []
        for key, value in RTSP_CFG:
            label = QLabel(key)
            label.setFixedWidth(30)
            textbox = QLineEdit(str(value))
            self.label_list.append(label)
            self.textbox_list.append(textbox)

        # Create save button
        self.save_message = QLabel('')
        self.save_message.setAlignment(Qt.AlignCenter)

        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_data)

        # Set layout
        vbox = QVBoxLayout()
        for label, textbox in zip(self.label_list, self.textbox_list):
            hbox = QHBoxLayout()
            hbox.addWidget(label)
            hbox.addWidget(textbox)
            vbox.addLayout(hbox)

        self.yaml_layout = QVBoxLayout()
        vbox.addLayout(self.yaml_layout)
        vbox.addWidget(self.save_message)
        vbox.addWidget(save_button)
        self.setLayout(vbox)

    def save_data(self):
        # Update YAML data with the text box values
        for label, textbox in zip(self.label_list, self.textbox_list):
            self.data[label.text()] = textbox.text()

        with open('./services/service_rtsp/configure/configure.yaml', 'w') as f:
            yaml.dump(self.data, f)

        # Inform the user that the data has been saved
        self.save_message.setText('Data saved to file')
        # self.setLayout(vbox)
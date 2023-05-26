from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QGridLayout, QMessageBox
from PyQt5.QtCore import Qt, QSize
from IsonTunnel.configfix import DETECT_CFG
from IsonTunnel.configfix.utils.configSaver import save_config, check_variable_type

class TabDetector(QWidget):
    def __init__(self):
        super().__init__()

        # Create labels and text boxes for each key-value pair in the YAML data
        self.label_list = []
        self.textbox_list = []

        for key, value in DETECT_CFG:
            label = QLabel(key)
            textbox = QLineEdit(str(value))
            self.label_list.append(label)
            self.textbox_list.append(textbox)

        # Create save button
        self.save_message = QLabel('')
        self.save_message.setAlignment(Qt.AlignCenter)

        save_button = QPushButton('Save')
        save_button.setMinimumSize(QSize(200, 200))
        save_button.clicked.connect(self.save_data)

        # # Set layout
        # vbox = QVBoxLayout()
        # for label, textbox in zip(self.label_list, self.textbox_list):
        #     hbox = QHBoxLayout()
        #     hbox.addWidget(label)
        #     hbox.addWidget(textbox)
        #     vbox.addLayout(hbox)
        vbox = QVBoxLayout()
        layout_confing = QGridLayout()
        for idx, (label, textbox) in enumerate(zip(self.label_list, self.textbox_list)):
            # MUST!! The first element of label Must be a 'camera_url'
            if label.text()== 'camera_url':
                layout_confing.addWidget(label, idx, 0, 4, -1)
                layout_confing.addLayout(self.get_cameraUrl_edits(textbox), idx, 1,  4, -1)
            else:
                layout_confing.addWidget(label, idx+3, 0)
                layout_confing.addWidget(textbox, idx+3, 1)

        self.yaml_layout = QVBoxLayout()
        vbox.addLayout(layout_confing)
        vbox.addLayout(self.yaml_layout)
        vbox.addWidget(self.save_message)
        vbox.addWidget(save_button)
        self.setLayout(vbox)

    def get_cameraUrl_edits(self, text):
        layout_edit_cameraUrl = QGridLayout()
        self.line_cameraUrl = []
        for t in eval(text.text()):
            line = QLineEdit(text=t)
            layout_edit_cameraUrl.addWidget(line)
            self.line_cameraUrl.append(line)
        return layout_edit_cameraUrl

    def save_data(self):
        data = {}
        
        # Get Key, Value from GUI
        for label, textbox in zip(self.label_list, self.textbox_list):
            if label.text() == 'camera_url':
                continue
            data[label.text()] = textbox.text()
        
        # get camera_url texts
        data['camera_url'] = []
        for textbox in self.line_cameraUrl:
            data['camera_url'].append(textbox.text())
        
        save_config(data, mode='detect')
        
        # Inform the user that the data has been saved
        QMessageBox.information(self, 'info', '저장되었습니다.')
            

            

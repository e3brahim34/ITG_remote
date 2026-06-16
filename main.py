"""Main entry point - Choose between controller or controlled device"""
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from utils.logger import Logger

logger = Logger(__name__)

class DeviceTypeDialog(QDialog):
    """Dialog to choose device type"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        """Initialize UI"""
        self.setWindowTitle("ITG Remote - Device Type")
        self.setGeometry(100, 100, 400, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                margin: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("اختر نوع الجهاز\nChoose Device Type")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Controller button
        controller_btn = QPushButton("🖥️ متحكم (Controller)\n- التحكم بجهاز آخر")
        controller_btn.clicked.connect(self.start_controller)
        layout.addWidget(controller_btn)
        
        # Controlled button
        controlled_btn = QPushButton("🔒 مُحكوم (Controlled)\n- السماح بالتحكم به")
        controlled_btn.clicked.connect(self.start_controlled)
        layout.addWidget(controlled_btn)
        
        self.setLayout(layout)
    
    def start_controller(self):
        """Start controller device"""
        logger.info("Starting as Controller Device")
        self.device_type = 'controller'
        self.accept()
    
    def start_controlled(self):
        """Start controlled device"""
        logger.info("Starting as Controlled Device")
        self.device_type = 'controlled'
        self.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Show device type dialog
    dialog = DeviceTypeDialog()
    
    if dialog.exec_() == QDialog.Accepted:
        if dialog.device_type == 'controller':
            from client.controller_device import ControllerDevice
            device = ControllerDevice()
            device.start()
        else:
            from client.controlled_device import ControlledDevice
            device = ControlledDevice()
            device.start()
    else:
        sys.exit(0)

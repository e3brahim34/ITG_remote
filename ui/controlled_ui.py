"""Controlled Device UI - Interface for device being controlled"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from ui.main_window import MainWindow
from ui.styles import DARK_THEME
from utils.logger import Logger
from utils.helpers import get_local_ip, get_machine_name

logger = Logger(__name__)

class ControlledUI(MainWindow):
    """UI for device being controlled"""
    
    # Signals
    accept_connection = pyqtSignal(str)  # device_id
    reject_connection = pyqtSignal(str)  # device_id
    
    def __init__(self):
        """Initialize controlled device UI"""
        super().__init__(title="ITG Remote - Controlled Device", width=800, height=600)
        self.init_ui()
        self.active_connections = {}
    
    def init_ui(self):
        """Initialize UI components"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Device info section
        info_frame = self.create_info_frame()
        main_layout.addWidget(info_frame)
        
        # Connections list
        main_layout.addWidget(QLabel("Active Connections:"))
        
        self.connections_list = QListWidget()
        self.connections_list.setStyleSheet("""
            QListWidget {
                background-color: #2e2e2e;
                border: 1px solid #404040;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #404040;
            }
        """)
        main_layout.addWidget(self.connections_list)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        stop_sharing_btn = QPushButton("Stop Sharing")
        stop_sharing_btn.setStyleSheet("background-color: #d32f2f;")
        stop_sharing_btn.clicked.connect(self.stop_sharing)
        buttons_layout.addWidget(stop_sharing_btn)
        
        main_layout.addLayout(buttons_layout)
        
        central.setLayout(main_layout)
    
    def create_info_frame(self) -> QFrame:
        """Create device info frame
        
        Returns:
            Info frame
        """
        frame = QFrame()
        frame.setStyleSheet("background-color: #2e2e2e; border: 1px solid #404040; padding: 15px;")
        layout = QVBoxLayout()
        
        # Device name
        name_label = QLabel(f"Device Name: {get_machine_name()}")
        name_label.setStyleSheet("font-size: 12px; margin: 5px;")
        layout.addWidget(name_label)
        
        # Device IP
        ip_label = QLabel(f"Device IP: {get_local_ip()}")
        ip_label.setStyleSheet("font-size: 12px; margin: 5px;")
        layout.addWidget(ip_label)
        
        # Status
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("font-size: 12px; margin: 5px; color: #4caf50;")
        layout.addWidget(self.status_label)
        
        frame.setLayout(layout)
        return frame
    
    def add_connection(self, device_id: str, device_name: str, device_ip: str):
        """Add connection to list
        
        Args:
            device_id: Device ID
            device_name: Device name
            device_ip: Device IP
        """
        item = QListWidgetItem(f"{device_name} ({device_ip})")
        item.setData(Qt.UserRole, device_id)
        self.connections_list.addItem(item)
        self.active_connections[device_id] = {
            'name': device_name,
            'ip': device_ip
        }
        logger.info(f"Connection added: {device_name}")
    
    def remove_connection(self, device_id: str):
        """Remove connection from list
        
        Args:
            device_id: Device ID
        """
        for i in range(self.connections_list.count()):
            item = self.connections_list.item(i)
            if item.data(Qt.UserRole) == device_id:
                self.connections_list.takeItem(i)
                break
        
        if device_id in self.active_connections:
            del self.active_connections[device_id]
        
        logger.info(f"Connection removed: {device_id}")
    
    def update_status(self, status: str, color: str = None):
        """Update device status
        
        Args:
            status: Status text
            color: Status color
        """
        color = color or "#4caf50"
        self.status_label.setText(f"Status: {status}")
        self.status_label.setStyleSheet(f"font-size: 12px; margin: 5px; color: {color};")
    
    def stop_sharing(self):
        """Stop screen sharing"""
        logger.info("Stopping screen sharing...")
        self.update_status("Stopped", "#ff9800")

"""Controller Device - Controls remote device"""
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
import sys
import time
from core.screen_capture import ScreenCapture
from core.input_controller import InputController
from core.encryption import EncryptionManager, SecureConnection
from core.connection import P2PConnection
from core.discovery import DeviceDiscovery
from ui.controller_ui import ControllerUI
from database.db_manager import DatabaseManager
from utils.logger import Logger
from utils.helpers import get_device_id, get_machine_name, get_local_ip
from utils.config import config

logger = Logger(__name__)

class ControllerDevice:
    """Device that controls remote device"""
    
    def __init__(self):
        """Initialize controller device"""
        self.device_id = get_device_id()
        self.device_name = get_machine_name()
        self.device_ip = get_local_ip()
        
        logger.info(f"Controller Device initialized: {self.device_name} ({self.device_ip})")
        
        # Initialize components
        self.input_controller = InputController()
        self.encryption = EncryptionManager(config.get('encryption_password'))
        self.secure_conn = SecureConnection(self.encryption)
        self.discovery = DeviceDiscovery(self.device_id, self.device_name)
        self.db_manager = DatabaseManager()
        
        # Current connection
        self.current_connection = None
        self.current_device_id = None
        self.current_connection_id = None
        
        # UI
        self.ui = None
    
    def start(self):
        """Start controller device"""
        logger.info("Starting controller device...")
        
        # Start device discovery
        self.discovery.on_device_found = self._on_device_found
        self.discovery.start_discovery()
        
        # Initialize UI
        app = QApplication(sys.argv)
        self.ui = ControllerUI()
        
        # Connect UI signals
        self.ui.connect_clicked.connect(self.connect_to_device)
        self.ui.disconnect_clicked.connect(self.disconnect_from_device)
        self.ui.mouse_clicked.connect(self.send_mouse_click)
        self.ui.key_pressed.connect(self.send_key_press)
        
        self.ui.show()
        
        # Auto-refresh devices
        refresh_timer = QTimer()
        refresh_timer.timeout.connect(self._refresh_devices)
        refresh_timer.start(5000)  # Refresh every 5 seconds
        
        sys.exit(app.exec_())
    
    def _on_device_found(self, device_info: dict):
        """Handle device found
        
        Args:
            device_info: Device information
        """
        device_id = device_info.get('device_id')
        device_name = device_info.get('device_name')
        device_ip = device_info.get('ip')
        
        logger.info(f"Device found: {device_name} at {device_ip}")
        
        if self.ui:
            self.ui.add_device(device_id, device_name, device_ip)
    
    def _refresh_devices(self):
        """Refresh discovered devices"""
        devices = self.discovery.get_discovered_devices()
        logger.debug(f"Discovered {len(devices)} devices")
    
    def connect_to_device(self, device_id: str):
        """Connect to remote device
        
        Args:
            device_id: Target device ID
        """
        devices = self.discovery.get_discovered_devices()
        
        if device_id not in devices:
            logger.error(f"Device not found: {device_id}")
            if self.ui:
                self.ui.show_message("Error", "Device not found")
            return
        
        device_info = devices[device_id]
        device_ip = device_info.get('ip')
        device_port = device_info.get('port', config.get('port', 25557))
        
        logger.info(f"Connecting to {device_info.get('device_name')} at {device_ip}:{device_port}")
        
        # Create P2P connection
        self.current_connection = P2PConnection(self.device_ip, 0, self.device_id)
        
        if self.current_connection.connect(device_ip, device_port):
            self.current_device_id = device_id
            self.current_connection_id = self.db_manager.log_connection(
                device_id,
                device_info.get('device_name'),
                device_ip
            )
            
            # Setup message handlers
            self.current_connection.on('screen_frame', self._on_screen_frame)
            
            logger.info("Connected successfully")
            if self.ui:
                self.ui.show_message("Success", f"Connected to {device_info.get('device_name')}")
        else:
            logger.error("Connection failed")
            if self.ui:
                self.ui.show_message("Error", "Failed to connect to device")
    
    def disconnect_from_device(self):
        """Disconnect from remote device"""
        if self.current_connection:
            self.current_connection.close()
            
            if self.current_connection_id:
                self.db_manager.end_connection(self.current_connection_id)
            
            self.current_connection = None
            self.current_device_id = None
            self.current_connection_id = None
            
            logger.info("Disconnected")
            if self.ui:
                self.ui.show_message("Info", "Disconnected from device")
    
    def _on_screen_frame(self, message: dict):
        """Handle screen frame received
        
        Args:
            message: Screen frame message
        """
        try:
            data = message.get('data', {})
            frame_data = bytes.fromhex(data)
            
            # Convert to pixmap
            pixmap = QPixmap()
            pixmap.loadFromData(frame_data, 'JPEG')
            
            if self.ui:
                self.ui.update_screen(pixmap)
        except Exception as e:
            logger.error(f"Failed to process screen frame: {str(e)}")
    
    def send_mouse_click(self, button: str):
        """Send mouse click to remote device
        
        Args:
            button: Mouse button
        """
        if not self.current_connection:
            logger.warning("Not connected")
            return
        
        self.current_connection.send_message('mouse_click', {'button': button})
        
        if self.current_connection_id:
            self.db_manager.log_activity(self.current_connection_id, 'sent_mouse_click', f"button={button}")
    
    def send_key_press(self, key: str):
        """Send key press to remote device
        
        Args:
            key: Key name
        """
        if not self.current_connection:
            logger.warning("Not connected")
            return
        
        self.current_connection.send_message('key_press', {'key': key})
        
        if self.current_connection_id:
            self.db_manager.log_activity(self.current_connection_id, 'sent_key_press', f"key={key}")


if __name__ == '__main__':
    device = ControllerDevice()
    device.start()

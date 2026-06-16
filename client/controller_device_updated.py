"""Updated Controller Device with Global Discovery"""
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
import sys
import time
from core.connection_updated import P2PConnection
from core.global_discovery import GlobalDiscovery
from ui.controller_ui import ControllerUI
from database.db_manager import DatabaseManager
from utils.logger import Logger
from utils.helpers import get_device_id, get_machine_name, get_local_ip
from utils.config import config

logger = Logger(__name__)

class ControllerDevice:
    """Device that controls remote device with global discovery"""
    
    def __init__(self):
        """Initialize controller device"""
        self.device_id = get_device_id()
        self.device_name = get_machine_name()
        self.device_ip = get_local_ip()
        
        logger.info(f"Controller Device: {self.device_name} ({self.device_ip})")
        
        # Initialize components
        self.global_discovery = GlobalDiscovery(self.device_id, self.device_name, 0)
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
        
        # Start global discovery
        self.global_discovery.on_device_found = self._on_device_found
        self.global_discovery.start()
        
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
        refresh_timer.start(3000)
        
        sys.exit(app.exec_())
    
    def _on_device_found(self, device_info: dict):
        """Handle device found"""
        device_id = device_info.get('device_id')
        device_name = device_info.get('device_name')
        device_ip = device_info.get('public_ip', 'Unknown')
        
        logger.info(f"Device found: {device_name} at {device_ip}")
        
        if self.ui:
            self.ui.add_device(device_id, device_name, device_ip)
    
    def _refresh_devices(self):
        """Refresh discovered devices"""
        devices = self.global_discovery.get_discovered_devices()
        logger.debug(f"Discovered {len(devices)} devices")
    
    def connect_to_device(self, device_id: str):
        """Connect to remote device"""
        devices = self.global_discovery.get_discovered_devices()
        
        if device_id not in devices:
            logger.error(f"Device not found: {device_id}")
            if self.ui:
                self.ui.show_message("خطأ", "الجهاز غير متاح")
            return
        
        device_info = devices[device_id]
        device_ip = device_info.get('public_ip')
        device_port = device_info.get('port', config.get('port', 25557))
        
        if not device_ip:
            logger.error("No public IP available")
            if self.ui:
                self.ui.show_message("خطأ", "عنوان IP غير متاح")
            return
        
        logger.info(f"Connecting to {device_info.get('device_name')} at {device_ip}:{device_port}")
        
        # Create P2P connection with NAT traversal
        self.current_connection = P2PConnection(self.device_ip, 0, self.device_id)
        
        if self.current_connection.connect(device_ip, device_port, use_nat_traversal=True):
            self.current_device_id = device_id
            self.current_connection_id = self.db_manager.log_connection(
                device_id,
                device_info.get('device_name'),
                device_ip
            )
            
            # Setup handlers
            self.current_connection.on('screen_frame', self._on_screen_frame)
            
            logger.info("Connected successfully")
            if self.ui:
                self.ui.show_message("نجح", f"متصل بـ {device_info.get('device_name')}")
        else:
            logger.error("Connection failed")
            if self.ui:
                self.ui.show_message("خطأ", "فشل الاتصال")
    
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
                self.ui.show_message("معلومة", "تم قطع الاتصال")
    
    def _on_screen_frame(self, message: dict):
        """Handle screen frame received"""
        try:
            data = message.get('data', {})
            if isinstance(data, dict):
                frame_data = bytes.fromhex(data.get('data', ''))
            else:
                frame_data = bytes.fromhex(data)
            
            pixmap = QPixmap()
            pixmap.loadFromData(frame_data, 'JPEG')
            
            if self.ui:
                self.ui.update_screen(pixmap)
        except Exception as e:
            logger.error(f"Frame processing error: {str(e)}")
    
    def send_mouse_click(self, button: str):
        """Send mouse click"""
        if not self.current_connection:
            logger.warning("Not connected")
            return
        
        self.current_connection.send_message('mouse_click', {'button': button})
        
        if self.current_connection_id:
            self.db_manager.log_activity(self.current_connection_id, 'sent_mouse_click', f"button={button}")
    
    def send_key_press(self, key: str):
        """Send key press"""
        if not self.current_connection:
            logger.warning("Not connected")
            return
        
        self.current_connection.send_message('key_press', {'key': key})
        
        if self.current_connection_id:
            self.db_manager.log_activity(self.current_connection_id, 'sent_key_press', f"key={key}")


if __name__ == '__main__':
    device = ControllerDevice()
    device.start()

"""Controlled Device - Serves screen and accepts input"""
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import sys
import time
from core.screen_capture import ScreenCapture
from core.input_controller import InputController
from core.encryption import EncryptionManager, SecureConnection
from core.connection import P2PConnection
from core.discovery import DeviceDiscovery
from ui.controlled_ui import ControlledUI
from database.db_manager import DatabaseManager
from utils.logger import Logger
from utils.helpers import get_device_id, get_machine_name, get_local_ip
from utils.config import config

logger = Logger(__name__)

class ControlledDevice:
    """Device that accepts remote control"""
    
    def __init__(self):
        """Initialize controlled device"""
        self.device_id = get_device_id()
        self.device_name = get_machine_name()
        self.device_ip = get_local_ip()
        
        logger.info(f"Controlled Device initialized: {self.device_name} ({self.device_ip})")
        
        # --- تعديل: تقليل الجودة وزيادة الفاصل الزمني لضمان استقرار الشبكة المحلية ---
        self.screen_capture = ScreenCapture(
            quality=40,          # تقليل الجودة من 85 إلى 40 (سيقلل حجم البيانات بنسبة 70%)
            interval=0.3         # إرسال صورة كل 0.3 ثانية بدلاً من 0.1 لتخفيف الضغط
        )
        # ----------------------------------------------------------------------

        self.input_controller = InputController()
        #self.encryption = EncryptionManager(config.get('encryption_password'))
        #self.secure_conn = SecureConnection(self.encryption)
        self.discovery = DeviceDiscovery(self.device_id, self.device_name)
        self.db_manager = DatabaseManager()
        
        self.p2p_server = None
        self.active_connections = {}
        self.ui = None

    def _send_screen_frame(self, connection: P2PConnection, frame: bytes):
        """إرسال فريم الشاشة للمتحكم"""
        try:
            # نتحقق فقط من أن المتغير connection ليس None
            if connection:
                hex_data = frame.hex()
                # نرسل البيانات مباشرة
                connection.send_message('screen_frame', {'data': hex_data})
        except Exception as e:
            # إذا استمر ظهور خطأ 10054 هنا، فالمشكلة في حجم البيانات
            logger.error(f"Failed to send screen frame: {str(e)}")
    def start(self):
        """Start controlled device"""
        logger.info("Starting controlled device...")
        
        # Start discovery broadcast
        self.discovery.start_broadcast(port=config.get('port', 25557))
        
        # Start P2P server
        self._start_p2p_server()
        
        # Initialize UI
        app = QApplication(sys.argv)
        self.ui = ControlledUI()
        self.ui.show()
        
        sys.exit(app.exec_())
    
    def _start_p2p_server(self):
        """Start P2P server"""
        port = config.get('port', 25557)
        self.p2p_server = P2PConnection(self.device_ip, port, self.device_id)
        
        if self.p2p_server.create_server():
            logger.info(f"P2P server started on port {port}")
            
            # Start accepting connections in separate thread
            from threading import Thread
            Thread(target=self._accept_connections, daemon=True).start()
        else:
            logger.error("Failed to start P2P server")
    
    def _accept_connections(self):
        """Accept incoming P2P connections"""
        while True:
            try:
                client_conn = self.p2p_server.accept_connection()
                if client_conn:
                    logger.info(f"New connection from {client_conn.host}:{client_conn.port}")
                    self._setup_client_connection(client_conn)
            except Exception as e:
                logger.error(f"Accept connection error: {str(e)}")
                time.sleep(1)
    
    def _setup_client_connection(self, connection: P2PConnection):
        """Setup client connection handlers
        
        Args:
            connection: P2P connection
        """
        device_ip = connection.host
        connection_id = self.db_manager.log_connection(self.device_id, self.device_name, device_ip)
        
        # Store connection
        self.active_connections[connection.device_id] = {
            'connection': connection,
            'connection_id': connection_id
        }
        
        # Update UI
        if self.ui:
            self.ui.add_connection(self.device_id, self.device_name, device_ip)
        
        # Register message handlers
        connection.on('get_screen', lambda msg: self._handle_get_screen(connection))
        connection.on('mouse_move', lambda msg: self._handle_mouse_move(msg, connection_id))
        connection.on('mouse_click', lambda msg: self._handle_mouse_click(msg, connection_id))
        connection.on('key_press', lambda msg: self._handle_key_press(msg, connection_id))
        
        # Start screen streaming
        self.screen_capture.start(on_frame=lambda frame: self._send_screen_frame(connection, frame))
    
    def _handle_get_screen(self, connection: P2PConnection):
        """Handle screen request
        
        Args:
            connection: P2P connection
        """
        frame = self.screen_capture.capture_single()
        if frame:
            connection.send_message('screen_frame', {'data': frame.hex()})
    
    def _handle_mouse_move(self, message: dict, connection_id: int):
        """Handle mouse move
        
        Args:
            message: Message data
            connection_id: Connection ID
        """
        data = message.get('data', {})
        x = data.get('x')
        y = data.get('y')
        
        if x is not None and y is not None:
            self.input_controller.move_mouse(x, y)
            self.db_manager.log_activity(connection_id, 'mouse_move', f"x={x}, y={y}")
    
    def _handle_mouse_click(self, message: dict, connection_id: int):
        """Handle mouse click
        
        Args:
            message: Message data
            connection_id: Connection ID
        """
        data = message.get('data', {})
        button = data.get('button', 'left')
        
        self.input_controller.click(button)
        self.db_manager.log_activity(connection_id, 'mouse_click', f"button={button}")
    
    def _handle_key_press(self, message: dict, connection_id: int):
        """Handle key press
        
        Args:
            message: Message data
            connection_id: Connection ID
        """
        data = message.get('data', {})
        key = data.get('key')
        
        if key:
            self.input_controller.press_key(key)
            self.db_manager.log_activity(connection_id, 'key_press', f"key={key}")
    
    

if __name__ == '__main__':
    device = ControlledDevice()
    device.start()

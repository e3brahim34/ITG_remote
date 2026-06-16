"""Updated Controlled Device with Global Discovery"""
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import sys
import time
from core.screen_capture import ScreenCapture
from core.input_controller import InputController
from core.connection_updated import P2PConnection
from core.global_discovery import GlobalDiscovery
from ui.controlled_ui import ControlledUI
from database.db_manager import DatabaseManager
from utils.logger import Logger
from utils.helpers import get_device_id, get_machine_name, get_local_ip
from utils.config import config

logger = Logger(__name__)

class ControlledDevice:
    """Device that accepts remote control with global discovery"""
    
    def __init__(self):
        """Initialize controlled device"""
        self.device_id = get_device_id()
        self.device_name = get_machine_name()
        self.device_ip = get_local_ip()
        self.listen_port = config.get('port', 25557)
        
        logger.info(f"Controlled Device: {self.device_name} ({self.device_ip})")
        
        # Initialize components
        self.screen_capture = ScreenCapture(
            quality=config.get('screen_quality', 40),
            interval=config.get('capture_interval', 0.3)
        )
        self.input_controller = InputController()
        self.global_discovery = GlobalDiscovery(self.device_id, self.device_name, self.listen_port)
        self.db_manager = DatabaseManager()
        
        # P2P connections
        self.p2p_server = None
        self.active_connections = {}
        
        # UI
        self.ui = None
    
    def start(self):
        """Start controlled device"""
        logger.info("Starting controlled device...")
        
        # Start P2P server
        self._start_p2p_server()
        
        # Start global discovery
        self.global_discovery.start()
        
        # Initialize UI
        app = QApplication(sys.argv)
        self.ui = ControlledUI()
        self.ui.show()
        
        # Status update timer
        status_timer = QTimer()
        status_timer.timeout.connect(self._update_status)
        status_timer.start(5000)
        
        sys.exit(app.exec_())
    
    def _start_p2p_server(self):
        """Start P2P server"""
        self.p2p_server = P2PConnection(self.device_ip, self.listen_port, self.device_id)
        
        if self.p2p_server.create_server():
            logger.info(f"P2P server started on port {self.listen_port}")
            
            # Start accepting connections
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
                logger.error(f"Accept error: {str(e)}")
                time.sleep(1)
    
    def _setup_client_connection(self, connection: P2PConnection):
        """Setup client connection handlers"""
        device_ip = connection.host
        connection_id = self.db_manager.log_connection(self.device_id, self.device_name, device_ip)
        
        self.active_connections[connection.device_id] = {
            'connection': connection,
            'connection_id': connection_id
        }
        
        if self.ui:
            self.ui.add_connection(connection.device_id, 'Controller', device_ip)
        
        # Register handlers
        connection.on('get_screen', lambda msg: self._handle_get_screen(connection))
        connection.on('mouse_move', lambda msg: self._handle_mouse_move(msg, connection_id))
        connection.on('mouse_click', lambda msg: self._handle_mouse_click(msg, connection_id))
        connection.on('key_press', lambda msg: self._handle_key_press(msg, connection_id))
        
        # Start screen streaming
        self.screen_capture.start(on_frame=lambda frame: self._send_screen_frame(connection, frame))
    
    def _handle_get_screen(self, connection: P2PConnection):
        """Handle screen request"""
        frame = self.screen_capture.capture_single()
        if frame:
            connection.send_message('screen_frame', {'data': frame.hex()})
    
    def _handle_mouse_move(self, message: dict, connection_id: int):
        """Handle mouse move"""
        data = message.get('data', {})
        x = data.get('x')
        y = data.get('y')
        
        if x is not None and y is not None:
            self.input_controller.move_mouse(x, y)
            self.db_manager.log_activity(connection_id, 'mouse_move', f"x={x}, y={y}")
    
    def _handle_mouse_click(self, message: dict, connection_id: int):
        """Handle mouse click"""
        data = message.get('data', {})
        button = data.get('button', 'left')
        self.input_controller.click(button)
        self.db_manager.log_activity(connection_id, 'mouse_click', f"button={button}")
    
    def _handle_key_press(self, message: dict, connection_id: int):
        """Handle key press"""
        data = message.get('data', {})
        key = data.get('key')
        if key:
            self.input_controller.press_key(key)
            self.db_manager.log_activity(connection_id, 'key_press', f"key={key}")
    
    def _send_screen_frame(self, connection: P2PConnection, frame: bytes):
        """Send screen frame"""
        try:
            if connection and connection.connected:
                connection.send_message('screen_frame', {'data': frame.hex()})
        except Exception as e:
            logger.error(f"Send frame error: {str(e)}")
    
    def _update_status(self):
        """Update UI status"""
        if self.ui:
            status = f"متصل (Connected)" if self.global_discovery.connected else "غير متصل (Disconnected)"
            color = "#4caf50" if self.global_discovery.connected else "#f44336"
            self.ui.update_status(status, color)


if __name__ == '__main__':
    device = ControlledDevice()
    device.start()

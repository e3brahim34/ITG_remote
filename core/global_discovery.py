"""Updated Device Discovery with Global Signaling Server"""
import socketio
import threading
from typing import Callable, Dict, Optional
from utils.logger import Logger
from utils.signaling_config import SIGNALING_SERVER_URL, BACKUP_SERVERS, DISCOVERY_INTERVAL
import time

logger = Logger(__name__)

class GlobalDiscovery:
    """Global device discovery using signaling server"""
    
    def __init__(self, device_id: str, device_name: str, port: int):
        """Initialize global discovery
        
        Args:
            device_id: Unique device identifier
            device_name: Display name of device
            port: P2P listening port
        """
        self.device_id = device_id
        self.device_name = device_name
        self.port = port
        self.sio = socketio.Client()
        self.discovered_devices: Dict[str, dict] = {}
        self.on_device_found: Optional[Callable] = None
        self.on_device_lost: Optional[Callable] = None
        self.connected = False
        self.server_url = SIGNALING_SERVER_URL
    
    def start(self):
        """Start global discovery"""
        logger.info("Starting global discovery...")
        
        # Register socket.io events
        @self.sio.on('connect')
        def on_connect():
            logger.info(f"Connected to signaling server: {self.server_url}")
            self.connected = True
            self._register_device()
        
        @self.sio.on('disconnect')
        def on_disconnect():
            logger.warning("Disconnected from signaling server")
            self.connected = False
        
        @self.sio.on('device_list')
        def on_device_list(data):
            self._handle_device_list(data)
        
        @self.sio.on('device_registered')
        def on_device_registered(data):
            device_info = data.get('device')
            if device_info and device_info.get('device_id') != self.device_id:
                self._on_new_device(device_info)
        
        @self.sio.on('device_unregistered')
        def on_device_unregistered(data):
            device_id = data.get('device_id')
            if device_id in self.discovered_devices:
                del self.discovered_devices[device_id]
                if self.on_device_lost:
                    self.on_device_lost(device_id)
                logger.info(f"Device unregistered: {device_id}")
        
        # Connect to server
        self._connect_to_server()
        
        # Start refresh thread
        refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        refresh_thread.start()
    
    def _connect_to_server(self):
        """Connect to signaling server"""
        try:
            self.sio.connect(
                self.server_url,
                transports=['websocket'],
                wait_timeout=10
            )
        except Exception as e:
            logger.error(f"Failed to connect to server: {str(e)}")
            # Try backup servers
            self._try_backup_servers()
    
    def _try_backup_servers(self):
        """Try connecting to backup servers"""
        for backup_url in BACKUP_SERVERS:
            if backup_url == self.server_url:
                continue
            try:
                logger.info(f"Trying backup server: {backup_url}")
                self.server_url = backup_url
                self.sio.connect(
                    backup_url,
                    transports=['websocket'],
                    wait_timeout=10
                )
                logger.info(f"Connected to backup server: {backup_url}")
                return
            except Exception as e:
                logger.warning(f"Backup server failed: {str(e)}")
    
    def _register_device(self):
        """Register device with signaling server"""
        try:
            device_info = {
                'device_id': self.device_id,
                'device_name': self.device_name,
                'port': self.port,
                'timestamp': time.time()
            }
            self.sio.emit('register_device', device_info)
            logger.info(f"Device registered: {self.device_name}")
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
    
    def _refresh_loop(self):
        """Refresh device list periodically"""
        while True:
            try:
                time.sleep(DISCOVERY_INTERVAL)
                if self.connected:
                    self.sio.emit('get_devices')
            except Exception as e:
                logger.error(f"Refresh error: {str(e)}")
    
    def _handle_device_list(self, data):
        """Handle device list from server
        
        Args:
            data: Device list data
        """
        devices = data.get('devices', [])
        for device_info in devices:
            if device_info.get('device_id') != self.device_id:
                if device_info.get('device_id') not in self.discovered_devices:
                    self._on_new_device(device_info)
    
    def _on_new_device(self, device_info: dict):
        """Handle newly discovered device
        
        Args:
            device_info: Device information
        """
        device_id = device_info.get('device_id')
        self.discovered_devices[device_id] = device_info
        logger.info(f"Device found: {device_info.get('device_name')}")
        
        if self.on_device_found:
            self.on_device_found(device_info)
    
    def get_discovered_devices(self) -> Dict[str, dict]:
        """Get discovered devices
        
        Returns:
            Dictionary of discovered devices
        """
        return self.discovered_devices.copy()
    
    def stop(self):
        """Stop discovery"""
        try:
            if self.connected:
                self.sio.emit('unregister_device', {'device_id': self.device_id})
            self.sio.disconnect()
            logger.info("Discovery stopped")
        except Exception as e:
            logger.error(f"Stop error: {str(e)}")

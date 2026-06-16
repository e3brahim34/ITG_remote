"""Updated P2P Connection with NAT Traversal Support"""
import socket
import threading
import json
import time
from typing import Callable, Optional, Dict, Any
from utils.logger import Logger
from core.nat_traversal import NATTraversal

logger = Logger(__name__)

class P2PConnection:
    """P2P connection with NAT traversal support"""
    
    def __init__(self, host: str, port: int, device_id: str):
        """Initialize P2P connection
        
        Args:
            host: Host IP address
            port: Port number
            device_id: Unique device identifier
        """
        self.host = host
        self.port = port
        self.device_id = device_id
        self.socket = None
        self.connected = False
        self.listeners: Dict[str, Callable] = {}
        self.receive_thread = None
        self.is_server = False
        self.nat_traversal = NATTraversal()
    
    def create_server(self) -> bool:
        """Create server socket for incoming connections
        
        Returns:
            True if successful
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.is_server = True
            logger.info(f"P2P Server created on {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to create server: {str(e)}")
            return False
    
    def connect(self, target_host: str, target_port: int, use_nat_traversal: bool = True) -> bool:
        """Connect to remote P2P peer with NAT traversal
        
        Args:
            target_host: Target host IP
            target_port: Target port
            use_nat_traversal: Enable NAT traversal
            
        Returns:
            True if successful
        """
        try:
            if use_nat_traversal:
                # Perform hole punching
                self.nat_traversal.hole_punch((target_host, target_port), self.port)
                time.sleep(0.5)  # Wait for hole punch
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((target_host, target_port))
            self.connected = True
            logger.info(f"Connected to {target_host}:{target_port}")
            
            # Start receiving messages
            self._start_receive_thread()
            return True
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            return False
    
    def accept_connection(self) -> Optional['P2PConnection']:
        """Accept incoming connection
        
        Returns:
            New P2PConnection instance for client
        """
        try:
            client_socket, client_address = self.socket.accept()
            logger.info(f"Connection accepted from {client_address}")
            
            # Create new connection object
            client_conn = P2PConnection(client_address[0], client_address[1], self.device_id)
            client_conn.socket = client_socket
            client_conn.connected = True
            client_conn._start_receive_thread()
            
            return client_conn
        except Exception as e:
            logger.error(f"Accept connection failed: {str(e)}")
            return None
    
    def send_data(self, data: bytes) -> bool:
        """Send data through socket
        
        Args:
            data: Data to send
            
        Returns:
            True if successful
        """
        try:
            if self.socket and self.connected:
                # Send data length first (4 bytes, big-endian)
                data_length = len(data)
                self.socket.sendall(data_length.to_bytes(4, 'big'))
                # Send data
                self.socket.sendall(data)
                return True
            return False
        except Exception as e:
            logger.error(f"Send failed: {str(e)}")
            self.connected = False
            return False
    
    def send_message(self, message_type: str, data: Any = None) -> bool:
        """Send JSON message
        
        Args:
            message_type: Type of message
            data: Message data
            
        Returns:
            True if successful
        """
        message = {
            'type': message_type,
            'device_id': self.device_id,
            'data': data,
            'timestamp': time.time()
        }
        json_data = json.dumps(message).encode()
        return self.send_data(json_data)
    
    def _start_receive_thread(self):
        """Start thread to receive messages"""
        if self.receive_thread is None or not self.receive_thread.is_alive():
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
    
    def _receive_loop(self):
        """Main receive loop"""
        while self.connected:
            try:
                # Receive data length
                length_bytes = self._receive_exact(4)
                if not length_bytes:
                    break
                
                data_length = int.from_bytes(length_bytes, 'big')
                
                # Validate data length
                if data_length > 10 * 1024 * 1024:  # 10MB limit
                    logger.error(f"Data length too large: {data_length}")
                    break
                
                # Receive data
                data = self._receive_exact(data_length)
                if not data:
                    break
                
                # Parse message
                try:
                    message = json.loads(data.decode())
                    self._trigger_listener(message.get('type'), message)
                except json.JSONDecodeError:
                    logger.error("Failed to decode message")
            except Exception as e:
                logger.error(f"Receive error: {str(e)}")
                self.connected = False
                break
    
    def _receive_exact(self, num_bytes: int) -> Optional[bytes]:
        """Receive exact number of bytes
        
        Args:
            num_bytes: Number of bytes to receive
            
        Returns:
            Received bytes or None
        """
        data = b''
        while len(data) < num_bytes:
            try:
                chunk = self.socket.recv(num_bytes - len(data))
                if not chunk:
                    return None
                data += chunk
            except socket.timeout:
                continue
        return data
    
    def on(self, message_type: str, callback: Callable):
        """Register message listener
        
        Args:
            message_type: Type of message to listen for
            callback: Callback function
        """
        self.listeners[message_type] = callback
    
    def _trigger_listener(self, message_type: str, message: dict):
        """Trigger registered listener
        
        Args:
            message_type: Type of message
            message: Message data
        """
        if message_type in self.listeners:
            try:
                self.listeners[message_type](message)
            except Exception as e:
                logger.error(f"Listener error: {str(e)}")
    
    def close(self):
        """Close connection"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        logger.info("P2P Connection closed")

"""Discovery Server - Helps devices find each other"""
import socket
import json
import threading
import time
from typing import Dict, Optional
from utils.logger import Logger
from server.config import *

logger = Logger(__name__)

class DiscoveryServer:
    """Server that helps devices discover each other on LAN"""
    
    def __init__(self):
        """Initialize discovery server"""
        self.devices: Dict[str, dict] = {}
        self.lock = threading.Lock()
        self.running = False
        self.server_socket = None
        self.server_thread = None
    
    def start(self, host=SERVER_HOST, port=SERVER_PORT):
        """Start discovery server
        
        Args:
            host: Server host
            port: Server port
        """
        if self.running:
            return
        
        self.running = True
        self.server_thread = threading.Thread(
            target=self._server_loop,
            args=(host, port),
            daemon=False
        )
        self.server_thread.start()
        logger.info(f"Discovery server started on {host}:{port}")
    
    def stop(self):
        """Stop discovery server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        if self.server_thread:
            self.server_thread.join(timeout=5)
        logger.info("Discovery server stopped")
    
    def _server_loop(self, host: str, port: int):
        """Main server loop"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(MAX_CONNECTIONS)
            self.server_socket.settimeout(1.0)
            
            # Start device cleanup thread
            cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            cleanup_thread.start()
            
            logger.info(f"Server listening on {host}:{port}")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    logger.info(f"Connection from {client_address}")
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"Accept error: {str(e)}")
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
        finally:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass
    
    def _handle_client(self, client_socket: socket.socket, client_address: tuple):
        """Handle client connection
        
        Args:
            client_socket: Client socket
            client_address: Client address
        """
        try:
            client_socket.settimeout(REQUEST_TIMEOUT)
            
            # Receive device info
            data = client_socket.recv(4096)
            if not data:
                return
            
            message = json.loads(data.decode())
            action = message.get('action')
            
            if action == 'register':
                self._handle_register(message, client_address, client_socket)
            elif action == 'discover':
                self._handle_discover(client_socket)
            elif action == 'unregister':
                self._handle_unregister(message)
            else:
                logger.warning(f"Unknown action: {action}")
        except Exception as e:
            logger.error(f"Client error: {str(e)}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def _handle_register(self, message: dict, client_address: tuple, client_socket: socket.socket):
        """Handle device registration
        
        Args:
            message: Registration message
            client_address: Client address
            client_socket: Client socket
        """
        device_id = message.get('device_id')
        device_info = message.get('device_info', {})
        
        with self.lock:
            device_info['ip'] = client_address[0]
            device_info['last_seen'] = time.time()
            self.devices[device_id] = device_info
        
        logger.info(f"Device registered: {device_info.get('name')} ({device_id})")
        
        # Send confirmation
        response = {'status': 'ok', 'device_id': device_id}
        client_socket.send(json.dumps(response).encode())
    
    def _handle_discover(self, client_socket: socket.socket):
        """Handle device discovery request
        
        Args:
            client_socket: Client socket
        """
        with self.lock:
            device_list = list(self.devices.values())
        
        response = {'devices': device_list}
        client_socket.send(json.dumps(response).encode())
        logger.debug(f"Sent {len(device_list)} devices")
    
    def _handle_unregister(self, message: dict):
        """Handle device unregistration
        
        Args:
            message: Unregistration message
        """
        device_id = message.get('device_id')
        
        with self.lock:
            if device_id in self.devices:
                del self.devices[device_id]
        
        logger.info(f"Device unregistered: {device_id}")
    
    def _cleanup_loop(self):
        """Cleanup disconnected devices"""
        while self.running:
            try:
                time.sleep(30)  # Cleanup every 30 seconds
                
                current_time = time.time()
                with self.lock:
                    expired = [
                        device_id for device_id, info in self.devices.items()
                        if current_time - info.get('last_seen', 0) > 60
                    ]
                    
                    for device_id in expired:
                        del self.devices[device_id]
                        logger.info(f"Removed expired device: {device_id}")
            except Exception as e:
                logger.error(f"Cleanup error: {str(e)}")
    
    def get_devices(self) -> Dict[str, dict]:
        """Get all registered devices
        
        Returns:
            Dictionary of devices
        """
        with self.lock:
            return dict(self.devices)


if __name__ == '__main__':
    server = DiscoveryServer()
    
    try:
        server.start()
        logger.info("Discovery server is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping server...")
        server.stop()

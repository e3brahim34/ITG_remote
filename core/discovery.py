"""Device discovery module for LAN"""
import socket
import json
import threading
from typing import Dict, Callable, Optional
from utils.logger import Logger

logger = Logger(__name__)

class DeviceDiscovery:
    """Discovers devices on LAN using UDP broadcast"""
    
    BROADCAST_PORT = 25555
    DISCOVERY_PORT = 25556
    
    def __init__(self, device_id: str, device_name: str):
        """Initialize device discovery
        
        Args:
            device_id: Unique device identifier
            device_name: Display name of device
        """
        self.device_id = device_id
        self.device_name = device_name
        self.discovered_devices: Dict[str, dict] = {}
        self.broadcast_socket = None
        self.listen_socket = None
        self.broadcasting = False
        self.listening = False
        self.on_device_found: Optional[Callable] = None
        self.on_device_lost: Optional[Callable] = None
    
    def start_broadcast(self, port: int = None, interval: float = 2.0):
        """Start broadcasting device info
        
        Args:
            port: Port to listen on (optional)
            interval: Broadcast interval in seconds
        """
        if self.broadcasting:
            return
        
        self.broadcasting = True
        thread = threading.Thread(
            target=self._broadcast_loop,
            args=(port or self.BROADCAST_PORT, interval),
            daemon=True
        )
        thread.start()
        logger.info("Device broadcast started")
    
    def start_discovery(self):
        """Start listening for device broadcasts"""
        if self.listening:
            return
        
        self.listening = True
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()
        logger.info("Device discovery started")
    
    def stop_broadcast(self):
        """Stop broadcasting"""
        self.broadcasting = False
        if self.broadcast_socket:
            try:
                self.broadcast_socket.close()
            except:
                pass
    
    def stop_discovery(self):
        """Stop listening for broadcasts"""
        self.listening = False
        if self.listen_socket:
            try:
                self.listen_socket.close()
            except:
                pass
    
    def _broadcast_loop(self, port: int, interval: float):
        """Main broadcast loop"""
        import time
        
        try:
            self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            while self.broadcasting:
                try:
                    device_info = {
                        'device_id': self.device_id,
                        'device_name': self.device_name,
                        'port': port
                    }
                    message = json.dumps(device_info).encode()
                    self.broadcast_socket.sendto(message, ('<broadcast>', self.DISCOVERY_PORT))
                except Exception as e:
                    logger.error(f"Broadcast error: {str(e)}")
                
                time.sleep(interval)
        except Exception as e:
            logger.error(f"Broadcast setup error: {str(e)}")
        finally:
            if self.broadcast_socket:
                try:
                    self.broadcast_socket.close()
                except:
                    pass
    
    def _listen_loop(self):
        """Main discovery listen loop"""
        try:
            self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listen_socket.bind(('', self.DISCOVERY_PORT))
            self.listen_socket.settimeout(5.0)
            
            while self.listening:
                try:
                    data, addr = self.listen_socket.recvfrom(1024)
                    device_info = json.loads(data.decode())
                    
                    # Ignore own broadcasts
                    if device_info.get('device_id') == self.device_id:
                        continue
                    
                    device_id = device_info.get('device_id')
                    if device_id not in self.discovered_devices:
                        device_info['ip'] = addr[0]
                        self.discovered_devices[device_id] = device_info
                        logger.info(f"Device found: {device_info.get('device_name')} at {addr[0]}")
                        
                        if self.on_device_found:
                            self.on_device_found(device_info)
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"Listen error: {str(e)}")
        except Exception as e:
            logger.error(f"Listen setup error: {str(e)}")
        finally:
            if self.listen_socket:
                try:
                    self.listen_socket.close()
                except:
                    pass
    
    def get_discovered_devices(self) -> Dict[str, dict]:
        """Get list of discovered devices
        
        Returns:
            Dictionary of discovered devices
        """
        return self.discovered_devices.copy()

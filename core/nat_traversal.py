"""NAT Traversal and Hole Punching for P2P connections"""
import socket
import threading
from typing import Optional, Tuple
from utils.logger import Logger
from utils.signaling_config import STUN_SERVERS
import json

logger = Logger(__name__)

class NATTraversal:
    """Handles NAT traversal for P2P connections"""
    
    def __init__(self):
        """Initialize NAT traversal"""
        self.public_ip = None
        self.public_port = None
        self.local_ip = self._get_local_ip()
    
    @staticmethod
    def _get_local_ip() -> str:
        """Get local IP address
        
        Returns:
            Local IP address
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def get_external_address(self, local_port: int) -> Optional[Tuple[str, int]]:
        """Get external IP and port using STUN
        
        Args:
            local_port: Local port number
            
        Returns:
            Tuple of (public_ip, public_port) or None
        """
        for stun_server in STUN_SERVERS:
            try:
                server_ip, server_port = stun_server.split(':')
                server_port = int(server_port)
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b'\x00\x01\x00\x00' + b'\x00' * 12, (server_ip, server_port))
                sock.settimeout(2)
                
                data, _ = sock.recvfrom(1024)
                sock.close()
                
                # Parse STUN response to get external address
                if len(data) > 28:
                    # Simple parsing - in production use proper STUN library
                    # This is a simplified version
                    logger.info(f"STUN response received from {stun_server}")
                    return self._parse_stun_response(data)
            except Exception as e:
                logger.debug(f"STUN failed with {stun_server}: {str(e)}")
        
        logger.warning("STUN negotiation failed, using local IP")
        return (self.local_ip, local_port)
    
    def _parse_stun_response(self, data: bytes) -> Optional[Tuple[str, int]]:
        """Parse STUN response
        
        Args:
            data: STUN response data
            
        Returns:
            Tuple of (ip, port) or None
        """
        try:
            # This is a simplified parser
            # In production, use proper STUN library like stun-python
            if len(data) > 28:
                # Extract port (bytes 24-26)
                port = int.from_bytes(data[24:26], 'big')
                # Extract IP (bytes 28-32)
                ip = '.'.join(str(b) for b in data[28:32])
                logger.info(f"STUN detected: {ip}:{port}")
                self.public_ip = ip
                self.public_port = port
                return (ip, port)
        except Exception as e:
            logger.error(f"STUN parse error: {str(e)}")
        
        return None
    
    def hole_punch(self, target_address: Tuple[str, int], local_port: int) -> bool:
        """Perform hole punching to establish connection
        
        Args:
            target_address: Target (ip, port)
            local_port: Local port
            
        Returns:
            True if successful
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('', local_port))
            sock.sendto(b'PUNCH', target_address)
            sock.close()
            logger.info(f"Hole punch sent to {target_address}")
            return True
        except Exception as e:
            logger.error(f"Hole punch failed: {str(e)}")
            return False

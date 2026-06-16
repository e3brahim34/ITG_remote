"""Helper functions"""
import socket
import platform
import uuid
import os

def get_local_ip():
    """Get local machine IP address
    
    Returns:
        IP address string
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_machine_name():
    """Get machine name
    
    Returns:
        Machine hostname
    """
    return socket.gethostname()

def get_device_id():
    """Get unique device ID
    
    Returns:
        UUID string
    """
    # Try to get hardware-based ID
    try:
        mac = uuid.getnode()
        return f"{mac:x}"
    except:
        # Fallback to random UUID
        return str(uuid.uuid4())

def get_os_info():
    """Get operating system information
    
    Returns:
        Dictionary with OS info
    """
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine()
    }

def get_screen_resolution():
    """Get screen resolution
    
    Returns:
        Tuple of (width, height)
    """
    try:
        import mss
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            return (monitor['width'], monitor['height'])
    except:
        return (1920, 1080)

def format_bytes(bytes_size):
    """Format bytes to human readable format
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def get_free_port():
    """Get a free port
    
    Returns:
        Available port number
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

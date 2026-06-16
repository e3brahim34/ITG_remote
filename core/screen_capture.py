"""Screen capture module for streaming"""
import mss
import numpy as np
from PIL import Image
import io
import threading
from typing import Optional, Callable
from utils.logger import Logger

logger = Logger(__name__)

class ScreenCapture:
    """Captures and compresses screen images"""
    
    def __init__(self, quality: int = 85, interval: float = 0.1):
        """Initialize screen capture
        
        Args:
            quality: JPEG compression quality (0-100)
            interval: Capture interval in seconds
        """
        self.quality = quality
        self.interval = interval
        self.capturing = False
        self.capture_thread = None
        self.on_frame_callback: Optional[Callable] = None
        self.monitor = None
    
    def start(self, on_frame: Callable = None):
        """Start screen capture
        
        Args:
            on_frame: Callback function for each frame (receives JPEG bytes)
        """
        if self.capturing:
            return
        
        self.on_frame_callback = on_frame
        self.capturing = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        logger.info("Screen capture started")
    
    def stop(self):
        """Stop screen capture"""
        self.capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        logger.info("Screen capture stopped")
    
    def _capture_loop(self):
        """Main capture loop"""
        with mss.mss() as sct:
            # Get primary monitor
            monitor = sct.monitors[1]
            
            while self.capturing:
                try:
                    # Capture screen
                    screenshot = sct.grab(monitor)
                    
                    # Convert to PIL Image
                    image = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                    
                    # Compress and convert to JPEG
                    jpeg_data = self._compress_image(image)
                    
                    # Call callback
                    if self.on_frame_callback:
                        self.on_frame_callback(jpeg_data)
                    
                    # Sleep for interval
                    import time
                    time.sleep(self.interval)
                except Exception as e:
                    logger.error(f"Capture error: {str(e)}")
    
    def _compress_image(self, image: Image.Image) -> bytes:
        """Compress image to JPEG
        
        Args:
            image: PIL Image object
            
        Returns:
            JPEG bytes
        """
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=self.quality, optimize=True)
        return buffer.getvalue()
    
    def capture_single(self) -> Optional[bytes]:
        """Capture single screenshot
        
        Returns:
            JPEG bytes or None
        """
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                image = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                return self._compress_image(image)
        except Exception as e:
            logger.error(f"Single capture error: {str(e)}")
            return None
    
    def get_screen_info(self) -> dict:
        """Get screen information
        
        Returns:
            Dictionary with screen details
        """
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                return {
                    'width': monitor['width'],
                    'height': monitor['height'],
                    'left': monitor['left'],
                    'top': monitor['top']
                }
        except Exception as e:
            logger.error(f"Failed to get screen info: {str(e)}")
            return {}

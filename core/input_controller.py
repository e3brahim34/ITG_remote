"""Input control module for mouse and keyboard"""
import pynput
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key
from utils.logger import Logger

logger = Logger(__name__)

class InputController:
    """Controls mouse and keyboard input"""
    
    def __init__(self):
        """Initialize input controller"""
        self.mouse = MouseController()      # بدلاً من Mouse()
        self.keyboard = KeyboardController() # بدلاً من Keyboard()
    
    # ============= Mouse Control =============
    
    def move_mouse(self, x: int, y: int):
        """Move mouse to position
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        try:
            self.mouse.position = (x, y)
        except Exception as e:
            logger.error(f"Mouse move error: {str(e)}")
    
    def click(self, button: str = 'left', count: int = 1):
        """Click mouse button
        
        Args:
            button: Button name ('left', 'right', 'middle')
            count: Number of clicks
        """
        try:
            btn = self._get_button(button)
            self.mouse.click(btn, count)
        except Exception as e:
            logger.error(f"Mouse click error: {str(e)}")
    
    def drag(self, x1: int, y1: int, x2: int, y2: int, button: str = 'left'):
        """Drag mouse from one position to another
        
        Args:
            x1: Starting X coordinate
            y1: Starting Y coordinate
            x2: Ending X coordinate
            y2: Ending Y coordinate
            button: Button to use
        """
        try:
            btn = self._get_button(button)
            with self.mouse.pressed(btn):
                self.mouse.position = (x1, y1)
                self.mouse.position = (x2, y2)
        except Exception as e:
            logger.error(f"Mouse drag error: {str(e)}")
    
    def scroll(self, x: int, y: int, dx: int = 0, dy: int = 1):
        """Scroll at position
        
        Args:
            x: X coordinate
            y: Y coordinate
            dx: Horizontal scroll amount
            dy: Vertical scroll amount
        """
        try:
            self.mouse.position = (x, y)
            self.mouse.scroll(dx, dy)
        except Exception as e:
            logger.error(f"Mouse scroll error: {str(e)}")
    
    @staticmethod
    def _get_button(button: str) -> Button:
        """Get button object from string
        
        Args:
            button: Button name
            
        Returns:
            Button object
        """
        buttons = {
            'left': Button.left,
            'right': Button.right,
            'middle': Button.middle
        }
        return buttons.get(button.lower(), Button.left)
    
    # ============= Keyboard Control =============
    
    def press_key(self, key: str):
        """Press and release a key
        
        Args:
            key: Key name
        """
        try:
            k = self._get_key(key)
            self.keyboard.press(k)
            self.keyboard.release(k)
        except Exception as e:
            logger.error(f"Key press error: {str(e)}")
    
    def type_text(self, text: str):
        """Type text
        
        Args:
            text: Text to type
        """
        try:
            self.keyboard.type(text)
        except Exception as e:
            logger.error(f"Type error: {str(e)}")
    
    def key_down(self, key: str):
        """Press key (hold)
        
        Args:
            key: Key name
        """
        try:
            k = self._get_key(key)
            self.keyboard.press(k)
        except Exception as e:
            logger.error(f"Key down error: {str(e)}")
    
    def key_up(self, key: str):
        """Release key
        
        Args:
            key: Key name
        """
        try:
            k = self._get_key(key)
            self.keyboard.release(k)
        except Exception as e:
            logger.error(f"Key up error: {str(e)}")
    
    def hotkey(self, *keys):
        """Press multiple keys simultaneously
        
        Args:
            keys: Key names
        """
        try:
            key_objects = [self._get_key(k) for k in keys]
            for k in key_objects:
                self.keyboard.press(k)
            for k in reversed(key_objects):
                self.keyboard.release(k)
        except Exception as e:
            logger.error(f"Hotkey error: {str(e)}")
    
    @staticmethod
    def _get_key(key_name: str):
        """Get key object from string
        
        Args:
            key_name: Key name
            
        Returns:
            Key object
        """
        # Special keys
        special_keys = {
            'enter': Key.enter,
            'return': Key.enter,
            'tab': Key.tab,
            'space': Key.space,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'esc': Key.esc,
            'escape': Key.esc,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'home': Key.home,
            'end': Key.end,
            'pageup': Key.page_up,
            'pagedown': Key.page_down,
            'shift': Key.shift,
            'ctrl': Key.ctrl,
            'alt': Key.alt,
            'cmd': Key.cmd,
            'windows': Key.cmd,
        }
        
        key_name_lower = key_name.lower()
        if key_name_lower in special_keys:
            return special_keys[key_name_lower]
        
        # Regular characters
        if len(key_name) == 1:
            return key_name
        
        return key_name

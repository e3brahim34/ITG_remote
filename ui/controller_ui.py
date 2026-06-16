"""Controller Device UI - Interface for controlling remote device"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QFrame, QComboBox, QSpinBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.styles import DARK_THEME
from utils.logger import Logger

logger = Logger(__name__)

class ControllerUI(MainWindow):
    """UI for controlling remote device"""
    
    # Signals
    connect_clicked = pyqtSignal(str)  # device_id
    disconnect_clicked = pyqtSignal()
    mouse_moved = pyqtSignal(int, int)  # x, y
    mouse_clicked = pyqtSignal(str)  # button
    key_pressed = pyqtSignal(str)  # key
    
    def __init__(self):
        """Initialize controller UI"""
        super().__init__(title="ITG Remote - Controller", width=1400, height=900)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        # Left panel - Device list
        left_panel = self.create_device_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Remote screen and controls
        right_panel = self.create_control_panel()
        main_layout.addWidget(right_panel, 3)
        
        central.setLayout(main_layout)
    
    def create_device_panel(self) -> QFrame:
        """Create device list panel
        
        Returns:
            Device panel frame
        """
        frame = QFrame()
        frame.setStyleSheet("background-color: #2e2e2e; border-right: 1px solid #404040;")
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Available Devices")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Device list area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #2e2e2e; border: none;")
        
        self.device_container = QWidget()
        self.device_layout = QVBoxLayout(self.device_container)
        self.device_layout.addStretch()
        scroll.setWidget(self.device_container)
        
        layout.addWidget(scroll)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Devices")
        refresh_btn.clicked.connect(self.refresh_devices)
        layout.addWidget(refresh_btn)
        
        frame.setLayout(layout)
        frame.setMaximumWidth(300)
        return frame
    
    def create_control_panel(self) -> QFrame:
        """Create control panel
        
        Returns:
            Control panel frame
        """
        frame = QFrame()
        layout = QVBoxLayout()
        
        # Screen display
        self.screen_label = QLabel()
        self.screen_label.setAlignment(Qt.AlignCenter)
        self.screen_label.setStyleSheet("background-color: #000000; border: 1px solid #404040;")
        self.screen_label.setMinimumSize(800, 600)
        layout.addWidget(self.screen_label)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        # Mouse buttons
        left_click_btn = QPushButton("Left Click")
        left_click_btn.clicked.connect(lambda: self.on_mouse_click('left'))
        buttons_layout.addWidget(left_click_btn)
        
        right_click_btn = QPushButton("Right Click")
        right_click_btn.clicked.connect(lambda: self.on_mouse_click('right'))
        buttons_layout.addWidget(right_click_btn)
        
        # Keyboard input
        self.key_input = QComboBox()
        self.key_input.addItems(['Enter', 'Tab', 'Delete', 'Backspace', 'Escape'])
        buttons_layout.addWidget(self.key_input)
        
        key_btn = QPushButton("Press Key")
        key_btn.clicked.connect(self.on_key_press)
        buttons_layout.addWidget(key_btn)
        
        # Disconnect button
        disconnect_btn = QPushButton("Disconnect")
        disconnect_btn.setStyleSheet("background-color: #d32f2f;")
        disconnect_btn.clicked.connect(self.on_disconnect)
        buttons_layout.addWidget(disconnect_btn)
        
        layout.addLayout(buttons_layout)
        
        frame.setLayout(layout)
        return frame
    
    def add_device(self, device_id: str, device_name: str, device_ip: str):
        """Add device to list
        
        Args:
            device_id: Device ID
            device_name: Device name
            device_ip: Device IP
        """
        btn = QPushButton(f"{device_name}\n{device_ip}")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 15px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        btn.clicked.connect(lambda: self.on_device_selected(device_id, device_name))
        
        # Insert before stretch
        self.device_layout.insertWidget(self.device_layout.count() - 1, btn)
    
    def refresh_devices(self):
        """Refresh device list"""
        logger.info("Refreshing devices...")
    
    def on_device_selected(self, device_id: str, device_name: str):
        """Handle device selection
        
        Args:
            device_id: Device ID
            device_name: Device name
        """
        logger.info(f"Selected device: {device_name}")
        self.connect_clicked.emit(device_id)
    
    def on_mouse_click(self, button: str):
        """Handle mouse click
        
        Args:
            button: Mouse button
        """
        logger.debug(f"Mouse click: {button}")
        self.mouse_clicked.emit(button)
    
    def on_key_press(self):
        """Handle key press"""
        key = self.key_input.currentText()
        logger.debug(f"Key pressed: {key}")
        self.key_pressed.emit(key)
    
    def on_disconnect(self):
        """Handle disconnect"""
        logger.info("Disconnecting...")
        self.disconnect_clicked.emit()
    
    def update_screen(self, pixmap: QPixmap):
        """Update screen display
        
        Args:
            pixmap: Screen image pixmap
        """
        scaled = pixmap.scaledToFit(800, 600, Qt.KeepAspectRatio)
        self.screen_label.setPixmap(scaled)
    
    def show_message(self, title: str, message: str):
        """Show message dialog
        
        Args:
            title: Dialog title
            message: Dialog message
        """
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, title, message)

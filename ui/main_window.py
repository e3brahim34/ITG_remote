"""Main application window"""
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from ui.styles import DARK_THEME

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, title="ITG Remote", width=1200, height=800):
        """Initialize main window
        
        Args:
            title: Window title
            width: Window width
            height: Window height
        """
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, width, height)
        self.setStyleSheet(DARK_THEME)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title_label)
        
        # Add placeholder
        placeholder = QLabel("Select an option from the menu")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("font-size: 14px; color: #999999;")
        layout.addWidget(placeholder)
        
        central_widget.setLayout(layout)
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")
        return menubar

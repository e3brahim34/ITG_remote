"""PyQt5 Styles and Themes"""

# Dark theme stylesheet
DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}

QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
}

QPushButton {
    background-color: #0d47a1;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1565c0;
}

QPushButton:pressed {
    background-color: #0d3a85;
}

QLineEdit, QTextEdit {
    background-color: #2e2e2e;
    color: #ffffff;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 5px;
}

QLabel {
    color: #ffffff;
}

QComboBox {
    background-color: #2e2e2e;
    color: #ffffff;
    border: 1px solid #404040;
    padding: 5px;
    border-radius: 4px;
}

QComboBox QAbstractItemView {
    background-color: #2e2e2e;
    color: #ffffff;
    selection-background-color: #0d47a1;
}

QTableWidget {
    background-color: #2e2e2e;
    color: #ffffff;
    border: 1px solid #404040;
    gridline-color: #404040;
}

QHeaderView::section {
    background-color: #1a1a1a;
    color: #ffffff;
    padding: 5px;
    border: none;
    border-right: 1px solid #404040;
}

QScrollBar:vertical {
    background-color: #2e2e2e;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #0d47a1;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background-color: #1565c0;
}

QStatusBar {
    background-color: #1a1a1a;
    color: #ffffff;
    border-top: 1px solid #404040;
}
"""

# Light theme stylesheet
LIGHT_THEME = """
QMainWindow {
    background-color: #ffffff;
    color: #000000;
}

QWidget {
    background-color: #ffffff;
    color: #000000;
}

QPushButton {
    background-color: #0d47a1;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1565c0;
}

QPushButton:pressed {
    background-color: #0d3a85;
}

QLineEdit, QTextEdit {
    background-color: #f5f5f5;
    color: #000000;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 5px;
}

QLabel {
    color: #000000;
}

QComboBox {
    background-color: #f5f5f5;
    color: #000000;
    border: 1px solid #cccccc;
    padding: 5px;
    border-radius: 4px;
}

QTableWidget {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #cccccc;
    gridline-color: #cccccc;
}

QHeaderView::section {
    background-color: #f5f5f5;
    color: #000000;
    padding: 5px;
    border: none;
    border-right: 1px solid #cccccc;
}
"""

def get_icon_color(theme: str = 'dark') -> str:
    """Get icon color based on theme
    
    Args:
        theme: Theme name ('dark' or 'light')
        
    Returns:
        Color string
    """
    return '#ffffff' if theme == 'dark' else '#000000'

def get_background_color(theme: str = 'dark') -> str:
    """Get background color based on theme
    
    Args:
        theme: Theme name
        
    Returns:
        Color string
    """
    return '#1e1e1e' if theme == 'dark' else '#ffffff'

def get_primary_color(theme: str = 'dark') -> str:
    """Get primary color based on theme
    
    Args:
        theme: Theme name
        
    Returns:
        Color string
    """
    return '#0d47a1'

def get_secondary_color(theme: str = 'dark') -> str:
    """Get secondary color based on theme
    
    Args:
        theme: Theme name
        
    Returns:
        Color string
    """
    return '#2e2e2e' if theme == 'dark' else '#f5f5f5'

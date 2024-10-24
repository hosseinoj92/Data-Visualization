# In gui/help_dialog.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt

from PyQt5.QtCore import QUrl

import sys
import os


class HelpDialog(QDialog):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(800, 600)  # Increased size for better readability
        self.init_ui(content)
    
    def init_ui(self, content):
        layout = QVBoxLayout()
        
        # QWebEngineView to display rich HTML content with JavaScript
        self.web_view = QWebEngineView()

        # Detect if running in PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            base_dir = os.path.join(sys._MEIPASS, 'gui/images/')
        else:
            base_dir = os.path.abspath('gui/images/')

        # Specify the base URL to resolve relative paths
        base_url = QUrl.fromLocalFile(base_dir)
        self.web_view.setHtml(content, base_url)  # Add base URL here

        layout.addWidget(self.web_view)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setFixedWidth(100)
        close_button.setFixedHeight(30)
        close_button.setStyleSheet("margin: 10px;")
        
        # Align the Close button to the right
        button_layout = QVBoxLayout()
        button_layout.addWidget(close_button, alignment=Qt.AlignRight)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

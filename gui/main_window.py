import os
import sys
from PyQt5.QtWidgets import QMainWindow, QTabWidget
from PyQt5.QtGui import QIcon

# Import the tab classes
from gui.general_tab import GeneralTab
from gui.normalization_tab import NormalizationTab
from gui.data_handling_tab import DataHandlingTab  # Import the new DataHandlingTab


def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Wiz Pro by Hossein Ostovar ")
        self.setGeometry(100, 100, 1200, 800)

        self.init_ui()

        # Load the stylesheet
        self.apply_stylesheet()

    def init_ui(self):
        # Create the tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Initialize tabs
        self.general_tab = GeneralTab()
        self.normalization_tab = NormalizationTab(general_tab=self.general_tab)
        self.data_handling_tab = DataHandlingTab()

        # Add tabs to the tab widget with icons
        general_icon_path = resource_path('gui/resources/general_icon.png')
        normalization_icon_path = resource_path('gui/resources/normalization_icon.png')
        data_icon_path = resource_path('gui/resources/data_icon.png')

        self.setWindowIcon(QIcon(resource_path('gui/resources/icon.png')))


        self.tabs.addTab(self.general_tab, QIcon(general_icon_path), "General")
        self.tabs.addTab(self.normalization_tab, QIcon(normalization_icon_path), "Normalization")
        self.tabs.addTab(self.data_handling_tab, QIcon(data_icon_path), "Data Handling")

        # Optionally, set the default tab
        self.tabs.setCurrentWidget(self.general_tab)

    def apply_stylesheet(self):
        """Load the global stylesheet."""
        stylesheet_path = resource_path('style.qss')
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r') as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Warning: stylesheet not found at {stylesheet_path}")

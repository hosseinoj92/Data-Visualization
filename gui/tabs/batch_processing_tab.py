# batch_processing_tab.py

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


from gui.panels.batch_file_handling_panels import BatchFileHandlingPanel
from gui.panels.batch_data_handling_panels import BatchDataHandlingPanel
from gui.panels.batch_metadata_handling_panels import BatchMetaDataHandlingPanel


import sys 

def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class BatchProcessingTab(QWidget):
    def __init__(self, general_tab=None, parent=None):
        super().__init__(parent)
        self.general_tab = general_tab  # Store reference to the general tab if needed
        self.init_ui()

        # Apply global stylesheet
        self.apply_stylesheet()

    def apply_stylesheet(self):
        """Load the global stylesheet."""
        stylesheet_path = resource_path('style.qss')
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r') as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Warning: stylesheet not found at {stylesheet_path}")

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create a tab widget to hold the sub-tabs
        self.sub_tabs = QTabWidget()
        main_layout.addWidget(self.sub_tabs)

        # Create instances of the panels
        self.batch_data_handling_panel = BatchDataHandlingPanel()
        self.batch_file_handling_panel = BatchFileHandlingPanel()
        self.batch_metadata_handling_panel = BatchMetaDataHandlingPanel()

        # Add icons to the sub-tabs
        data_handling_icon_path = resource_path('gui/resources/batch_data_handling_icon.png')
        file_handling_icon_path = resource_path('gui/resources/batch_file_handling_icon.png')
        metadata_handling_icon_path = resource_path('gui/resources/batch_metadata_handling_icon.png')

        # Add sub-tabs to the tab widget
        self.sub_tabs.addTab(
            self.batch_data_handling_panel,
            QIcon(data_handling_icon_path),
            "Batch Data Handling"
        )
        self.sub_tabs.addTab(
            self.batch_file_handling_panel,
            QIcon(file_handling_icon_path),
            "Batch File Handling"
        )
        self.sub_tabs.addTab(
            self.batch_metadata_handling_panel,
            QIcon(metadata_handling_icon_path),
            "Batch Meta Data Handling"
        )

        # Connect signals from the panels if needed
        self.batch_data_handling_panel.data_processed.connect(self.on_data_processed)
        self.batch_file_handling_panel.files_processed.connect(self.on_files_processed)
        self.batch_metadata_handling_panel.metadata_processed.connect(self.on_metadata_processed)

    def on_data_processed(self):
        print("Data processed in Batch Data Handling Panel.")

    def on_files_processed(self):
        print("Files processed in Batch File Handling Panel.")

    def on_metadata_processed(self):
        print("Metadata processed in Batch Meta Data Handling Panel.")
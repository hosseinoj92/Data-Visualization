#gui/panels selected_data_panel.py

import os
from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt,QUrl, QMimeData

from gui.utils.widgets import DraggableListWidget  # Import the DraggableListWidget from widgets.py

import sys
from PyQt5.QtGui import QIcon

def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class SelectedDataPanel(QGroupBox):
    def __init__(self, include_retract_button=False, parent=None):
        super().__init__("Selected Data", parent)
        self.last_directory = os.path.expanduser("~")  # Initialize to user's home directory
        self.all_selected = False  # Initialize selection state
        self.init_ui(include_retract_button)

        # Apply global stylesheet
        self.apply_stylesheet()

    def apply_stylesheet(self):
        """Load the global stylesheet."""
        stylesheet_path = os.path.join(os.path.dirname(__file__), 'style.qss')
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r') as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Warning: stylesheet not found at {stylesheet_path}")

    def init_ui(self, include_retract_button):
        self.layout = QVBoxLayout()

        # Set up buttons
        self.file_selector_button = QPushButton("Choose Files")
        file_selector_path = resource_path('gui/resources/select_folder_icon.png')
        self.file_selector_button.setIcon(QIcon(file_selector_path))

        self.add_file_button = QPushButton("Add Files")
        add_file_path = resource_path('gui/resources/add.png')
        self.add_file_button.setIcon(QIcon(add_file_path))

        self.select_all_button = QPushButton("Select All")
        select_all_path = resource_path('gui/resources/select_all.png')
        self.select_all_button.setIcon(QIcon(select_all_path))


        # Set up tooltips
        self.file_selector_button.setToolTip("Click to choose and add files.")
        self.add_file_button.setToolTip("Click to add more files.")
        self.select_all_button.setToolTip("Click to select/deselect all files.")

        # Optional Retract Button
        if include_retract_button:
            self.retract_button = QPushButton("Retract from General")
            self.layout.addWidget(self.retract_button)

        # Draggable and Selectable List Widget
        self.selected_files_list = DraggableListWidget()

        # Scroll Area for the List Widget
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.selected_files_list)

        # Add buttons to the layout
        self.layout.addWidget(self.file_selector_button)

        # Create a horizontal layout for "Add Files" and "Select All" buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_file_button)
        buttons_layout.addWidget(self.select_all_button)

        # Add the horizontal layout to the main layout
        self.layout.addLayout(buttons_layout)

        # Add the scroll area containing the list widget
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

        # Connect buttons to their respective functions
        self.file_selector_button.clicked.connect(self.choose_files)
        self.add_file_button.clicked.connect(self.add_files_via_dialog)
        self.select_all_button.clicked.connect(self.toggle_select_all)

    def choose_files(self):
        """
        Open a file dialog to select multiple files and add them to the panel.
        """
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            self.last_directory,  # Open the last used directory
            "All Files (*)"
        )
        if file_paths:
            self.add_files(file_paths)
            # Update last_directory to the directory of the last selected file
            self.last_directory = os.path.dirname(file_paths[-1])

    def add_files(self, file_paths):
        """
        Add one or multiple files to the Selected Data Panel.
        """
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        for file_path in file_paths:
            self.add_file_to_panel(file_path)

    def add_files_via_dialog(self):
        """
        Open a file dialog to select multiple files and add them to the panel.
        This method is connected to the "Add Files" button.
        """
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Add Files",
            self.last_directory,
            "All Files (*)"
        )
        if file_paths:
            self.add_files(file_paths)
            # Update last_directory to the directory of the last selected file
            self.last_directory = os.path.dirname(file_paths[-1])


    def add_file_to_panel(self, file_path):
        """
        Add a single file to the panel if it's not already present.
        """
        if not self.is_file_in_list(file_path):
            self.selected_files_list.add_file_to_panel(file_path)  # Use DraggableListWidget's method

    def is_file_in_list(self, file_path):
        """
        Check if a file is already in the list.
        """
        for index in range(self.selected_files_list.count()):
            if os.path.abspath(file_path) == os.path.abspath(self.selected_files_list.item(index).data(Qt.UserRole)):
                return True
        return False

    def toggle_select_all(self):
        """
        Toggle between selecting all files and deselecting all files.
        """
        if not self.all_selected:
            # Select all
            for index in range(self.selected_files_list.count()):
                item = self.selected_files_list.item(index)
                item.setCheckState(Qt.Checked)
            self.select_all_button.setText("Deselect All")
            self.all_selected = True
        else:
            # Deselect all
            for index in range(self.selected_files_list.count()):
                item = self.selected_files_list.item(index)
                item.setCheckState(Qt.Unchecked)
            self.select_all_button.setText("Select All")
            self.all_selected = False

    def get_selected_files(self):
        """
        Retrieve a list of file paths that are currently selected (checked).
        """
        selected_items = [
            item for item in self.selected_files_list.findItems("*", Qt.MatchWildcard)
            if item.checkState() == Qt.Checked
        ]
        return [item.data(Qt.UserRole) for item in selected_items]  # Retrieve from Qt.UserRole


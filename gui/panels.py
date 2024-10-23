# gui/panels.py

import os
from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QScrollArea, QCheckBox, QSpinBox, QComboBox, QHBoxLayout,
    QListWidgetItem, QColorDialog, QMessageBox, QFileDialog, QWidget, QMenu, QDialog,QDoubleSpinBox,QApplication
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from utils import read_numeric_data  # Ensure this import is correct
import h5py
import pandas as pd
from PyQt5.QtCore import pyqtSignal
import numpy as np
import matplotlib.pyplot as plt
from gui.help_dialog import HelpDialog
from gui.help_content import (MIN_MAX_NORMALIZATION_HELP,Z_SCORE_NORMALIZATION_HELP, 
                              ROBUST_SCALING_NORMALIZATION_HELP,AUC_NORMALIZATION_HELP,INTERVAL_AUC_NORMALIZATION_HELP,
                              TOTAL_INTENSITY_NORMALIZATION_HELP,REFERENCE_PEAK_NORMALIZATION_HELP,BASELINE_CORRECTION_NORMALIZATION_HELP

                              )




def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



#################################################################


class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.MultiSelection)  # Enable multi-selection
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

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


    def keyPressEvent(self, event):
        """
        Handle key press events. If the Delete key is pressed, remove selected items.
        Also handle Ctrl+C and Ctrl+V for copy and paste.
        """
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
        elif event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            self.copy_selected_items()
        elif event.key() == Qt.Key_V and event.modifiers() & Qt.ControlModifier:
            self.paste_items()
        else:
            super().keyPressEvent(event)

    def copy_selected_items(self):
        selected_items = self.selectedItems()
        if not selected_items:
            return
        file_paths = [item.data(Qt.UserRole) for item in selected_items]
        # Join the file paths into a single string, separated by newlines
        file_paths_str = '\n'.join(file_paths)
        # Access the clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(file_paths_str)

    def paste_items(self):
        clipboard = QApplication.clipboard()
        file_paths_str = clipboard.text()
        if not file_paths_str:
            return
        file_paths = file_paths_str.split('\n')
        for file_path in file_paths:
            if file_path:
                self.add_file_to_panel(file_path)

    def delete_selected_items(self):
        """
        Delete all selected items from the list after confirmation.
        """
        selected_items = self.selectedItems()
        if not selected_items:
            return
        reply = QMessageBox.question(
            self, 'Confirm Deletion',
            f"Are you sure you want to delete the selected {len(selected_items)} file(s)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for item in selected_items:
                self.takeItem(self.row(item))
            QMessageBox.information(self, "Deletion Successful", f"Deleted {len(selected_items)} file(s).")

    def open_context_menu(self, position):
        """
        Create a context menu with a 'Delete' option on right-click.
        """
        context_menu = QMenu(self)
        delete_action = context_menu.addAction("Delete")
        action = context_menu.exec_(self.mapToGlobal(position))
        if action == delete_action:
            self.delete_selected_items()

    def dragEnterEvent(self, event):
        """
        Accept the drag event if it contains URLs (files).
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """
        Accept the drag move event if it contains URLs (files).
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Handle the drop event by adding the dropped files to the list.
        """
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    self.add_file_to_panel(file_path)
            event.acceptProposedAction()
        else:
            event.ignore()

    def add_file_to_panel(self, file_path):
        """
        Add a single file to the list.
        Avoid adding duplicates.
        """
        file_name = os.path.basename(file_path)
        # Avoid adding duplicates
        existing_files = [os.path.abspath(self.item(i).data(Qt.UserRole)) for i in range(self.count())]
        if os.path.abspath(file_path) in existing_files:
            return
        item = QListWidgetItem(file_name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Unchecked)
        item.setData(Qt.UserRole, file_path)
        self.addItem(item)



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
        stylesheet_path = resource_path('style.qss')
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r') as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Warning: stylesheet not found at {stylesheet_path}")


    def init_ui(self, include_retract_button):
        self.layout = QVBoxLayout()

        # Set up buttons
        self.file_selector_button = QPushButton("Choose Files")
        self.add_file_button = QPushButton("Add Files")
        self.select_all_button = QPushButton("Select All")
        #self.remove_selected_button = QPushButton("Remove Selected")

        # Set up tooltips
        self.file_selector_button.setToolTip("Click to choose and add files.")
        self.add_file_button.setToolTip("Click to add more files.")
        self.select_all_button.setToolTip("Click to select/deselect all files.")
        #self.remove_selected_button.setToolTip("Click to remove selected files.")

        # Optional Retract Button
        if include_retract_button:
            self.retract_button = QPushButton("Retract from General")
            self.layout.addWidget(self.retract_button)

        # Draggable and Selectable List Widget
        self.selected_files_list = DraggableListWidget()  # Changed from QListWidget to DraggableListWidget

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
        self.add_file_button.clicked.connect(self.add_files)
        self.select_all_button.clicked.connect(self.toggle_select_all)
        #self.remove_selected_button.clicked.connect(self.remove_selected_files)  # Connect Remove Button

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

    '''def remove_selected_files(self):
        """
        Remove selected files from the Selected Data Panel.
        """
        selected_items = self.selected_files_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "No files selected to remove.")
            return
        reply = QMessageBox.question(
            self, 'Confirm Removal',
            f"Are you sure you want to remove the selected {len(selected_items)} file(s)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for item in selected_items:
                self.selected_files_list.takeItem(self.selected_files_list.row(item))
            QMessageBox.information(self, "Removal Successful", f"Removed {len(selected_items)} file(s).")'''

    # Optional Retract Functionality
    def retract_from_general(self):
        # Implementation as per your application logic
        pass

class BaseNormalizationMethodPanel(QWidget):
    """
    Abstract base class for normalization method panels.
    Each normalization method should inherit from this class and implement the required methods.
    """
    def __init__(self, method_name, parent=None):
        super().__init__(parent)
        self.method_name = method_name
        self.init_ui()
    
    def init_ui(self):
        """
        Initialize the UI components. Must be implemented by subclasses.
        """
        raise NotImplementedError("Must implement init_ui in subclass")
    
    def get_parameters(self):
        """
        Retrieve method-specific parameters. Must be implemented by subclasses.
        """
        raise NotImplementedError("Must implement get_parameters in subclass")

####################################################################

class MinMaxNormalizationPanel(BaseNormalizationMethodPanel):
    def __init__(self, parent=None):
        super().__init__("Min-Max Normalization", parent)

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
        self.layout = QVBoxLayout()

        # Help button with icon
        help_button = QPushButton("Help")
        help_icon = QIcon(resource_path("gui/resources/help_icon.png"))
        help_button.setIcon(help_icon)
        help_button.clicked.connect(self.show_help)
        self.layout.addWidget(help_button)

        # Apply and Save Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")

        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        send_icon = QIcon(resource_path("gui/resources/send_icon.png"))
        self.send_to_data_panel_button.setIcon(send_icon)

        self.apply_button.setEnabled(True)   # Enabled by default
        self.save_button.setEnabled(False)   # Disabled by default
        self.send_to_data_panel_button.setEnabled(False)  # Disabled by default

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # Custom Min-Max Range
        self.use_custom_range_checkbox = QCheckBox("Use custom min-max values")
        self.layout.addWidget(self.use_custom_range_checkbox)

        custom_range_layout = QHBoxLayout()
        custom_range_layout.addWidget(QLabel("Min:"))
        self.custom_min_spinbox = QDoubleSpinBox()
        self.custom_min_spinbox.setEnabled(False)
        self.custom_min_spinbox.setRange(-1e6, 1e6)
        self.custom_min_spinbox.setValue(0.0)
        custom_range_layout.addWidget(self.custom_min_spinbox)

        custom_range_layout.addWidget(QLabel("Max:"))
        self.custom_max_spinbox = QDoubleSpinBox()
        self.custom_max_spinbox.setEnabled(False)
        self.custom_max_spinbox.setRange(-1e6, 1e6)
        self.custom_max_spinbox.setValue(1.0)
        custom_range_layout.addWidget(self.custom_max_spinbox)

        self.layout.addLayout(custom_range_layout)

        # Connect signals
        self.use_custom_range_checkbox.stateChanged.connect(self.toggle_custom_range)
        self.custom_min_spinbox.valueChanged.connect(self.validate_inputs)
        self.custom_max_spinbox.valueChanged.connect(self.validate_inputs)

        self.setLayout(self.layout)

    def show_help(self):
        help_content = MIN_MAX_NORMALIZATION_HELP
        dialog = HelpDialog("Min-Max Normalization Help", help_content, self)
        dialog.exec_()

    def toggle_custom_range(self, state):
        enabled = state == Qt.Checked
        self.custom_min_spinbox.setEnabled(enabled)
        self.custom_max_spinbox.setEnabled(enabled)
        self.save_button.setEnabled(False)  # Disable Save until normalization is applied

        # Enable Apply button based on input validity
        self.validate_inputs()

    def validate_inputs(self):
        if self.use_custom_range_checkbox.isChecked():
            custom_min = self.custom_min_spinbox.value()
            custom_max = self.custom_max_spinbox.value()
            if custom_max > custom_min:
                self.apply_button.setEnabled(True)
            else:
                self.apply_button.setEnabled(False)
        else:
            # If not using custom range, Apply should be enabled
            self.apply_button.setEnabled(True)
    
    def get_parameters(self):
        params = {}
        params['use_custom'] = self.use_custom_range_checkbox.isChecked()
        if params['use_custom']:
            custom_min = self.custom_min_spinbox.value()
            custom_max = self.custom_max_spinbox.value()
            if custom_max <= custom_min:
                QMessageBox.warning(self, "Invalid Range", "Custom Max must be greater than Custom Min.")
                return None
            params['custom_min'] = custom_min
            params['custom_max'] = custom_max
        else:
            params['custom_min'] = None
            params['custom_max'] = None
        return params


##################################################################

class ZScoreNormalizationPanel(BaseNormalizationMethodPanel):
    def __init__(self, parent=None):
        super().__init__("Z-score Normalization", parent)
    
    def init_ui(self):
        self.layout = QVBoxLayout()

        # Help Button
        help_button = QPushButton("Help")
        help_icon = QIcon("gui/resources/help_icon.png")  # Use resource path
        help_button.setIcon(help_icon)
        help_button.clicked.connect(self.show_help)
        self.layout.addWidget(help_button)

        # Apply and Save Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")

        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        send_icon = QIcon(resource_path("gui/resources/send_icon.png"))
        self.send_to_data_panel_button.setIcon(send_icon)

        self.apply_button.setEnabled(True)   # Enabled by default
        self.save_button.setEnabled(False)   # Disabled by default
        self.send_to_data_panel_button.setEnabled(False)  # Disabled by default
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # Parameters for Z-score
        self.layout.addWidget(QLabel("Z-score Parameters:"))

        # Input for Mean
        self.mean_input = QLineEdit()
        self.mean_input.setPlaceholderText("Leave blank for data mean")
        self.layout.addWidget(QLabel("Mean:"))
        self.layout.addWidget(self.mean_input)

        # Input for Standard Deviation
        self.std_input = QLineEdit()
        self.std_input.setPlaceholderText("Leave blank for data std")
        self.layout.addWidget(QLabel("Standard Deviation:"))
        self.layout.addWidget(self.std_input)

        # Connect inputs to enable Apply button
        self.mean_input.textChanged.connect(self.validate_inputs)
        self.std_input.textChanged.connect(self.validate_inputs)

        self.setLayout(self.layout)

    def show_help(self):
        help_content = Z_SCORE_NORMALIZATION_HELP
        dialog = HelpDialog("Z-score Normalization Help", help_content, self)
        dialog.exec_()

    def validate_inputs(self):
        mean_text = self.mean_input.text()
        std_text = self.std_input.text()
        valid = True

        # If mean is provided, it must be a valid float
        if mean_text:
            try:
                float(mean_text)
            except ValueError:
                valid = False

        # If std is provided, it must be a valid float and not zero
        if std_text:
            try:
                std_val = float(std_text)
                if std_val == 0:
                    valid = False
            except ValueError:
                valid = False

        # Enable Apply button if inputs are valid
        self.apply_button.setEnabled(valid)

    def get_parameters(self):
        params = {}
        mean_text = self.mean_input.text()
        std_text = self.std_input.text()
        try:
            params['mean'] = float(mean_text) if mean_text else None
            params['std'] = float(std_text) if std_text else None
            if params['std'] is not None and params['std'] == 0:
                QMessageBox.warning(self, "Invalid Standard Deviation", "Standard deviation cannot be zero.")
                return None
            return params
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numerical values for mean and standard deviation.")
            return None
###########################################################

class RobustScalingNormalizationPanel(BaseNormalizationMethodPanel):
    def __init__(self, parent=None):
        super().__init__("Robust Scaling Normalization", parent)
    
    def init_ui(self):
        self.layout = QVBoxLayout()

        # Help Button
        help_button = QPushButton("Help")
        help_icon = QIcon("gui/resources/help_icon.png")  # Use resource path
        help_button.setIcon(help_icon)
        help_button.clicked.connect(self.show_help)
        self.layout.addWidget(help_button)

        # Apply and Save Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")

        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        send_icon = QIcon(resource_path("gui/resources/send_icon.png"))
        self.send_to_data_panel_button.setIcon(send_icon)


        self.apply_button.setEnabled(True)   # Enabled by default
        self.save_button.setEnabled(False)   # Disabled by default
        self.send_to_data_panel_button.setEnabled(False)  # Disabled by default

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # Parameters for Robust Scaling
        self.layout.addWidget(QLabel("Robust Scaling Parameters:"))

        # Input for Quantile Range
        self.quantile_min_input = QLineEdit()
        self.quantile_min_input.setPlaceholderText("e.g., 25")
        self.layout.addWidget(QLabel("Quantile Min (%):"))
        self.layout.addWidget(self.quantile_min_input)

        self.quantile_max_input = QLineEdit()
        self.quantile_max_input.setPlaceholderText("e.g., 75")
        self.layout.addWidget(QLabel("Quantile Max (%):"))
        self.layout.addWidget(self.quantile_max_input)

        # Connect inputs to enable Apply button
        self.quantile_min_input.textChanged.connect(self.validate_inputs)
        self.quantile_max_input.textChanged.connect(self.validate_inputs)

        self.setLayout(self.layout)

    def show_help(self):
        help_content = ROBUST_SCALING_NORMALIZATION_HELP
        dialog = HelpDialog("Robust Scaling Normalization Help", help_content, self)
        dialog.exec_()

    def validate_inputs(self):
        min_text = self.quantile_min_input.text()
        max_text = self.quantile_max_input.text()
        valid = True

        # If min is provided, it must be a valid float between 0 and 100
        if min_text:
            try:
                min_val = float(min_text)
                if not (0 <= min_val < 100):
                    valid = False
            except ValueError:
                valid = False

        # If max is provided, it must be a valid float between 0 and 100
        if max_text:
            try:
                max_val = float(max_text)
                if not (0 < max_val <= 100):
                    valid = False
            except ValueError:
                valid = False

        # If both min and max are provided, ensure max > min
        if min_text and max_text:
            try:
                min_val = float(min_text)
                max_val = float(max_text)
                if max_val <= min_val:
                    valid = False
            except ValueError:
                valid = False

        # Enable Apply button if inputs are valid or if inputs are empty (use inherent stats)
        if (not min_text and not max_text) or valid:
            self.apply_button.setEnabled(True)
        else:
            self.apply_button.setEnabled(False)

    def get_parameters(self):
        params = {}
        min_text = self.quantile_min_input.text()
        max_text = self.quantile_max_input.text()
        try:
            params['quantile_min'] = float(min_text) if min_text else 25.0  # Default to 25%
            params['quantile_max'] = float(max_text) if max_text else 75.0  # Default to 75%
            if not (0 <= params['quantile_min'] < params['quantile_max'] <= 100):
                QMessageBox.warning(self, "Invalid Quantile Range", "Quantile Min must be less than Quantile Max and both between 0 and 100.")
                return None
            return params
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numerical values for quantiles.")
            return None
###############################################

class AUCNormalizationPanel(BaseNormalizationMethodPanel):
    def __init__(self, parent=None):
        super().__init__("AUC Normalization", parent)

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Help Button
        help_button = QPushButton("Help")
        help_icon = QIcon("gui/resources/help_icon.png")  # Use resource path
        help_button.setIcon(help_icon)
        help_button.clicked.connect(self.show_help)
        self.layout.addWidget(help_button)

        # Apply and Save Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")

        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        send_icon = QIcon(resource_path("gui/resources/send_icon.png"))
        self.send_to_data_panel_button.setIcon(send_icon)


        self.apply_button.setEnabled(True)   # Enabled by default
        self.save_button.setEnabled(False)   # Disabled by default
        self.send_to_data_panel_button.setEnabled(False)  # Disabled by default
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # Parameters for AUC Normalization
        self.layout.addWidget(QLabel("AUC Normalization Parameters:"))

        # Input for Sorting (optional, to ensure x-values are sorted)
        self.sort_checkbox = QCheckBox("Sort data by X-axis")
        self.sort_checkbox.setChecked(True)  # Enabled by default
        self.layout.addWidget(self.sort_checkbox)

        # Connect signals
        self.sort_checkbox.stateChanged.connect(self.on_sort_checkbox_changed)

        self.setLayout(self.layout)

    def show_help(self):
        help_content = AUC_NORMALIZATION_HELP
        dialog = HelpDialog("AUC Normalization Help", help_content, self)
        dialog.exec_()

    def on_sort_checkbox_changed(self, state):
        # If the user unchecks sorting, ensure that Apply can still proceed
        self.save_button.setEnabled(False)  # Disable Save until normalization is applied
        self.apply_button.setEnabled(True)  # Enable Apply button

    def get_parameters(self):
        params = {}
        # Check if sorting is enabled
        params['sort_data'] = self.sort_checkbox.isChecked()
        return params
########################################################
class IntervalAUCNormalizationPanel(BaseNormalizationMethodPanel):
    def __init__(self, parent=None):
        super().__init__("Interval AUC Normalization", parent)

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Help Button
        help_button = QPushButton("Help")
        help_icon = QIcon("gui/resources/help_icon.png")  # Use resource path
        help_button.setIcon(help_icon)
        help_button.clicked.connect(self.show_help)
        self.layout.addWidget(help_button)

        # Apply and Save Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")

        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        send_icon = QIcon(resource_path("gui/resources/send_icon.png"))
        self.send_to_data_panel_button.setIcon(send_icon)


        self.apply_button.setEnabled(False)   # Disabled until valid input
        self.save_button.setEnabled(False)    # Disabled by default
        self.send_to_data_panel_button.setEnabled(False)  # Disabled by default

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # Parameters for Interval AUC Normalization
        self.layout.addWidget(QLabel("Interval AUC Normalization Parameters:"))

        # Checkbox to enable/disable Desired AUC
        self.enable_desired_auc_checkbox = QCheckBox("Enable Desired AUC")
        self.enable_desired_auc_checkbox.setChecked(True)  # Enabled by default
        self.layout.addWidget(self.enable_desired_auc_checkbox)

        # Desired AUC Input
        desired_auc_layout = QHBoxLayout()
        desired_auc_layout.addWidget(QLabel("Desired AUC:"))
        self.desired_auc_input = QDoubleSpinBox()
        self.desired_auc_input.setRange(0.0001, 1e6)
        self.desired_auc_input.setValue(1.0)
        desired_auc_layout.addWidget(self.desired_auc_input)
        self.layout.addLayout(desired_auc_layout)

        # Interval Start Input
        interval_start_layout = QHBoxLayout()
        interval_start_layout.addWidget(QLabel("Interval Start (x):"))
        self.interval_start_input = QDoubleSpinBox()
        self.interval_start_input.setRange(-1e6, 1e6)
        self.interval_start_input.setValue(0.0)
        interval_start_layout.addWidget(self.interval_start_input)
        self.layout.addLayout(interval_start_layout)

        # Interval End Input
        interval_end_layout = QHBoxLayout()
        interval_end_layout.addWidget(QLabel("Interval End (x):"))
        self.interval_end_input = QDoubleSpinBox()
        self.interval_end_input.setRange(-1e6, 1e6)
        self.interval_end_input.setValue(10.0)
        interval_end_layout.addWidget(self.interval_end_input)
        self.layout.addLayout(interval_end_layout)

        # Connect signals for validation and checkbox state
        self.enable_desired_auc_checkbox.stateChanged.connect(self.toggle_desired_auc)
        self.desired_auc_input.valueChanged.connect(self.validate_inputs)
        self.interval_start_input.valueChanged.connect(self.validate_inputs)
        self.interval_end_input.valueChanged.connect(self.validate_inputs)

        self.setLayout(self.layout)

        # **Invoke validation upon initialization**
        self.validate_inputs()

    def show_help(self):
        help_content = INTERVAL_AUC_NORMALIZATION_HELP
        dialog = HelpDialog("Interval AUC Normalization Help", help_content, self)
        dialog.exec_()

    def toggle_desired_auc(self, state):
        enabled = state == Qt.Checked
        self.desired_auc_input.setEnabled(enabled)
        self.save_button.setEnabled(False)  # Disable Save until normalization is applied
        self.validate_inputs()

    def validate_inputs(self):
        start = self.interval_start_input.value()
        end = self.interval_end_input.value()
        desired_auc = self.desired_auc_input.value() if self.enable_desired_auc_checkbox.isChecked() else 1.0

        if end > start and desired_auc > 0:
            self.apply_button.setEnabled(True)
        else:
            self.apply_button.setEnabled(False)

    def get_parameters(self):
        params = {}
        enabled = self.enable_desired_auc_checkbox.isChecked()
        if enabled:
            desired_auc = self.desired_auc_input.value()
            if desired_auc <= 0:
                QMessageBox.warning(self, "Invalid AUC", "Desired AUC must be greater than zero.")
                return None
            params['desired_auc'] = desired_auc
        else:
            params['desired_auc'] = 1.0  # Default scaling factor

        start = self.interval_start_input.value()
        end = self.interval_end_input.value()
        if end <= start:
            QMessageBox.warning(self, "Invalid Interval", "Interval End must be greater than Interval Start.")
            return None
        params['interval_start'] = start
        params['interval_end'] = end

        return params
    
########################################################
class TotalIntensityNormalizationPanel(BaseNormalizationMethodPanel):
    def __init__(self, parent=None):
        super().__init__("Total Intensity Normalization", parent)

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Help Button
        help_button = QPushButton("Help")
        help_icon = QIcon("gui/resources/help_icon.png")  # Use resource path
        help_button.setIcon(help_icon)
        help_button.clicked.connect(self.show_help)
        self.layout.addWidget(help_button)

        # Apply and Save Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")

        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        send_icon = QIcon(resource_path("gui/resources/send_icon.png"))
        self.send_to_data_panel_button.setIcon(send_icon)


        self.apply_button.setEnabled(False)   # Disabled until valid input
        self.save_button.setEnabled(False)    # Disabled by default
        self.send_to_data_panel_button.setEnabled(False)  # Disabled by default

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # Parameters for Total Intensity Normalization
        self.layout.addWidget(QLabel("Total Intensity Normalization Parameters:"))

        # Checkbox to enable/disable Desired Total Intensity
        self.enable_desired_intensity_checkbox = QCheckBox("Enable Desired Total Intensity")
        self.enable_desired_intensity_checkbox.setChecked(True)  # Enabled by default
        self.layout.addWidget(self.enable_desired_intensity_checkbox)

        # Desired Total Intensity Input
        desired_intensity_layout = QHBoxLayout()
        desired_intensity_layout.addWidget(QLabel("Desired Total Intensity:"))
        self.desired_intensity_input = QDoubleSpinBox()
        self.desired_intensity_input.setRange(0.0001, 1e9)
        self.desired_intensity_input.setValue(1.0)
        desired_intensity_layout.addWidget(self.desired_intensity_input)
        self.layout.addLayout(desired_intensity_layout)

        # Connect signals for validation and checkbox state
        self.enable_desired_intensity_checkbox.stateChanged.connect(self.toggle_desired_intensity)
        self.desired_intensity_input.valueChanged.connect(self.validate_inputs)

        self.setLayout(self.layout)

        # **Invoke validation upon initialization**
        self.validate_inputs()

    def show_help(self):
        help_content = TOTAL_INTENSITY_NORMALIZATION_HELP
        dialog = HelpDialog("Total Intensity Normalization Help", help_content, self)
        dialog.exec_()

    def toggle_desired_intensity(self, state):
        enabled = state == Qt.Checked
        self.desired_intensity_input.setEnabled(enabled)
        self.save_button.setEnabled(False)  # Disable Save until normalization is applied
        self.validate_inputs()

    def validate_inputs(self):
        enabled = self.enable_desired_intensity_checkbox.isChecked()
        desired_intensity = self.desired_intensity_input.value() if enabled else 1.0

        if desired_intensity > 0:
            self.apply_button.setEnabled(True)
        else:
            self.apply_button.setEnabled(False)

    def get_parameters(self):
        params = {}
        enabled = self.enable_desired_intensity_checkbox.isChecked()
        if enabled:
            desired_intensity = self.desired_intensity_input.value()
            if desired_intensity <= 0:
                QMessageBox.warning(self, "Invalid Intensity", "Desired Total Intensity must be greater than zero.")
                return None
            params['desired_total_intensity'] = desired_intensity
        else:
            params['desired_total_intensity'] = 1.0  # Default scaling factor

        return params
###############################################################


class ReferencePeakNormalizationPanel(BaseNormalizationMethodPanel):
    def __init__(self, parent=None):
        super().__init__("Reference Peak Normalization", parent)

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Help Button
        help_button = QPushButton("Help")
        help_icon = QIcon("gui/resources/help_icon.png")  # Use resource path
        help_button.setIcon(help_icon)
        help_button.clicked.connect(self.show_help)
        self.layout.addWidget(help_button)

        # Apply and Save Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")

        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        send_icon = QIcon(resource_path("gui/resources/send_icon.png"))
        self.send_to_data_panel_button.setIcon(send_icon)


        self.apply_button.setEnabled(False)   # Disabled until valid input
        self.save_button.setEnabled(False)    # Disabled by default
        self.send_to_data_panel_button.setEnabled(False)  # Disabled by default

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # Parameters for Reference Peak Normalization
        self.layout.addWidget(QLabel("Reference Peak Normalization Parameters:"))

        # Reference Peak X-Value Input
        ref_peak_layout = QHBoxLayout()
        ref_peak_layout.addWidget(QLabel("Reference Peak X-Value:"))
        self.ref_peak_input = QLineEdit()
        self.ref_peak_input.setPlaceholderText("e.g., 5.0")
        self.ref_peak_input.setText("5.0")  # Default value
        ref_peak_layout.addWidget(self.ref_peak_input)
        self.layout.addLayout(ref_peak_layout)

        # Desired Reference Intensity Input
        desired_intensity_layout = QHBoxLayout()
        desired_intensity_layout.addWidget(QLabel("Desired Reference Intensity:"))
        self.desired_intensity_input = QDoubleSpinBox()
        self.desired_intensity_input.setRange(0.0001, 1e6)
        self.desired_intensity_input.setValue(1.0)
        desired_intensity_layout.addWidget(self.desired_intensity_input)
        self.layout.addLayout(desired_intensity_layout)

        # Connect signals for validation
        self.ref_peak_input.textChanged.connect(self.validate_inputs)
        self.desired_intensity_input.valueChanged.connect(self.validate_inputs)

        self.setLayout(self.layout)

        # **Invoke validation upon initialization**
        self.validate_inputs()

    def show_help(self):
        help_content = REFERENCE_PEAK_NORMALIZATION_HELP
        dialog = HelpDialog("Reference Peak Normalization Help", help_content, self)
        dialog.exec_()

    def validate_inputs(self):
        ref_peak_text = self.ref_peak_input.text()
        desired_intensity = self.desired_intensity_input.value()

        try:
            ref_peak = float(ref_peak_text)
            if desired_intensity > 0:
                self.apply_button.setEnabled(True)
            else:
                self.apply_button.setEnabled(False)
        except ValueError:
            self.apply_button.setEnabled(False)

    def get_parameters(self):
        params = {}
        ref_peak_text = self.ref_peak_input.text()
        desired_intensity = self.desired_intensity_input.value()

        try:
            ref_peak = float(ref_peak_text)
            if desired_intensity <= 0:
                QMessageBox.warning(self, "Invalid Intensity", "Desired Reference Intensity must be greater than zero.")
                return None
            params['reference_peak_x'] = ref_peak
            params['desired_reference_intensity'] = desired_intensity
            return params
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid numerical value for the Reference Peak X-Value.")
            return None
###############################################################

class BaselineCorrectionNormalizationPanel(BaseNormalizationMethodPanel):
    def __init__(self, parent=None):
        super().__init__("Baseline Correction Normalization", parent)

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Help Button
        help_button = QPushButton("Help")
        help_icon = QIcon("gui/resources/help_icon.png")  # Use resource path
        help_button.setIcon(help_icon)
        help_button.clicked.connect(self.show_help)
        self.layout.addWidget(help_button)

        # Apply and Save Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")
        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        send_icon = QIcon(resource_path("gui/resources/send_icon.png"))
        self.send_to_data_panel_button.setIcon(send_icon)

        self.apply_button.setEnabled(False)   # Disabled until valid input
        self.save_button.setEnabled(False)    # Disabled by default
        self.send_to_data_panel_button.setEnabled(False)  # Disabled by default
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # Parameters for Baseline Correction
        self.layout.addWidget(QLabel("Baseline Correction Parameters:"))

        # Lambda Parameter
        lambda_layout = QHBoxLayout()
        lambda_layout.addWidget(QLabel("Lambda (λ):"))
        self.lambda_input = QLineEdit()
        self.lambda_input.setText("1e6")  # Default value
        lambda_layout.addWidget(self.lambda_input)
        self.layout.addLayout(lambda_layout)

        # Asymmetry Parameter
        p_layout = QHBoxLayout()
        p_layout.addWidget(QLabel("Asymmetry (p):"))
        self.p_input = QLineEdit()
        self.p_input.setText("0.01")  # Default value
        p_layout.addWidget(self.p_input)
        self.layout.addLayout(p_layout)

        # Number of Iterations
        niter_layout = QHBoxLayout()
        niter_layout.addWidget(QLabel("Iterations (niter):"))
        self.niter_input = QLineEdit()
        self.niter_input.setText("10")  # Default value
        niter_layout.addWidget(self.niter_input)
        self.layout.addLayout(niter_layout)

        # Connect input changes to validation
        self.lambda_input.textChanged.connect(self.validate_inputs)
        self.p_input.textChanged.connect(self.validate_inputs)
        self.niter_input.textChanged.connect(self.validate_inputs)

        self.setLayout(self.layout)

        # **Invoke validation upon initialization**
        self.validate_inputs()

    def show_help(self):
        help_content = BASELINE_CORRECTION_NORMALIZATION_HELP
        dialog = HelpDialog("Baseline Correction Normalization Help", help_content, self)
        dialog.exec_()

    def validate_inputs(self):
        try:
            lambda_val = float(self.lambda_input.text())
            p_val = float(self.p_input.text())
            niter_val = int(self.niter_input.text())
            if lambda_val <= 0 or not (0 < p_val < 1) or niter_val <= 0:
                self.apply_button.setEnabled(False)
            else:
                self.apply_button.setEnabled(True)
        except ValueError:
            self.apply_button.setEnabled(False)

    def get_parameters(self):
        try:
            lambda_val = float(self.lambda_input.text())
            p_val = float(self.p_input.text())
            niter_val = int(self.niter_input.text())
            if lambda_val <= 0 or not (0 < p_val < 1) or niter_val <= 0:
                QMessageBox.warning(self, "Invalid Parameters", "Please enter valid parameter values.")
                return None
            return {
                'lambda_': lambda_val,
                'p': p_val,
                'niter': niter_val
            }
        except ValueError:
            QMessageBox.warning(self, "Invalid Inputs", "Please enter numeric values for all parameters.")
            return None
        
#############################################################

class BaselineCorrectionWithFileNormalizationPanel(BaseNormalizationMethodPanel):
    def __init__(self, parent=None):
        super().__init__("Baseline Correction with File", parent)
        
        # Apply global stylesheet if applicable
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
        self.layout = QVBoxLayout()

        # Help Button
        help_button = QPushButton("Help")
        help_icon = QIcon(resource_path("gui/resources/help_icon.png"))
        help_button.setIcon(help_icon)
        help_button.clicked.connect(self.show_help)
        self.layout.addWidget(help_button)

        # Apply and Save Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")
        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        send_icon = QIcon(resource_path("gui/resources/send_icon.png"))
        self.send_to_data_panel_button.setIcon(send_icon)

        self.apply_button.setEnabled(False)   # Disabled until a file is selected
        self.save_button.setEnabled(False)    # Disabled until normalization is applied
        self.send_to_data_panel_button.setEnabled(False)  # Disabled until normalization is applied

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # File Selection for Reference Data
        self.layout.addWidget(QLabel("Select Reference File:"))
        file_selection_layout = QHBoxLayout()
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)
        self.choose_file_button = QPushButton("Choose File")
        self.choose_file_button.clicked.connect(self.choose_reference_file)
        file_selection_layout.addWidget(self.file_path_display)
        file_selection_layout.addWidget(self.choose_file_button)
        self.layout.addLayout(file_selection_layout)

        self.setLayout(self.layout)

        # Connect signals
        self.file_path_display.textChanged.connect(self.validate_inputs)

    def show_help(self):
        help_content = "Help content for Baseline Correction with File."
        dialog = HelpDialog("Baseline Correction with File Help", help_content, self)
        dialog.exec_()

    def choose_reference_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Reference File",
            "",
            "Data Files (*.csv *.txt);;All Files (*)"
        )
        if file_path:
            self.file_path_display.setText(file_path)
            self.validate_inputs()

    def validate_inputs(self):
        if self.file_path_display.text():
            self.apply_button.setEnabled(True)
        else:
            self.apply_button.setEnabled(False)

    def get_parameters(self):
        params = {}
        reference_file_path = self.file_path_display.text()
        if not os.path.isfile(reference_file_path):
            QMessageBox.warning(self, "Invalid File", "Please select a valid reference file.")
            return None
        params['reference_file_path'] = reference_file_path
        return params


##############################################################
class DatasetSelectionDialog(QDialog):
    def __init__(self, structure, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Datasets")
        self.structure = structure
        self.selected_datasets = []
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Instruction Label
        instruction_label = QLabel("Select the datasets to combine:")
        self.layout.addWidget(instruction_label)
        
        # List Widget with Checkboxes
        self.list_widget = QListWidget()
        for dataset_name in sorted(self.structure.keys()):
            item = QListWidgetItem(dataset_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)
        self.layout.addWidget(self.list_widget)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(buttons_layout)
        
        # Connections
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def accept(self):
        self.selected_datasets = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.checkState() == Qt.Checked:
                self.selected_datasets.append(item.text())
        
        if not self.selected_datasets:
            QMessageBox.warning(self, "No Datasets Selected", "Please select at least one dataset.")
            return  # Do not close the dialog
        
        super().accept()
    
    def get_selected_datasets(self):
        return self.selected_datasets


class AxisDetailsPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Axis Details", parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout()

        self.layout.addWidget(QLabel("Title Label (LaTeX):"), 0, 0)
        self.title_name_input = QLineEdit()
        self.layout.addWidget(self.title_name_input, 0, 1, 1, 2)

        self.layout.addWidget(QLabel("X-axis Label (LaTeX):"), 1, 0)
        self.x_axis_input = QLineEdit()
        self.layout.addWidget(self.x_axis_input, 1, 1, 1, 2)

        self.layout.addWidget(QLabel("Y-axis Label (LaTeX):"), 2, 0)
        self.y_axis_input = QLineEdit()
        self.layout.addWidget(self.y_axis_input, 2, 1, 1, 2)

        self.layout.addWidget(QLabel("X-axis Range (min, max):"), 3, 0)
        self.x_min_input = QLineEdit()
        self.x_max_input = QLineEdit()
        self.layout.addWidget(self.x_min_input, 3, 1)
        self.layout.addWidget(self.x_max_input, 3, 2)

        self.layout.addWidget(QLabel("Y-axis Range (min, max):"), 4, 0)
        self.y_min_input = QLineEdit()
        self.y_max_input = QLineEdit()
        self.layout.addWidget(self.y_min_input, 4, 1)
        self.layout.addWidget(self.y_max_input, 4, 2)

        self.layout.addWidget(QLabel("Axis Font Size:"), 5, 0)
        self.axis_font_size_input = QSpinBox()
        self.axis_font_size_input.setRange(8, 32)
        self.axis_font_size_input.setValue(12)
        self.layout.addWidget(self.axis_font_size_input, 5, 1)

        self.layout.addWidget(QLabel("Title Font Size:"), 6, 0)
        self.title_font_size_input = QSpinBox()
        self.title_font_size_input.setRange(8, 32)
        self.title_font_size_input.setValue(14)
        self.layout.addWidget(self.title_font_size_input, 6, 1)

        self.layout.addWidget(QLabel("Legend Font Size:"), 7, 0)
        self.legend_font_size_input = QSpinBox()
        self.legend_font_size_input.setRange(8, 32)
        self.legend_font_size_input.setValue(10)
        self.layout.addWidget(self.legend_font_size_input, 7, 1)

        self.setLayout(self.layout)

    def get_axis_details(self):
        return {
            'title': self.title_name_input.text(),
            'x_label': self.x_axis_input.text(),
            'y_label': self.y_axis_input.text(),
            'x_min': self.x_min_input.text(),
            'x_max': self.x_max_input.text(),
            'y_min': self.y_min_input.text(),
            'y_max': self.y_max_input.text(),
            'axis_font_size': self.axis_font_size_input.value(),
            'title_font_size': self.title_font_size_input.value(),
            'legend_font_size': self.legend_font_size_input.value(),
        }


class AdditionalTextPanel(QGroupBox):
    color_changed = pyqtSignal(str)  # Signal to emit the new color

    def __init__(self, parent=None):
        super().__init__("Additional Text", parent)
        self.text_color = 'black'  # Default text color
        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout()

        self.layout.addWidget(QLabel("Text (LaTeX):"), 0, 0)
        self.additional_text_input = QLineEdit()
        self.layout.addWidget(self.additional_text_input, 0, 1, 1, 2)

        self.layout.addWidget(QLabel("X Position:"), 1, 0)
        self.text_x_position = QLineEdit()
        self.layout.addWidget(self.text_x_position, 1, 1)

        self.layout.addWidget(QLabel("Y Position:"), 2, 0)
        self.text_y_position = QLineEdit()
        self.layout.addWidget(self.text_y_position, 2, 1)

        self.layout.addWidget(QLabel("Text Size:"), 3, 0)
        self.text_size_input = QSpinBox()
        self.text_size_input.setRange(8, 32)
        self.text_size_input.setValue(12)
        self.layout.addWidget(self.text_size_input, 3, 1)

        self.layout.addWidget(QLabel("Text Color:"), 4, 0)
        self.text_color_button = QPushButton("Choose Color")
        self.layout.addWidget(self.text_color_button, 4, 1)

        # Add a QLabel to display the selected color
        self.color_display = QLabel()
        self.color_display.setFixedSize(30, 30)
        self.color_display.setStyleSheet(f"background-color: {self.text_color}; border: 1px solid black;")
        self.layout.addWidget(self.color_display, 4, 2)

        self.add_text_button = QPushButton("Add to Plot")
        self.delete_text_button = QPushButton("Delete from Plot")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_text_button)
        button_layout.addWidget(self.delete_text_button)

        self.layout.addLayout(button_layout, 5, 0, 1, 3)

        self.setLayout(self.layout)

        # Connections for choosing color
        self.text_color_button.clicked.connect(self.choose_text_color)

    def get_text_details(self):
        return {
            'text': self.additional_text_input.text(),
            'x_pos': self.text_x_position.text(),
            'y_pos': self.text_y_position.text(),
            'size': self.text_size_input.value(),
            'color': self.text_color
        }

    def set_text_color(self, color):
        self.text_color = color

    def choose_text_color(self):
        color = QColorDialog.getColor(initial=QColor(self.text_color), parent=self, title="Select Text Color")
        if color.isValid():
            self.set_text_color(color.name())
            # Update the color display label
            self.color_display.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            # Emit the signal with the new color
            self.color_changed.emit(color.name())
        else:
            QMessageBox.information(self, "Color Selection Cancelled", "No color was selected.")


class CustomAnnotationsPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Custom Annotations", parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.annotation_type_combo = QComboBox()
        self.annotation_type_combo.addItems(["None", "Annotation Point", "Vertical Line", "Horizontal Line"])
        self.layout.addWidget(self.annotation_type_combo)

        self.apply_changes_button = QPushButton("Apply All Changes")
        self.layout.addWidget(self.apply_changes_button)

        self.calculate_distance_button = QPushButton("Calculate Distance")
        self.layout.addWidget(self.calculate_distance_button)

        self.setLayout(self.layout)

    def get_annotation_type(self):
        return self.annotation_type_combo.currentText()


class PlotVisualsPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Plot Visuals", parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel("Plot Type:"))
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(["Line", "Bar", "Scatter", "Histogram", "Pie"])
        self.layout.addWidget(self.plot_type_combo)

        self.add_grid_checkbox = QCheckBox("Add Grid")
        self.layout.addWidget(self.add_grid_checkbox)

        self.add_sub_grid_checkbox = QCheckBox("Add Sub-Grid")
        self.layout.addWidget(self.add_sub_grid_checkbox)

        self.layout.addWidget(QLabel("Plot Style:"))
        self.plot_style_combo = QComboBox()
        self.plot_style_combo.addItems([
            "Default", "full_grid", "seaborn", "ggplot", "fivethirtyeight",
            "dark_background", "grayscale", "tableau-colorblind10", "classic"
        ])
        self.layout.addWidget(self.plot_style_combo)

        self.apply_legends_checkbox = QCheckBox("Apply Legends")
        self.layout.addWidget(self.apply_legends_checkbox)

        self.setLayout(self.layout)

    def get_plot_visuals(self):
        return {
            'plot_type': self.plot_type_combo.currentText(),
            'add_grid': self.add_grid_checkbox.isChecked(),
            'add_sub_grid': self.add_sub_grid_checkbox.isChecked(),
            'plot_style': self.plot_style_combo.currentText(),
            'apply_legends': self.apply_legends_checkbox.isChecked(),
        }


class PlotDetailsPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Plot Details", parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel("X-axis Column #:"))
        self.x_axis_col_input = QLineEdit()
        self.layout.addWidget(self.x_axis_col_input)

        self.layout.addWidget(QLabel("Y-axis Column #:"))
        self.y_axis_col_input = QLineEdit()
        self.layout.addWidget(self.y_axis_col_input)

        self.layout.addWidget(QLabel("Line Style:"))
        self.line_style_combo = QComboBox()
        self.line_style_combo.addItems(["Solid", "Dashed", "Dash-Dot"])
        self.layout.addWidget(self.line_style_combo)

        self.layout.addWidget(QLabel("Point Style:"))
        self.point_style_combo = QComboBox()
        self.point_style_combo.addItems(["None", "Circle", "Square", "Triangle Up", "Triangle Down", "Star", "Plus", "Cross"])
        self.layout.addWidget(self.point_style_combo)

        self.layout.addWidget(QLabel("Line Thickness:"))
        self.line_thickness_combo = QComboBox()
        self.line_thickness_combo.addItems(["1", "2", "3", "4", "5"])
        self.layout.addWidget(self.line_thickness_combo)

        self.layout.addWidget(QLabel("Scale Type:"))
        self.scale_type_combo = QComboBox()
        self.scale_type_combo.addItems(["Linear", "Logarithmic X-axis", "Logarithmic Y-axis", "Logarithmic Both Axes"])
        self.layout.addWidget(self.scale_type_combo)

        self.setLayout(self.layout)

    def get_plot_details(self):
        return {
            'x_axis_col': self.x_axis_col_input.text(),
            'y_axis_col': self.y_axis_col_input.text(),
            'line_style': self.line_style_combo.currentText(),
            'point_style': self.point_style_combo.currentText(),
            'line_thickness': self.line_thickness_combo.currentText(),
            'scale_type': self.scale_type_combo.currentText(),
        }

class NormalizationMethodPanel(QWidget):
    def __init__(self, method_name, parent=None):
        super().__init__(parent)
        self.method_name = method_name
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        # 1. Help Button
        help_button = QPushButton("Help")
        help_icon = QIcon("gui/resources/help_icon.png")  # Use resource path
        help_button.setIcon(help_icon)
        help_button.clicked.connect(self.show_help)
        self.layout.addWidget(help_button)

        # 2. Apply and Save Buttons (Created Before Method-Specific UI)
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")
        self.apply_button.setEnabled(False)  # Initially disabled
        self.save_button.setEnabled(False)   # Initially disabled
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        self.layout.addLayout(button_layout)

        # 3. Method-Specific UI
        if self.method_name == "Min-Max Normalization":
            self.init_min_max_normalization_ui()
        else:
            self.layout.addWidget(QLabel("No normalization methods available."))

        self.setLayout(self.layout)

    def show_help(self):
        explanations = {
            "Min-Max Normalization": "Rescales data to a fixed range, typically [0, 1].",
            # Add explanations for other methods here when implemented
        }
        explanation = explanations.get(self.method_name, "No explanation available.")
        QMessageBox.information(self, f"{self.method_name} Help", explanation)

    def get_parameters(self):
        # Return method-specific parameters
        params = {}
        if self.method_name == "Min-Max Normalization":
            params['use_custom'] = self.use_custom_range_checkbox.isChecked()
            if params['use_custom']:
                custom_min = self.custom_min_spinbox.value()
                custom_max = self.custom_max_spinbox.value()
                if custom_max <= custom_min:
                    QMessageBox.warning(self, "Invalid Range", "Custom Max must be greater than Custom Min.")
                    return None
                params['custom_min'] = custom_min
                params['custom_max'] = custom_max
            else:
                params['custom_min'] = None
                params['custom_max'] = None
        else:
            pass  # Other methods may not require extra parameters
        return params

    def init_min_max_normalization_ui(self):
        # Checkbox to toggle custom min-max values
        self.use_custom_range_checkbox = QCheckBox("Use custom min-max values")
        self.layout.addWidget(self.use_custom_range_checkbox)

        # Layout for custom min and max spin boxes
        custom_range_layout = QHBoxLayout()
        custom_range_layout.addWidget(QLabel("Min:"))
        self.custom_min_spinbox = QDoubleSpinBox()
        self.custom_min_spinbox.setEnabled(False)
        self.custom_min_spinbox.setRange(-1e6, 1e6)
        self.custom_min_spinbox.setValue(0.0)  # Default min
        custom_range_layout.addWidget(self.custom_min_spinbox)

        custom_range_layout.addWidget(QLabel("Max:"))
        self.custom_max_spinbox = QDoubleSpinBox()
        self.custom_max_spinbox.setEnabled(False)
        self.custom_max_spinbox.setRange(-1e6, 1e6)
        self.custom_max_spinbox.setValue(1.0)  # Default max
        custom_range_layout.addWidget(self.custom_max_spinbox)

        self.layout.addLayout(custom_range_layout)

        # Connect the checkbox to enable/disable spin boxes
        self.use_custom_range_checkbox.stateChanged.connect(self.toggle_custom_range)

        # Connect spin boxes to enable Apply button
        self.custom_min_spinbox.valueChanged.connect(self.enable_apply_button)
        self.custom_max_spinbox.valueChanged.connect(self.enable_apply_button)

        # **Bug Fix: Enable Apply Button by Default**
        # If "Use custom min-max values" is unchecked, Apply should be enabled
        self.apply_button.setEnabled(True)

    def toggle_custom_range(self, state):
        enabled = state == Qt.Checked
        self.custom_min_spinbox.setEnabled(enabled)
        self.custom_max_spinbox.setEnabled(enabled)
        self.save_button.setEnabled(False)  # Disable Save until normalization is applied

        if not enabled:
            # If not using custom range, ensure Apply is enabled
            self.apply_button.setEnabled(True)
        else:
            # If using custom range, validate inputs before enabling Apply
            self.enable_apply_button()

    def enable_apply_button(self):
        if self.method_name == "Min-Max Normalization":
            if self.use_custom_range_checkbox.isChecked():
                custom_min = self.custom_min_spinbox.value()
                custom_max = self.custom_max_spinbox.value()
                if custom_max > custom_min:
                    self.apply_button.setEnabled(True)
                else:
                    self.apply_button.setEnabled(False)
            else:
                # If not using custom range, Apply should be enabled
                self.apply_button.setEnabled(True)
        else:
            self.apply_button.setEnabled(True)

class GeneratedCSVFilesPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Generated CSV Files", parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Draggable and Selectable List Widget for CSV Files
        self.csv_files_list = DraggableListWidget()
        self.layout.addWidget(self.csv_files_list)

        # Buttons for Managing CSV Files
        buttons_layout = QHBoxLayout()
        self.delete_csv_button = QPushButton("Delete Selected CSV Files")
        self.delete_csv_button.setIcon(QIcon('gui/resources/delete_icon.png'))  # Ensure the icon exists
        self.delete_csv_button.clicked.connect(self.delete_selected_csv_files)
        buttons_layout.addWidget(self.delete_csv_button)
        buttons_layout.addStretch()
        self.layout.addLayout(buttons_layout)

    def add_csv_file(self, csv_file_path):
        file_name = os.path.basename(csv_file_path)
        item = QListWidgetItem(file_name)
        item.setData(Qt.UserRole, csv_file_path)
        item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.csv_files_list.add_file_to_panel(csv_file_path)

    def get_selected_csv_files(self):
        selected_items = [
            item for item in self.csv_files_list.findItems("*", Qt.MatchWildcard)
            if item.checkState() == Qt.Checked
        ]
        return [item.data(Qt.UserRole) for item in selected_items]

    def delete_selected_csv_files(self):
        selected_items = self.csv_files_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "No CSV files selected to delete.")
            return
        reply = QMessageBox.question(
            self, 'Confirm Deletion',
            f"Are you sure you want to delete the selected {len(selected_items)} CSV file(s)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for item in selected_items:
                csv_file_path = item.data(Qt.UserRole)
                try:
                    os.remove(csv_file_path)
                except Exception as e:
                    QMessageBox.warning(self, "Deletion Error", f"Failed to delete {csv_file_path}:\n{e}")
                    continue
                self.csv_files_list.takeItem(self.csv_files_list.row(item))
            QMessageBox.information(self, "Deletion Successful", f"Deleted {len(selected_items)} CSV file(s).")

class DatasetSelectionExportPanel(QGroupBox):
    def __init__(self, selected_data_panel, h5_handling_panel, parent=None):
        super().__init__("Dataset Selection and Export", parent)
        self.selected_data_panel = selected_data_panel
        self.h5_handling_panel = h5_handling_panel
        self.init_ui()
        self.selected_datasets = []

    def init_ui(self):
        layout = QVBoxLayout()

        # Instruction Label
        instruction_label = QLabel("Select Datasets to Combine into CSV:")
        layout.addWidget(instruction_label)

        # Select Datasets Button
        self.select_datasets_button = QPushButton("Select Datasets")
        self.select_datasets_button.setIcon(QIcon('gui/resources/select_datasets_icon.png'))  # Ensure the icon exists
        layout.addWidget(self.select_datasets_button)

        # Combine and Export Button
        self.combine_export_button = QPushButton("Combine and Export")
        self.combine_export_button.setIcon(QIcon('gui/resources/combine_export_icon.png'))  # Ensure the icon exists
        self.combine_export_button.setEnabled(False)  # Disabled until datasets are selected
        layout.addWidget(self.combine_export_button)

        # Add to Selected Data Panel Checkbox
        self.add_to_selected_checkbox = QCheckBox("Add CSV to Selected Data Panel")
        self.add_to_selected_checkbox.setChecked(True)
        layout.addWidget(self.add_to_selected_checkbox)

        # Spacer
        layout.addStretch()

        self.setLayout(layout)

        # Connections
        self.select_datasets_button.clicked.connect(self.open_dataset_selection_dialog)
        self.combine_export_button.clicked.connect(self.combine_and_export_datasets)

    def open_dataset_selection_dialog(self):
        # Ensure that H5 files have been processed
        if not hasattr(self.h5_handling_panel, 'h5_files') or not self.h5_handling_panel.h5_files:
            QMessageBox.warning(self, "No H5 Files Processed", "Please process H5 files before selecting datasets.")
            return

        # Use the structure from the first H5 file (since all are consistent)
        structure = self.h5_handling_panel.structures[0]

        # Show the structure and get selected datasets
        selected_datasets = self.show_structure_and_get_datasets(structure)
        if selected_datasets:
            self.selected_datasets = selected_datasets
            self.combine_export_button.setEnabled(True)
        else:
            self.selected_datasets = []
            self.combine_export_button.setEnabled(False)

    def show_structure_and_get_datasets(self, structure):
        # Display the structure and allow the user to select datasets
        dialog = DatasetSelectionDialog(structure, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_datasets = dialog.get_selected_datasets()
            return selected_datasets
        else:
            return []

    def combine_and_export_datasets(self):
        if not self.selected_datasets:
            QMessageBox.warning(self, "No Datasets Selected", "Please select at least one dataset to combine.")
            return

        # Get H5 files to process
        h5_files = self.h5_handling_panel.h5_files
        if not h5_files:
            QMessageBox.warning(self, "No H5 Files Processed", "Please process H5 files before exporting datasets.")
            return

        # Initialize list to store CSV file paths
        csv_files = []

        # Process each H5 file
        for file in h5_files:
            try:
                with h5py.File(file, 'r') as h5_file:
                    data = self.extract_datasets(h5_file, self.selected_datasets)

                # Combine datasets into a single CSV
                combined_csv = self.combine_datasets_to_csv(data, file)
                csv_files.append(combined_csv)

                # If add to selected data panel is checked, add CSV to the panel
                if self.add_to_selected_checkbox.isChecked():
                    self.selected_data_panel.add_file_to_panel([combined_csv])

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to process H5 file {file}:\n{e}")
                continue  # Proceed to next file

        if csv_files:
            QMessageBox.information(self, "Export Complete", "Selected datasets have been combined and exported as CSV files.")
            # Optionally, enable sending to tabs
            self.parent().send_to_tabs_group.setEnabled(True)
        else:
            QMessageBox.warning(self, "No CSV Created", "No CSV files were created.")

    def extract_datasets(self, h5_file, datasets):
        # Extract selected datasets
        data = {}
        for dataset_name in datasets:
            data[dataset_name] = h5_file[dataset_name][:]
        return data

    def combine_datasets_to_csv(self, data, h5_file_path):
        # Combine datasets into a DataFrame
        df = pd.DataFrame()
        for dataset_name, values in data.items():
            # Handle datasets based on dimensions
            if values.ndim == 1:
                df[dataset_name] = values
            elif values.ndim == 2:
                # For 2D datasets, flatten columns
                for i in range(values.shape[1]):
                    col_name = f"{dataset_name}_{i}"
                    df[col_name] = values[:, i]
            else:
                # Skip datasets with higher dimensions
                continue

        # Define the CSV file path
        base_name = os.path.splitext(os.path.basename(h5_file_path))[0]
        csv_file_name = f"{base_name}_combined.csv"
        csv_file_path = os.path.join(os.path.dirname(h5_file_path), csv_file_name)

        # Save DataFrame to CSV
        df.to_csv(csv_file_path, index=False)
        return csv_file_path

    def extract_datasets(self, h5_file, datasets):
        # Extract selected datasets
        data = {}
        for dataset_name in datasets:
            if dataset_name in h5_file:
                data[dataset_name] = h5_file[dataset_name][:]
            else:
                raise KeyError(f"Dataset {dataset_name} not found in H5 file.")
        return data
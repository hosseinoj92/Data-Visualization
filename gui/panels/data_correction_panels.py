#gui/panels data_correction_panles.py

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QLabel, 
    QDoubleSpinBox, QLineEdit, QSpinBox, QFileDialog,
    QMessageBox,QListWidgetItem, QGroupBox,QWidget, QComboBox, 
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os
import sys
from gui.dialogs.help_dialog import HelpDialog
from gui.utils.help_content import (
                              NOISE_REDUCTION, UNIT_CONVERTER_HELP,
                                SHIFT_BASELINE_HELP, DATA_CUTTING_HELP
                              )




def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



class CorrectMissingDataPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Correct Missing Data"
        self.init_ui()

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

        self.apply_button.setEnabled(True)   # Enabled by default
        self.save_button.setEnabled(False)   # Disabled until applied
        self.send_to_data_panel_button.setEnabled(False)  # Disabled until applied

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # Add "Apply for Batch" checkbox
        self.apply_for_batch_checkbox = QCheckBox("Apply for Batch")
        self.apply_for_batch_checkbox.stateChanged.connect(self.toggle_batch_mode)
        self.layout.addWidget(self.apply_for_batch_checkbox)

        # Batch mode X and Y column input
        batch_layout = QHBoxLayout()
        self.batch_x_label = QLabel("X Column:")
        self.batch_x_spinbox = QSpinBox()
        self.batch_x_spinbox.setRange(1, 100)
        self.batch_x_spinbox.setEnabled(False)

        self.batch_y_label = QLabel("Y Column:")
        self.batch_y_spinbox = QSpinBox()
        self.batch_y_spinbox.setRange(1, 100)
        self.batch_y_spinbox.setEnabled(False)

        batch_layout.addWidget(self.batch_x_label)
        batch_layout.addWidget(self.batch_x_spinbox)
        batch_layout.addWidget(self.batch_y_label)
        batch_layout.addWidget(self.batch_y_spinbox)

        self.layout.addLayout(batch_layout)

        # Add X and Y column selection
        self.layout.addWidget(QLabel("Select X and Y Columns:"))
        x_y_layout = QHBoxLayout()
        self.x_column_combo = QComboBox()
        self.y_column_combo = QComboBox()
        x_y_layout.addWidget(QLabel("X Column:"))
        x_y_layout.addWidget(self.x_column_combo)
        x_y_layout.addWidget(QLabel("Y Column:"))
        x_y_layout.addWidget(self.y_column_combo)
        self.layout.addLayout(x_y_layout)

        # Options for Handling Missing Data
        self.layout.addWidget(QLabel("Choose how to handle missing data:"))

        self.method_combo = QComboBox()
        self.method_combo.addItems(["Remove Rows with Missing Data", "Replace with Mean", "Replace with Median"])
        self.layout.addWidget(self.method_combo)

        self.setLayout(self.layout)

    def toggle_batch_mode(self, state):
        is_checked = (state == Qt.Checked)
        self.batch_x_spinbox.setEnabled(is_checked)
        self.batch_y_spinbox.setEnabled(is_checked)
        self.batch_x_label.setEnabled(is_checked)
        self.batch_y_label.setEnabled(is_checked)
        # Disable x_column_combo and y_column_combo when batch mode is enabled
        self.x_column_combo.setEnabled(not is_checked)
        self.y_column_combo.setEnabled(not is_checked)

    def set_data_columns(self, columns):
        self.x_column_combo.clear()
        self.x_column_combo.addItems(columns)
        self.y_column_combo.clear()
        self.y_column_combo.addItems(columns)


    def show_help(self):
        help_content = (
            "This method allows you to handle missing data (NaN values) in your datasets.\n\n"
            "Options:\n"
            "- Remove Rows with Missing Data: Deletes any row that contains a missing value.\n"
            "- Replace with Mean: Replaces missing values with the mean of the column.\n"
            "- Replace with Median: Replaces missing values with the median of the column."
        )
        dialog = HelpDialog("Correct Missing Data Help", help_content, self)
        dialog.exec_()


    def get_parameters(self):
        params = {
            'method': self.method_combo.currentText(),
            'apply_for_batch': self.apply_for_batch_checkbox.isChecked(),
        }
        if self.apply_for_batch_checkbox.isChecked():
            params['x_column_index'] = self.batch_x_spinbox.value() - 1  # zero-based index
            params['y_column_index'] = self.batch_y_spinbox.value() - 1  # zero-based index
        else:
            params['x_column'] = self.x_column_combo.currentText()
            params['y_column'] = self.y_column_combo.currentText()
        return params


class NoiseReductionPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Noise Reduction"
        self.init_ui()

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

        self.apply_button.setEnabled(True)   # Enabled by default
        self.save_button.setEnabled(False)   # Disabled until applied
        self.send_to_data_panel_button.setEnabled(False)  # Disabled until applied

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # Add "Apply for Batch" checkbox
        self.apply_for_batch_checkbox = QCheckBox("Apply for Batch")
        self.apply_for_batch_checkbox.stateChanged.connect(self.toggle_batch_mode)
        self.layout.addWidget(self.apply_for_batch_checkbox)

        # Batch mode X and Y column input
        batch_layout = QHBoxLayout()
        self.batch_x_label = QLabel("X Column:")
        self.batch_x_spinbox = QSpinBox()
        self.batch_x_spinbox.setRange(1, 100)
        self.batch_x_spinbox.setEnabled(False)

        self.batch_y_label = QLabel("Y Column:")
        self.batch_y_spinbox = QSpinBox()
        self.batch_y_spinbox.setRange(1, 100)
        self.batch_y_spinbox.setEnabled(False)

        batch_layout.addWidget(self.batch_x_label)
        batch_layout.addWidget(self.batch_x_spinbox)
        batch_layout.addWidget(self.batch_y_label)
        batch_layout.addWidget(self.batch_y_spinbox)

        self.layout.addLayout(batch_layout)

        # Add X and Y column selection
        self.layout.addWidget(QLabel("Select X and Y Columns:"))
        x_y_layout = QHBoxLayout()
        self.x_column_combo = QComboBox()
        self.y_column_combo = QComboBox()
        x_y_layout.addWidget(QLabel("X Column:"))
        x_y_layout.addWidget(self.x_column_combo)
        x_y_layout.addWidget(QLabel("Y Column:"))
        x_y_layout.addWidget(self.y_column_combo)
        self.layout.addLayout(x_y_layout)

        # Options for Noise Reduction
        self.layout.addWidget(QLabel("Choose a noise reduction method:"))

        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Moving Average Smoothing",
            "Savitzky-Golay Filter",
            "Wavelet Denoising"
        ])
        self.layout.addWidget(self.method_combo)

        # Parameters area
        self.parameters_layout = QVBoxLayout()
        self.layout.addLayout(self.parameters_layout)

        # Initialize parameters for each method
        self.init_parameters()

        # Connect method selection change
        self.method_combo.currentIndexChanged.connect(self.on_method_change)

        self.setLayout(self.layout)

    def toggle_batch_mode(self, state):
        is_checked = (state == Qt.Checked)
        self.batch_x_spinbox.setEnabled(is_checked)
        self.batch_y_spinbox.setEnabled(is_checked)
        self.batch_x_label.setEnabled(is_checked)
        self.batch_y_label.setEnabled(is_checked)
        # Disable x_column_combo and y_column_combo when batch mode is enabled
        self.x_column_combo.setEnabled(not is_checked)
        self.y_column_combo.setEnabled(not is_checked)

    def set_data_columns(self, columns):
        self.x_column_combo.clear()
        self.x_column_combo.addItems(columns)
        self.y_column_combo.clear()
        self.y_column_combo.addItems(columns)


    def init_parameters(self):
        self.parameter_widgets = {}

        # Moving Average Smoothing Parameters
        moving_avg_layout = QHBoxLayout()
        moving_avg_layout.addWidget(QLabel("Window Size:"))
        self.ma_window_size_spin = QSpinBox()
        self.ma_window_size_spin.setRange(1, 100)
        self.ma_window_size_spin.setValue(5)
        moving_avg_layout.addWidget(self.ma_window_size_spin)
        self.parameter_widgets["Moving Average Smoothing"] = moving_avg_layout

        # Savitzky-Golay Filter Parameters
        savgol_layout = QHBoxLayout()
        savgol_layout.addWidget(QLabel("Window Size:"))
        self.sg_window_size_spin = QSpinBox()
        self.sg_window_size_spin.setRange(3, 101)
        self.sg_window_size_spin.setSingleStep(2)
        self.sg_window_size_spin.setValue(5)
        savgol_layout.addWidget(self.sg_window_size_spin)

        savgol_layout.addWidget(QLabel("Polynomial Order:"))
        self.sg_poly_order_spin = QSpinBox()
        self.sg_poly_order_spin.setRange(1, 10)
        self.sg_poly_order_spin.setValue(2)
        savgol_layout.addWidget(self.sg_poly_order_spin)
        self.parameter_widgets["Savitzky-Golay Filter"] = savgol_layout

        # Wavelet Denoising Parameters
        wavelet_layout = QHBoxLayout()
        wavelet_layout.addWidget(QLabel("Wavelet:"))
        self.wavelet_combo = QComboBox()
        self.wavelet_combo.addItems(["db1", "db2", "db4", "sym5", "coif1"])
        wavelet_layout.addWidget(self.wavelet_combo)

        wavelet_layout.addWidget(QLabel("Level:"))
        self.wavelet_level_spin = QSpinBox()
        self.wavelet_level_spin.setRange(1, 10)
        self.wavelet_level_spin.setValue(1)
        wavelet_layout.addWidget(self.wavelet_level_spin)
        self.parameter_widgets["Wavelet Denoising"] = wavelet_layout

        # Display initial parameters
        self.on_method_change()

    def on_method_change(self):
        # Clear existing parameter widgets
        for i in reversed(range(self.parameters_layout.count())):
            widget = self.parameters_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Add parameter widgets for the selected method
        method = self.method_combo.currentText()
        if method in self.parameter_widgets:
            self.parameters_layout.addLayout(self.parameter_widgets[method])

    def show_help(self):
        help_content = NOISE_REDUCTION
        dialog = HelpDialog("Noise Reduction Help", help_content, self)
        dialog.exec_()


    def get_parameters(self):
        method = self.method_combo.currentText()
        params = {'method': method, 'apply_for_batch': self.apply_for_batch_checkbox.isChecked()}

        if self.apply_for_batch_checkbox.isChecked():
            params['x_column_index'] = self.batch_x_spinbox.value() - 1  # Zero-based index
            params['y_column_index'] = self.batch_y_spinbox.value() - 1  # Zero-based index
        else:
            params['x_column'] = self.x_column_combo.currentText()
            params['y_column'] = self.y_column_combo.currentText()

        if method == "Moving Average Smoothing":
            window_size = self.ma_window_size_spin.value()
            if window_size < 1:
                QMessageBox.warning(self, "Invalid Parameter", "Window size must be at least 1.")
                return None
            params['window_size'] = window_size

        elif method == "Savitzky-Golay Filter":
            window_size = self.sg_window_size_spin.value()
            poly_order = self.sg_poly_order_spin.value()
            if window_size % 2 == 0 or window_size < 3:
                QMessageBox.warning(self, "Invalid Parameter", "Window size must be an odd number greater than or equal to 3.")
                return None
            if poly_order >= window_size:
                QMessageBox.warning(self, "Invalid Parameter", "Polynomial order must be less than window size.")
                return None
            params['window_size'] = window_size
            params['poly_order'] = poly_order

        elif method == "Wavelet Denoising":
            wavelet = self.wavelet_combo.currentText()
            level = self.wavelet_level_spin.value()
            params['wavelet'] = wavelet
            params['level'] = level

        return params
    
class UnitConverterPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Unit Converter"
        self.init_ui()

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

        self.apply_button.setEnabled(True)   # Enabled by default
        self.save_button.setEnabled(False)   # Disabled until applied
        self.send_to_data_panel_button.setEnabled(False)  # Disabled until applied

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # Add "Apply for Batch" checkbox
        self.apply_for_batch_checkbox = QCheckBox("Apply for Batch")
        self.apply_for_batch_checkbox.stateChanged.connect(self.toggle_batch_mode)
        self.layout.addWidget(self.apply_for_batch_checkbox)

        # Batch mode X and Y column input
        batch_layout = QHBoxLayout()
        self.batch_x_label = QLabel("X Column:")
        self.batch_x_spinbox = QSpinBox()
        self.batch_x_spinbox.setRange(1, 100)
        self.batch_x_spinbox.setEnabled(False)

        self.batch_y_label = QLabel("Y Column:")
        self.batch_y_spinbox = QSpinBox()
        self.batch_y_spinbox.setRange(1, 100)
        self.batch_y_spinbox.setEnabled(False)

        batch_layout.addWidget(self.batch_x_label)
        batch_layout.addWidget(self.batch_x_spinbox)
        batch_layout.addWidget(self.batch_y_label)
        batch_layout.addWidget(self.batch_y_spinbox)

        self.layout.addLayout(batch_layout)

        # Add X and Y column selection
        self.layout.addWidget(QLabel("Select X and Y Columns:"))
        x_y_layout = QHBoxLayout()
        self.x_column_combo = QComboBox()
        self.y_column_combo = QComboBox()
        x_y_layout.addWidget(QLabel("X Column:"))
        x_y_layout.addWidget(self.x_column_combo)
        x_y_layout.addWidget(QLabel("Y Column:"))
        x_y_layout.addWidget(self.y_column_combo)
        self.layout.addLayout(x_y_layout)

        # Instructions
        instructions = QLabel("Enter formulas to convert units for X and Y axes. Use 'x' or 'y' as variables.")
        instructions.setWordWrap(True)
        self.layout.addWidget(instructions)

        # Formula input for X-axis
        self.layout.addWidget(QLabel("X-axis Conversion Formula:"))
        self.x_formula_input = QLineEdit()
        self.x_formula_input.setPlaceholderText("e.g., x * 1000")
        self.layout.addWidget(self.x_formula_input)

        # Formula input for Y-axis
        self.layout.addWidget(QLabel("Y-axis Conversion Formula:"))
        self.y_formula_input = QLineEdit()
        self.y_formula_input.setPlaceholderText("e.g., y / 2")
        self.layout.addWidget(self.y_formula_input)

        self.setLayout(self.layout)


    def toggle_batch_mode(self, state):
        is_checked = (state == Qt.Checked)
        self.batch_x_spinbox.setEnabled(is_checked)
        self.batch_y_spinbox.setEnabled(is_checked)
        self.batch_x_label.setEnabled(is_checked)
        self.batch_y_label.setEnabled(is_checked)
        # Disable x_column_combo and y_column_combo when batch mode is enabled
        self.x_column_combo.setEnabled(not is_checked)
        self.y_column_combo.setEnabled(not is_checked)

    def set_data_columns(self, columns):
        self.x_column_combo.clear()
        self.x_column_combo.addItems(columns)
        self.y_column_combo.clear()
        self.y_column_combo.addItems(columns)


    def show_help(self):
        help_content = UNIT_CONVERTER_HELP
        dialog = HelpDialog("Unit Converter Help", help_content, self)
        dialog.exec_()


    def get_parameters(self):
        params = {
            'method': self.method_name,
            'x_formula': self.x_formula_input.text().strip(),
            'y_formula': self.y_formula_input.text().strip(),
            'apply_for_batch': self.apply_for_batch_checkbox.isChecked()
        }
        if self.apply_for_batch_checkbox.isChecked():
            params['x_column_index'] = self.batch_x_spinbox.value() - 1  # Zero-based index
            params['y_column_index'] = self.batch_y_spinbox.value() - 1  # Zero-based index
        else:
            params['x_column'] = self.x_column_combo.currentText()
            params['y_column'] = self.y_column_combo.currentText()
        return params



class ShiftBaselinePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Shift Baseline"
        self.init_ui()

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

        self.apply_button.setEnabled(True)   # Enabled by default
        self.save_button.setEnabled(False)   # Disabled until applied
        self.send_to_data_panel_button.setEnabled(False)  # Disabled until applied

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # Add "Apply for Batch" checkbox
        self.apply_for_batch_checkbox = QCheckBox("Apply for Batch")
        self.apply_for_batch_checkbox.stateChanged.connect(self.toggle_batch_mode)
        self.layout.addWidget(self.apply_for_batch_checkbox)

        # Batch mode X and Y column input
        batch_layout = QHBoxLayout()
        self.batch_x_label = QLabel("X Column:")
        self.batch_x_spinbox = QSpinBox()
        self.batch_x_spinbox.setRange(1, 100)
        self.batch_x_spinbox.setEnabled(False)

        self.batch_y_label = QLabel("Y Column:")
        self.batch_y_spinbox = QSpinBox()
        self.batch_y_spinbox.setRange(1, 100)
        self.batch_y_spinbox.setEnabled(False)

        batch_layout.addWidget(self.batch_x_label)
        batch_layout.addWidget(self.batch_x_spinbox)
        batch_layout.addWidget(self.batch_y_label)
        batch_layout.addWidget(self.batch_y_spinbox)

        self.layout.addLayout(batch_layout)

        # Add X and Y column selection
        self.layout.addWidget(QLabel("Select X and Y Columns:"))
        x_y_layout = QHBoxLayout()
        self.x_column_combo = QComboBox()
        self.y_column_combo = QComboBox()
        x_y_layout.addWidget(QLabel("X Column:"))
        x_y_layout.addWidget(self.x_column_combo)
        x_y_layout.addWidget(QLabel("Y Column:"))
        x_y_layout.addWidget(self.y_column_combo)
        self.layout.addLayout(x_y_layout)

        # Instructions
        instructions = QLabel("Shift the baseline by adjusting the minimum Y-value to a desired value.")
        instructions.setWordWrap(True)
        self.layout.addWidget(instructions)

        # Input for Desired Baseline Value
        input_layout = QHBoxLayout()
        self.baseline_label = QLabel("Desired Baseline Value:")
        self.baseline_input = QLineEdit()
        self.baseline_input.setPlaceholderText("e.g., 0")
        self.baseline_input.setText("0")  # Default value is zero
        input_layout.addWidget(self.baseline_label)
        input_layout.addWidget(self.baseline_input)
        self.layout.addLayout(input_layout)

        self.setLayout(self.layout)

    def toggle_batch_mode(self, state):
        is_checked = (state == Qt.Checked)
        self.batch_x_spinbox.setEnabled(is_checked)
        self.batch_y_spinbox.setEnabled(is_checked)
        self.batch_x_label.setEnabled(is_checked)
        self.batch_y_label.setEnabled(is_checked)
        # Disable x_column_combo and y_column_combo when batch mode is enabled
        self.x_column_combo.setEnabled(not is_checked)
        self.y_column_combo.setEnabled(not is_checked)

    def set_data_columns(self, columns):
        self.x_column_combo.clear()
        self.x_column_combo.addItems(columns)
        self.y_column_combo.clear()
        self.y_column_combo.addItems(columns)


    def show_help(self):
        help_content = SHIFT_BASELINE_HELP  
        dialog = HelpDialog("Shift Baseline Help", SHIFT_BASELINE_HELP, self)
        dialog.exec_()

    def get_parameters(self):
        """
        Retrieve parameters entered by the user.

        Returns:
            dict: Contains the method name and desired baseline value.
        """
        try:
            baseline_str = self.baseline_input.text().strip()
            if not baseline_str:
                desired_baseline = 0.0  # Default to zero if empty
            else:
                desired_baseline = float(baseline_str)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid numerical value for the baseline.")
            return None

        params = {
            'method': self.method_name,
            'desired_baseline': desired_baseline,
            'apply_for_batch': self.apply_for_batch_checkbox.isChecked()
        }
        if self.apply_for_batch_checkbox.isChecked():
            params['x_column_index'] = self.batch_x_spinbox.value() - 1  # Zero-based index
            params['y_column_index'] = self.batch_y_spinbox.value() - 1  # Zero-based index
        else:
            params['x_column'] = self.x_column_combo.currentText()
            params['y_column'] = self.y_column_combo.currentText()
        return params

class DataCuttingPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Data Cutting"
        self.init_ui()

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

        self.apply_button.setEnabled(True)   # Enabled by default
        self.save_button.setEnabled(False)   # Disabled until applied
        self.send_to_data_panel_button.setEnabled(False)  # Disabled until applied

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.send_to_data_panel_button)
        self.layout.addLayout(button_layout)

        # Add "Apply for Batch" checkbox
        self.apply_for_batch_checkbox = QCheckBox("Apply for Batch")
        self.apply_for_batch_checkbox.stateChanged.connect(self.toggle_batch_mode)
        self.layout.addWidget(self.apply_for_batch_checkbox)

        # Batch mode X and Y column input
        batch_layout = QHBoxLayout()
        self.batch_x_label = QLabel("X Column:")
        self.batch_x_spinbox = QSpinBox()
        self.batch_x_spinbox.setRange(1, 100)
        self.batch_x_spinbox.setEnabled(False)

        self.batch_y_label = QLabel("Y Column:")
        self.batch_y_spinbox = QSpinBox()
        self.batch_y_spinbox.setRange(1, 100)
        self.batch_y_spinbox.setEnabled(False)

        batch_layout.addWidget(self.batch_x_label)
        batch_layout.addWidget(self.batch_x_spinbox)
        batch_layout.addWidget(self.batch_y_label)
        batch_layout.addWidget(self.batch_y_spinbox)

        self.layout.addLayout(batch_layout)


        # Add X and Y column selection
        self.layout.addWidget(QLabel("Select X and Y Columns:"))
        x_y_layout = QHBoxLayout()
        self.x_column_combo = QComboBox()
        self.y_column_combo = QComboBox()
        x_y_layout.addWidget(QLabel("X Column:"))
        x_y_layout.addWidget(self.x_column_combo)
        x_y_layout.addWidget(QLabel("Y Column:"))
        x_y_layout.addWidget(self.y_column_combo)
        self.layout.addLayout(x_y_layout)

        # Instructions
        instructions = QLabel("Define the X interval to cut the data.\nOnly data points within [X Start, X End] will be retained.")
        instructions.setWordWrap(True)
        self.layout.addWidget(instructions)

        # Input fields for X Start and X End
        input_layout = QHBoxLayout()
        self.x_start_label = QLabel("X Start:")
        self.x_start_input = QLineEdit()
        self.x_start_input.setPlaceholderText("Enter starting X value")
        input_layout.addWidget(self.x_start_label)
        input_layout.addWidget(self.x_start_input)

        self.x_end_label = QLabel("X End:")
        self.x_end_input = QLineEdit()
        self.x_end_input.setPlaceholderText("Enter ending X value")
        input_layout.addWidget(self.x_end_label)
        input_layout.addWidget(self.x_end_input)

        self.layout.addLayout(input_layout)

        self.setLayout(self.layout)

    def toggle_batch_mode(self, state):
        is_checked = (state == Qt.Checked)
        self.batch_x_spinbox.setEnabled(is_checked)
        self.batch_y_spinbox.setEnabled(is_checked)
        self.batch_x_label.setEnabled(is_checked)
        self.batch_y_label.setEnabled(is_checked)
        # Disable x_column_combo and y_column_combo when batch mode is enabled
        self.x_column_combo.setEnabled(not is_checked)
        self.y_column_combo.setEnabled(not is_checked)
        
    def set_data_columns(self, columns):
        self.x_column_combo.clear()
        self.x_column_combo.addItems(columns)
        self.y_column_combo.clear()
        self.y_column_combo.addItems(columns)


    def show_help(self):
        help_content = DATA_CUTTING_HELP
        dialog = HelpDialog("Data Cutting Help", help_content, self)
        dialog.exec_()
    def get_parameters(self):
        """
        Retrieve parameters entered by the user.

        Returns:
            dict: Contains the method name and X start and end values.
        """
        try:
            x_start_str = self.x_start_input.text().strip()
            x_end_str = self.x_end_input.text().strip()
            x_start = float(x_start_str)
            x_end = float(x_end_str)
            if x_start > x_end:
                QMessageBox.warning(self, "Invalid Input", "X Start should be less than or equal to X End.")
                return None
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numerical values for X Start and X End.")
            return None

        params = {
            'method': self.method_name,
            'x_start': x_start,
            'x_end': x_end,
            'apply_for_batch': self.apply_for_batch_checkbox.isChecked()
        }
        if self.apply_for_batch_checkbox.isChecked():
            params['x_column_index'] = self.batch_x_spinbox.value() - 1  # Zero-based index
            params['y_column_index'] = self.batch_y_spinbox.value() - 1  # Zero-based index
        else:
            params['x_column'] = self.x_column_combo.currentText()
            params['y_column'] = self.y_column_combo.currentText()
        return params

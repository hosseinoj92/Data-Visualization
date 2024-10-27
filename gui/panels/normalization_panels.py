#gui/panels normalization_panels.py


from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QLabel, 
    QDoubleSpinBox, QLineEdit, QSpinBox, QFileDialog,QMessageBox,QListWidgetItem, QGroupBox,QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os
import sys
from gui.dialogs.help_dialog import HelpDialog  # Assuming the HelpDialog is located in gui/help_dialog.py
from gui.utils.help_content import (
    MIN_MAX_NORMALIZATION_HELP, Z_SCORE_NORMALIZATION_HELP, ROBUST_SCALING_NORMALIZATION_HELP,
    AUC_NORMALIZATION_HELP, INTERVAL_AUC_NORMALIZATION_HELP, TOTAL_INTENSITY_NORMALIZATION_HELP,
    REFERENCE_PEAK_NORMALIZATION_HELP, BASELINE_CORRECTION_NORMALIZATION_HELP, SUBTRACTION_NORMALIZATION_HELP
)
from gui.utils.widgets import DraggableListWidget



def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

#######################################################

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

class BaseNormalizationMethodPanel(QWidget):
    """
    Abstract base class for normalization method panels.
    Each normalization method should inherit from this class and implement the required methods.
    """
    def __init__(self, method_name, parent=None):
        super(BaseNormalizationMethodPanel, self).__init__(parent)
        self.method_name = method_name
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components. Must be implemented by subclasses."""
        raise NotImplementedError("Must implement init_ui in subclass")

    def get_parameters(self):
        """Retrieve method-specific parameters. Must be implemented by subclasses."""
        raise NotImplementedError("Must implement get_parameters in subclass")


class MinMaxNormalizationPanel(BaseNormalizationMethodPanel):
    def __init__(self, parent=None):
        super().__init__("Min-Max Normalization", parent)
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
        help_content = SUBTRACTION_NORMALIZATION_HELP
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
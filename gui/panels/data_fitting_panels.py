# gui/panels/data_fitting_panels.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QComboBox, QSizePolicy, QRadioButton, QButtonGroup, QSpinBox,QTextEdit,
    QFileDialog, QDialog,QGroupBox, QDoubleSpinBox, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDoubleValidator
from functools import partial
import json
import numpy as np
from gui.dialogs.help_dialog import HelpDialog
from gui.utils.help_content import (PEAK_FITTING_HELP, POLYNOMIAL_FITTING_HELP, CUSTOM_FITTING_HELP, 
                                    LOG_EXP_POWER_HELP,FOURIER_TRANSFORM_HELP,
)

import sympy as sp
from sympy import symbols, sympify, latex
from matplotlib import pyplot as plt
import tempfile
from PyQt5.QtGui import QPixmap
import os

class GaussianFittingPanel(QWidget):
    parameters_changed = pyqtSignal()
    run_peak_finder_signal = pyqtSignal()
    manual_peak_picker_signal = pyqtSignal(bool)  

    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Gaussian Fitting"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # **Add Column Selection Section**
        column_selection_layout = QHBoxLayout()
        column_selection_layout.addWidget(QLabel("Select X Column:"))
        self.x_column_combo = QComboBox()
        column_selection_layout.addWidget(self.x_column_combo)
        column_selection_layout.addWidget(QLabel("Select Y Column:"))
        self.y_column_combo = QComboBox()
        column_selection_layout.addWidget(self.y_column_combo)
        layout.addLayout(column_selection_layout)

        # Peak Parameters Table
        self.peak_table = QTableWidget(0, 6)
        self.peak_table.setHorizontalHeaderLabels(['Function', 'Param1', 'Param2', 'Param3', 'Param4', 'Enable'])
        self.peak_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set specific column widths
        self.peak_table.setColumnWidth(0, 120)  # Function column
        self.peak_table.setColumnWidth(1, 80)   # Param1
        self.peak_table.setColumnWidth(2, 80)   # Param2
        self.peak_table.setColumnWidth(3, 80)   # Param3
        self.peak_table.setColumnWidth(4, 80)   # Param4
        self.peak_table.setColumnWidth(5, 60)   # Enable column

        # Set resize mode for horizontal header
        header = self.peak_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(QLabel("Peaks"))
        layout.addWidget(self.peak_table)

        # Buttons to manage peaks
        buttons_layout = QHBoxLayout()
        self.add_peak_button = QPushButton("Add Peak")
        self.remove_peak_button = QPushButton("Remove Peak")
        # Add Manual Peak Picker button
        self.manual_peak_picker_button = QPushButton("Manual Peak Picker")
        self.manual_peak_picker_button.setCheckable(True)  # Make it a toggle button
        buttons_layout.addWidget(self.add_peak_button)
        buttons_layout.addWidget(self.remove_peak_button)
        buttons_layout.addWidget(self.manual_peak_picker_button)
        layout.addLayout(buttons_layout)

        # Peak Finder Parameters
        layout.addWidget(QLabel("Peak Finder Parameters"))
        peak_finder_layout = QHBoxLayout()
        self.sensitivity_label = QLabel("Sensitivity:")
        self.sensitivity_input = QLineEdit()
        self.sensitivity_input.setValidator(QDoubleValidator(0.0, 1.0, 2))
        self.sensitivity_input.setText("0.5")
        peak_finder_layout.addWidget(self.sensitivity_label)
        peak_finder_layout.addWidget(self.sensitivity_input)
        self.run_peak_finder_button = QPushButton("Run Peak Finder")
        peak_finder_layout.addWidget(self.run_peak_finder_button)
        layout.addLayout(peak_finder_layout)

        # Apply, Save, Send to Data Panel, Help Buttons
        buttons_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")
        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        self.help_button = QPushButton("Help")
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.send_to_data_panel_button)
        buttons_layout.addWidget(self.help_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Connect Signals
        self.add_peak_button.clicked.connect(self.add_peak)
        self.remove_peak_button.clicked.connect(self.remove_peak)
        self.manual_peak_picker_button.clicked.connect(self.manual_peak_picker)
        self.run_peak_finder_button.clicked.connect(self.run_peak_finder)
        self.help_button.clicked.connect(self.show_help)

        # Connect column combo boxes to emit parameter changes
        self.x_column_combo.currentIndexChanged.connect(self.parameters_changed.emit)
        self.y_column_combo.currentIndexChanged.connect(self.parameters_changed.emit)

        # Disconnect existing connections to prevent multiple connections
        try:
            self.peak_table.cellChanged.disconnect()
        except TypeError:
            pass  # No existing connection

        self.peak_table.cellChanged.connect(self.on_peak_table_cell_changed)

        # Disable Save and Send buttons initially
        self.save_button.setEnabled(False)
        self.send_to_data_panel_button.setEnabled(False)

    def set_data_columns(self, columns):
        """Populate the X and Y column combo boxes with available columns."""
        self.x_column_combo.clear()
        self.y_column_combo.clear()
        self.x_column_combo.addItems(columns)
        self.y_column_combo.addItems(columns)
        print(f"GaussianFittingPanel: Columns updated to {columns}")  # **ADDED DEBUG STATEMENT**
  
    def manual_peak_picker(self):
        if self.manual_peak_picker_button.isChecked():
            # Emit the signal to notify the DataFittingTab to enter manual peak picking mode
            self.manual_peak_picker_signal.emit(True)
        else:
            # Emit signal to exit manual peak picking mode
            self.manual_peak_picker_signal.emit(False)

    def add_peak(self):
        self.add_peak_row(1.0, 0.0, 1.0)

    def on_peak_table_cell_changed(self, row, column):
        self.parameters_changed.emit()

    def remove_peak(self):
        current_row = self.peak_table.currentRow()
        if current_row >= 0:
            try:
                self.peak_table.blockSignals(True)  # Block signals to prevent premature fitting
                # Remove two rows corresponding to the peak
                self.peak_table.removeRow(current_row)  # Remove current row
                self.peak_table.removeRow(current_row)  # Remove the next row
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error removing peak: {e}")
            finally:
                self.peak_table.blockSignals(False)  # Re-enable signals after removing the row
        else:
            QMessageBox.warning(self, "Remove Peak", "Please select a peak to remove.")


    def add_peak_row(self, amplitude, center, width, function_type='Gaussian'):
        try:
            self.peak_table.blockSignals(True)  # Block signals to prevent premature fitting
            row_position = self.peak_table.rowCount()
            # Insert two rows
            self.peak_table.insertRow(row_position)
            self.peak_table.insertRow(row_position + 1)

            # Function Type ComboBox in first row
            function_combo = QComboBox()
            function_combo.addItems(['Gaussian', 'Lorentzian', 'Voigt', 
                                     'Pseudo-Voigt', 'Exponential Gaussian', 
                                     'Split Gaussian', 'Split Lorentzian'])
            function_combo.setCurrentText(function_type)
            function_combo.currentTextChanged.connect(partial(self.update_row_parameters, row_position))
            self.peak_table.setCellWidget(row_position, 0, function_combo)

            # Set parameter names in the first row
            param_labels = []
            if function_type in ['Gaussian', 'Lorentzian']:
                param_labels = ['Amplitude', 'Center', 'Width', '']
            elif function_type == 'Voigt':
                param_labels = ['Amplitude', 'Center', 'Sigma', 'Gamma']
            elif function_type == 'Pseudo-Voigt':
                param_labels = ['Amplitude', 'Center', 'Width', 'Fraction']
            elif function_type == 'Exponential Gaussian':
                param_labels = ['Amplitude', 'Center', 'Sigma', 'Gamma']
            elif function_type == 'Split Gaussian':
                param_labels = ['Amplitude', 'Center', 'Sigma_Left', 'Sigma_Right']
            elif function_type == 'Split Lorentzian':
                param_labels = ['Amplitude', 'Center', 'Gamma_Left', 'Gamma_Right']
            else:
                param_labels = ['', '', '', '']

            for col, label in enumerate(param_labels, start=1):
                item = QTableWidgetItem(label)
                item.setFlags(Qt.ItemIsEnabled)  # Non-editable
                self.peak_table.setItem(row_position, col, item)

            # Enable checkbox in the first row
            enable_item = QTableWidgetItem()
            enable_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            enable_item.setCheckState(Qt.Checked)
            self.peak_table.setItem(row_position, 5, enable_item)

            # Now in the second row, we put the parameter input widgets
            # Empty cell in column 0 (Function column)
            empty_item = QTableWidgetItem('')
            empty_item.setFlags(Qt.ItemIsEnabled)
            self.peak_table.setItem(row_position + 1, 0, empty_item)

            # Create parameter widgets in the second row without labels
            self.create_parameter_widgets(row_position + 1, function_type, amplitude, center, width)

            # Adjust the row heights if needed
            self.peak_table.setRowHeight(row_position, 20)
            self.peak_table.setRowHeight(row_position + 1, 30)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error adding peak: {e}")
        finally:
            self.peak_table.blockSignals(False)  # Re-enable signals after adding the row

    def create_parameter_widgets(self, row, function_type, param1=1.0, param2=0.0, param3=1.0, param4=0.0):
        # Remove existing parameter widgets if any
        for col in range(1, 5):
            old_widget = self.peak_table.cellWidget(row, col)
            if old_widget is not None:
                old_widget.deleteLater()
                self.peak_table.setCellWidget(row, col, None)

        # Initialize parameter widgets without labels
        param_widgets = []
        if function_type in ['Gaussian', 'Lorentzian']:
            param_widgets.append(ParameterWidget(param1))
            param_widgets.append(ParameterWidget(param2))
            param_widgets.append(ParameterWidget(param3))
            param_widgets.append(QWidget())  # Empty widget for param4
        elif function_type == 'Voigt':
            param_widgets.append(ParameterWidget(param1))
            param_widgets.append(ParameterWidget(param2))
            param_widgets.append(ParameterWidget(param3))
            param_widgets.append(ParameterWidget(param4))
        elif function_type == 'Pseudo-Voigt':
            param_widgets.append(ParameterWidget(param1))
            param_widgets.append(ParameterWidget(param2))
            param_widgets.append(ParameterWidget(param3))
            param_widgets.append(ParameterWidget(param4))
        elif function_type == 'Exponential Gaussian':
            param_widgets.append(ParameterWidget(param1))
            param_widgets.append(ParameterWidget(param2))
            param_widgets.append(ParameterWidget(param3))
            param_widgets.append(ParameterWidget(param4))
        elif function_type == 'Split Gaussian':
            param_widgets.append(ParameterWidget(param1))
            param_widgets.append(ParameterWidget(param2))
            param_widgets.append(ParameterWidget(param3))
            param_widgets.append(ParameterWidget(param4))
        elif function_type == 'Split Lorentzian':
            param_widgets.append(ParameterWidget(param1))
            param_widgets.append(ParameterWidget(param2))
            param_widgets.append(ParameterWidget(param3))
            param_widgets.append(ParameterWidget(param4))
        else:
            param_widgets.extend([QWidget(), QWidget(), QWidget(), QWidget()])

        # Set parameter widgets
        for col, widget in enumerate(param_widgets, start=1):
            self.peak_table.setCellWidget(row, col, widget)

    def update_row_parameters(self, row):
        function_combo = self.peak_table.cellWidget(row, 0)
        function_type = function_combo.currentText()
        # Update parameter names in the first row (current row)
        param_labels = []
        if function_type in ['Gaussian', 'Lorentzian']:
            param_labels = ['Amplitude', 'Center', 'Width', '']
        elif function_type == 'Voigt':
            param_labels = ['Amplitude', 'Center', 'Sigma', 'Gamma']
        elif function_type == 'Pseudo-Voigt':
            param_labels = ['Amplitude', 'Center', 'Width', 'Fraction']
        elif function_type == 'Exponential Gaussian':
            param_labels = ['Amplitude', 'Center', 'Sigma', 'Gamma']
        elif function_type == 'Split Gaussian':
            param_labels = ['Amplitude', 'Center', 'Sigma_Left', 'Sigma_Right']
        elif function_type == 'Split Lorentzian':
            param_labels = ['Amplitude', 'Center', 'Gamma_Left', 'Gamma_Right']
        else:
            param_labels = ['', '', '', '']

        for col, label in enumerate(param_labels, start=1):
            item = QTableWidgetItem(label)
            item.setFlags(Qt.ItemIsEnabled)  # Non-editable
            self.peak_table.setItem(row, col, item)

        # Get current parameter values before recreating the widgets
        param_row = row + 1
        current_values = []
        for col in range(1, 5):
            widget = self.peak_table.cellWidget(param_row, col)
            if isinstance(widget, ParameterWidget):
                try:
                    value = float(widget.get_value())
                except ValueError:
                    value = 0.0
                current_values.append(value)
            else:
                current_values.append(0.0)

        # Now recreate the parameter widgets with existing values
        self.create_parameter_widgets(param_row, function_type, *current_values)

    def run_peak_finder(self):
        # Emit the signal to notify the parent to run the peak finder
        self.run_peak_finder_signal.emit()

    def show_help(self):
            help_content = PEAK_FITTING_HELP
            dialog = HelpDialog("Peak Fitting Help", help_content, self)
            dialog.exec_()

    def get_parameters(self):
        peaks = []
        row = 0
        while row < self.peak_table.rowCount():
            function_combo = self.peak_table.cellWidget(row, 0)
            function_type = function_combo.currentText()
            enable_item = self.peak_table.item(row, 5)
            if enable_item.checkState() == Qt.Checked:
                try:
                    # The parameter widgets are in the next row
                    param_row = row + 1
                    param_widgets = [self.peak_table.cellWidget(param_row, col) for col in range(1, 5)]
                    param_values = []
                    for widget in param_widgets:
                        if isinstance(widget, ParameterWidget):
                            param_values.append(float(widget.get_value()))
                        else:
                            param_values.append(None)

                    amplitude = param_values[0] if param_values[0] is not None else 1.0
                    center = param_values[1] if param_values[1] is not None else 0.0

                    if function_type in ['Gaussian', 'Lorentzian']:
                        width = param_values[2] if param_values[2] is not None else 1.0
                        peaks.append({
                            'function_type': function_type,
                            'amplitude': amplitude,
                            'center': center,
                            'sigma': width  # Use 'sigma' to match model parameter
                        })
                    elif function_type == 'Voigt':
                        sigma = param_values[2] if param_values[2] is not None else 1.0
                        gamma = param_values[3] if param_values[3] is not None else 1.0
                        peaks.append({
                            'function_type': function_type,
                            'amplitude': amplitude,
                            'center': center,
                            'sigma': sigma,
                            'gamma': gamma
                        })
                    elif function_type == 'Pseudo-Voigt':
                        sigma = param_values[2] if param_values[2] is not None else 1.0
                        fraction = param_values[3] if param_values[3] is not None else 0.5
                        peaks.append({
                            'function_type': function_type,
                            'amplitude': amplitude,
                            'center': center,
                            'sigma': sigma,  # Use 'sigma' to match model parameter
                            'fraction': fraction
                        })

                    elif function_type == 'Exponential Gaussian':
                        sigma = param_values[2] if param_values[2] is not None else 1.0
                        gamma = param_values[3] if param_values[3] is not None else 1.0
                        peaks.append({
                            'function_type': function_type,
                            'amplitude': amplitude,
                            'center': center,
                            'sigma': sigma,
                            'gamma': gamma
                        })
                    elif function_type == 'Split Gaussian':
                        sigma_left = param_values[2] if param_values[2] is not None else 1.0
                        sigma_right = param_values[3] if param_values[3] is not None else 1.0
                        peaks.append({
                            'function_type': function_type,
                            'amplitude': amplitude,
                            'center': center,
                            'sigma_left': sigma_left,
                            'sigma_right': sigma_right
                        })
                    elif function_type == 'Split Lorentzian':
                        gamma_left = param_values[2] if param_values[2] is not None else 1.0
                        gamma_right = param_values[3] if param_values[3] is not None else 1.0
                        peaks.append({
                            'function_type': function_type,
                            'amplitude': amplitude,
                            'center': center,
                            'gamma_left': gamma_left,
                            'gamma_right': gamma_right
                        })
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", f"Invalid numerical value in peak starting at row {row + 1}.")
                    return None
            row += 2  # Move to the next peak (skip the parameter row)
    
        if not peaks:
            QMessageBox.warning(self, "No Peaks", "Please add and enable at least one peak.")
            return None

        # **Add the following code to include selected X and Y columns**
        x_column = self.x_column_combo.currentText()
        y_column = self.y_column_combo.currentText()

        if not x_column or not y_column:
            QMessageBox.warning(self, "Column Selection", "Please select both X and Y columns for fitting.")
            return None

        print("get_parameters: Retrieved peaks:", peaks)
        return {
            'peaks': peaks,
            'x_column': x_column,
            'y_column': y_column
        }

class ParameterWidget(QWidget):
    def __init__(self, param_value):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.line_edit = QLineEdit()
        self.line_edit.setText(f"{param_value:.2f}")  # Initialize with two decimal digits
        self.line_edit.setValidator(QDoubleValidator(bottom=-1e10, top=1e10, decimals=2))  # Allow two decimal digits
        self.layout.addWidget(self.line_edit)
        
        # Connect the editingFinished signal to format the text
        self.line_edit.editingFinished.connect(self.format_text)
    
    def format_text(self):
        """Formats the text to two decimal digits when editing is finished."""
        text = self.line_edit.text()
        try:
            value = float(text)
            formatted_value = f"{value:.2f}"
            self.line_edit.setText(formatted_value)
        except ValueError:
            # If the input is not a valid float, reset to '0.00' or handle as needed
            self.line_edit.setText("0.00")
    
    def get_value(self):
        return self.line_edit.text()
    
    def set_value(self, value):
        self.line_edit.setText(f"{value:.2f}")


class PolynomialFittingPanel(QWidget):
    parameters_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Polynomial Fitting"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

       # Add Column Selection Section
        column_selection_layout = QHBoxLayout()
        column_selection_layout.addWidget(QLabel("Select X Column:"))
        self.x_column_combo = QComboBox()
        column_selection_layout.addWidget(self.x_column_combo)
        column_selection_layout.addWidget(QLabel("Select Y Column:"))
        self.y_column_combo = QComboBox()
        column_selection_layout.addWidget(self.y_column_combo)
        layout.addLayout(column_selection_layout)

        # Fitting Type Selection
        layout.addWidget(QLabel("Select Fitting Type:"))
        self.linear_radio = QRadioButton("Linear Fitting")
        self.polynomial_radio = QRadioButton("Polynomial Fitting")
        self.linear_radio.setChecked(True)

        self.fitting_type_group = QButtonGroup()
        self.fitting_type_group.addButton(self.linear_radio)
        self.fitting_type_group.addButton(self.polynomial_radio)

        layout.addWidget(self.linear_radio)
        layout.addWidget(self.polynomial_radio)

        # Degree of Polynomial
        self.degree_label = QLabel("Polynomial Degree:")
        self.degree_spinbox = QSpinBox()
        self.degree_spinbox.setMinimum(2)
        self.degree_spinbox.setMaximum(10)
        self.degree_spinbox.setValue(2)
        self.degree_label.setVisible(False)
        self.degree_spinbox.setVisible(False)

        degree_layout = QHBoxLayout()
        degree_layout.addWidget(self.degree_label)
        degree_layout.addWidget(self.degree_spinbox)
        layout.addLayout(degree_layout)

        # Buttons: Apply, Save, Send to Data Panel, Help
        buttons_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")
        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        self.help_button = QPushButton("Help")
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.send_to_data_panel_button)
        buttons_layout.addWidget(self.help_button)
        layout.addLayout(buttons_layout)

        # Disable Save and Send buttons initially
        self.save_button.setEnabled(False)
        self.send_to_data_panel_button.setEnabled(False)

        self.setLayout(layout)

        # Connect Signals
        self.linear_radio.toggled.connect(self.toggle_degree_visibility)
        self.apply_button.clicked.connect(self.parameters_changed.emit)
        self.help_button.clicked.connect(self.show_help)

        # Connect column combo boxes to emit parameter changes
        self.x_column_combo.currentIndexChanged.connect(self.parameters_changed.emit)
        self.y_column_combo.currentIndexChanged.connect(self.parameters_changed.emit)

    def toggle_degree_visibility(self):
        is_polynomial = self.polynomial_radio.isChecked()
        self.degree_label.setVisible(is_polynomial)
        self.degree_spinbox.setVisible(is_polynomial)

    def set_data_columns(self, columns):
        """Populate the X and Y column combo boxes with available columns."""
        self.x_column_combo.clear()
        self.y_column_combo.clear()
        self.x_column_combo.addItems(columns)
        self.y_column_combo.addItems(columns)

    def get_parameters(self):
        fitting_type = 'linear' if self.linear_radio.isChecked() else 'polynomial'
        degree = self.degree_spinbox.value() if fitting_type == 'polynomial' else 1

        # Get selected columns
        x_column = self.x_column_combo.currentText()
        y_column = self.y_column_combo.currentText()

        if not x_column or not y_column:
            QMessageBox.warning(self, "Column Selection", "Please select both X and Y columns for fitting.")
            return None

        return {
            'fitting_type': fitting_type,
            'degree': degree,
            'x_column': x_column,
            'y_column': y_column
        }

    def show_help(self):
        help_content = POLYNOMIAL_FITTING_HELP
        QMessageBox.information(self, "Polynomial Fitting Help", help_content)



class CustomFittingPanel(QWidget):
    parameters_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Custom Fitting"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Add Column Selection Section
        column_selection_layout = QHBoxLayout()
        column_selection_layout.addWidget(QLabel("Select X Column:"))
        self.x_column_combo = QComboBox()
        column_selection_layout.addWidget(self.x_column_combo)
        column_selection_layout.addWidget(QLabel("Select Y Column:"))
        self.y_column_combo = QComboBox()
        column_selection_layout.addWidget(self.y_column_combo)
        layout.addLayout(column_selection_layout)

        # Instruction Label
        layout.addWidget(QLabel("Define your custom fitting function:"))

        # Text Edit for function definition
        self.function_text_edit = QTextEdit()
        self.function_text_edit.setPlaceholderText("Enter your function here, e.g., a * np.sin(b * x) + c")
        layout.addWidget(self.function_text_edit)

        # **Add "Show Equation" Button**
        self.show_equation_button = QPushButton("Show Equation")
        layout.addWidget(self.show_equation_button)

        # Parameters Table
        self.parameters_table = QTableWidget(0, 4)  # Now 4 columns
        self.parameters_table.setHorizontalHeaderLabels(['Parameter', 'Initial Guess', 'Min', 'Max'])
        self.parameters_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(QLabel("Parameters"))
        layout.addWidget(self.parameters_table)

        # Buttons to manage parameters
        param_buttons_layout = QHBoxLayout()
        self.add_param_button = QPushButton("Add Parameter")
        self.remove_param_button = QPushButton("Remove Parameter")
        param_buttons_layout.addWidget(self.add_param_button)
        param_buttons_layout.addWidget(self.remove_param_button)
        layout.addLayout(param_buttons_layout)

        # Optimization method and max iterations
        opt_layout = QHBoxLayout()
        self.optimization_method_label = QLabel("Optimization Method:")
        self.optimization_method_combo = QComboBox()
        self.optimization_method_combo.addItems(['leastsq', 'least_squares', 'differential_evolution', 'brute', 'basinhopping'])
        opt_layout.addWidget(self.optimization_method_label)
        opt_layout.addWidget(self.optimization_method_combo)

        self.max_iter_label = QLabel("Max Iterations:")
        self.max_iter_spinbox = QSpinBox()
        self.max_iter_spinbox.setRange(1, 10000)
        self.max_iter_spinbox.setValue(1000)
        opt_layout.addWidget(self.max_iter_label)
        opt_layout.addWidget(self.max_iter_spinbox)
        layout.addLayout(opt_layout)

        # Save and Load Function Buttons
        save_load_layout = QHBoxLayout()
        self.save_function_button = QPushButton("Save Function")
        self.load_function_button = QPushButton("Load Function")
        save_load_layout.addWidget(self.save_function_button)
        save_load_layout.addWidget(self.load_function_button)
        layout.addLayout(save_load_layout)

        # Apply, Save, Send to Data Panel, Help Buttons
        buttons_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")
        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        self.help_button = QPushButton("Help")
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.send_to_data_panel_button)
        buttons_layout.addWidget(self.help_button)
        layout.addLayout(buttons_layout)

        # Disable Save and Send buttons initially
        self.save_button.setEnabled(False)
        self.send_to_data_panel_button.setEnabled(False)

        self.setLayout(layout)

        # Connect Signals
        self.add_param_button.clicked.connect(self.add_parameter)
        self.remove_param_button.clicked.connect(self.remove_parameter)
        self.function_text_edit.textChanged.connect(self.parameters_changed.emit)
        self.apply_button.clicked.connect(self.parameters_changed.emit)
        self.help_button.clicked.connect(self.show_help)
        self.save_function_button.clicked.connect(self.save_function)
        self.load_function_button.clicked.connect(self.load_function)
        self.show_equation_button.clicked.connect(self.show_equation)

        # Connect column combo boxes to emit parameter changes
        self.x_column_combo.currentIndexChanged.connect(self.parameters_changed.emit)
        self.y_column_combo.currentIndexChanged.connect(self.parameters_changed.emit)

        # Initialize parameters
        self.parameters = {}

    def set_data_columns(self, columns):
        """Populate the X and Y column combo boxes with available columns."""
        self.x_column_combo.clear()
        self.y_column_combo.clear()
        self.x_column_combo.addItems(columns)
        self.y_column_combo.addItems(columns)

    def add_parameter(self):
        row_position = self.parameters_table.rowCount()
        self.parameters_table.insertRow(row_position)
        # Parameter name
        param_name_item = QTableWidgetItem(f"param{row_position+1}")
        self.parameters_table.setItem(row_position, 0, param_name_item)
        # Initial guess
        initial_guess_item = QTableWidgetItem("1.0")
        self.parameters_table.setItem(row_position, 1, initial_guess_item)
        # Min and Max items
        min_item = QTableWidgetItem("-inf")
        self.parameters_table.setItem(row_position, 2, min_item)
        max_item = QTableWidgetItem("inf")
        self.parameters_table.setItem(row_position, 3, max_item)
        self.parameters_changed.emit()

    def show_equation(self):
        # Get the function string from the input
        function_str = self.function_text_edit.toPlainText()
        if not function_str.strip():
            QMessageBox.warning(self, "No Function", "Please enter a custom function.")
            return

        # Define the variable symbols
        x = sp.symbols('x')
        # Prepare the namespace for sympify
        namespace = {'x': x}
        # Add parameters to the namespace
        for row in range(self.parameters_table.rowCount()):
            param_name_item = self.parameters_table.item(row, 0)
            if param_name_item:
                param_name = param_name_item.text().strip()
                if param_name.isidentifier():
                    namespace[param_name] = sp.symbols(param_name)

        # Map numpy functions to SymPy functions
        numpy_to_sympy = {
            # Remove prefixes
            'np.': '',      # Remove 'np.' prefix
            'numpy.': '',   # Remove 'numpy.' prefix
            'math.': '',    # Remove 'math.' prefix

            # Trigonometric Functions
            'sin': 'sin',
            'cos': 'cos',
            'tan': 'tan',
            'arcsin': 'asin',
            'arccos': 'acos',
            'arctan': 'atan',
            'arctan2': 'atan2',  # May require special handling
            'hypot': 'hypot',    # May require special handling

            # Hyperbolic Functions
            'sinh': 'sinh',
            'cosh': 'cosh',
            'tanh': 'tanh',
            'arcsinh': 'asinh',
            'arccosh': 'acosh',
            'arctanh': 'atanh',

            # Exponential and Logarithmic Functions
            'exp': 'exp',
            'expm1': 'expm1',
            'log': 'log',       # Natural logarithm
            'log10': 'log10',
            'log2': 'log',      # SymPy's log can take a base as a second argument
            'log1p': 'log1p',

            # Power and Root Functions
            'power': '**',      # Exponentiation operator
            'sqrt': 'sqrt',
            'square': '**2',
            'cbrt': 'cbrt',     # Cube root, may need to define as x**(1/3)
            'reciprocal': '1/',

            # Rounding Functions
            'ceil': 'ceiling',
            'floor': 'floor',
            'trunc': 'trunc',
            'rint': 'round',    # Closest integer

            # Special Functions
            'abs': 'Abs',
            'fabs': 'Abs',
            'sign': 'sign',
            'mod': 'Mod',
            'remainder': 'Mod',
            'fmod': 'Mod',

            # Constants
            'pi': 'pi',
            'e': 'E',
            'inf': 'oo',        # Infinity in SymPy
            'nan': 'nan',       # Not a number

            # Statistical Functions (for scalar inputs)
            'maximum': 'Max',
            'minimum': 'Min',
            'fmax': 'Max',
            'fmin': 'Min',

            # Angle Conversion
            'deg2rad': 'deg2rad',  # Multiply by pi/180
            'rad2deg': 'rad2deg',  # Multiply by 180/pi

            # Other Mathematical Functions
            'clip': 'clip',     # Requires custom handling
            'where': 'Piecewise',  # Conditional expressions

            # Error Functions
            'erf': 'erf',
            'erfc': 'erfc',
            'gamma': 'gamma',
            'lgamma': 'loggamma',

            # Bessel Functions
            'j0': 'besselj0',
            'j1': 'besselj1',
            'jn': 'besselj',    # Bessel function of integer order n
            'y0': 'bessely0',
            'y1': 'bessely1',
            'yn': 'bessely',    # Bessel function of the second kind

            # Miscellaneous Functions
            'logical_and': 'And',    # Logical operations, may not directly map
            'logical_or': 'Or',
            'logical_not': 'Not',
            'logical_xor': 'Xor',
            'bitwise_and': 'And',
            'bitwise_or': 'Or',
            'bitwise_xor': 'Xor',
            'invert': 'Not',
            'left_shift': '<<',
            'right_shift': '>>',
            # Note: Logical and bitwise operations may need custom handling

            # Special Mathematical Constants
            'np.pi': 'pi',
            'np.e': 'E',
            'np.euler_gamma': 'EulerGamma',
            'np.inf': 'oo',
            'np.nan': 'nan',

            # Additional Functions
            'heaviside': 'Heaviside',
            'signbit': 'sign',
            'sinc': 'sinc',    # Normalized sinc function
            'deg2rad': '*pi/180',
            'rad2deg': '*180/pi',

            # Mathematical Operators
            'add': '+',
            'subtract': '-',
            'multiply': '*',
            'divide': '/',
            'true_divide': '/',
            'floor_divide': '//',
            'negative': '-',
            'positive': '+',

            # Complex Numbers
            'real': 're',
            'imag': 'im',
            'conj': 'conjugate',
            'angle': 'arg',
            'absolute': 'Abs',

            # Polynomial Functions
            'polyval': 'polyval',  # Requires custom handling
            'roots': 'roots',      # Requires custom handling

            # Special Cases (may require custom handling)
            'clip': 'Piecewise',
            'select': 'Piecewise',
            'interp': 'interp',    # Interpolation functions
            'vectorize': '',       # Not applicable in SymPy

            # Random Functions (not applicable)
            # 'random': '',

            # Fourier Transforms (not applicable)
            # 'fft': '',

            # Linear Algebra Functions (not applicable)
            # 'dot': '',
            # 'inner': '',
            # 'outer': '',

            # Set Functions (not applicable)
            # 'union1d': '',
            # 'intersect1d': '',

            # Date/Time Functions (not applicable)
            # 'datetime64': '',
        }


        # Replace numpy functions with SymPy equivalents
        for np_func, sp_func in numpy_to_sympy.items():
            function_str = function_str.replace(np_func, sp_func)

        try:
            # Parse the function string into a SymPy expression
            sympy_expr = sympify(function_str, locals=namespace)
            # Convert the SymPy expression to LaTeX
            latex_str = latex(sympy_expr, mode='plain')
        except Exception as e:
            QMessageBox.warning(self, "Parsing Error", f"Failed to parse the function:\n{e}")
            return

        # Render the LaTeX expression using Matplotlib
        try:
            # Create a temporary file to save the image
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
                fig = plt.figure(figsize=(0.1, 0.1))
                fig.text(0, 0, f"${latex_str}$", fontsize=12)
                plt.axis('off')
                plt.savefig(tmpfile.name, bbox_inches='tight', pad_inches=0.5)
                plt.close(fig)
                image_path = tmpfile.name

            # Create a new dialog to display the equation
            equation_dialog = QDialog(self)
            equation_dialog.setWindowTitle("Equation Preview")
            dialog_layout = QVBoxLayout()
            equation_dialog.setLayout(dialog_layout)

            # Display the image in a QLabel
            equation_label = QLabel()
            pixmap = QPixmap(image_path)
            equation_label.setPixmap(pixmap)
            equation_label.setAlignment(Qt.AlignCenter)
            dialog_layout.addWidget(equation_label)

            # Add Close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(equation_dialog.close)
            dialog_layout.addWidget(close_button)

            # Show the dialog
            equation_dialog.exec_()

            # Remove the temporary image file
            os.unlink(image_path)

        except Exception as e:
            QMessageBox.warning(self, "Rendering Error", f"Failed to render the equation:\n{e}")
            return

    def remove_parameter(self):
        current_row = self.parameters_table.currentRow()
        if current_row >= 0:
            self.parameters_table.removeRow(current_row)
            self.parameters_changed.emit()
        else:
            QMessageBox.warning(self, "Remove Parameter", "Please select a parameter to remove.")

    def get_parameters(self):
        # Retrieve the function string
        function_str = self.function_text_edit.toPlainText()
        if not function_str.strip():
            QMessageBox.warning(self, "No Function", "Please enter a custom function.")
            return None

        # Get selected columns
        x_column = self.x_column_combo.currentText()
        y_column = self.y_column_combo.currentText()

        if not x_column or not y_column:
            QMessageBox.warning(self, "Column Selection", "Please select both X and Y columns for fitting.")
            return None

        # Retrieve parameters and initial guesses
        params = {}
        for row in range(self.parameters_table.rowCount()):
            param_name_item = self.parameters_table.item(row, 0)
            initial_guess_item = self.parameters_table.item(row, 1)
            min_item = self.parameters_table.item(row, 2)
            max_item = self.parameters_table.item(row, 3)
            if param_name_item and initial_guess_item and min_item and max_item:
                param_name = param_name_item.text().strip()
                if not param_name.isidentifier():
                    QMessageBox.warning(self, "Invalid Parameter Name", f"'{param_name}' is not a valid parameter name.")
                    return None
                try:
                    initial_guess = float(initial_guess_item.text())
                    min_val = float(min_item.text()) if min_item.text().strip() not in ['', '-inf'] else -np.inf
                    max_val = float(max_item.text()) if max_item.text().strip() not in ['', 'inf'] else np.inf
                except ValueError:
                    QMessageBox.warning(self, "Invalid Parameter Value", f"Invalid value for parameter '{param_name}'.")
                    return None
                params[param_name] = {'value': initial_guess, 'min': min_val, 'max': max_val}
            else:
                QMessageBox.warning(self, "Incomplete Parameters", "Please complete all parameter fields.")
                return None

        # Retrieve optimization method and max iterations
        optimization_method = self.optimization_method_combo.currentText()
        max_iterations = self.max_iter_spinbox.value()

        return {
            'function_str': function_str,
            'params': params,
            'optimization_method': optimization_method,
            'max_iterations': max_iterations,
            'x_column': x_column,
            'y_column': y_column
        }

    def save_function(self):
        function_data = self.get_parameters()
        if function_data is None:
            return  # Error message already shown

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Custom Function",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(function_data, f, indent=4)
                QMessageBox.information(self, "Save Successful", f"Custom function saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Save Failed", f"Failed to save custom function:\n{e}")

    def load_function(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Custom Function",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    function_data = json.load(f)
                self.set_parameters(function_data)
                QMessageBox.information(self, "Load Successful", f"Custom function loaded from:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Load Failed", f"Failed to load custom function:\n{e}")

    def set_parameters(self, function_data):
        # Set function string
        self.function_text_edit.setText(function_data.get('function_str', ''))

        # Clear existing parameters
        self.parameters_table.setRowCount(0)

        # Set parameters
        params = function_data.get('params', {})
        for param_name, param_info in params.items():
            row_position = self.parameters_table.rowCount()
            self.parameters_table.insertRow(row_position)
            # Parameter name
            param_name_item = QTableWidgetItem(param_name)
            self.parameters_table.setItem(row_position, 0, param_name_item)
            # Initial guess
            initial_guess_item = QTableWidgetItem(str(param_info.get('value', 1.0)))
            self.parameters_table.setItem(row_position, 1, initial_guess_item)
            # Min and Max items
            min_val = param_info.get('min', -np.inf)
            max_val = param_info.get('max', np.inf)
            min_item = QTableWidgetItem(str(min_val) if min_val != -np.inf else "-inf")
            max_item = QTableWidgetItem(str(max_val) if max_val != np.inf else "inf")
            self.parameters_table.setItem(row_position, 2, min_item)
            self.parameters_table.setItem(row_position, 3, max_item)

        # Set optimization method and max iterations
        optimization_method = function_data.get('optimization_method', 'leastsq')
        max_iterations = function_data.get('max_iterations', 1000)
        self.optimization_method_combo.setCurrentText(optimization_method)
        self.max_iter_spinbox.setValue(max_iterations)

        self.parameters_changed.emit()

    def show_help(self):
            help_content = CUSTOM_FITTING_HELP
            dialog = HelpDialog("Custom Fitting Help", help_content, self)
            dialog.exec_()


class LogExpPowerFittingPanel(QWidget):
    """Panel for Logarithmic, Exponential, and Power-law Fitting."""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # Create main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Add Column Selection Section
        column_selection_layout = QHBoxLayout()
        column_selection_layout.addWidget(QLabel("Select X Column:"))
        self.x_column_combo = QComboBox()
        column_selection_layout.addWidget(self.x_column_combo)
        column_selection_layout.addWidget(QLabel("Select Y Column:"))
        self.y_column_combo = QComboBox()
        column_selection_layout.addWidget(self.y_column_combo)
        main_layout.addLayout(column_selection_layout)

        # Fitting type selection
        fitting_type_layout = QHBoxLayout()
        fitting_type_label = QLabel("Select Fitting Type:")
        self.fitting_type_combo = QComboBox()
        self.fitting_type_combo.addItems(["Logarithmic", "Exponential", "Power-law"])
        self.fitting_type_combo.currentTextChanged.connect(self.update_parameter_fields)
        fitting_type_layout.addWidget(fitting_type_label)
        fitting_type_layout.addWidget(self.fitting_type_combo)
        main_layout.addLayout(fitting_type_layout)
        
        # Parameter inputs
        self.parameter_groupbox = QGroupBox("Parameters")
        self.parameter_layout = QGridLayout()
        self.parameter_groupbox.setLayout(self.parameter_layout)
        main_layout.addWidget(self.parameter_groupbox)
        
        # Initialize parameter fields
        self.parameter_fields = {}
        self.update_parameter_fields(self.fitting_type_combo.currentText())
        
        # Optimization options
        optimization_groupbox = QGroupBox("Optimization Options")
        optimization_layout = QGridLayout()
        optimization_groupbox.setLayout(optimization_layout)
        
        # Optimization method selection
        optimization_method_label = QLabel("Optimization Method:")
        self.optimization_method_combo = QComboBox()
        self.optimization_method_combo.addItems([
            "leastsq", "least_squares", "differential_evolution", "brute",
            "basinhopping", 
        ])
        optimization_layout.addWidget(optimization_method_label, 0, 0)
        optimization_layout.addWidget(self.optimization_method_combo, 0, 1)
        
        # Maximum iterations
        max_iterations_label = QLabel("Max Iterations:")
        self.max_iterations_spin = QSpinBox()
        self.max_iterations_spin.setRange(1, 1000000)
        self.max_iterations_spin.setValue(1000)
        optimization_layout.addWidget(max_iterations_label, 1, 0)
        optimization_layout.addWidget(self.max_iterations_spin, 1, 1)
        
        main_layout.addWidget(optimization_groupbox)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")
        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        self.help_button = QPushButton("Help")
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.send_to_data_panel_button)
        buttons_layout.addWidget(self.help_button)
        main_layout.addLayout(buttons_layout)
        
        # Initially disable save and send buttons until fitting is applied
        self.save_button.setEnabled(False)
        self.send_to_data_panel_button.setEnabled(False)
        
        # Connect help button
        self.help_button.clicked.connect(self.show_help)

       # Connect column combo boxes to emit parameter changes
        self.x_column_combo.currentIndexChanged.connect(self.parameters_changed.emit)
        self.y_column_combo.currentIndexChanged.connect(self.parameters_changed.emit)


    def set_data_columns(self, columns):
        """Populate the X and Y column combo boxes with available columns."""
        self.x_column_combo.clear()
        self.y_column_combo.clear()
        self.x_column_combo.addItems(columns)
        self.y_column_combo.addItems(columns)    

    def update_parameter_fields(self, fitting_type):
        # Clear existing parameter fields
        for i in reversed(range(self.parameter_layout.count())):
            widget = self.parameter_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.parameter_fields.clear()
        
        # Define parameters based on fitting type
        if fitting_type == "Logarithmic":
            params = ['a', 'b']
        elif fitting_type == "Exponential":
            params = ['a', 'b', 'c']
        elif fitting_type == "Power-law":
            params = ['a', 'b', 'c']
        else:
            params = []
        
        # Create input fields for each parameter
        for row, param in enumerate(params):
            label = QLabel(f"{param}:")
            init_spin = QDoubleSpinBox()
            init_spin.setRange(-1e6, 1e6)
            init_spin.setDecimals(2)
            init_spin.setValue(1.0)
            min_spin = QDoubleSpinBox()
            min_spin.setRange(-1e6, 1e6)
            min_spin.setDecimals(2)
            min_spin.setValue(-1e6)
            max_spin = QDoubleSpinBox()
            max_spin.setRange(-1e6, 1e6)
            max_spin.setDecimals(2)
            max_spin.setValue(1e6)
            self.parameter_layout.addWidget(label, row, 0)
            self.parameter_layout.addWidget(QLabel("Initial:"), row, 1)
            self.parameter_layout.addWidget(init_spin, row, 2)
            self.parameter_layout.addWidget(QLabel("Min:"), row, 3)
            self.parameter_layout.addWidget(min_spin, row, 4)
            self.parameter_layout.addWidget(QLabel("Max:"), row, 5)
            self.parameter_layout.addWidget(max_spin, row, 6)
            self.parameter_fields[param] = {
                'init': init_spin,
                'min': min_spin,
                'max': max_spin
            }
    
    def get_parameters(self):
        fitting_type = self.fitting_type_combo.currentText()
        params = {}
        for param_name, widgets in self.parameter_fields.items():
            init_value = widgets['init'].value()
            min_value = widgets['min'].value()
            max_value = widgets['max'].value()
            params[param_name] = {
                'value': init_value,
                'min': min_value,
                'max': max_value
            }
        optimization_method = self.optimization_method_combo.currentText()
        max_iterations = self.max_iterations_spinbox.value()

        # Get selected columns
        x_column = self.x_column_combo.currentText()
        y_column = self.y_column_combo.currentText()

        if not x_column or not y_column:
            QMessageBox.warning(self, "Column Selection", "Please select both X and Y columns for fitting.")
            return None

        return {
            'fitting_type': fitting_type,
            'params': params,
            'optimization_method': optimization_method,
            'max_iterations': max_iterations,
            'x_column': x_column,
            'y_column': y_column
        }
    
    
    def show_help(self):
            help_content = LOG_EXP_POWER_HELP
            dialog = HelpDialog("Custom Fitting Help", help_content, self)
            dialog.exec_()


class FourierTransformPanel(QWidget):
    parameters_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Fourier Transform"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Add Column Selection Section
        column_selection_layout = QHBoxLayout()
        column_selection_layout.addWidget(QLabel("Select Time Column:"))
        self.time_column_combo = QComboBox()
        column_selection_layout.addWidget(self.time_column_combo)
        column_selection_layout.addWidget(QLabel("Select Data Column:"))
        self.data_column_combo = QComboBox()
        column_selection_layout.addWidget(self.data_column_combo)
        layout.addLayout(column_selection_layout)

        self.x_scale_label = QLabel("X-axis Scale:")
        self.x_scale_combo = QComboBox()
        self.x_scale_combo.addItems(['linear', 'log'])

        self.y_scale_label = QLabel("Y-axis Scale:")
        self.y_scale_combo = QComboBox()
        self.y_scale_combo.addItems(['linear', 'log'])

        # Add these widgets to your panel's layout
        layout.addWidget(self.x_scale_label)
        layout.addWidget(self.x_scale_combo)
        layout.addWidget(self.y_scale_label)
        layout.addWidget(self.y_scale_combo)


        # Transform Type Selection
        transform_type_layout = QHBoxLayout()
        transform_type_layout.addWidget(QLabel("Transform Type:"))
        self.transform_type_combo = QComboBox()
        self.transform_type_combo.addItems(["FFT", "Inverse FFT"])
        transform_type_layout.addWidget(self.transform_type_combo)
        layout.addLayout(transform_type_layout)

        # Advanced Options Section
        advanced_options_group = QGroupBox("Advanced Options")
        advanced_options_layout = QVBoxLayout()

        # Window Function Selection
        window_function_layout = QHBoxLayout()
        window_function_layout.addWidget(QLabel("Window Function:"))
        self.window_function_combo = QComboBox()
        self.window_function_combo.addItems([
            "None", "Hamming", "Hanning", "Blackman", "Bartlett", "Kaiser"
        ])
        window_function_layout.addWidget(self.window_function_combo)
        advanced_options_layout.addLayout(window_function_layout)

        # Zero-padding Option
        zero_padding_layout = QHBoxLayout()
        zero_padding_layout.addWidget(QLabel("Zero-padding Length:"))
        self.zero_padding_spinbox = QSpinBox()
        self.zero_padding_spinbox.setRange(0, 1000000)
        self.zero_padding_spinbox.setValue(0)
        zero_padding_layout.addWidget(self.zero_padding_spinbox)
        advanced_options_layout.addLayout(zero_padding_layout)

        advanced_options_group.setLayout(advanced_options_layout)
        layout.addWidget(advanced_options_group)

        # Buttons: Apply, Save, Send to Data Panel, Help
        buttons_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")
        self.send_to_data_panel_button = QPushButton("Send to Data Panel")
        self.help_button = QPushButton("Help")
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.send_to_data_panel_button)
        buttons_layout.addWidget(self.help_button)
        layout.addLayout(buttons_layout)

        # Disable Save and Send buttons initially
        self.save_button.setEnabled(False)
        self.send_to_data_panel_button.setEnabled(False)

        self.setLayout(layout)

        # Connect Signals
        self.apply_button.clicked.connect(self.parameters_changed.emit)
        self.help_button.clicked.connect(self.show_help)

        # Connect column combo boxes to emit parameter changes
        self.time_column_combo.currentIndexChanged.connect(self.parameters_changed.emit)
        self.data_column_combo.currentIndexChanged.connect(self.parameters_changed.emit)

    def set_data_columns(self, columns):
        """Populate the data and time column combo boxes with available columns."""
        self.data_column_combo.clear()
        self.data_column_combo.addItems(columns)
        self.time_column_combo.clear()
        self.time_column_combo.addItems(columns)

    def get_parameters(self):
        # Ensure columns are selected
        if not self.time_column_combo.currentText():
            QMessageBox.warning(self, "No Time Column Selected", "Please select a time column.")
            return None
        if not self.data_column_combo.currentText():
            QMessageBox.warning(self, "No Data Column Selected", "Please select a data column.")
            return None

        parameters = {
            'data_column': self.data_column_combo.currentText(),
            'time_column': self.time_column_combo.currentText(),
            'transform_type': self.transform_type_combo.currentText(),
            'window_function': self.window_function_combo.currentText(),
            'zero_padding': self.zero_padding_spinbox.value(),
        }
        return parameters


    def show_help(self):
        help_content = FOURIER_TRANSFORM_HELP
        dialog = HelpDialog("Fourier Transform Help", help_content, self)
        dialog.exec_()

    def get_axis_scaling(self):
        x_scale = self.x_scale_combo.currentText()
        y_scale = self.y_scale_combo.currentText()
        return x_scale, y_scale
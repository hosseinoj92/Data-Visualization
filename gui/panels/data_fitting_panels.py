# gui/panels/data_fitting_panels.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QComboBox, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDoubleValidator
from functools import partial

class GaussianFittingPanel(QWidget):
    parameters_changed = pyqtSignal()
    run_peak_finder_signal = pyqtSignal()
    manual_peak_picker_signal = pyqtSignal(bool)  # Add this signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Gaussian Fitting"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

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

        # Disconnect existing connections to prevent multiple connections
        try:
            self.peak_table.cellChanged.disconnect()
        except TypeError:
            pass  # No existing connection

        self.peak_table.cellChanged.connect(self.on_peak_table_cell_changed)

        # Disable Save and Send buttons initially
        self.save_button.setEnabled(False)
        self.send_to_data_panel_button.setEnabled(False)

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

            # Create parameter widgets in the second row
            self.create_parameter_widgets(row_position + 1, function_type, amplitude, center, width)

            # Set cell spans if needed (e.g., span Function cell over two rows)
            # self.peak_table.setSpan(row_position, 0, 2, 1)  # Optional: Span Function cell over two rows

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

        # Initialize parameter widgets with empty labels
        param_widgets = []
        if function_type in ['Gaussian', 'Lorentzian']:
            param_widgets.append(ParameterWidget('', param1))  # Amplitude
            param_widgets.append(ParameterWidget('', param2))  # Center
            param_widgets.append(ParameterWidget('', param3))  # Width
            param_widgets.append(QWidget())  # Empty widget for param4
        elif function_type == 'Voigt':
            param_widgets.append(ParameterWidget('', param1))  # Amplitude
            param_widgets.append(ParameterWidget('', param2))  # Center
            param_widgets.append(ParameterWidget('', param3))  # Sigma
            param_widgets.append(ParameterWidget('', param4))  # Gamma
        elif function_type == 'Pseudo-Voigt':
            param_widgets.append(ParameterWidget('', param1))  # Amplitude
            param_widgets.append(ParameterWidget('', param2))  # Center
            param_widgets.append(ParameterWidget('', param3))  # Width
            param_widgets.append(ParameterWidget('', param4))  # Fraction
        elif function_type == 'Exponential Gaussian':
            param_widgets.append(ParameterWidget('', param1))  # Amplitude
            param_widgets.append(ParameterWidget('', param2))  # Center
            param_widgets.append(ParameterWidget('', param3))  # Sigma
            param_widgets.append(ParameterWidget('', param4))  # Gamma
        elif function_type == 'Split Gaussian':
            param_widgets.append(ParameterWidget('', param1))  # Amplitude
            param_widgets.append(ParameterWidget('', param2))  # Center
            param_widgets.append(ParameterWidget('', param3))  # Sigma_Left
            param_widgets.append(ParameterWidget('', param4))  # Sigma_Right
        elif function_type == 'Split Lorentzian':
            param_widgets.append(ParameterWidget('', param1))  # Amplitude
            param_widgets.append(ParameterWidget('', param2))  # Center
            param_widgets.append(ParameterWidget('', param3))  # Gamma_Left
            param_widgets.append(ParameterWidget('', param4))  # Gamma_Right
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
        QMessageBox.information(self, "Gaussian Fitting Help", "This is where you can provide help information about Gaussian fitting.")
    
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

        print("get_parameters: Retrieved peaks:", peaks)
        return {'peaks': peaks}


from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

class ParameterWidget(QWidget):
    def __init__(self, param_name, param_value):
        super().__init__()
        self.param_name = param_name
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # If param_name is empty, don't show the label
        if self.param_name:
            self.label = QLabel(param_name)
            self.layout.addWidget(self.label)
        
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
    
    def get_param_name(self):
        return self.param_name
    
    def set_param_name(self, name):
        self.param_name = name
        self.label.setText(name)
    
    def set_value(self, value):
        self.line_edit.setText(f"{value:.2f}")

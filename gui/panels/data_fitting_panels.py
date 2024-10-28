# gui/panels/data_fitting_panels.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QComboBox,QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDoubleValidator

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
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

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
                self.peak_table.removeRow(current_row)
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
            self.peak_table.insertRow(row_position)
            
            # Function Type ComboBox
            function_combo = QComboBox()
            function_combo.addItems(['Gaussian', 'Lorentzian', 'Voigt', 'Pseudo-Voigt'])  # Added new functions here
            function_combo.setCurrentText(function_type)
            function_combo.currentTextChanged.connect(lambda _, row=row_position: self.update_row_parameters(row))
            self.peak_table.setCellWidget(row_position, 0, function_combo)
            
            # Initialize parameter items
            param1_item = QTableWidgetItem(f"{amplitude}")
            param2_item = QTableWidgetItem(f"{center}")
            param3_item = QTableWidgetItem(f"{width}")
            param4_item = QTableWidgetItem("")  # Additional parameter for Voigt and Pseudo-Voigt
            enable_item = QTableWidgetItem()
            enable_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            enable_item.setCheckState(Qt.Checked)

            self.peak_table.setItem(row_position, 1, param1_item)
            self.peak_table.setItem(row_position, 2, param2_item)
            self.peak_table.setItem(row_position, 3, param3_item)
            self.peak_table.setItem(row_position, 4, param4_item)
            self.peak_table.setItem(row_position, 5, enable_item)

            # Update parameters based on function type
            self.update_row_parameters(row_position)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error adding peak: {e}")
        finally:
            self.peak_table.blockSignals(False)  # Re-enable signals after adding the row

    def update_row_parameters(self, row):
        function_combo = self.peak_table.cellWidget(row, 0)
        function_type = function_combo.currentText()

        # Get parameter items
        param1_item = self.peak_table.item(row, 1)
        param2_item = self.peak_table.item(row, 2)
        param3_item = self.peak_table.item(row, 3)
        param4_item = self.peak_table.item(row, 4)

        # Set default values and parameter names based on function type
        if function_type in ['Gaussian', 'Lorentzian']:
            # Set tooltips
            param1_item.setToolTip('Amplitude')
            param2_item.setToolTip('Center')
            param3_item.setToolTip('Width')
            param4_item.setToolTip('N/A')
            param4_item.setFlags(Qt.NoItemFlags)
            param4_item.setText('')

            # Set default values
            param1_item.setText(param1_item.text() or '1.0')
            param2_item.setText(param2_item.text() or '0.0')
            param3_item.setText(param3_item.text() or '1.0')

        elif function_type == 'Voigt':
            # Set tooltips
            param1_item.setToolTip('Amplitude')
            param2_item.setToolTip('Center')
            param3_item.setToolTip('Sigma')
            param4_item.setToolTip('Gamma')
            param4_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)

            # Set default values
            param1_item.setText(param1_item.text() or '1.0')
            param2_item.setText(param2_item.text() or '0.0')
            param3_item.setText(param3_item.text() or '1.0')
            param4_item.setText(param4_item.text() or '1.0')

        elif function_type == 'Pseudo-Voigt':
            # Set tooltips
            param1_item.setToolTip('Amplitude')
            param2_item.setToolTip('Center')
            param3_item.setToolTip('Width')
            param4_item.setToolTip('Fraction')
            param4_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)

            # Set default values
            param1_item.setText(param1_item.text() or '1.0')
            param2_item.setText(param2_item.text() or '0.0')
            param3_item.setText(param3_item.text() or '1.0')
            param4_item.setText(param4_item.text() or '0.5')




    def run_peak_finder(self):
        # Emit the signal to notify the parent to run the peak finder
        self.run_peak_finder_signal.emit()

    def show_help(self):
        QMessageBox.information(self, "Gaussian Fitting Help", "This is where you can provide help information about Gaussian fitting.")
        
    def get_parameters(self):
        peaks = []
        for row in range(self.peak_table.rowCount()):
            function_combo = self.peak_table.cellWidget(row, 0)
            function_type = function_combo.currentText()
            param1_item = self.peak_table.item(row, 1)
            param2_item = self.peak_table.item(row, 2)
            param3_item = self.peak_table.item(row, 3)
            param4_item = self.peak_table.item(row, 4)
            enable_item = self.peak_table.item(row, 5)
            if enable_item.checkState() == Qt.Checked:
                try:
                    amplitude = float(param1_item.text())
                    center = float(param2_item.text())
                    if function_type in ['Gaussian', 'Lorentzian']:
                        width = float(param3_item.text())
                        peaks.append({
                            'function_type': function_type,
                            'amplitude': amplitude,
                            'center': center,
                            'width': width
                        })
                    elif function_type == 'Voigt':
                        sigma = float(param3_item.text())
                        gamma = float(param4_item.text())
                        peaks.append({
                            'function_type': function_type,
                            'amplitude': amplitude,
                            'center': center,
                            'sigma': sigma,
                            'gamma': gamma
                        })
                    elif function_type == 'Pseudo-Voigt':
                        width = float(param3_item.text())
                        fraction = float(param4_item.text())
                        peaks.append({
                            'function_type': function_type,
                            'amplitude': amplitude,
                            'center': center,
                            'width': width,
                            'fraction': fraction
                        })
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", f"Invalid numerical value in row {row + 1}.")
                    return None
        if not peaks:
            QMessageBox.warning(self, "No Peaks", "Please add and enable at least one peak.")
            return None

        print("get_parameters: Retrieved peaks:", peaks)

        return {'peaks': peaks}


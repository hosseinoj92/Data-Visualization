# gui/panels/data_fitting_panels.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDoubleValidator

class GaussianFittingPanel(QWidget):
    parameters_changed = pyqtSignal()
    run_peak_finder_signal = pyqtSignal()  # Define the signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Gaussian Fitting"
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()


        # Peak Parameters Table
        self.peak_table = QTableWidget(0, 5)
        self.peak_table.setHorizontalHeaderLabels(['Function', 'Amplitude', 'Center', 'Width', 'Enable'])
        self.peak_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(QLabel("Peaks"))
        layout.addWidget(self.peak_table)
        
        # Buttons to manage peaks
        buttons_layout = QHBoxLayout()
        self.add_peak_button = QPushButton("Add Peak")
        self.remove_peak_button = QPushButton("Remove Peak")
        buttons_layout.addWidget(self.add_peak_button)
        buttons_layout.addWidget(self.remove_peak_button)
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
            function_combo.addItems(['Gaussian', 'Lorentzian'])
            function_combo.setCurrentText(function_type)
            self.peak_table.setCellWidget(row_position, 0, function_combo)
            
            amplitude_item = QTableWidgetItem(f"{amplitude}")
            center_item = QTableWidgetItem(f"{center}")
            width_item = QTableWidgetItem(f"{width}")
            enable_item = QTableWidgetItem()
            enable_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            enable_item.setCheckState(Qt.Checked)

            self.peak_table.setItem(row_position, 1, amplitude_item)
            self.peak_table.setItem(row_position, 2, center_item)
            self.peak_table.setItem(row_position, 3, width_item)
            self.peak_table.setItem(row_position, 4, enable_item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error adding peak: {e}")
        finally:
            self.peak_table.blockSignals(False)  # Re-enable signals after adding the row



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
            amplitude_item = self.peak_table.item(row, 1)
            center_item = self.peak_table.item(row, 2)
            width_item = self.peak_table.item(row, 3)
            enable_item = self.peak_table.item(row, 4)
            if enable_item.checkState() == Qt.Checked:
                try:
                    amplitude = float(amplitude_item.text())
                    center = float(center_item.text())
                    width = float(width_item.text())
                    peaks.append({
                        'function_type': function_type,
                        'amplitude': amplitude,
                        'center': center,
                        'width': width
                    })
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", f"Invalid numerical value in row {row + 1}.")
                    return None
        if not peaks:
            QMessageBox.warning(self, "No Peaks", "Please add and enable at least one peak.")
            return None

        # Add debugging statement
        print("get_parameters: Retrieved peaks:", peaks)

        return {'peaks': peaks}

# gui/panels/data_fitting_panels.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QHBoxLayout, QMessageBox,QCheckBox
)
from PyQt5.QtCore import pyqtSignal

class CurveFittingPanel(QWidget):
    apply_button = pyqtSignal()
    save_button = pyqtSignal()
    send_to_data_panel_button = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Curve Fitting"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Select Fitting Type
        fitting_type_layout = QHBoxLayout()
        fitting_type_label = QLabel("Fitting Type:")
        self.fitting_type_combo = QComboBox()
        self.fitting_type_combo.addItems(["Polynomial", "Exponential", "Logarithmic"])
        fitting_type_layout.addWidget(fitting_type_label)
        fitting_type_layout.addWidget(self.fitting_type_combo)
        layout.addLayout(fitting_type_layout)

        # Degree for Polynomial
        self.degree_layout = QHBoxLayout()
        self.degree_label = QLabel("Degree:")
        self.degree_input = QLineEdit()
        self.degree_input.setPlaceholderText("Enter polynomial degree")
        self.degree_layout.addWidget(self.degree_label)
        self.degree_layout.addWidget(self.degree_input)
        layout.addLayout(self.degree_layout)

        # Parameters for Exponential/Logarithmic
        self.params_layout = QVBoxLayout()
        self.param1_layout = QHBoxLayout()
        self.param1_label = QLabel("Parameter 1:")
        self.param1_input = QLineEdit()
        self.param1_layout.addWidget(self.param1_label)
        self.param1_layout.addWidget(self.param1_input)
        self.params_layout.addLayout(self.param1_layout)

        self.param2_layout = QHBoxLayout()
        self.param2_label = QLabel("Parameter 2:")
        self.param2_input = QLineEdit()
        self.param2_layout.addWidget(self.param2_label)
        self.param2_layout.addWidget(self.param2_input)
        self.params_layout.addLayout(self.param2_layout)

        layout.addLayout(self.params_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply Fitting")
        self.save_btn = QPushButton("Save Fitting Results")
        self.send_btn = QPushButton("Send to Data Panel")
        buttons_layout.addWidget(self.apply_btn)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.send_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Connect buttons
        self.apply_btn.clicked.connect(self.apply_fitting)
        self.save_btn.clicked.connect(self.save_fitting_results)
        self.send_btn.clicked.connect(self.send_to_data_panel)

    def apply_fitting(self):
        # Emit the apply signal with necessary parameters
        self.apply_button.emit()

    def save_fitting_results(self):
        # Emit the save signal
        self.save_button.emit()

    def send_to_data_panel(self):
        # Emit the send signal
        self.send_to_data_panel_button.emit()

class ParameterOptimizationPanel(QWidget):
    apply_button = pyqtSignal()
    save_button = pyqtSignal()
    send_to_data_panel_button = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Parameter Optimization"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Optimization Method
        optimization_method_layout = QHBoxLayout()
        optimization_method_label = QLabel("Optimization Method:")
        self.optimization_method_combo = QComboBox()
        self.optimization_method_combo.addItems(["Least Squares", "Maximum Likelihood", "Bayesian"])
        optimization_method_layout.addWidget(optimization_method_label)
        optimization_method_layout.addWidget(self.optimization_method_combo)
        layout.addLayout(optimization_method_layout)

        # Initial Parameters
        initial_params_layout = QHBoxLayout()
        initial_params_label = QLabel("Initial Parameters:")
        self.initial_params_input = QLineEdit()
        self.initial_params_input.setPlaceholderText("Enter initial parameters separated by commas")
        initial_params_layout.addWidget(initial_params_label)
        initial_params_layout.addWidget(self.initial_params_input)
        layout.addLayout(initial_params_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply Optimization")
        self.save_btn = QPushButton("Save Optimization Results")
        self.send_btn = QPushButton("Send to Data Panel")
        buttons_layout.addWidget(self.apply_btn)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.send_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Connect buttons
        self.apply_btn.clicked.connect(self.apply_optimization)
        self.save_btn.clicked.connect(self.save_optimization_results)
        self.send_btn.clicked.connect(self.send_to_data_panel)

    def apply_optimization(self):
        self.apply_button.emit()

    def save_optimization_results(self):
        self.save_button.emit()

    def send_to_data_panel(self):
        self.send_to_data_panel_button.emit()

class ResidualAnalysisPanel(QWidget):
    apply_button = pyqtSignal()
    save_button = pyqtSignal()
    send_to_data_panel_button = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_name = "Residual Analysis"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Residual Plot Type
        residual_plot_layout = QHBoxLayout()
        residual_plot_label = QLabel("Residual Plot Type:")
        self.residual_plot_combo = QComboBox()
        self.residual_plot_combo.addItems(["Standard", "Normalized", "Percentage"])
        residual_plot_layout.addWidget(residual_plot_label)
        residual_plot_layout.addWidget(self.residual_plot_combo)
        layout.addLayout(residual_plot_layout)

        # Trend Line
        trend_line_layout = QHBoxLayout()
        self.trend_line_checkbox = QCheckBox("Add Trend Line")
        trend_line_layout.addWidget(self.trend_line_checkbox)
        layout.addLayout(trend_line_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply Residual Analysis")
        self.save_btn = QPushButton("Save Residual Analysis")
        self.send_btn = QPushButton("Send to Data Panel")
        buttons_layout.addWidget(self.apply_btn)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.send_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Connect buttons
        self.apply_btn.clicked.connect(self.apply_residual_analysis)
        self.save_btn.clicked.connect(self.save_residual_analysis)
        self.send_btn.clicked.connect(self.send_to_data_panel)

    def apply_residual_analysis(self):
        self.apply_button.emit()

    def save_residual_analysis(self):
        self.save_button.emit()

    def send_to_data_panel(self):
        self.send_to_data_panel_button.emit()

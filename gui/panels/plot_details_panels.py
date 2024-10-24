
import os
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QLabel, QFileDialog, QListWidgetItem, 
    QMessageBox, QScrollArea, QCheckBox, QWidget, QDialog, 
    QLineEdit,QComboBox, QListWidget, QGridLayout, QSpinBox,QColorDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import h5py
import pandas as pd
from gui.utils.widgets import DraggableListWidget  
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QColor

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
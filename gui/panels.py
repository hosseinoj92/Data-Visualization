# gui/panels.py

import os
from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QScrollArea, QCheckBox, QSpinBox, QComboBox, QHBoxLayout,
    QListWidgetItem, QColorDialog, QMessageBox, QFileDialog, QWidget
)
from PyQt5.QtCore import Qt

class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.MultiSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    file_name = os.path.basename(file_path)
                    item = QListWidgetItem(file_name)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                    item.setData(Qt.UserRole, file_path)
                    self.addItem(item)
        else:
            event.ignore()

class SelectedDataPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Selected Data", parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.file_selector_button = QPushButton("Choose Files")
        self.add_file_button = QPushButton("Add Files")
        self.select_all_button = QPushButton("Select All")
        self.selected_files_list = DraggableListWidget()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.selected_files_list)

        self.layout.addWidget(self.file_selector_button)
        self.layout.addWidget(self.add_file_button)
        self.layout.addWidget(self.select_all_button)
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

    def get_selected_files(self):
        selected_items = [
            item for item in self.selected_files_list.findItems("*", Qt.MatchWildcard)
            if item.checkState() == Qt.Checked
        ]
        return [item.data(Qt.UserRole) for item in selected_items]

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
    def __init__(self, parent=None):
        super().__init__("Additional Text", parent)
        self.init_ui()
        self.text_color = 'black'  # Default text color

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

        self.add_text_button = QPushButton("Add to Plot")
        self.delete_text_button = QPushButton("Delete from Plot")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_text_button)
        button_layout.addWidget(self.delete_text_button)

        self.layout.addLayout(button_layout, 5, 0, 1, 3)

        self.setLayout(self.layout)

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


'''class NormalizationMethodPanel(QWidget):
    def __init__(self, method_name):
        super().__init__()
        self.method_name = method_name
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Add input fields based on method_name
        if self.method_name == "Area Within a Specific Interval":
            self.layout.addWidget(QLabel("Start Interval:"))
            self.start_interval_input = QLineEdit()
            self.layout.addWidget(self.start_interval_input)

            self.layout.addWidget(QLabel("End Interval:"))
            self.end_interval_input = QLineEdit()
            self.layout.addWidget(self.end_interval_input)
        elif self.method_name == "Normalization to a Reference Peak":
            self.layout.addWidget(QLabel("Reference Peak Index:"))
            self.reference_peak_index_input = QLineEdit()
            self.layout.addWidget(self.reference_peak_index_input)
        elif self.method_name == "Multiplicative Scatter Correction (MSC)":
            self.layout.addWidget(QLabel("Reference Spectrum File:"))
            self.reference_spectrum_button = QPushButton("Choose Reference Spectrum")
            self.layout.addWidget(self.reference_spectrum_button)
            self.reference_spectrum_button.clicked.connect(self.choose_reference_spectrum)
        elif self.method_name == "Baseline Correction Normalization":
            self.layout.addWidget(QLabel("Baseline File:"))
            self.baseline_file_button = QPushButton("Choose Baseline File")
            self.layout.addWidget(self.baseline_file_button)
            self.baseline_file_button.clicked.connect(self.choose_baseline_file)
        elif self.method_name == "Normalization Within a Moving Window":
            self.layout.addWidget(QLabel("Window Size:"))
            self.window_size_input = QLineEdit()
            self.layout.addWidget(self.window_size_input)
        # For other methods, no additional inputs are needed

        # Add Apply button
        self.apply_button = QPushButton("Apply Normalization")
        self.layout.addWidget(self.apply_button)

    def get_parameters(self):
        params = {}
        if self.method_name == "Area Within a Specific Interval":
            try:
                start = float(self.start_interval_input.text())
                end = float(self.end_interval_input.text())
                params['interval'] = (start, end)
            except ValueError:
                QMessageBox.warning(self, "Invalid Parameters", "Please enter valid interval values.")
                return None
        elif self.method_name == "Normalization to a Reference Peak":
            try:
                reference_peak_index = int(self.reference_peak_index_input.text())
                params['reference_peak_index'] = reference_peak_index
            except ValueError:
                QMessageBox.warning(self, "Invalid Parameters", "Please enter a valid reference peak index.")
                return None
        elif self.method_name == "Multiplicative Scatter Correction (MSC)":
            if not hasattr(self, 'reference_spectrum_file'):
                QMessageBox.warning(self, "Missing Reference", "Please choose a reference spectrum file.")
                return None
            else:
                params['reference_spectrum_file'] = self.reference_spectrum_file
        elif self.method_name == "Baseline Correction Normalization":
            if not hasattr(self, 'baseline_file'):
                QMessageBox.warning(self, "Missing Baseline", "Please choose a baseline file.")
                return None
            else:
                params['baseline_file'] = self.baseline_file
        elif self.method_name == "Normalization Within a Moving Window":
            try:
                window_size = int(self.window_size_input.text())
                params['window_size'] = window_size
            except ValueError:
                QMessageBox.warning(self, "Invalid Parameters", "Please enter a valid window size.")
                return None
        # For other methods, no parameters
        return params

    def choose_reference_spectrum(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Reference Spectrum", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            self.reference_spectrum_file = file_path
            self.reference_spectrum_button.setText(os.path.basename(file_path))

    def choose_baseline_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Baseline File", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            self.baseline_file = file_path
            self.baseline_file_button.setText(os.path.basename(file_path))'''


# gui/panels.py

class NormalizationMethodPanel(QWidget):
    def __init__(self, method_name):
        super().__init__()
        self.method_name = method_name
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Add input fields based on method_name
        if self.method_name == "Area Within a Specific Interval":
            self.layout.addWidget(QLabel("Start Interval:"))
            self.start_interval_input = QLineEdit()
            self.layout.addWidget(self.start_interval_input)

            self.layout.addWidget(QLabel("End Interval:"))
            self.end_interval_input = QLineEdit()
            self.layout.addWidget(self.end_interval_input)
        
        elif self.method_name == "Normalization to a Reference Peak":
            self.layout.addWidget(QLabel("Reference Peak Index:"))
            self.reference_peak_index_input = QLineEdit()
            self.layout.addWidget(self.reference_peak_index_input)
        
        elif self.method_name == "Multiplicative Scatter Correction (MSC)":
            self.layout.addWidget(QLabel("Reference Spectrum File:"))
            self.reference_spectrum_button = QPushButton("Choose Reference Spectrum")
            self.layout.addWidget(self.reference_spectrum_button)
            self.reference_spectrum_button.clicked.connect(self.choose_reference_spectrum)
        
        elif self.method_name == "Baseline Correction Normalization":
            self.layout.addWidget(QLabel("Baseline File:"))
            self.baseline_file_button = QPushButton("Choose Baseline File")
            self.layout.addWidget(self.baseline_file_button)
            self.baseline_file_button.clicked.connect(self.choose_baseline_file)
        
        elif self.method_name == "Normalization Within a Moving Window":
            self.layout.addWidget(QLabel("Window Size:"))
            self.window_size_input = QLineEdit()
            self.layout.addWidget(self.window_size_input)
        
        # Add Apply and Save buttons
        self.apply_button = QPushButton("Apply Normalization")
        self.save_button = QPushButton("Save Normalized Data")
        self.layout.addWidget(self.apply_button)
        self.layout.addWidget(self.save_button)

    def choose_reference_spectrum(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Reference Spectrum", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            self.reference_spectrum_file = file_path
            self.reference_spectrum_button.setText(os.path.basename(file_path))

    def choose_baseline_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Baseline File", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            self.baseline_file = file_path
            self.baseline_file_button.setText(os.path.basename(file_path))

    def get_parameters(self):
        params = {}
        try:
            if self.method_name == "Area Within a Specific Interval":
                start = float(self.start_interval_input.text())
                end = float(self.end_interval_input.text())
                params['interval'] = (start, end)
            
            elif self.method_name == "Normalization to a Reference Peak":
                reference_peak_index = int(self.reference_peak_index_input.text())
                params['reference_peak_index'] = reference_peak_index
            
            elif self.method_name == "Multiplicative Scatter Correction (MSC)":
                if not hasattr(self, 'reference_spectrum_file'):
                    QMessageBox.warning(self, "Missing Reference", "Please choose a reference spectrum file.")
                    return None
                params['reference'] = self.reference_spectrum_file
            
            elif self.method_name == "Baseline Correction Normalization":
                if not hasattr(self, 'baseline_file'):
                    QMessageBox.warning(self, "Missing Baseline", "Please choose a baseline file.")
                    return None
                params['baseline'] = self.baseline_file
            
            elif self.method_name == "Normalization Within a Moving Window":
                window_size = int(self.window_size_input.text())
                params['window_size'] = window_size
            
        except ValueError:
            QMessageBox.warning(self, "Invalid Parameters", "Please enter valid parameter values.")
            return None

        return params

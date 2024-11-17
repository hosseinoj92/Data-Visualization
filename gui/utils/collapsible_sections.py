# gui/utils/collapsible_sections.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QToolButton, QScrollArea, QSizePolicy,
    QPushButton, QHBoxLayout, QFrame, QFileDialog, QListWidgetItem, QColorDialog, QTableWidget, QHeaderView, QTableWidgetItem,
    QMessageBox, QButtonGroup, QGroupBox, QVBoxLayout, QDialog, 
    QComboBox, QSpinBox, QCheckBox, QLineEdit, QDoubleSpinBox,QFormLayout

)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QIcon

from gui.panels.selected_data_panel import SelectedDataPanel
from gui.panels.plot_details_panels import ( AxisDetailsPanel, AdditionalTextPanel,
    CustomAnnotationsPanel, PlotVisualsPanel, PlotDetailsPanel, )

from plots.plotting import plot_data
from gui.dialogs.latex_compatibility_dialog import LaTeXCompatibilityDialog 

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
import matplotlib.text
from gui.plot.expanded_plot_window import ExpandedPlotWindow 
from gui.dialogs.save_plot_dialog import SavePlotDialog
import seaborn as sns
from matplotlib import style
from matplotlib import font_manager as fm
import sys
from fontTools.ttLib import TTFont
from PyQt5.QtCore import Qt, pyqtSignal, QEvent





def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

####################################

class CollapsibleSection(QWidget):

    # Define a custom signal that emits the instance of the expanded section
    section_expanded = pyqtSignal(object)

    def __init__(self, title, content_widget, parent=None):
        super().__init__(parent)
        self.toggle_button = QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        # Connect the toggled signal instead of clicked
        self.toggle_button.toggled.connect(self.on_toggle)

        self.content_area = QWidget()
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        self.setLayout(main_layout)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(15, 0, 0, 0)
        self.content_layout.setSpacing(5)
        self.content_area.setLayout(self.content_layout)
        self.content_layout.addWidget(content_widget)

    def on_toggle(self, checked):
        if checked:
            print(f"'{self.toggle_button.text()}' section expanded.")
            self.toggle_button.setArrowType(Qt.DownArrow)
            self.content_area.setMaximumHeight(16777215)  # Expand to full size
            # Emit the signal indicating this section has been expanded
            self.section_expanded.emit(self)
        else:
            print(f"'{self.toggle_button.text()}' section collapsed.")
            self.toggle_button.setArrowType(Qt.RightArrow)
            self.content_area.setMaximumHeight(0)  # Collapse




class SubplotsConfigDialog(QDialog):
    apply_clicked = pyqtSignal()  

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Subplots")

        self.resize(800, 600)
        self.setMinimumSize(700, 600)
 
        self.current_configs = []  # List of configurations (dictionaries)
        self.subplot_configs = []  # To store subplot configurations
        self.subplot_containers = []  # To store subplot containers
        self.is_first_subplot = True  # Flag to check if it's the first subplot
        self.layout_settings = {'rows': 1, 'columns': 1, 'auto_layout': False}
        self.general_tab = parent  # Store the reference to GeneralTab

        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout()

        # Buttons to add/remove subplots
        buttons_layout = QHBoxLayout()
        self.add_subplot_button = QPushButton("Add Subplot")
        self.add_subplot_button.clicked.connect(self.add_subplot)
        self.remove_subplot_button = QPushButton("Remove Selected Subplot")
        self.remove_subplot_button.clicked.connect(self.remove_selected_subplots)
        buttons_layout.addWidget(self.add_subplot_button)
        buttons_layout.addWidget(self.remove_subplot_button)
        self.main_layout.addLayout(buttons_layout)

        # Scroll area to hold subplot configurations
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.subplots_container = QWidget()
        self.subplots_layout = QVBoxLayout()
        self.subplots_container.setLayout(self.subplots_layout)
        self.scroll_area.setWidget(self.subplots_container)
        self.main_layout.addWidget(self.scroll_area)

        # Layout settings
        layout_settings_group = QGroupBox("Layout Settings")
        layout_settings_layout = QHBoxLayout()
        layout_settings_group.setLayout(layout_settings_layout)

        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setMinimum(1)
        self.rows_spinbox.setValue(1)
        self.columns_spinbox = QSpinBox()
        self.columns_spinbox.setMinimum(1)
        self.columns_spinbox.setValue(1)
        self.auto_layout_checkbox = QCheckBox("Auto Layout")
        self.auto_layout_checkbox.stateChanged.connect(self.toggle_layout_inputs)

        layout_settings_layout.addWidget(QLabel("Rows:"))
        layout_settings_layout.addWidget(self.rows_spinbox)
        layout_settings_layout.addWidget(QLabel("Columns:"))
        layout_settings_layout.addWidget(self.columns_spinbox)
        layout_settings_layout.addWidget(self.auto_layout_checkbox)

        self.main_layout.addWidget(layout_settings_group)

        # Action buttons
        action_buttons_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.on_apply_clicked)  # Connect to custom method
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(self.apply_button)
        action_buttons_layout.addWidget(self.cancel_button)
        self.main_layout.addLayout(action_buttons_layout)

        self.setLayout(self.main_layout)
        
    def get_current_configs(self):
        return self.current_configs

    def toggle_layout_inputs(self, state):
        if state == Qt.Checked:
            self.rows_spinbox.setEnabled(False)
            self.columns_spinbox.setEnabled(False)
        else:
            self.rows_spinbox.setEnabled(True)
            self.columns_spinbox.setEnabled(True)

    def add_subplot(self):
        subplot_container = SubplotContainer(self.general_tab, self)
        self.subplots_layout.addWidget(subplot_container)
        self.subplot_containers.append(subplot_container)
        self.subplot_configs.append(subplot_container.subplot_config_widget)
        # Automatically add an initial dataset to prevent crashes
        subplot_container.subplot_config_widget.add_dataset()


    def on_apply_clicked(self):
        # Collect the current configurations without overwriting self.subplot_configs
        self.current_configs = self.get_subplot_configs()
        self.layout_settings = self.get_layout_settings()
        # Emit the signal to update the plot
        self.apply_clicked.emit()

    def remove_selected_subplots(self):
        to_remove = []
        for idx, container in enumerate(self.subplot_containers):
            subplot = container.subplot_config_widget
            if subplot.remove_checkbox.isChecked():
                self.subplots_layout.removeWidget(container)
                container.deleteLater()
                to_remove.append(idx)
        for idx in reversed(to_remove):
            del self.subplot_configs[idx]
            del self.subplot_containers[idx]
        # Reset the is_first_subplot flag in case all subplots are removed
        if not self.subplot_containers:
            self.is_first_subplot = True

    def get_subplot_configs(self):
        configs = []
        for subplot in self.subplot_configs:
            config = subplot.get_config()
            if config and config['datasets']:
                configs.append(config)
        return configs

    def get_layout_settings(self):
        return {
            'rows': self.rows_spinbox.value(),
            'columns': self.columns_spinbox.value(),
            'auto_layout': self.auto_layout_checkbox.isChecked()
        }

    

# In SubplotConfigWidget within tabs.py

class SubplotConfigWidget(QWidget):
    def __init__(self, general_tab, parent=None):
        super().__init__(parent)
        self.general_tab = general_tab  # Store the GeneralTab reference

        self.legend_location_mapping = {
            "Best": "best",
            "Upper Right": "upper right",
            "Upper Left": "upper left",
            "Lower Left": "lower left",
            "Lower Right": "lower right",
            "Right": "right",
            "Center Left": "center left",
            "Center Right": "center right",
            "Lower Center": "lower center",
            "Upper Center": "upper center",
            "Center": "center"
        }

        self.advanced_options = {}  # To store advanced options for this subplot

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Use QFormLayout for the subplot details
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft)
        form_layout.setSpacing(10)

        # Subplot Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter subplot title")
        form_layout.addRow("Subplot Title:", self.title_input)

        # Title Font Size
        self.title_font_size_spinbox = QSpinBox()
        self.title_font_size_spinbox.setRange(6, 24)
        self.title_font_size_spinbox.setValue(14)
        form_layout.addRow("Title Font Size:", self.title_font_size_spinbox)

        # X Axis Label
        self.x_axis_label_input = QLineEdit()
        self.x_axis_label_input.setPlaceholderText("Enter X axis label")
        form_layout.addRow("X Axis Label:", self.x_axis_label_input)

        # Y Axis Label
        self.y_axis_label_input = QLineEdit()
        self.y_axis_label_input.setPlaceholderText("Enter Y axis label")
        form_layout.addRow("Y Axis Label:", self.y_axis_label_input)

        main_layout.addLayout(form_layout)

        # Advanced Options Button
        self.advanced_options_button = QPushButton("Advanced Options")
        advanced_options_icon_path = resource_path("gui/resources/advanced_options_icon.png")
        if os.path.exists(advanced_options_icon_path):
            self.advanced_options_button.setIcon(QIcon(advanced_options_icon_path))
        else:
            print(f"Warning: Advanced Options icon not found at {advanced_options_icon_path}")
        self.advanced_options_button.clicked.connect(self.open_advanced_options_dialog)
        main_layout.addWidget(self.advanced_options_button)

        # Container for multiple DatasetConfigWidgets
        self.datasets_container = QVBoxLayout()
        main_layout.addLayout(self.datasets_container)

        # Buttons to add/remove datasets
        datasets_buttons_layout = QHBoxLayout()
        self.add_dataset_button = QPushButton("Add Dataset")
        add_icon_path = resource_path("gui/resources/add.png")
        if os.path.exists(add_icon_path):
            self.add_dataset_button.setIcon(QIcon(add_icon_path))
        else:
            print(f"Warning: Add icon not found at {add_icon_path}")
        self.add_dataset_button.clicked.connect(self.add_dataset)
        self.remove_dataset_button = QPushButton("Remove Selected Dataset")
        remove_icon_path = resource_path("gui/resources/remove.png")
        if os.path.exists(remove_icon_path):
            self.remove_dataset_button.setIcon(QIcon(remove_icon_path))
        else:
            print(f"Warning: Remove icon not found at {remove_icon_path}")
        self.remove_dataset_button.clicked.connect(self.remove_selected_datasets)
        datasets_buttons_layout.addWidget(self.add_dataset_button)
        datasets_buttons_layout.addWidget(self.remove_dataset_button)
        main_layout.addLayout(datasets_buttons_layout)

        # Grid Options
        grid_layout = QHBoxLayout()
        self.enable_grid_checkbox = QCheckBox("Enable Grid")
        self.enable_grid_checkbox.setChecked(True)  # Set default to checked
        grid_layout.addWidget(self.enable_grid_checkbox)
        main_layout.addLayout(grid_layout)

        # Legend Options
        legend_layout = QFormLayout()
        self.enable_legend_checkbox = QCheckBox("Enable Legend")
        self.enable_legend_checkbox.setChecked(True)  # Set default to checked

        self.legend_location_dropdown = QComboBox()
        self.legend_location_dropdown.addItems([
            "Best", "Upper Right", "Upper Left", "Lower Left",
            "Lower Right", "Right", "Center Left", "Center Right",
            "Lower Center", "Upper Center", "Center"
        ])
        self.legend_location_dropdown.setMaximumWidth(150)

        self.legend_font_size_spinbox = QSpinBox()
        self.legend_font_size_spinbox.setRange(6, 24)
        self.legend_font_size_spinbox.setValue(10)
        self.legend_font_size_spinbox.setMaximumWidth(100)

        legend_layout.addRow(self.enable_legend_checkbox)
        legend_layout.addRow("Legend Location:", self.legend_location_dropdown)
        legend_layout.addRow("Legend Font Size:", self.legend_font_size_spinbox)
        main_layout.addLayout(legend_layout)

        # Remove Subplot Checkbox
        remove_layout = QHBoxLayout()
        self.remove_checkbox = QCheckBox("Remove Subplot")
        remove_layout.addStretch()
        remove_layout.addWidget(self.remove_checkbox)
        main_layout.addLayout(remove_layout)

        self.setLayout(main_layout)

    def open_advanced_options_dialog(self):
        dialog = SubplotAdvancedOptionsDialog(self)
        # Pre-populate dialog with existing advanced options
        dialog.set_advanced_options(self.advanced_options)
        if dialog.exec_() == QDialog.Accepted:
            # Retrieve the advanced options from the dialog
            self.advanced_options = dialog.get_advanced_options()
        else:
            pass  # Do nothing if canceled


    def add_dataset(self):
        dataset_widget = DatasetConfigWidget(self.general_tab, self)
        self.datasets_container.addWidget(dataset_widget)

    def remove_selected_datasets(self):
        # Iterate in reverse to safely remove widgets while iterating
        for i in reversed(range(self.datasets_container.count())):
            dataset_widget = self.datasets_container.itemAt(i).widget()
            if dataset_widget and dataset_widget.remove_checkbox.isChecked():
                self.datasets_container.removeWidget(dataset_widget)
                dataset_widget.deleteLater()

    def get_config(self):
        config = {}
        config['subplot_title'] = self.title_input.text()
        config['title_font_size'] = self.title_font_size_spinbox.value()
        config['x_axis_label'] = self.x_axis_label_input.text()
        config['y_axis_label'] = self.y_axis_label_input.text()
        config['enable_grid'] = self.enable_grid_checkbox.isChecked()
        config['enable_legend'] = self.enable_legend_checkbox.isChecked()

        # Map legend location to Matplotlib value
        legend_location_display = self.legend_location_dropdown.currentText()
        legend_location = self.legend_location_mapping.get(legend_location_display, 'best')
        config['legend_location'] = legend_location

        config['legend_font_size'] = self.legend_font_size_spinbox.value()
        config['datasets'] = []

        # Include advanced options
        config['advanced_options'] = self.advanced_options  
        config['advanced_options'] = self.advanced_options

        # Include LaTeX options if they exist
        if hasattr(self, 'latex_options'):
            config['latex_options'] = self.latex_options  
        else:
            config['latex_options'] = None  

        for i in range(self.datasets_container.count()):
            dataset_widget = self.datasets_container.itemAt(i).widget()
            if dataset_widget:
                dataset_config = dataset_widget.get_config()
                if dataset_config['dataset']:
                    config['datasets'].append(dataset_config)

        return config




class DatasetConfigWidget(QWidget):
    def __init__(self, general_tab, parent=None):
        super().__init__(parent)
        self.general_tab = general_tab  # Store the GeneralTab reference
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # First Row
        row1_layout = QHBoxLayout()

        # Dataset selection
        row1_layout.addWidget(QLabel("Dataset:"))
        self.dataset_dropdown = QComboBox()
        self.dataset_dropdown.setMaximumWidth(150)
        self.dataset_dropdown.currentIndexChanged.connect(self.update_columns)
        row1_layout.addWidget(self.dataset_dropdown)

        # X Column selection
        row1_layout.addWidget(QLabel("X Column:"))
        self.x_column_dropdown = QComboBox()
        self.x_column_dropdown.setMaximumWidth(100)
        row1_layout.addWidget(self.x_column_dropdown)

        # Y Column selection
        row1_layout.addWidget(QLabel("Y Column:"))
        self.y_column_dropdown = QComboBox()
        self.y_column_dropdown.setMaximumWidth(100)
        row1_layout.addWidget(self.y_column_dropdown)

        # Legend Label
        row1_layout.addWidget(QLabel("Legend Label:"))
        self.legend_label_input = QLineEdit()
        self.legend_label_input.setMaximumWidth(150)
        row1_layout.addWidget(self.legend_label_input)

        main_layout.addLayout(row1_layout)

        # Second Row
        row2_layout = QHBoxLayout()

        # Line Style
        row2_layout.addWidget(QLabel("Line Style:"))
        self.line_style_combo = QComboBox()
        self.line_style_combo.addItems(['Solid', 'Dashed', 'Dash-Dot', 'None'])
        self.line_style_combo.setMaximumWidth(100)
        row2_layout.addWidget(self.line_style_combo)

        # Point Style
        row2_layout.addWidget(QLabel("Point Style:"))
        self.point_style_combo = QComboBox()
        self.point_style_combo.addItems([
            'None', 'Circle', 'Square', 'Triangle Up', 'Triangle Down', 'Star',
            'Plus', 'Cross', 'Diamond', 'Pentagon', 'Hexagon'
        ])
        self.point_style_combo.setMaximumWidth(100)
        row2_layout.addWidget(self.point_style_combo)

        # Line Thickness
        row2_layout.addWidget(QLabel("Line Thickness:"))
        self.line_thickness_spinbox = QDoubleSpinBox()
        self.line_thickness_spinbox.setRange(0.1, 10.0)
        self.line_thickness_spinbox.setSingleStep(0.1)
        self.line_thickness_spinbox.setValue(1.0)
        self.line_thickness_spinbox.setMaximumWidth(80)
        row2_layout.addWidget(self.line_thickness_spinbox)

        # Remove Dataset Checkbox
        self.remove_checkbox = QCheckBox("Remove")
        row2_layout.addWidget(self.remove_checkbox)

        # Add spacer to push the Remove checkbox to the right
        row2_layout.addStretch()

        main_layout.addLayout(row2_layout)

        self.setLayout(main_layout)

        # Now populate datasets after initializing all widgets
        self.populate_datasets()

    def populate_datasets(self):
        data_files = self.general_tab.selected_data_panel.get_selected_files()
        self.dataset_dropdown.clear()
        for file in data_files:
            file_name = os.path.basename(file)
            self.dataset_dropdown.addItem(file_name, userData=file)
        if self.dataset_dropdown.count() > 0:
            self.dataset_dropdown.setCurrentIndex(0)
            self.update_columns()

    def update_columns(self):
        dataset_index = self.dataset_dropdown.currentIndex()
        dataset_path = self.dataset_dropdown.itemData(dataset_index)
        if not dataset_path:
            return
        try:
            df = pd.read_csv(dataset_path)
            columns = df.columns.tolist()
            self.x_column_dropdown.clear()
            self.y_column_dropdown.clear()
            for idx, col in enumerate(columns, start=1):
                display_text = f"{idx}: {col}"
                self.x_column_dropdown.addItem(display_text, userData=idx - 1)
                self.y_column_dropdown.addItem(display_text, userData=idx - 1)
            if self.x_column_dropdown.count() > 0:
                self.x_column_dropdown.setCurrentIndex(0)  # Set first column as default for X
            if self.y_column_dropdown.count() > 1:
                self.y_column_dropdown.setCurrentIndex(1)  # Set second column as default for Y
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load columns from {dataset_path}: {e}")

    def get_config(self):
        config = {}
        config['dataset'] = self.dataset_dropdown.currentData()
        config['x_column'] = self.x_column_dropdown.currentData()
        config['y_column'] = self.y_column_dropdown.currentData()
        legend_label = self.legend_label_input.text() or os.path.splitext(os.path.basename(config['dataset']))[0]
        config['legend_label'] = rf"{legend_label}"  # Use raw string

        # Get styling options
        config['line_style'] = self.line_style_combo.currentText()
        config['point_style'] = self.point_style_combo.currentText()
        config['line_thickness'] = self.line_thickness_spinbox.value()

        return config
class SubplotAdvancedOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Options")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Scale Type
        scale_type_layout = QHBoxLayout()
        scale_type_layout.addWidget(QLabel("Scale Type:"))
        self.scale_type_combo = QComboBox()
        self.scale_type_combo.addItems(["Linear", "Logarithmic X-Axis", "Logarithmic Y-Axis", "Logarithmic Both Axes"])
        scale_type_layout.addWidget(self.scale_type_combo)
        layout.addLayout(scale_type_layout)

        # Plot Style
        plot_style_layout = QHBoxLayout()
        plot_style_layout.addWidget(QLabel("Plot Style:"))
        self.plot_style_combo = QComboBox()
        # Dynamically get available styles from Matplotlib
        available_styles = plt.style.available
        self.plot_style_combo.addItems(available_styles)
        plot_style_layout.addWidget(self.plot_style_combo)
        layout.addLayout(plot_style_layout)

        # Action Buttons
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def set_advanced_options(self, options):
        # Set the dialog widgets based on the provided options
        self.scale_type_combo.setCurrentText(options.get('scale_type', 'Linear'))
        self.plot_style_combo.setCurrentText(options.get('plot_style', 'default'))

    def get_advanced_options(self):
        options = {
            'scale_type': self.scale_type_combo.currentText(),
            'plot_style': self.plot_style_combo.currentText()
        }
        return options


class SubplotContainer(QWidget):
    def __init__(self, general_tab, parent=None):
        super().__init__(parent)
        self.general_tab = general_tab
        self.parent_dialog = parent  # Reference to SubplotsConfigDialog
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add separator line at the top (except for the first subplot)
        if not self.parent_dialog.is_first_subplot:
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            separator.setStyleSheet("QFrame { color: black; }")  
            layout.addWidget(separator)
        else:
            # Indicate that the first subplot has been added
            self.parent_dialog.is_first_subplot = False

        # Add the SubplotConfigWidget
        self.subplot_config_widget = SubplotConfigWidget(self.general_tab, self)
        layout.addWidget(self.subplot_config_widget)

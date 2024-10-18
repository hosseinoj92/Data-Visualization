# gui/normalization_tab.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QToolButton, QScrollArea, QSizePolicy,
    QPushButton, QHBoxLayout, QFrame, QFileDialog, QListWidgetItem, QColorDialog, QTableWidget, QHeaderView, QTableWidgetItem,
    QMessageBox,QTextEdit,
      QButtonGroup, QGroupBox, QVBoxLayout, QDialog, QComboBox, QSpinBox, QCheckBox, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QIcon

from gui.panels import (
    SelectedDataPanel, AxisDetailsPanel, AdditionalTextPanel,
    CustomAnnotationsPanel, PlotVisualsPanel, PlotDetailsPanel, 
    MinMaxNormalizationPanel, ZScoreNormalizationPanel, RobustScalingNormalizationPanel,
    AUCNormalizationPanel,IntervalAUCNormalizationPanel,TotalIntensityNormalizationPanel,
    ReferencePeakNormalizationPanel
)
from plots.plotting import plot_data
from gui.latex_compatibility_dialog import LaTeXCompatibilityDialog 
from gui.collapsible_sections import * 

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
import matplotlib.text
from gui.expanded_plot_window import ExpandedPlotWindow 
from gui.save_plot_dialog import SavePlotDialog
import seaborn as sns
from matplotlib import style
from matplotlib import font_manager as fm
import sys
from fontTools.ttLib import TTFont
from utils import read_numeric_data
from functools import partial 

################################################################


class NormalizationTab(QWidget):

    plot_updated = pyqtSignal()  # Define the custom signal

    def __init__(self, general_tab, parent=None):
        super().__init__(parent)
        self.general_tab = general_tab
        self.is_collapsing = False  # Flag to prevent recursive signal handling
        self.init_ui()
        self.expanded_window = None  # To track the expanded window

    def init_ui(self):
        self.layout = QGridLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        # Initialize last_directory
        self.last_directory = os.path.expanduser("~")  

        # Column 0: Selected Data and Collapsible Sections
        self.selected_data_panel = SelectedDataPanel(include_retract_button=True)

        # Create collapsible sections for other panels
        self.collapsible_sections = []

        # Plot Details Section
        self.plot_details_panel = PlotDetailsPanel()
        plot_details_section = CollapsibleSection("Plot Details", self.plot_details_panel)
        plot_details_section.section_expanded.connect(self.on_section_expanded)
        self.collapsible_sections.append(plot_details_section)

        # Axis Details Section
        self.axis_details_panel = AxisDetailsPanel()
        axis_details_section = CollapsibleSection("Axis Details", self.axis_details_panel)
        axis_details_section.section_expanded.connect(self.on_section_expanded)
        self.collapsible_sections.append(axis_details_section)

        # Plot Visuals Section
        self.plot_visuals_panel = PlotVisualsPanel()
        plot_visuals_section = CollapsibleSection("Plot Visuals", self.plot_visuals_panel)
        plot_visuals_section.section_expanded.connect(self.on_section_expanded)
        self.collapsible_sections.append(plot_visuals_section)

        # Custom Annotations Section
        self.custom_annotations_panel = CustomAnnotationsPanel()
        custom_annotations_section = CollapsibleSection("Custom Annotations", self.custom_annotations_panel)
        custom_annotations_section.section_expanded.connect(self.on_section_expanded)
        self.collapsible_sections.append(custom_annotations_section)

        # Additional Text Section
        self.additional_text_panel = AdditionalTextPanel()
        additional_text_section = CollapsibleSection("Additional Text", self.additional_text_panel)
        additional_text_section.section_expanded.connect(self.on_section_expanded)
        self.collapsible_sections.append(additional_text_section)

        # QGroupBox for Plot Handling
        self.plot_handling_groupbox = QGroupBox("Plot Handling")
        plot_handling_layout = QVBoxLayout()
        self.plot_handling_groupbox.setLayout(plot_handling_layout)

        # Add collapsible sections to the plot handling layout
        for section in self.collapsible_sections:
            plot_handling_layout.addWidget(section)

        # Arrange Column 0
        column0_layout = QVBoxLayout()
        column0_layout.addWidget(self.selected_data_panel)
        column0_layout.addWidget(self.plot_handling_groupbox)
        column0_layout.addStretch()  # Push content to the top

        column0_widget = QWidget()
        column0_widget.setLayout(column0_layout)
        self.layout.addWidget(column0_widget, 0, 0)

        # Column 1: Normalization Functionalities with Collapsible Sections

        # Define normalization methods and their corresponding panels
        self.normalization_methods = [
            ("Min-Max Normalization", MinMaxNormalizationPanel),
            ("Z-score Normalization", ZScoreNormalizationPanel),
            ("Robust Scaling Normalization", RobustScalingNormalizationPanel),
            ("AUC Normalization", AUCNormalizationPanel), 
            ("Interval AUC Normalization", IntervalAUCNormalizationPanel),
            ("Total Intensity Normalization", TotalIntensityNormalizationPanel),
            ("Reference Peak Normalization", ReferencePeakNormalizationPanel), 
            
        ]

        self.normalization_sections = []

        # Create NormalizationMethodPanel for each method
        for method_name, panel_class in self.normalization_methods:
            panel = panel_class()
            section = CollapsibleSection(method_name, panel)
            section.section_expanded.connect(self.on_normalization_section_expanded)
            self.normalization_sections.append(section)

            # Connect Apply and Save buttons to the respective methods
            panel.apply_button.clicked.connect(lambda checked, p=panel: self.apply_normalization(p))
            panel.save_button.clicked.connect(lambda checked, p=panel: self.save_normalized_data(p))

        # QGroupBox for Normalization Methods
        self.normalization_methods_groupbox = QGroupBox("Normalization Methods")
        normalization_methods_layout = QVBoxLayout()
        self.normalization_methods_groupbox.setLayout(normalization_methods_layout)

        # Add normalization sections to the normalization methods layout
        for section in self.normalization_sections:
            normalization_methods_layout.addWidget(section)

        # Optionally, add a label if no normalization methods are available
        if not self.normalization_methods:
            normalization_methods_layout.addWidget(QLabel("No normalization methods available."))

        # Basic Corrections GroupBox (empty for now)
        self.basic_corrections_groupbox = QGroupBox("Basic Corrections")
        basic_corrections_layout = QVBoxLayout()
        self.basic_corrections_groupbox.setLayout(basic_corrections_layout)
        # Add widgets to basic_corrections_layout in future steps

        # Arrange Column 1
        column1_layout = QVBoxLayout()
        column1_layout.setContentsMargins(0, 0, 0, 0)
        column1_layout.setSpacing(10)

        # Add the "Basic Corrections" and "Normalization Methods" panels
        column1_layout.addWidget(self.basic_corrections_groupbox)
        column1_layout.addWidget(self.normalization_methods_groupbox)
        column1_layout.addStretch()

        column1_widget = QWidget()
        column1_widget.setLayout(column1_layout)
        self.layout.addWidget(column1_widget, 0, 1)

        # Column 2: Plotting Interface
        # Plot area
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Create a QFrame with rounded corners for the plot
        self.plot_frame = QFrame()
        self.plot_frame.setObjectName("PlotFrame")
        self.plot_frame.setFrameShape(QFrame.StyledPanel)
        self.plot_frame.setFrameShadow(QFrame.Raised)

        # Set layout for plot_frame
        self.plot_frame_layout = QVBoxLayout(self.plot_frame)
        self.plot_frame_layout.setContentsMargins(5, 5, 5, 5)
        self.plot_frame_layout.addWidget(self.toolbar)
        self.plot_frame_layout.addWidget(self.canvas)

        # Plot area layout
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.plot_frame)

        # Control Buttons
        self.update_button = QPushButton("Update Plot")
        self.update_button.setIcon(QIcon('gui/resources/update_icon.png'))
        self.update_button.clicked.connect(self.update_plot)

        self.show_data_structure_button = QPushButton("Show Data Structure")
        self.show_data_structure_button.setIcon(QIcon('gui/resources/data_structure_icon.png'))
        self.show_data_structure_button.clicked.connect(self.show_data_structure)

        self.plot_type_2d_button = QPushButton("2D")
        self.plot_type_2d_button.setIcon(QIcon('gui/resources/2d_icon.png'))
        self.plot_type_2d_button.clicked.connect(self.plot_2d)

        self.plot_type_3d_button = QPushButton("3D")
        self.plot_type_3d_button.setIcon(QIcon('gui/resources/3d_icon.png'))
        self.plot_type_3d_button.clicked.connect(self.plot_3d)

        self.expand_button = QPushButton("Expand Window")
        self.expand_button.setIcon(QIcon('gui/resources/expand2_icon.png'))  # Set new expand icon
        self.expand_button.clicked.connect(self.expand_window)

        self.save_plot_button = QPushButton("Save Plot")  # New Save Plot Button
        self.save_plot_button.setIcon(QIcon('gui/resources/save_icon.png'))  # Optional: add an icon
        self.save_plot_button.clicked.connect(self.save_plot_with_options)

        self.plot_buttons_layout = QHBoxLayout()
        self.plot_buttons_layout.addWidget(self.update_button)
        self.plot_buttons_layout.addWidget(self.plot_type_2d_button)
        self.plot_buttons_layout.addWidget(self.plot_type_3d_button)
        self.plot_buttons_layout.addWidget(self.show_data_structure_button)
        self.plot_buttons_layout.addWidget(self.expand_button)
        self.plot_buttons_layout.addWidget(self.save_plot_button)

        plot_layout.addLayout(self.plot_buttons_layout)

        plot_widget = QWidget()
        plot_widget.setLayout(plot_layout)
        self.layout.addWidget(plot_widget, 0, 2)

        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 2)  # Column 1 is now equally stretched
        self.layout.setColumnStretch(2, 4)

        # Initialize plot type and other variables
        self.plot_type = "2D"
        self.text_items = []
        self.annotations = []
        self.annotation_mode = None  # None, 'point', 'vline', 'hline'
        self.temp_annotation = None
        self.selected_lines = []
        self.normalized_data = {}  # To store normalized data

        # Connect signals and slots from the panels
        self.connect_signals()

        # Connect the canvas to the event handler
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

        # Update the plot_frame stylesheet
        self.plot_frame.setStyleSheet("""
            #PlotFrame {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: #ffffff;  /* Set to white */
            }
        """)

        # Define normalization functions
        self.define_normalization_functions()

    def define_normalization_functions(self):
        # Normalization functions defined within the class

        def min_max_normalization(y, use_custom=False, custom_min=0, custom_max=1):
            if use_custom:
                y_min = custom_min
                y_max = custom_max
            else:
                y_min = np.min(y)
                y_max = np.max(y)
            if y_max - y_min == 0:
                QMessageBox.warning(None, "Invalid Range", "Max and Min values are the same. Cannot normalize.")
                return np.zeros_like(y)
            return (y - y_min) / (y_max - y_min)

        def z_score_normalization(y, mean=None, std=None):
            if mean is None:
                mean = np.mean(y)
            if std is None:
                std = np.std(y)
            if std == 0:
                QMessageBox.warning(None, "Invalid Standard Deviation", "Standard deviation is zero. Cannot normalize.")
                return np.zeros_like(y)
            return (y - mean) / std


        def robust_scaling_normalization(y, quantile_min=25.0, quantile_max=75.0):
            median = np.median(y)
            q_min = np.percentile(y, quantile_min)
            q_max = np.percentile(y, quantile_max)
            iqr = q_max - q_min
            if iqr == 0:
                QMessageBox.warning(None, "Invalid IQR", "Interquartile range is zero. Cannot normalize.")
                return np.zeros_like(y)
            return (y - median) / iqr


        def auc_normalization(y,x=None, sort_data=True):
            if sort_data:
                # Sort y based on x-values; assuming y corresponds to sorted x
                sorted_indices = np.argsort(y)
                y_sorted = y[sorted_indices]
            else:
                y_sorted = y

            # Calculate AUC using the Trapezoidal Rule
            auc = np.trapz(y_sorted, dx=1)  # Assuming uniform spacing; adjust 'dx' as needed
            if auc == 0:
                QMessageBox.warning(None, "Invalid AUC", "Area Under Curve is zero. Cannot normalize.")
                return np.zeros_like(y)

            # Normalize y
            y_normalized = y / auc
            return y_normalized


        def interval_auc_normalization(y, x, desired_auc, interval_start, interval_end):
            # Sort data based on x-values
            sorted_indices = np.argsort(x)
            x_sorted = x[sorted_indices]
            y_sorted = y[sorted_indices]

            # Find indices within the interval
            interval_mask = (x_sorted >= interval_start) & (x_sorted <= interval_end)
            if not np.any(interval_mask):
                QMessageBox.warning(None, "Invalid Interval", "No data points found within the specified interval.")
                return None

            x_interval = x_sorted[interval_mask]
            y_interval = y_sorted[interval_mask]

            # Calculate current AUC within the interval
            current_auc = np.trapz(y_interval, x_interval)
            if current_auc == 0:
                QMessageBox.warning(None, "Invalid AUC", "Current AUC within the interval is zero. Cannot normalize.")
                return None

            # Calculate scaling factor
            scaling_factor = desired_auc / current_auc

            # Scale all y-values
            y_normalized = y * scaling_factor
            return y_normalized
        def total_intensity_normalization(y, desired_total_intensity=1.0):
            current_total = np.sum(y)
            if current_total == 0:
                QMessageBox.warning(None, "Invalid Total Intensity", "Sum of Y-values is zero. Cannot normalize.")
                return np.zeros_like(y)
            scaling_factor = desired_total_intensity / current_total
            y_normalized = y * scaling_factor
            return y_normalized
        def reference_peak_normalization(y, x, reference_peak_x, desired_reference_intensity):
            # Find the index closest to the reference_peak_x
            ref_index = np.argmin(np.abs(x - reference_peak_x))
            y_ref = y[ref_index]
            if y_ref == 0:
                QMessageBox.warning(None, "Invalid Reference Peak", "Reference Peak intensity is zero. Cannot normalize.")
                return None
            scaling_factor = desired_reference_intensity / y_ref
            y_normalized = y * scaling_factor
            return y_normalized
    
        self.normalization_functions = [
            min_max_normalization,          # Index 0
            z_score_normalization,          # Index 1
            robust_scaling_normalization,   # Index 2
            auc_normalization,      
            interval_auc_normalization,
            total_intensity_normalization,  
            reference_peak_normalization,
            # Add other normalization functions here as implemented
        ]
            
    
    def get_normalization_function(self, method_index):
        if 0 <= method_index < len(self.normalization_functions):
            return self.normalization_functions[method_index]
        else:
            return None
        
    def apply_normalization(self, panel):

        # Get the selected data files
        data_files = self.selected_data_panel.get_selected_files()
        if not data_files:
            QMessageBox.warning(self, "No Data Selected", "Please select data files to normalize.")
            return

        # Get normalization method index
        try:
            method_index = next(
                index for index, (name, cls) in enumerate(self.normalization_methods)
                if name == panel.method_name
            )
        except StopIteration:
            QMessageBox.warning(self, "Invalid Method", "Selected normalization method is not recognized.")
            return

        method_func = self.get_normalization_function(method_index)
        if method_func is None:
            QMessageBox.warning(self, "Invalid Method", "Selected normalization method is not implemented.")
            return

        # Get parameters from panel
        params = panel.get_parameters()
        if params is None:
            return  # Error message already shown

        # Define which methods accept the 'x' parameter
        methods_accepting_x = ["AUC Normalization", "Interval AUC Normalization", "Reference Peak Normalization"]

        # Apply normalization to each selected file
        self.normalized_data = {}  # Reset normalized data
        for file_path in data_files:
            try:
                df = pd.read_csv(file_path)
                plot_details = self.plot_details_panel.get_plot_details()
                x_col = int(plot_details['x_axis_col']) - 1
                y_col = int(plot_details['y_axis_col']) - 1
                x = df.iloc[:, x_col].values
                y = df.iloc[:, y_col].values

                # Determine if 'x' should be passed based on the method
                if panel.method_name in methods_accepting_x:
                    if panel.method_name == "Interval AUC Normalization":
                        # For Interval AUC Normalization, pass additional parameters
                        y_normalized = method_func(
                            y,
                            x=x,
                            desired_auc=params['desired_auc'],
                            interval_start=params['interval_start'],
                            interval_end=params['interval_end']
                        )
                    elif panel.method_name == "Reference Peak Normalization":
                        # For Reference Peak Normalization, pass reference_peak_x and desired_reference_intensity
                        y_normalized = method_func(
                            y,
                            x=x,
                            reference_peak_x=params['reference_peak_x'],
                            desired_reference_intensity=params['desired_reference_intensity']
                        )
                    else:
                        # For AUC Normalization, pass 'x' along with other parameters
                        y_normalized = method_func(y, x=x, **params)
                elif panel.method_name == "Total Intensity Normalization":
                    # For Total Intensity Normalization, pass the desired_total_intensity
                    y_normalized = method_func(y, desired_total_intensity=params['desired_total_intensity'])
                else:
                    # For other normalization methods, do not pass 'x'
                    y_normalized = method_func(y, **params)

                if y_normalized is None:
                    continue

                # Store normalized data
                self.normalized_data[file_path] = (x, y_normalized)

            except TypeError as te:
                QMessageBox.warning(self, "Type Error", f"Type error in file {file_path}: {te}")
                print(f"Type error in file {file_path}: {te}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error normalizing file {file_path}: {e}")
                print(f"Error normalizing file {file_path}: {e}")

        # Update the plot with normalized data
        self.update_normalized_plot()
        panel.save_button.setEnabled(True)


    def save_normalized_data(self, panel):
        print("save_normalized_data called")
        if not self.normalized_data:
            QMessageBox.warning(self, "No Normalized Data", "Please apply normalization first.")
            print("No normalized data to save.")
            return

        # Select normalization method for naming
        method_name = panel.method_name.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "").replace("/", "_")
        print(f"Method Name for Saving: {method_name}")

        # Ask user to select folder to save files
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Save Normalized Data")
        if not directory:
            print("No directory selected for saving.")
            return

        normalized_file_paths = []  # To store paths of saved normalized files

        for file_path, (x, y_normalized) in self.normalized_data.items():
            try:
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                new_file_name = f"{base_name}_{method_name}.csv"
                new_file_path = os.path.join(directory, new_file_name)
                print(f"Saving normalized file to: {new_file_path}")

                # Create dataframe to save
                plot_details = self.plot_details_panel.get_plot_details()
                x_label = plot_details.get('x_label', 'X')
                y_label = plot_details.get('y_label', 'Y')

                df = pd.DataFrame({
                    x_label: x,
                    y_label: y_normalized
                })

                df.to_csv(new_file_path, index=False)
                print(f"File saved: {new_file_path}")

                normalized_file_paths.append(new_file_path)  # Add to list

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error saving file {new_file_path}: {e}")
                print(f"Error saving file {new_file_path}: {e}")

        if normalized_file_paths:
            # **Feature: Add Normalized Files to Selected Data Panel**
            self.selected_data_panel.add_files(normalized_file_paths)  # Assuming this method exists
            print(f"Normalized files added to Selected Data panel: {normalized_file_paths}")

        QMessageBox.information(self, "Save Successful", f"Normalized data saved to {directory}")
        print("All normalized files saved successfully.")

    def update_normalized_plot(self):
        if not self.normalized_data:
            QMessageBox.warning(self, "No Normalized Data", "Please apply normalization first.")
            return

        # Gather plot settings
        plot_details = self.plot_details_panel.get_plot_details()
        axis_details = self.axis_details_panel.get_axis_details()
        plot_visuals = self.plot_visuals_panel.get_plot_visuals()

        # Clear the figure
        self.figure.clear()

        # Prepare the axis
        ax = self.figure.add_subplot(111, projection='3d' if self.plot_type == "3D" else None)

        # Plot each normalized data
        for i, (file_path, (x, y_normalized)) in enumerate(self.normalized_data.items()):
            label = os.path.splitext(os.path.basename(file_path))[0] + "_normalized"
            line_style = {'Solid': '-', 'Dashed': '--', 'Dash-Dot': '-.'}.get(plot_details['line_style'], '-')
            point_style = {
                "None": "",
                "Circle": "o",
                "Square": "s",
                "Triangle Up": "^",
                "Triangle Down": "v",
                "Star": "*",
                "Plus": "+",
                "Cross": "x"
            }.get(plot_details['point_style'], "")
            line_thickness = int(plot_details['line_thickness'])

            plot_type = plot_visuals['plot_type'].lower()

            if plot_type == "line":
                if self.plot_type == "3D":
                    ax.plot(x, [i]*len(x), y_normalized, label=label, linestyle=line_style, marker=point_style, linewidth=line_thickness)
                else:
                    ax.plot(x, y_normalized, label=label, linestyle=line_style, marker=point_style, linewidth=line_thickness)
            elif plot_type == "bar":
                if self.plot_type == "3D":
                    ax.bar(x, y_normalized, zs=i, zdir='y', label=label)
                else:
                    ax.bar(x, y_normalized, label=label)
            elif plot_type == "scatter":
                if self.plot_type == "3D":
                    ax.scatter(x, [i]*len(x), y_normalized, label=label)
                else:
                    ax.scatter(x, y_normalized, label=label)
            elif plot_type == "histogram":
                if self.plot_type == "3D":
                    ax.hist(y_normalized, zs=i, zdir='y', label=label)
                else:
                    ax.hist(y_normalized, label=label)
            elif plot_type == "pie":
                if self.plot_type == "3D":
                    pass  # Pie chart in 3D doesn't make sense
                else:
                    ax.pie(y_normalized, labels=x)

        # Set axis labels and title with adjusted padding
        ax.set_title(axis_details['title'], fontsize=axis_details['title_font_size'], pad=20)
        ax.set_xlabel(axis_details['x_label'], fontsize=axis_details['axis_font_size'])
        if self.plot_type == "3D":
            ax.set_ylabel('Offset', fontsize=axis_details['axis_font_size'])
            ax.set_zlabel(axis_details['y_label'], fontsize=axis_details['axis_font_size'])
        else:
            ax.set_ylabel(axis_details['y_label'], fontsize=axis_details['axis_font_size'])

        # Apply axis ranges
        try:
            x_min = float(axis_details['x_min']) if axis_details['x_min'] else None
            x_max = float(axis_details['x_max']) if axis_details['x_max'] else None
            y_min = float(axis_details['y_min']) if axis_details['y_min'] else None
            y_max = float(axis_details['y_max']) if axis_details['y_max'] else None

            if x_min is not None and x_max is not None:
                ax.set_xlim(x_min, x_max)
            if y_min is not None and y_max is not None:
                ax.set_ylim(y_min, y_max)
        except ValueError:
            QMessageBox.warning(self, "Invalid Axis Range", "Please enter valid axis range values.")

        # Apply scales
        scale_type = plot_details['scale_type'].lower()
        x_scale = 'linear'
        y_scale = 'linear'
        if 'logarithmic x-axis' in scale_type:
            x_scale = 'log'
        if 'logarithmic y-axis' in scale_type:
            y_scale = 'log'
        if 'logarithmic both axes' in scale_type:
            x_scale = y_scale = 'log'
        ax.set_xscale(x_scale)
        ax.set_yscale(y_scale)

        # Apply grid settings
        if plot_visuals['add_grid']:
            ax.grid(True)
        if plot_visuals['add_sub_grid']:
            ax.minorticks_on()
            ax.grid(which='minor', linestyle=':', linewidth='0.5')

        # Add legend if required
        if plot_visuals['apply_legends']:
            ax.legend(fontsize=axis_details['legend_font_size'])

        # Redraw the figure
        self.canvas.draw_idle()

    def on_normalization_section_expanded(self, expanded_section):
        if self.is_collapsing:
            return
        self.is_collapsing = True
        # When a section is expanded, collapse all other sections
        for section in self.normalization_sections:
            if section != expanded_section and section.toggle_button.isChecked():
                section.toggle_button.setChecked(False)
        self.is_collapsing = False

    def connect_signals(self):
        # Access panels
        #normalization_tab = self

        self.selected_data_panel.file_selector_button.clicked.connect(self.choose_files)
        self.selected_data_panel.add_file_button.clicked.connect(self.add_files)
        self.selected_data_panel.select_all_button.clicked.connect(self.toggle_select_all_files)
        #self.additional_text_panel.text_color_button.clicked.connect(self.choose_text_color)
        self.additional_text_panel.add_text_button.clicked.connect(self.add_text_to_plot)
        self.additional_text_panel.delete_text_button.clicked.connect(self.delete_text_from_plot)
        self.custom_annotations_panel.apply_changes_button.clicked.connect(self.apply_changes)
        self.custom_annotations_panel.calculate_distance_button.clicked.connect(self.start_distance_calculation)
        #self.selected_data_panel.retract_button.clicked.connect(self.retract_from_general)
        self.expand_button.clicked.connect(self.expand_window)

        # Connect the "Retract from General" button if it exists
        if hasattr(self.selected_data_panel, 'retract_button'):
            self.selected_data_panel.retract_button.clicked.connect(self.retract_from_general)


    def on_section_expanded(self, expanded_section):
        print(f"Section '{expanded_section.toggle_button.text()}' expanded. Collapsing other sections.")
        if self.is_collapsing:
            return
        self.is_collapsing = True
        # When a section is expanded, collapse all other sections
        for section in self.collapsible_sections:
            if section != expanded_section and section.toggle_button.isChecked():
                print(f"Collapsing section '{section.toggle_button.text()}'")
                section.toggle_button.setChecked(False)
        self.is_collapsing = False

                
    def choose_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", self.last_directory, "CSV Files (*.csv);;All Files (*)")
        if files:
            self.last_directory = os.path.dirname(files[0])  # Update the last directory
            self.selected_data_panel.selected_files_list.clear()
            for file in files:
                file_name = os.path.basename(file)  # Get only the file name
                item = QListWidgetItem(file_name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                item.setData(Qt.UserRole, file)  # Store the full file path in the item
                self.selected_data_panel.selected_files_list.addItem(item)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", self.last_directory, "CSV Files (*.csv);;All Files (*)")
        if files:
            self.last_directory = os.path.dirname(files[0])  # Update the last directory
            for file in files:
                file_name = os.path.basename(file)  # Get only the file name
                item = QListWidgetItem(file_name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                item.setData(Qt.UserRole, file)  # Store the full file path in the item
                self.selected_data_panel.selected_files_list.addItem(item)

    def toggle_select_all_files(self):
        select_all = self.selected_data_panel.select_all_button.text() == "Select All"
        for index in range(self.selected_data_panel.selected_files_list.count()):
            item = self.selected_data_panel.selected_files_list.item(index)
            item.setCheckState(Qt.Checked if select_all else Qt.Unchecked)
        self.selected_data_panel.select_all_button.setText("Deselect All" if select_all else "Select All")

    def retract_from_general(self):
        # **Access the General Tab's SelectedDataPanel**
        general_selected_data_panel = self.general_tab.selected_data_panel

        # **Retrieve selected files from the General Tab**
        selected_items = [
            item for item in general_selected_data_panel.selected_files_list.findItems("*", Qt.MatchWildcard)
            if item.checkState() == Qt.Checked
        ]

        if not selected_items:
            QMessageBox.warning(self, "No Data Selected", "No files are selected in the General Tab.")
            return

        # **Add selected files from General Tab to Normalization Tab without clearing existing files**
        added_files = []
        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            # Use the add_file_to_panel method to handle duplicates
            self.selected_data_panel.add_file_to_panel(file_path)
            # After adding, find the item and set it as checked
            for i in range(self.selected_data_panel.selected_files_list.count()):
                norm_item = self.selected_data_panel.selected_files_list.item(i)
                if norm_item.data(Qt.UserRole) == file_path:
                    norm_item.setCheckState(Qt.Checked)
                    added_files.append(file_path)
                    break

        if added_files:
            QMessageBox.information(self, "Retract Successful", f"Added {len(added_files)} file(s) to the Normalization Tab.")
        else:
            QMessageBox.information(self, "No New Files", "No new files were added (they may already exist).")
    
    def delete_selected_file(self):
        selected_items = self.selected_data_panel.selected_files_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.selected_data_panel.selected_files_list.takeItem(self.selected_data_panel.selected_files_list.row(item))

    '''def choose_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color.name()
            self.additional_text_panel.set_text_color(self.text_color)
'''
    def add_text_to_plot(self):
        text_details = self.additional_text_panel.get_text_details()
        if text_details['text'] and self.plot_type == "2D":
            try:
                x_pos = float(text_details['x_pos'])
                y_pos = float(text_details['y_pos'])
                text_size = text_details['size']
                text_color = text_details['color']
                text_item = self.figure.gca().text(x_pos, y_pos, text_details['text'], fontsize=text_size, color=text_color, transform=self.figure.gca().transData, ha='left')
                self.text_items.append(text_item)
                self.canvas.draw_idle()
            except ValueError:
                print("Invalid x or y position for additional text")

    def delete_text_from_plot(self):
        if self.text_items:
            text_item = self.text_items.pop()  # Remove the last added text item
            text_item.remove()  # Remove it from the plot
            self.canvas.draw_idle()

    def update_plot(self):
        # Gather all parameters from panels
        print("Parent tab: update_plot called")

        data_files = self.selected_data_panel.get_selected_files()
        plot_details = self.plot_details_panel.get_plot_details()
        axis_details = self.axis_details_panel.get_axis_details()
        plot_visuals = self.plot_visuals_panel.get_plot_visuals()
        # Call the plot_data function
        plot_data(self.figure, data_files, plot_details, axis_details, plot_visuals, is_3d=(self.plot_type == "3D"))

        # Re-add all existing text items
        ax = self.figure.gca()
        if self.plot_type == "2D":
            for text_item in self.text_items:
                ax.add_artist(text_item)

        self.canvas.draw_idle()
        print("NormalizationTab: plot_updated signal emitted")  # Debugging statement
        self.plot_updated.emit()

    def plot_2d(self):
        self.plot_type = "2D"
        self.update_plot()

    def plot_3d(self):
        self.plot_type = "3D"
        self.update_plot()

    def show_data_structure(self):
        # Get the selected file names
        selected_items = [
            item for item in self.selected_data_panel.selected_files_list.findItems("*", Qt.MatchWildcard)
            if item.checkState() == Qt.Checked
        ]

        if not selected_items:
            QMessageBox.warning(self, "No Data Selected", "No files are selected to show data structure.")
            return

        # Create a new window to show the data structure
        self.data_window = QWidget()
        self.data_window.setWindowTitle("Data Structure - Normalization Tab")
        self.data_layout = QVBoxLayout(self.data_window)

        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            try:
                df, x, y = self.read_numeric_data(file_path)
                if df is None:
                    continue  # Skip files with insufficient or invalid data

                df_head = df.head()

                table = QTableWidget()
                table.setRowCount(len(df_head))
                table.setColumnCount(len(df_head.columns))
                table.setHorizontalHeaderLabels(df_head.columns.tolist())
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

                for i in range(len(df_head)):
                    for j in range(len(df_head.columns)):
                        table.setItem(i, j, QTableWidgetItem(str(df_head.iloc[i, j])))

                self.data_layout.addWidget(QLabel(f"File: {item.text()}"))
                self.data_layout.addWidget(table)

                # Add Show Raw Data button
                show_raw_data_button = QPushButton("Show Raw Data")
                show_raw_data_button.clicked.connect(partial(self.show_raw_data, file_path))
                self.data_layout.addWidget(show_raw_data_button)

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error loading file {file_path}: {e}")

        self.data_window.setLayout(self.data_layout)
        self.data_window.setGeometry(150, 150, 800, 600)
        self.data_window.show()

    def show_raw_data(self, file_path):
        try:
            # Read the first 20 lines of the raw data file
            with open(file_path, 'r') as f:
                lines = [next(f) for _ in range(20)]
            raw_data = ''.join(lines)

            # Create a new window to display the raw data
            raw_data_window = QWidget()
            raw_data_window.setWindowTitle(f"Raw Data - {os.path.basename(file_path)}")
            layout = QVBoxLayout(raw_data_window)
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(raw_data)
            layout.addWidget(text_edit)
            raw_data_window.setLayout(layout)
            raw_data_window.setGeometry(200, 200, 600, 400)
            raw_data_window.show()

            # Keep a reference to the window
            if not hasattr(self, 'raw_data_windows'):
                self.raw_data_windows = []
            self.raw_data_windows.append(raw_data_window)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error reading raw data from {file_path}: {e}")

    def expand_window(self):
        print("Expand Window button clicked.")
        if self.expanded_window is not None:
            print("Expanded window already exists, bringing it to front.")
            self.expanded_window.raise_()
            return

        # Create a new expanded window
        try:
            print("NormalizationTab: Creating a new ExpandedPlotWindow.")
            self.expanded_window = ExpandedPlotWindow(self)
            self.expanded_window.closed.connect(self.on_expanded_window_closed)
            self.expanded_window.show()
        except Exception as e:
            print(f"NormalizationTab: Error creating ExpandedPlotWindow: {e}")

        # Connect to the closed signal to reset the reference
        #self.expanded_window.destroyed.connect(self.on_expanded_window_closed)

    def on_expanded_window_closed(self):
        print("Expanded window closed.")
        self.expanded_window = None
        print("self.expanded_window has been reset to None.")

    def on_click(self, event):
        if self.plot_type != "2D":
            return

        annotation_type = self.custom_annotations_panel.get_annotation_type()
        if annotation_type == "Annotation Point":
            self.add_annotation_point(event)
        elif annotation_type == "Vertical Line":
            self.add_vertical_line(event)
        elif annotation_type == "Horizontal Line":
            self.add_horizontal_line(event)
        elif annotation_type == "None":
            self.select_line(event)

    def on_mouse_move(self, event):
        if self.plot_type != "2D" or not self.annotation_mode:
            return

        if self.temp_annotation:
            self.temp_annotation.remove()
            self.temp_annotation = None

        if self.annotation_mode == 'vline':
            self.temp_annotation = self.figure.gca().axvline(x=event.xdata, color='r', linestyle='--')
        elif self.annotation_mode == 'hline':
            self.temp_annotation = self.figure.gca().axhline(y=event.ydata, color='b', linestyle='--')

        self.canvas.draw_idle()

    def add_annotation_point(self, event):
        if event.xdata is None or event.ydata is None:
            return
        star, = self.figure.gca().plot(event.xdata, event.ydata, marker='*', color='black', markersize=10)
        text = self.figure.gca().text(event.xdata, event.ydata, f'({event.xdata:.2f}, {event.ydata:.2f})', fontsize=10, color='black', ha='left')
        self.annotations.append((star, text))
        self.canvas.draw_idle()

    def add_vertical_line(self, event):
        if event.xdata is None:
            return
        line = self.figure.gca().axvline(x=event.xdata, color='r', linestyle='--')
        self.annotations.append(line)
        self.canvas.draw_idle()

    def add_horizontal_line(self, event):
        if event.ydata is None:
            return
        line = self.figure.gca().axhline(y=event.ydata, color='b', linestyle='--')
        self.annotations.append(line)
        self.canvas.draw_idle()

    def apply_changes(self):
        self.annotation_mode = None
        self.temp_annotation = None
        self.custom_annotations_panel.annotation_type_combo.setCurrentText("None")
        self.canvas.draw_idle()

    def select_line(self, event):
        if event.xdata is None or event.ydata is None:
            return

        for ann in self.annotations:
            if isinstance(ann, plt.Line2D):
                # Check if it's a vertical line
                if np.allclose(ann.get_xdata(), [ann.get_xdata()[0]]) and event.inaxes == ann.axes and ann.contains(event)[0]:
                    self.selected_lines.append(ann)
                    if len(self.selected_lines) == 2:
                        self.calculate_distance()
                    break
                # Check if it's a horizontal line
                elif np.allclose(ann.get_ydata(), [ann.get_ydata()[0]]) and event.inaxes == ann.axes and ann.contains(event)[0]:
                    self.selected_lines.append(ann)
                    if len(self.selected_lines) == 2:
                        self.calculate_distance()
                    break

    def start_distance_calculation(self):
        self.selected_lines.clear()
        self.custom_annotations_panel.annotation_type_combo.setCurrentText("None")

    def calculate_distance(self):
        if len(self.selected_lines) < 2:
            return

        line1, line2 = self.selected_lines
        ax = self.figure.gca()

        if np.allclose(line1.get_xdata(), [line1.get_xdata()[0]]) and np.allclose(line2.get_xdata(), [line2.get_xdata()[0]]):  # Both lines are vertical
            x1 = line1.get_xdata()[0]
            x2 = line2.get_xdata()[0]
            dist = abs(x2 - x1)

            # Draw a horizontal arrow between the lines
            arrow = ax.annotate(f'd = {dist:.2f}', xy=((x1 + x2) / 2, ax.get_ylim()[1] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05),
                                xytext=((x1 + x2) / 2, ax.get_ylim()[1] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05),
                                arrowprops=dict(facecolor='black', arrowstyle='<->', lw=1.5),
                                ha='center', va='center')
            self.annotations.append(arrow)

        elif np.allclose(line1.get_ydata(), [line1.get_ydata()[0]]) and np.allclose(line2.get_ydata(), [line2.get_ydata()[0]]):  # Both lines are horizontal
            y1 = line1.get_ydata()[0]
            y2 = line2.get_ydata()[0]
            dist = abs(y2 - y1)

            # Draw a vertical arrow between the lines
            arrow = ax.annotate(f'd = {dist:.2f}', xy=(ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.05, (y1 + y2) / 2),
                                xytext=(ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.05, (y1 + y2) / 2),
                                arrowprops=dict(facecolor='black', arrowstyle='<->', lw=1.5),
                                ha='center', va='center', rotation=90)
            self.annotations.append(arrow)

        self.selected_lines.clear()
        self.canvas.draw_idle()

    def read_numeric_data(self, file_path):
        return read_numeric_data(file_path, parent=self)
    
    def save_plot_with_options(self):
        print("Save Plot button clicked.")
        dialog = SavePlotDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            width_pixels, height_pixels, quality = dialog.get_values()
            print(f"Saving plot with width: {width_pixels}px, height: {height_pixels}px, quality: {quality}")
            self.save_plot(width_pixels, height_pixels, quality)

    def save_plot(self, width_pixels, height_pixels, quality):
        # Map quality to dpi
        quality_dpi_mapping = {
            "Low": 72,
            "Medium": 150,
            "High": 300,
            "Very High": 600
        }
        dpi = quality_dpi_mapping.get(quality, 150)  # Default to 150 DPI if not found
        
        # Keep the figure size in inches based on width and height
        width_in = width_pixels / 100  # Convert pixels to "figure inches" (for matplotlib size control)
        height_in = height_pixels / 100  # Same conversion
        
        # Store original figure size and DPI
        original_size = self.figure.get_size_inches()
        original_dpi = self.figure.get_dpi()

        # Set the figure size to the new dimensions in inches
        self.figure.set_size_inches(width_in, height_in)
        
        # Define the file path
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Plot", 
            "", 
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)", 
            options=options
        )
        if file_path:
            try:
                # Save the figure with the specified DPI, affecting only the quality (sharpness) not the size
                self.figure.savefig(file_path, dpi=dpi)
                QMessageBox.information(self, "Save Successful", f"Plot saved successfully at:\n{file_path}")
                print(f"Plot saved successfully at: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Save Failed", f"Failed to save plot:\n{e}")
                print(f"Failed to save plot: {e}")
        
        # Restore original figure size and DPI after saving to avoid affecting the interactive plot
        self.figure.set_size_inches(original_size)
        self.figure.set_dpi(original_dpi)
        
        # Redraw the canvas to make sure the interactive plot looks normal after saving
        self.canvas.draw_idle()
        print("Figure size and DPI restored to original after saving.")

# gui/normalization_tab.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QToolButton, QScrollArea, QSizePolicy,
    QPushButton, QHBoxLayout, QFrame, QFileDialog, QListWidgetItem, QColorDialog, QTableWidget, QHeaderView, QTableWidgetItem,
    QMessageBox,QTextEdit,
      QButtonGroup, QGroupBox, QVBoxLayout, QDialog, QComboBox, QSpinBox, QCheckBox, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QIcon


from gui.panels.normalization_panels import(MinMaxNormalizationPanel, ZScoreNormalizationPanel, RobustScalingNormalizationPanel,
    AUCNormalizationPanel,IntervalAUCNormalizationPanel,TotalIntensityNormalizationPanel,
    ReferencePeakNormalizationPanel,
    BaselineCorrectionNormalizationPanel,BaselineCorrectionWithFileNormalizationPanel,
)

from gui.panels.data_correction_panels import ( CorrectMissingDataPanel, 
    NoiseReductionPanel,UnitConverterPanel,ShiftBaselinePanel,
    DataCuttingPanel,
   
)

from gui.panels.selected_data_panel import SelectedDataPanel
from gui.panels.plot_details_panels import ( AxisDetailsPanel, AdditionalTextPanel,
    CustomAnnotationsPanel, PlotVisualsPanel, PlotDetailsPanel, )


from plots.plotting import plot_data
from gui.dialogs.latex_compatibility_dialog import LaTeXCompatibilityDialog 
from gui.utils.collapsible_sections import * 

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
from utils import read_numeric_data
from functools import partial 
import math
from scipy.signal import savgol_filter  # For Savitzky-Golay Filter
import pywt  # For Wavelet Denoising
from functools import partial


# Add resource_path function
def resource_path(relative_path):
    """ Get absolute path to resource, works for development and PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

################################################################


class NormalizationTab(QWidget):

    plot_updated = pyqtSignal()  # Define the custom signal

    def __init__(self, general_tab, parent=None):
        super().__init__(parent)
        self.general_tab = general_tab
        self.is_collapsing = False  # Flag to prevent recursive signal handling
        self.init_ui()
        self.expanded_window = None  # To track the expanded window

        # Apply global stylesheet
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
            ("Baseline Correction Normalization", BaselineCorrectionNormalizationPanel), 
            ("Baseline Correction with File", BaselineCorrectionWithFileNormalizationPanel)
            
            
        ]

        self.normalization_sections = []

        # Create NormalizationMethodPanel for each method
        for method_name, panel_class in self.normalization_methods:
            panel = panel_class()
            section = CollapsibleSection(method_name, panel)
            section.section_expanded.connect(self.on_normalization_section_expanded)
            self.normalization_sections.append(section)

            # Connect Apply, Save, and Send to Data Panel buttons
            panel.apply_button.clicked.connect(lambda checked, p=panel: self.apply_normalization(p))
            panel.save_button.clicked.connect(lambda checked, p=panel: self.save_normalized_data(p))
            panel.send_to_data_panel_button.clicked.connect(lambda checked, p=panel: self.send_normalized_data_to_data_panel(p))

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
        # Define basic corrections methods and their corresponding panels
        self.basic_corrections_methods = [
            ("Correct Missing Data", CorrectMissingDataPanel),
            ("Noise Reduction", NoiseReductionPanel),
            ("Unit Converter", UnitConverterPanel),
            ("Shift Baseline", ShiftBaselinePanel),
            ("Data Cutting", DataCuttingPanel)

        ]

        self.basic_corrections_panels = []

        for method_name, panel_class in self.basic_corrections_methods:
            panel = panel_class()
            section = CollapsibleSection(method_name, panel)
            section.section_expanded.connect(self.on_basic_corrections_section_expanded)
            self.basic_corrections_panels.append(section)

            # Connect Apply, Save, and Send to Data Panel buttons
            panel.apply_button.clicked.connect(lambda checked, p=panel: self.apply_basic_correction(p))
            panel.save_button.clicked.connect(lambda checked, p=panel: self.save_normalized_data(p))
            panel.send_to_data_panel_button.clicked.connect(lambda checked, p=panel: self.send_normalized_data_to_data_panel(p))

            basic_corrections_layout.addWidget(section)



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
        # Plot area setup (same as original but updated icons with resource_path)
        self.update_button = QPushButton("Update Plot")
        update_icon_path = resource_path('gui/resources/update_icon.png')
        self.update_button.setIcon(QIcon(update_icon_path))
        self.update_button.clicked.connect(self.update_plot)

        self.show_data_structure_button = QPushButton("Show Data Structure")
        data_structure_icon_path = resource_path('gui/resources/data_structure_icon.png')
        self.show_data_structure_button.setIcon(QIcon(data_structure_icon_path))
        self.show_data_structure_button.clicked.connect(self.show_data_structure)

        self.plot_type_2d_button = QPushButton("2D")
        plot_2d_icon_path = resource_path('gui/resources/2d_icon.png')
        self.plot_type_2d_button.setIcon(QIcon(plot_2d_icon_path))
        self.plot_type_2d_button.clicked.connect(self.plot_2d)

        self.plot_type_3d_button = QPushButton("3D")
        plot_3d_icon_path = resource_path('gui/resources/3d_icon.png')
        self.plot_type_3d_button.setIcon(QIcon(plot_3d_icon_path))
        self.plot_type_3d_button.clicked.connect(self.plot_3d)

        self.expand_button = QPushButton("Expand Window")
        expand_icon_path = resource_path('gui/resources/expand2_icon.png')
        self.expand_button.setIcon(QIcon(expand_icon_path))
        self.expand_button.clicked.connect(self.expand_window)

        self.save_plot_button = QPushButton("Save Plot")
        save_icon_path = resource_path('gui/resources/save_icon.png')
        self.save_plot_button.setIcon(QIcon(save_icon_path))
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

    def apply_basic_correction(self, panel):
        # Clear the previous normalized data
        self.normalized_data = {}

        # Get the selected data files
        data_files = self.selected_data_panel.get_selected_files()
        if not data_files:
            QMessageBox.warning(self, "No Data Selected", "Please select data files to correct.")
            return

        # Get parameters from panel
        params = panel.get_parameters()
        if params is None:
            return  # Error message already shown

        method = params['method']

        # Process each data file
        for file_path in data_files:
            try:
                # Use read_numeric_data to read the file
                df, _, _ = self.read_numeric_data(file_path)
                if df is None:
                    print(f"Skipping file {file_path} due to insufficient data.")
                    continue

                plot_details = self.plot_details_panel.get_plot_details()
                x_col = int(plot_details['x_axis_col']) - 1
                y_col = int(plot_details['y_axis_col']) - 1

                # Validate column indices
                if x_col >= df.shape[1] or y_col >= df.shape[1]:
                    print(f"Selected columns do not exist in {file_path}.")
                    QMessageBox.warning(self, "Invalid Columns", f"Selected columns do not exist in {file_path}.")
                    continue

                # Extract selected columns
                x_series = df.iloc[:, x_col]
                y_series = df.iloc[:, y_col]

                # Handle missing data
                if method == "Remove Rows with Missing Data":
                    df_cleaned = df.dropna(subset=[df.columns[x_col], df.columns[y_col]])
                elif method in ["Replace with Mean", "Replace with Median"]:
                    # Use the helper function for localized replacement
                    y_series = self.interpolate_missing_values(y_series, method=method.split()[-1].lower())
                    df_cleaned = pd.DataFrame({df.columns[x_col]: x_series, df.columns[y_col]: y_series})
                
                elif method == "Moving Average Smoothing":
                    window_size = params['window_size']
                    y_series = y_series.rolling(window=window_size, center=True).mean()
                    df_cleaned = pd.DataFrame({df.columns[x_col]: x_series, df.columns[y_col]: y_series})
                elif method == "Savitzky-Golay Filter":
                    window_size = params['window_size']
                    poly_order = params['poly_order']
                    y_filtered = self.savitzky_golay_filter(y_series.values, window_size, poly_order)
                    y_series = pd.Series(y_filtered)
                    df_cleaned = pd.DataFrame({df.columns[x_col]: x_series, df.columns[y_col]: y_series})
                elif method == "Wavelet Denoising":
                    wavelet = params['wavelet']
                    level = params['level']
                    y_filtered = self.wavelet_denoising(y_series.values, wavelet, level)
                    y_series = pd.Series(y_filtered[:len(y_series)])  # Ensure length matches
                    df_cleaned = pd.DataFrame({df.columns[x_col]: x_series, df.columns[y_col]: y_series})
            
                elif method == "Unit Converter":
                    x_formula = params['x_formula']
                    y_formula = params['y_formula']

                    x_series_converted, y_series_converted = self.apply_unit_conversion(
                    x_series, y_series, x_formula, y_formula)

                    if x_series_converted is None or y_series_converted is None:
                        # Error already shown
                        continue

                    df_cleaned = pd.DataFrame({
                        df.columns[x_col]: x_series_converted,
                        df.columns[y_col]: y_series_converted
                    })
                
                elif method == "Shift Baseline":
                    desired_baseline = params['desired_baseline']
                    y_min = y_series.min()
                    shift_value = desired_baseline - y_min
                    y_series_shifted = y_series + shift_value
                    df_cleaned = pd.DataFrame({
                        df.columns[x_col]: x_series,
                        df.columns[y_col]: y_series_shifted
                    })

                elif method == "Data Cutting":
                    # Handle Data Cutting
                    x_start = params.get('x_start')
                    x_end = params.get('x_end')
                    mask = (x_series >= x_start) & (x_series <= x_end)
                    df_cleaned = df[mask]
                    
                else:
                    QMessageBox.warning(self, "Unknown Method", f"Unknown method: {method}")
                    continue

                # Convert to numeric and drop NaNs resulting from conversion
                x_series = pd.to_numeric(df_cleaned.iloc[:, 0], errors='coerce')
                y_series = pd.to_numeric(df_cleaned.iloc[:, 1], errors='coerce')
                valid_mask = x_series.notna() & y_series.notna()
                x = x_series[valid_mask].values
                y = y_series[valid_mask].values

                if len(x) == 0 or len(y) == 0:
                    QMessageBox.warning(self, "No Valid Data", f"No valid numeric data found after correction in {file_path}.")
                    continue

                # Store corrected data
                self.normalized_data[file_path] = (x, y)

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error processing file {file_path}: {e}")
                print(f"Error processing file {file_path}: {e}")

        # Update the plot with corrected data
        self.update_normalized_plot()
        panel.save_button.setEnabled(True)
        panel.send_to_data_panel_button.setEnabled(True)

    
    def moving_average_smoothing(self, y, window_size):
        return np.convolve(y, np.ones(window_size)/window_size, mode='same')

    def savitzky_golay_filter(self, y, window_size, poly_order):
        from scipy.signal import savgol_filter
        return savgol_filter(y, window_length=window_size, polyorder=poly_order)

    def wavelet_denoising(self, y, wavelet, level):
        import pywt
        coeffs = pywt.wavedec(y, wavelet, level=level)
        # Thresholding
        sigma = np.median(np.abs(coeffs[-level])) / 0.6745
        uthresh = sigma * np.sqrt(2 * np.log(len(y)))
        coeffs[1:] = (pywt.threshold(i, value=uthresh, mode='soft') for i in coeffs[1:])
        return pywt.waverec(coeffs, wavelet)

    def apply_unit_conversion(self, x_series, y_series, x_formula, y_formula):
        """
        Apply user-defined formulas to x_series and y_series.

        Parameters:
        - x_series (pd.Series): Original X-values.
        - y_series (pd.Series): Original Y-values.
        - x_formula (str): Formula to apply to X-values.
        - y_formula (str): Formula to apply to Y-values.

        Returns:
        - (pd.Series, pd.Series): Transformed X and Y series.
        """
        # Create a safe namespace for evaluation
        namespace = {'np': np, 'pd': pd, 'math': math}
        # Copy the original series to avoid modifying them
        x_new = x_series.copy()
        y_new = y_series.copy()

        try:
            if x_formula:
                x = x_series.values  # Use 'x' as variable
                x_new = eval(x_formula, namespace, {'x': x})
                x_new = pd.Series(x_new)
            if y_formula:
                y = y_series.values  # Use 'y' as variable
                y_new = eval(y_formula, namespace, {'y': y})
                y_new = pd.Series(y_new)
        except Exception as e:
            QMessageBox.warning(self, "Formula Error", f"Error in applying formula:\n{e}")
            return None, None

        return x_new, y_new


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
        
        def baseline_correction_with_file(y, reference_y):
            """
            Performs baseline correction by subtracting the reference Y-values from the data Y-values.

            Parameters:
            - y: numpy array of Y-values from the data file
            - reference_y: numpy array of Y-values from the reference file

            Returns:
            - y_corrected: baseline-corrected Y-values
            """
            if len(y) != len(reference_y):
                QMessageBox.warning(None, "Data Mismatch", "The length of data Y-values and reference Y-values do not match.")
                return None
            y_corrected = y - reference_y
            return y_corrected
        
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
        
        def baseline_correction(y, x, lambda_=1e6, p=0.01, niter=10):
            """
            Performs baseline correction using Asymmetric Least Squares (ALS) method.
            
            Parameters:
            - y: numpy array of Y-values (1D)
            - x: numpy array of X-values
            - lambda_: smoothing parameter (default: 1e6)
            - p: asymmetry parameter (default: 0.01)
            - niter: number of iterations (default: 10)
            
            Returns:
            - y_corrected: baseline-corrected Y-values
            - baseline: estimated baseline
            """
            from scipy import sparse
            from scipy.sparse.linalg import spsolve
            
            L = len(y)
            D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L-2))
            D = lambda_ * D.dot(D.transpose())  # Precompute D^T * D
            w = np.ones(L)
            
            for i in range(niter):
                W = sparse.diags(w, 0)
                Z = W + D
                try:
                    z = spsolve(Z, w * y)
                except Exception as e:
                    QMessageBox.warning(None, "Baseline Correction Error", f"Error during baseline correction: {e}")
                    return None, None
                w = p * (y > z) + (1 - p) * (y < z)
            
            y_corrected = y - z
            return y_corrected, z
        
        self.normalization_functions = [
            min_max_normalization,          # Index 0
            z_score_normalization,          # Index 1
            robust_scaling_normalization,   # Index 2
            auc_normalization,      
            interval_auc_normalization,
            total_intensity_normalization,  
            reference_peak_normalization,
            baseline_correction,   
            baseline_correction_with_file,  
            # Add other normalization functions here as implemented
        ]
        
    
    def get_normalization_function(self, method_index):
        if 0 <= method_index < len(self.normalization_functions):
            return self.normalization_functions[method_index]
        else:
            return None
        
    def apply_normalization(self, panel):
        # Clear the previous normalized data
        self.normalized_data = {}

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
        methods_accepting_x = [
            "AUC Normalization",
            "Interval AUC Normalization",
            "Reference Peak Normalization",
            "Baseline Correction Normalization"
        ]

        # Define which methods require a reference file
        methods_requiring_reference_file = [
            "Baseline Correction with File"
        ]

        # Process each data file
        for file_path in data_files:
            try:
                # Use read_numeric_data to read the file
                df, _, _ = self.read_numeric_data(file_path)
                if df is None:
                    print(f"Skipping file {file_path} due to insufficient data.")
                    continue

                plot_details = self.plot_details_panel.get_plot_details()
                x_col = int(plot_details['x_axis_col']) - 1
                y_col = int(plot_details['y_axis_col']) - 1

                # Validate column indices
                if x_col >= df.shape[1] or y_col >= df.shape[1]:
                    print(f"Selected columns do not exist in {file_path}.")
                    QMessageBox.warning(self, "Invalid Columns", f"Selected columns do not exist in {file_path}.")
                    continue

                # Extract selected columns and convert to numeric
                x_series = pd.to_numeric(df.iloc[:, x_col], errors='coerce')
                y_series = pd.to_numeric(df.iloc[:, y_col], errors='coerce')

                # Drop rows where x or y is NaN
                valid_mask = x_series.notna() & y_series.notna()
                x = x_series[valid_mask].values
                y = y_series[valid_mask].values

                if len(x) == 0 or len(y) == 0:
                    QMessageBox.warning(self, "No Valid Data", f"No valid numeric data found in selected columns of {file_path}.")
                    continue

                # Apply the appropriate normalization method
                if panel.method_name == "Baseline Correction with File":
                    # Handle Baseline Correction with File normalization
                    reference_file_path = params.get('reference_file_path')
                    if not reference_file_path or not os.path.isfile(reference_file_path):
                        QMessageBox.warning(self, "Invalid Reference File", "Please select a valid reference file for baseline correction.")
                        continue

                    # Read reference data
                    ref_df, _, _ = self.read_numeric_data(reference_file_path)
                    if ref_df is None:
                        QMessageBox.warning(self, "Reference Data Error", "Failed to read the reference data file or insufficient data.")
                        continue

                    # Extract selected columns from reference data
                    ref_x_series = pd.to_numeric(ref_df.iloc[:, x_col], errors='coerce')
                    ref_y_series = pd.to_numeric(ref_df.iloc[:, y_col], errors='coerce')

                    # Drop rows where x or y is NaN in reference data
                    ref_valid_mask = ref_x_series.notna() & ref_y_series.notna()
                    ref_x = ref_x_series[ref_valid_mask].values
                    ref_y = ref_y_series[ref_valid_mask].values

                    if len(ref_x) == 0 or len(ref_y) == 0:
                        QMessageBox.warning(self, "No Valid Reference Data", f"No valid numeric data found in selected columns of the reference file.")
                        continue

                    # Ensure that the x-values match
                    if not np.array_equal(x, ref_x):
                        QMessageBox.warning(self, "Data Mismatch", f"X-values in {file_path} do not match the reference file.")
                        continue

                    # Apply the baseline correction with file
                    y_normalized = method_func(y, reference_y=ref_y)
                    if y_normalized is None:
                        QMessageBox.warning(self, "Normalization Failed", f"Baseline Correction with File failed for file {file_path}.")
                        continue

                    # Store normalized data
                    self.normalized_data[file_path] = (x, y_normalized)

                elif panel.method_name == "Baseline Correction Normalization":
                    # Apply Baseline Correction Normalization
                    y_corrected, baseline = method_func(
                        y=y,
                        x=x,
                        lambda_=params.get('lambda_', 1e6),
                        p=params.get('p', 0.01),
                        niter=params.get('niter', 10)
                    )
                    if y_corrected is None:
                        QMessageBox.warning(self, "Normalization Failed", f"Baseline Correction failed for file {file_path}.")
                        continue
                    # Store normalized data
                    self.normalized_data[file_path] = (x, y_corrected)

                elif panel.method_name in methods_accepting_x:
                    # Methods that require 'x'
                    if panel.method_name == "AUC Normalization":
                        y_normalized = method_func(y, x=x, sort_data=params.get('sort_data', True))
                    elif panel.method_name == "Interval AUC Normalization":
                        y_normalized = method_func(
                            y,
                            x=x,
                            desired_auc=params.get('desired_auc', 1.0),
                            interval_start=params.get('interval_start', x.min()),
                            interval_end=params.get('interval_end', x.max())
                        )
                    elif panel.method_name == "Reference Peak Normalization":
                        y_normalized = method_func(
                            y,
                            x=x,
                            reference_peak_x=params.get('reference_peak_x', x[np.argmax(y)]),
                            desired_reference_intensity=params.get('desired_reference_intensity', 1.0)
                        )
                    else:
                        y_normalized = method_func(y, x=x, **params)

                    if y_normalized is None:
                        QMessageBox.warning(self, "Normalization Failed", f"Normalization failed for file {file_path}.")
                        continue
                    # Store normalized data
                    self.normalized_data[file_path] = (x, y_normalized)

                else:
                    # Methods that do not require 'x'
                    y_normalized = method_func(y, **params)
                    if y_normalized is None:
                        QMessageBox.warning(self, "Normalization Failed", f"Normalization failed for file {file_path}.")
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
        panel.send_to_data_panel_button.setEnabled(True)




    def save_normalized_data(self, panel):
        if not self.normalized_data:
            QMessageBox.warning(self, "No Normalized Data", "Please apply normalization first.")
            return

        # Get currently selected files
        data_files = self.selected_data_panel.get_selected_files()
        if not data_files:
            QMessageBox.warning(self, "No Data Selected", "Please select data files to save.")
            return

        # Select normalization method for naming
        method_name = panel.method_name.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "").replace("/", "_")

        # Ask user to select folder to save files
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Save Normalized Data")
        if not directory:
            return

        normalized_file_paths = []

        for file_path in data_files:
            if file_path in self.normalized_data:
                x, y_normalized = self.normalized_data[file_path]
                try:
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    new_file_name = f"{base_name}_{method_name}.csv"
                    new_file_path = os.path.join(directory, new_file_name)

                    plot_details = self.plot_details_panel.get_plot_details()
                    x_label = plot_details.get('x_label', 'X')
                    y_label = plot_details.get('y_label', 'Y')

                    df = pd.DataFrame({
                        x_label: x,
                        y_label: y_normalized
                    })

                    df.to_csv(new_file_path, index=False)
                    normalized_file_paths.append(new_file_path)

                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error saving file {new_file_path}: {e}")


        #if normalized_file_paths:
            # **Feature: Add Normalized Files to Selected Data Panel**
            #self.selected_data_panel.add_files(normalized_file_paths)  # Assuming this method exists
            #print(f"Normalized files added to Selected Data panel: {normalized_file_paths}")

        QMessageBox.information(self, "Save Successful", f"Normalized data saved to {directory}")
        print("All normalized files saved successfully.")

    def update_normalized_plot(self):
        if not self.normalized_data:
            QMessageBox.warning(self, "No Normalized Data", "Please apply normalization first.")
            return
        
        # Get currently selected files
        data_files = self.selected_data_panel.get_selected_files()
        if not data_files:
            QMessageBox.warning(self, "No Data Selected", "Please select data files to plot.")
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
    def send_normalized_data_to_data_panel(self, panel):
        if not self.normalized_data:
            QMessageBox.warning(self, "No Normalized Data", "Please apply normalization first.")
            return

        # Get currently selected files
        data_files = self.selected_data_panel.get_selected_files()
        if not data_files:
            QMessageBox.warning(self, "No Data Selected", "Please select data files to send.")
            return

        # Get method name for naming the files
        method_name = panel.method_name.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "").replace("/", "_")

        # Create a temporary directory to save the files
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix='normalized_data_')

        normalized_file_paths = []

        for file_path in data_files:
            if file_path in self.normalized_data:
                x, y_normalized = self.normalized_data[file_path]
                try:
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    new_file_name = f"{base_name}_{method_name}.csv"
                    new_file_path = os.path.join(temp_dir, new_file_name)

                    plot_details = self.plot_details_panel.get_plot_details()
                    x_label = plot_details.get('x_label', 'X')
                    y_label = plot_details.get('y_label', 'Y')

                    df = pd.DataFrame({
                        x_label: x,
                        y_label: y_normalized
                    })

                    df.to_csv(new_file_path, index=False)
                    normalized_file_paths.append(new_file_path)

                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error saving file {new_file_path}: {e}")

        if normalized_file_paths:
            # Add normalized files to Selected Data panel
            self.selected_data_panel.add_files(normalized_file_paths)
            QMessageBox.information(self, "Send Successful", "Normalized data sent to Selected Data panel.")
        else:
            QMessageBox.warning(self, "No Data Sent", "No normalized data was sent to the Selected Data panel.")

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

    def on_basic_corrections_section_expanded(self, expanded_section):
        if self.is_collapsing:
            return
        self.is_collapsing = True
        # When a section is expanded, collapse all other sections in basic corrections
        for section in self.basic_corrections_panels:
            if section != expanded_section and section.toggle_button.isChecked():
                section.toggle_button.setChecked(False)
        self.is_collapsing = False

    def interpolate_missing_values(self, series, method='mean'):
        """
        Replace NaN values in a pandas Series with the mean or median of the nearest non-NaN values above and below.

        Parameters:
        - series (pd.Series): The data series with potential NaN values.
        - method (str): 'mean' or 'median' specifying the replacement method.

        Returns:
        - pd.Series: The series with NaNs replaced.
        """
        for idx in series[series.isna()].index:
            # Find the nearest non-NaN above
            prev_idx = series[:idx].last_valid_index()
            # Find the nearest non-NaN below
            next_idx = series[idx + 1:].first_valid_index()

            # Initialize replacement value
            replacement = None

            # Retrieve the values
            if prev_idx is not None and next_idx is not None:
                val_prev = series.loc[prev_idx]
                val_next = series.loc[next_idx]
                if method == 'mean':
                    replacement = (val_prev + val_next) / 2
                elif method == 'median':
                    replacement = np.median([val_prev, val_next])
            elif prev_idx is not None:
                replacement = series.loc[prev_idx]
            elif next_idx is not None:
                replacement = series.loc[next_idx]

            # Replace the NaN with the calculated replacement value
            if replacement is not None:
                series.at[idx] = replacement
            else:
                # If no non-NaN values are found, leave it as NaN or decide on a default value
                pass  # You can choose to fill with 0 or another default value if desired

        return series

                
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

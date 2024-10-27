# gui/tabs/data_fitting_tab.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QToolButton, QScrollArea, QSizePolicy,
    QPushButton, QHBoxLayout, QFrame, QFileDialog, QListWidgetItem, QColorDialog, QTableWidget, QHeaderView, QTableWidgetItem,
    QMessageBox, QTextEdit, QButtonGroup, QGroupBox, QVBoxLayout, QDialog, QComboBox, QSpinBox, QCheckBox, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QIcon

from gui.panels.selected_data_panel import SelectedDataPanel
from gui.panels.plot_details_panels import (
    AxisDetailsPanel, AdditionalTextPanel,
    CustomAnnotationsPanel, PlotVisualsPanel, PlotDetailsPanel,
)

from plots.plotting import plot_data
from gui.utils.collapsible_sections import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
import matplotlib.text
from gui.plot.expanded_plot_window import ExpandedPlotWindow
from gui.dialogs.save_plot_dialog import SavePlotDialog
import sys
from utils import read_numeric_data
from functools import partial
from gui.panels.data_fitting_panels import GaussianFittingPanel
from functools import partial
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, peak_widths  # Ensure peak_widths is imported



def resource_path(relative_path):
    """ Get absolute path to resource, works for development and PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DataFittingTab(QWidget):

    plot_updated = pyqtSignal()  # Define the custom signal

    def __init__(self, general_tab, parent=None):
        super().__init__(parent)
        self.general_tab = general_tab
        self.is_collapsing = False  # Flag to prevent recursive signal handling
        self.fitted_data = {}  # To store fitted data
        self._updating_plot = False  # Initialize the flag
        self.column_names = {}  # Initialize column names dictionary



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

        # Column 1: Fitting Functionalities with Collapsible Sections
        # Create a QGroupBox for Fitting Methods
        self.fitting_methods_groupbox = QGroupBox("Fitting Methods")
        self.fitting_methods_groupbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)  # Set size policy

        fitting_methods_layout = QVBoxLayout()
        self.fitting_methods_groupbox.setLayout(fitting_methods_layout)

        # Add stretch at the end to push content to the top
        fitting_methods_layout.addStretch()


        self.fitting_methods = [
            ("Gaussian and Lorentzian Fitting", GaussianFittingPanel),
            # You can add more methods here in the future
        ]

        self.fitting_sections = []

                # Create FittingMethodPanel for each method
        for method_name, panel_class in self.fitting_methods:
            panel = panel_class()
            section = CollapsibleSection(method_name, panel)
            section.section_expanded.connect(self.on_fitting_section_expanded)
            self.fitting_sections.append(section)
            
            # Connect Apply, Save, and Send to Data Panel buttons using partial
            panel.apply_button.clicked.connect(partial(self.apply_fitting, panel))
            panel.save_button.clicked.connect(partial(self.save_fitted_data, panel))
            panel.send_to_data_panel_button.clicked.connect(partial(self.send_fitted_data_to_data_panel, panel))
            
            # Connect Run Peak Finder signal
            panel.run_peak_finder_signal.connect(partial(self.run_peak_finder, panel))

            # Connect parameters_changed signal
            #panel.parameters_changed.connect(partial(self.update_fitted_plot, panel))

            fitting_methods_layout.addWidget(section)

        # Arrange Column 1
        column1_layout = QVBoxLayout()
        column1_layout.setContentsMargins(0, 0, 0, 0)
        column1_layout.setSpacing(10)

        # Add the fitting methods groupbox to Column 1
        column1_layout.addWidget(self.fitting_methods_groupbox)


       # Set alignment for column1_layout to push content to the top
        column1_layout.addStretch()  # Add stretch to push content to the top

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

    def connect_signals(self):
        # Access panels
        self.selected_data_panel.file_selector_button.clicked.connect(self.choose_files)
        self.selected_data_panel.add_file_button.clicked.connect(self.add_files)
        self.selected_data_panel.select_all_button.clicked.connect(self.toggle_select_all_files)
        # self.additional_text_panel.text_color_button.clicked.connect(self.choose_text_color)
        self.additional_text_panel.add_text_button.clicked.connect(self.add_text_to_plot)
        self.additional_text_panel.delete_text_button.clicked.connect(self.delete_text_from_plot)
        self.custom_annotations_panel.apply_changes_button.clicked.connect(self.apply_changes)
        self.custom_annotations_panel.calculate_distance_button.clicked.connect(self.start_distance_calculation)
        # self.selected_data_panel.retract_button.clicked.connect(self.retract_from_general)
        self.expand_button.clicked.connect(self.expand_window)

        # Connect the "Retract from General" button if it exists
        if hasattr(self.selected_data_panel, 'retract_button'):
            self.selected_data_panel.retract_button.clicked.connect(self.retract_from_general)

    def on_section_expanded(self, expanded_section):
        if self.is_collapsing:
            return
        self.is_collapsing = True
        # When a section is expanded, collapse all other sections
        for section in self.collapsible_sections:
            if section != expanded_section and section.toggle_button.isChecked():
                section.toggle_button.setChecked(False)
        self.is_collapsing = False

    # Implement all other methods from NormalizationTab that are necessary
    # for the functionalities of the first and third columns

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

        # **Add selected files from General Tab to Data Fitting Tab without clearing existing files**
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
            QMessageBox.information(self, "Retract Successful", f"Added {len(added_files)} file(s) to the Data Fitting Tab.")
        else:
            QMessageBox.information(self, "No New Files", "No new files were added (they may already exist).")


    def on_fitting_section_expanded(self, expanded_section):
        if self.is_collapsing:
            return
        self.is_collapsing = True
        # When a section is expanded, collapse all other sections
        for section in self.fitting_sections:
            if section != expanded_section and section.toggle_button.isChecked():
                section.toggle_button.setChecked(False)
        self.is_collapsing = False

    def apply_fitting(self, panel, update_plot=True):
        # Get the selected data files
        data_files = self.selected_data_panel.get_selected_files()
        if not data_files:
            QMessageBox.warning(self, "No Data Selected", "Please select data files to fit.")
            return

        # Get fitting parameters from the panel
        params = panel.get_parameters()
        if params is None:
            return  # Error message already shown

        # Prepare to store any errors
        fitting_errors = []

        # Process each data file
        for file_path in data_files:
            try:
                # Use read_numeric_data to read the file
                df, x, y = self.read_numeric_data(file_path)
                if df is None:
                    print(f"Skipping file {file_path} due to insufficient data.")
                    continue

                # Extract column names
                if len(df.columns) >= 2:
                    x_col_name = df.columns[0]
                    y_col_name = df.columns[1]
                else:
                    x_col_name = 'X'
                    y_col_name = 'Y'

                self.column_names[file_path] = (x_col_name, y_col_name)  # Store column names

                # Perform fitting with mixed function types
                fitted_y, fit_info = self.perform_mixed_fitting(x, y, params['peaks'])

                if fitted_y is None or fit_info is None:
                    error_message = f"Fitting failed for file {file_path}."
                    fitting_errors.append(error_message)
                    print(error_message)
                    continue  # Skip this file

                # Store fitted data
                self.fitted_data[file_path] = (x, y, fitted_y, fit_info)

            except Exception as e:
                error_message = f"Error fitting file {file_path}: {e}"
                fitting_errors.append(error_message)
                print(error_message)

        if fitting_errors:
            QMessageBox.warning(self, "Fitting Errors", "\n".join(fitting_errors))

        # Open a separate interactive matplotlib window with the results
        self.plot_fitting_results(data_files)

        panel.save_button.setEnabled(True)
        panel.send_to_data_panel_button.setEnabled(True)


    def plot_fitting_results(self, data_files):
        import matplotlib.pyplot as plt

        # Create a new figure
        fig, ax = plt.subplots()

        # For each file, plot the data and the fit
        for file_path in data_files:
            if file_path in self.fitted_data:
                x, y, fitted_y, fit_info = self.fitted_data[file_path]
                label = os.path.basename(file_path)
                # Prepare label with additional parameters
                r_squared = fit_info['r_squared']
                reduced_chi_squared = fit_info['reduced_chi_squared']

                # Collect errors and function types for each peak
                fit_params = fit_info['fit_params']
                param_info = []
                for i, params in enumerate(fit_params):
                    function_type = params['function_type']
                    amplitude_err = params['amplitude_err']
                    center_err = params['center_err']
                    width_err = params['width_err']
                    param_info.append(
                        f"Peak {i+1} ({function_type}): Amp_err={amplitude_err:.2e}, Center_err={center_err:.2e}, Width_err={width_err:.2e}"
                    )

                params_text = '\n'.join(param_info)
                label_fit = f"{label} Fit\n$R^2$={r_squared:.4f}, $\chi^2$={reduced_chi_squared:.4f}\n{params_text}"

                # Plot original data
                ax.plot(x, y, 'b.', label=f"{label} Data")
                # Plot fitted curve
                ax.plot(x, fitted_y, 'r-', label=label_fit)
            else:
                print(f"No fitted data for file {file_path}")

        # Set labels
        if self.fitted_data:
            first_file_path = next(iter(self.fitted_data))
            x_col_name, y_col_name = self.column_names.get(first_file_path, ('X', 'Y'))
            ax.set_xlabel(x_col_name)
            ax.set_ylabel(y_col_name)
        else:
            ax.set_xlabel('X')
            ax.set_ylabel('Y')

        ax.legend(loc='best', fontsize='small')
        plt.title('Fitting Results')
        plt.show()

    

    def perform_mixed_fitting(self, x, y, peaks):
        from scipy.optimize import curve_fit

        # Ensure x and y are numpy arrays
        x = np.array(x)
        y = np.array(y)

        # Add debugging statement
        print("perform_mixed_fitting: Received peaks:", peaks)

        def composite_function(x, *params):
            y_fit = np.zeros_like(x)
            epsilon = 1e-10  # Small value to prevent division by zero
            for i, peak in enumerate(peaks):
                amplitude = params[i*3]
                center = params[i*3 + 1]
                width = params[i*3 + 2]
                width = max(width, epsilon)  # Ensure width is not zero
                function_type = peak['function_type']
                if function_type == 'Gaussian':
                    y_fit += amplitude * np.exp(-((x - center) ** 2) / (2 * width ** 2))
                elif function_type == 'Lorentzian':
                    y_fit += amplitude * (width ** 2 / ((x - center) ** 2 + width ** 2))
            return y_fit


        # Prepare initial guesses and bounds
        initial_guesses = []
        lower_bounds = []
        upper_bounds = []

        for peak in peaks:
            initial_guesses.extend([
                peak['amplitude'],
                peak['center'],
                peak['width']
            ])
            lower_bounds.extend([0, -np.inf, 0])  # amplitude >=0, center any, width >0
            upper_bounds.extend([np.inf, np.inf, np.inf])  # no upper bounds

        # Add debugging statement
        print("Initial guesses:", initial_guesses)
        print("Lower bounds:", lower_bounds)
        print("Upper bounds:", upper_bounds)

        try:
            popt, pcov = curve_fit(
                composite_function,
                x,
                y,
                p0=initial_guesses,
                bounds=(lower_bounds, upper_bounds),
                max_nfev=10000  # Increase maximum number of function evaluations
            )
        except RuntimeError as e:
            QMessageBox.warning(self, "Fitting Error", f"Fitting failed: {e}")
            print(f"Fitting failed: {e}")
            return None, None

        # Generate fitted y-values
        fitted_y = composite_function(x, *popt)

        # Extract fitted parameters with uncertainties
        fit_params = []
        for i in range(len(peaks)):
            amplitude = popt[i*3]
            center = popt[i*3 + 1]
            width = popt[i*3 + 2]
            amplitude_err = np.sqrt(pcov[i*3, i*3]) if pcov[i*3, i*3] > 0 else np.nan
            center_err = np.sqrt(pcov[i*3 + 1, i*3 + 1]) if pcov[i*3 + 1, i*3 + 1] > 0 else np.nan
            width_err = np.sqrt(pcov[i*3 + 2, i*3 + 2]) if pcov[i*3 + 2, i*3 + 2] > 0 else np.nan
            fit_params.append({
                'function_type': peaks[i]['function_type'],
                'amplitude': amplitude,
                'amplitude_err': amplitude_err,
                'center': center,
                'center_err': center_err,
                'width': width,
                'width_err': width_err
            })

        # Calculate residuals
        residuals = y - fitted_y

        # Calculate R-squared
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot)

        # Calculate Reduced Chi-Squared
        degrees_of_freedom = len(y) - len(popt)
        reduced_chi_squared = ss_res / degrees_of_freedom if degrees_of_freedom > 0 else np.nan

        # Prepare fit_info dictionary
        fit_info = {
            'fit_params': fit_params,
            'residuals': residuals,
            'r_squared': r_squared,
            'reduced_chi_squared': reduced_chi_squared,
        }

        print(f"Fitted Parameters: {fit_params}")  # Debugging statement
        print(f"Fitted Y-values Sample: {fitted_y[:5]}")  # Debugging statement
        print(f"R-squared: {r_squared}, Reduced Chi-Squared: {reduced_chi_squared}")

        return fitted_y, fit_info

    def perform_gaussian_fitting(self, x, y, peaks):
        from scipy.optimize import curve_fit

        # Ensure x and y are numpy arrays
        x = np.array(x)
        y = np.array(y)

        # Define the composite Gaussian function
        def gaussian(x, *params):
            y_fit = np.zeros_like(x)
            for i in range(0, len(params), 3):
                amplitude = params[i]
                center = params[i+1]
                width = params[i+2]
                y_fit += amplitude * np.exp(-((x - center) ** 2) / (2 * width ** 2))
            return y_fit

        # Prepare initial guesses
        initial_guesses = []
        for peak in peaks:
            initial_guesses.extend([
                peak['amplitude'],
                peak['center'],
                peak['width']
            ])

        # Define bounds: amplitude >0, width>0
        lower_bounds = []
        upper_bounds = []
        for _ in peaks:
            lower_bounds.extend([0, -np.inf, 0])  # amplitude >=0, center any, width >0
            upper_bounds.extend([np.inf, np.inf, np.inf])  # no upper bounds

        try:
            popt, pcov = curve_fit(
                gaussian,
                x,
                y,
                p0=initial_guesses,
                bounds=(lower_bounds, upper_bounds)
            )
        except RuntimeError as e:
            QMessageBox.warning(self, "Fitting Error", f"Gaussian fitting failed: {e}")
            print(f"Gaussian fitting failed: {e}")
            return None, None

        # Generate fitted y-values
        fitted_y = gaussian(x, *popt)

        # Extract fitted parameters with uncertainties
        fit_params = []
        for i in range(0, len(popt), 3):
            amplitude = popt[i]
            center = popt[i+1]
            width = popt[i+2]
            amplitude_err = np.sqrt(pcov[i, i]) if pcov[i, i] > 0 else np.nan
            center_err = np.sqrt(pcov[i+1, i+1]) if pcov[i+1, i+1] > 0 else np.nan
            width_err = np.sqrt(pcov[i+2, i+2]) if pcov[i+2, i+2] > 0 else np.nan
            fit_params.append({
                'amplitude': amplitude,
                'amplitude_err': amplitude_err,
                'center': center,
                'center_err': center_err,
                'width': width,
                'width_err': width_err
            })

        # Calculate residuals
        residuals = y - fitted_y

        # Calculate R-squared
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot)

        # Calculate Reduced Chi-Squared
        degrees_of_freedom = len(y) - len(popt)
        reduced_chi_squared = ss_res / degrees_of_freedom if degrees_of_freedom > 0 else np.nan

        # Prepare fit_info dictionary
        fit_info = {
            'fit_params': fit_params,
            'residuals': residuals,
            'r_squared': r_squared,
            'reduced_chi_squared': reduced_chi_squared,
        }

        print(f"Fitted Gaussian Parameters: {fit_params}")  # Debugging statement
        print(f"Fitted Y-values Sample: {fitted_y[:5]}")  # Debugging statement
        print(f"R-squared: {r_squared}, Reduced Chi-Squared: {reduced_chi_squared}")

        return fitted_y, fit_info


    def perform_lorentzian_fitting(self, x, y, peaks):
        from scipy.optimize import curve_fit

        # Ensure x and y are numpy arrays
        x = np.array(x)
        y = np.array(y)

        # Define the composite Lorentzian function
        def lorentzian(x, *params):
            y = np.zeros_like(x)
            for i in range(0, len(params), 3):
                amplitude = params[i]
                center = params[i+1]
                width = params[i+2]
                y += amplitude * (width ** 2 / ((x - center) ** 2 + width ** 2))
            return y

        # Prepare initial guesses
        initial_guesses = []
        for peak in peaks:
            initial_guesses.extend([
                peak['amplitude'],
                peak['center'],
                peak['width']
            ])

        # Define bounds: amplitude >0, width>0
        lower_bounds = []
        upper_bounds = []
        for _ in peaks:
            lower_bounds.extend([0, -np.inf, 0])  # amplitude >=0, center any, width >0
            upper_bounds.extend([np.inf, np.inf, np.inf])  # no upper bounds

        try:
            popt, pcov = curve_fit(
                lorentzian, 
                x, 
                y, 
                p0=initial_guesses, 
                bounds=(lower_bounds, upper_bounds)
            )
        except RuntimeError as e:
            QMessageBox.warning(self, "Fitting Error", f"Lorentzian fitting failed: {e}")
            print(f"Lorentzian fitting failed: {e}")
            return None, None

        # Generate fitted y-values
        fitted_y = lorentzian(x, *popt)

        # Extract fitted parameters with uncertainties
        fit_params = []
        for i in range(0, len(popt), 3):
            amplitude = popt[i]
            center = popt[i+1]
            width = popt[i+2]
            amplitude_err = np.sqrt(pcov[i, i]) if pcov[i, i] > 0 else np.nan
            center_err = np.sqrt(pcov[i+1, i+1]) if pcov[i+1, i+1] > 0 else np.nan
            width_err = np.sqrt(pcov[i+2, i+2]) if pcov[i+2, i+2] > 0 else np.nan
            fit_params.append({
                'amplitude': amplitude,
                'amplitude_err': amplitude_err,
                'center': center,
                'center_err': center_err,
                'width': width,
                'width_err': width_err
            })

        # Calculate residuals
        residuals = y - fitted_y

        # Calculate R-squared
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot)

        # Calculate Reduced Chi-Squared
        degrees_of_freedom = len(y) - len(popt)
        reduced_chi_squared = ss_res / degrees_of_freedom if degrees_of_freedom > 0 else np.nan

        # Prepare fit_info dictionary
        fit_info = {
            'fit_params': fit_params,
            'residuals': residuals,
            'r_squared': r_squared,
            'reduced_chi_squared': reduced_chi_squared,
        }

        print(f"Fitted Lorentzian Parameters: {fit_params}")  # Debugging statement
        print(f"Fitted Y-values Sample: {fitted_y[:5]}")  # Debugging statement
        print(f"R-squared: {r_squared}, Reduced Chi-Squared: {reduced_chi_squared}")

        return fitted_y, fit_info


    def send_fitted_data_to_data_panel(self, panel):
        if not self.fitted_data:
            QMessageBox.warning(self, "No Fitted Data", "Please apply fitting first.")
            return

        # Get currently selected files
        data_files = self.selected_data_panel.get_selected_files()
        if not data_files:
            QMessageBox.warning(self, "No Data Selected", "Please select data files to send.")
            return

        # Prepare to send data to the data panel
        # For this example, we'll save the fitted data to temporary files and add them to the selected data panel

        import tempfile

        fitted_file_paths = []

        for file_path in data_files:
            if file_path in self.fitted_data:
                x, y, fitted_y, fit_info = self.fitted_data[file_path]
                try:
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    new_file_name = f"{base_name}_fitted.csv"
                    temp_dir = tempfile.gettempdir()
                    new_file_path = os.path.join(temp_dir, new_file_name)

                    # Get original column names
                    x_col_name, y_col_name = self.column_names.get(file_path, ('X', 'Y'))

                    # Save x and fitted_y to CSV
                    df = pd.DataFrame({
                        x_col_name: x,
                        'Fitted_' + y_col_name: fitted_y
                    })

                    df.to_csv(new_file_path, index=False)
                    fitted_file_paths.append(new_file_path)

                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error saving file {new_file_path}: {e}")

        if fitted_file_paths:
            # Add fitted files to Selected Data panel
            self.selected_data_panel.add_files(fitted_file_paths)
            QMessageBox.information(self, "Send Successful", "Fitted data sent to Selected Data panel.")
        else:
            QMessageBox.warning(self, "No Data Sent", "No fitted data was sent to the Selected Data panel.")

    def run_peak_finder(self, panel):
        # Get the selected data files
        data_files = self.selected_data_panel.get_selected_files()
        if not data_files:
            QMessageBox.warning(self, "No Data Selected", "Please select a data file to run the peak finder.")
            return

        # For simplicity, use the first selected data file
        file_path = data_files[0]

        try:
            # Read the data
            df, x, y = self.read_numeric_data(file_path)
            if df is None:
                QMessageBox.warning(self, "Data Error", "Failed to read the data file or insufficient data.")
                return

            # Get sensitivity from panel
            try:
                sensitivity = float(panel.sensitivity_input.text())
                if not (0.0 < sensitivity < 1.0):
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Invalid Sensitivity", "Please enter a valid sensitivity value between 0 and 1.")
                return

            # Adjust parameters based on sensitivity
            # Lower sensitivity -> higher threshold (fewer peaks)
            # Higher sensitivity -> lower threshold (more peaks)
            height_threshold = max(y) * sensitivity
            prominence_threshold = max(y) * (0.1 * sensitivity)  # Adjust as needed
            distance_threshold = max(1, len(x) // 100)  # Adjust based on data density

            # Find peaks
            peaks_indices, properties = find_peaks(y, height=height_threshold, prominence=prominence_threshold, distance=distance_threshold)

            if len(peaks_indices) == 0:
                QMessageBox.information(self, "No Peaks Found", "No peaks were found with the given sensitivity.")
                return

            # Calculate peak widths using peak_widths
            widths_result = peak_widths(y, peaks_indices, rel_height=0.5)
            widths = widths_result[0]

            # Clear existing peaks in the table
            panel.peak_table.setRowCount(0)

            # Add detected peaks to the table with default function type
            for idx, width in zip(peaks_indices, widths):
                amplitude = y[idx]
                center = x[idx]
                panel.add_peak_row(amplitude, center, width, function_type='Gaussian')  # Default function type

            QMessageBox.information(self, "Peak Finder", f"Found {len(peaks_indices)} peak(s).")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error running peak finder: {e}")
            print(f"Error running peak finder: {e}")

    def update_fitted_plot(self, panel=None):
        if not self.fitted_data:
            print("No fitted data to plot.")  # Debugging statement
            return

        # If panel parameter is provided, re-apply fitting
        if panel:
            if self._updating_plot:
                return  # Prevent recursion if already updating
            self._updating_plot = True
            try:
                self.apply_fitting(panel, update_plot=False)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error during fitting: {e}")
                print(f"Error during fitting: {e}")
            finally:
                self._updating_plot = False
            # After re-applying fitting, update the plot
            self.update_fitted_plot()  # Call without panel to plot
            return

        # Clear the figure
        self.figure.clear()

        # Prepare the axis
        ax = self.figure.add_subplot(111)

        # Plot each fitted data
        for file_path, (x, y, fitted_y, fit_info) in self.fitted_data.items():
            label = os.path.basename(file_path)
            # Prepare label with additional parameters
            r_squared = fit_info['r_squared']
            reduced_chi_squared = fit_info['reduced_chi_squared']
            label_fit = f"{label} Fit\n$R^2$={r_squared:.4f}, $\chi^2$={reduced_chi_squared:.4f}"
            # Plot original data
            ax.plot(x, y, 'b.', label=f"{label} Data")
            # Plot fitted curve
            ax.plot(x, fitted_y, 'r-', label=label_fit)

        # Set labels
        if self.fitted_data:
            first_file_path = next(iter(self.fitted_data))
            x_col_name, y_col_name = self.column_names.get(first_file_path, ('X', 'Y'))
            ax.set_xlabel(x_col_name)
            ax.set_ylabel(y_col_name)
        else:
            ax.set_xlabel('X')
            ax.set_ylabel('Y')

        ax.legend()

        self.canvas.draw_idle()
        print("Plot updated with fitted data.")  # Debugging statement



    def save_fitted_data(self, panel):
        if not self.fitted_data:
            QMessageBox.warning(self, "No Fitted Data", "Please apply fitting first.")
            return

        # Get currently selected files
        data_files = self.selected_data_panel.get_selected_files()
        if not data_files:
            QMessageBox.warning(self, "No Data Selected", "Please select data files to save.")
            return

        # Ask user to select folder to save files
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Save Fitted Data")
        if not directory:
            return

        for file_path in data_files:
            if file_path in self.fitted_data:
                x, y, fitted_y, fit_info = self.fitted_data[file_path]
                try:
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    new_file_name = f"{base_name}_fitted.csv"
                    new_file_path = os.path.join(directory, new_file_name)

                    # Get original column names
                    x_col_name, y_col_name = self.column_names.get(file_path, ('X', 'Y'))

                    # Save x, original y, fitted y, residuals to CSV
                    df = pd.DataFrame({
                        x_col_name: x,
                        y_col_name: y,
                        'Fitted_' + y_col_name: fitted_y,
                        'Residuals': fit_info['residuals']
                    })

                    df.to_csv(new_file_path, index=False)

                    # Save fitting parameters to a separate file
                    params_file_name = f"{base_name}_fit_parameters.csv"
                    params_file_path = os.path.join(directory, params_file_name)

                    # Prepare parameters DataFrame
                    fit_params = fit_info['fit_params']
                    params_data = []
                    for i, peak_params in enumerate(fit_params):
                        params_data.append({
                            'Peak': i+1,
                            'Amplitude': peak_params['amplitude'],
                            'Amplitude_err': peak_params['amplitude_err'],
                            'Center': peak_params['center'],
                            'Center_err': peak_params['center_err'],
                            'Width': peak_params['width'],
                            'Width_err': peak_params['width_err'],
                        })
                    params_df = pd.DataFrame(params_data)
                    # Add R-squared and Reduced Chi-Squared at the end
                    params_df.loc[len(params_df)] = {
                        'Peak': 'Overall',
                        'Amplitude': np.nan,
                        'Amplitude_err': np.nan,
                        'Center': np.nan,
                        'Center_err': np.nan,
                        'Width': np.nan,
                        'Width_err': np.nan,
                        'R_squared': fit_info['r_squared'],
                        'Reduced_Chi_squared': fit_info['reduced_chi_squared']
                    }

                    params_df.to_csv(params_file_path, index=False)

                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error saving file {new_file_path}: {e}")

        QMessageBox.information(self, "Save Successful", f"Fitted data saved to {directory}")
        print("All fitted files saved successfully.")


    def update_plot(self):
        # Gather all parameters from panels
        print("DataFittingTab: update_plot called")

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
        print("DataFittingTab: plot_updated signal emitted")
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
        self.data_window.setWindowTitle("Data Structure - Data Fitting Tab")
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
            print("DataFittingTab: Creating a new ExpandedPlotWindow.")
            self.expanded_window = ExpandedPlotWindow(self)
            self.expanded_window.closed.connect(self.on_expanded_window_closed)
            self.expanded_window.show()
        except Exception as e:
            print(f"DataFittingTab: Error creating ExpandedPlotWindow: {e}")

    def on_expanded_window_closed(self):
        print("Expanded window closed.")
        self.expanded_window = None
        print("self.expanded_window has been reset to None.")

    def add_text_to_plot(self):
        text_details = self.additional_text_panel.get_text_details()
        if text_details['text'] and self.plot_type == "2D":
            try:
                x_pos = float(text_details['x_pos'])
                y_pos = float(text_details['y_pos'])
                text_size = text_details['size']
                text_color = text_details['color']
                text_item = self.figure.gca().text(
                    x_pos, y_pos, text_details['text'],
                    fontsize=text_size, color=text_color,
                    transform=self.figure.gca().transData, ha='left'
                )
                self.text_items.append(text_item)
                self.canvas.draw_idle()
            except ValueError:
                print("Invalid x or y position for additional text")

    def delete_text_from_plot(self):
        if self.text_items:
            text_item = self.text_items.pop()  # Remove the last added text item
            text_item.remove()  # Remove it from the plot
            self.canvas.draw_idle()

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

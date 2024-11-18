# gui/tabs/general_tab.py


from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QToolButton, QScrollArea, QSizePolicy,
    QPushButton, QHBoxLayout, QFrame, QFileDialog, QListWidgetItem, QColorDialog, QTableWidget, QHeaderView, QTableWidgetItem,
    QMessageBox, QButtonGroup, QGroupBox,QTextEdit,
      QVBoxLayout, QDialog, QComboBox, QSpinBox, QCheckBox,
        QLineEdit,QMessageBox,QDoubleSpinBox, QSplitter

)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QIcon

from gui.panels.selected_data_panel import SelectedDataPanel
from gui.panels.plot_details_panels import ( AxisDetailsPanel, AdditionalTextPanel,
    CustomAnnotationsPanel, PlotVisualsPanel, PlotDetailsPanel, )

from plots.plotting import plot_data
from gui.dialogs.latex_compatibility_dialog import LaTeXCompatibilityDialog 
from utils import read_numeric_data

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
from functools import partial  # Import at the top



def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

################################################################

class GeneralTab(QWidget):

    plot_updated = pyqtSignal()  # Define the custom signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.expanded_window = None  # To track the expanded window
        self.canvas.installEventFilter(self)

        self.apply_stylesheet()

        # Initialize the styles dictionary
        self.data_series_styles = {}

    def apply_stylesheet(self):
        stylesheet_path = resource_path('style.qss')
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r') as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Warning: stylesheet not found at {stylesheet_path}")

    def init_ui(self):
        # Initialize the main grid layout
        self.layout = QGridLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        # Initialize last_directory
        self.last_directory = os.path.expanduser("~")  

        # Instantiate panels
        self.selected_data_panel = SelectedDataPanel()
        self.axis_details_panel = AxisDetailsPanel()
        self.additional_text_panel = AdditionalTextPanel()
        self.custom_annotations_panel = CustomAnnotationsPanel()
        self.plot_visuals_panel = PlotVisualsPanel()
        self.plot_details_panel = PlotDetailsPanel()

        # Create a vertical splitter for the left column
        left_splitter = QSplitter(Qt.Vertical)

        # Add the Selected Data Panel to the splitter
        left_splitter.addWidget(self.selected_data_panel)

        # Create a widget to hold the lower panels (Plot Details and Custom Annotations)
        lower_left_widget = QWidget()
        lower_left_layout = QVBoxLayout(lower_left_widget)
        lower_left_layout.setContentsMargins(0, 0, 0, 0)
        lower_left_layout.setSpacing(5)

        # Add Plot Details Panel and Custom Annotations Panel to the lower layout
        lower_left_layout.addWidget(self.plot_details_panel)
        lower_left_layout.addWidget(self.custom_annotations_panel)

        # Add the lower widget to the splitter
        left_splitter.addWidget(lower_left_widget)

        # Set the stretch factors to allocate more space to Selected Data Panel
        left_splitter.setStretchFactor(0, 3)  # Selected Data Panel
        left_splitter.setStretchFactor(1, 1)  # Lower panels

        # Do the same for the right column (Axis Details and Additional Text)
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self.axis_details_panel)

        lower_right_widget = QWidget()
        lower_right_layout = QVBoxLayout(lower_right_widget)
        lower_right_layout.setContentsMargins(0, 0, 0, 0)
        lower_right_layout.setSpacing(5)

        lower_right_layout.addWidget(self.plot_visuals_panel)
        lower_right_layout.addWidget(self.additional_text_panel)

        right_splitter.addWidget(lower_right_widget)

        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 1)

        # Add splitters to the grid layout
        self.layout.addWidget(left_splitter, 0, 0)
        self.layout.addWidget(right_splitter, 0, 1)

        # Adjust column stretch to allocate more space to the plot area
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 4)

        # Initialize plot type and annotation variables
        self.plot_type = "2D"
        self.text_items = []
        self.annotations = []
        self.annotation_mode = None  # None, 'point', 'vline', 'hline'
        self.temp_annotation = None
        self.selected_lines = []

        # Plot area setup
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

        # Initialize buttons
        self.update_button = QPushButton("Update Plot")
        update_icon_path = resource_path('gui/resources/update_icon.png')
        self.update_button.setIcon(QIcon(update_icon_path))
        self.update_button.clicked.connect(self.update_plot)

        self.customize_styles_button = QPushButton("Customize Data Styles")
        customize_styles_icon_path = resource_path('gui/resources/data_styles_icon.png')
        self.customize_styles_button.setIcon(QIcon(customize_styles_icon_path))
        self.customize_styles_button.clicked.connect(self.open_data_styles_dialog)

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

        self.configure_subplots_button = QPushButton("Configure Subplots")
        configure_subplots_icon_path = resource_path('gui/resources/configure_subplots_icon.png')
        self.configure_subplots_button.setIcon(QIcon(configure_subplots_icon_path))
        self.configure_subplots_button.clicked.connect(self.open_subplots_config_dialog)

        # Create two separate horizontal layouts for the button rows
        self.plot_buttons_layout_row1 = QHBoxLayout()
        self.plot_buttons_layout_row2 = QHBoxLayout()

        # Add buttons to Row 1
        self.plot_buttons_layout_row1.addWidget(self.update_button)
        self.plot_buttons_layout_row1.addWidget(self.customize_styles_button)
        self.plot_buttons_layout_row1.addWidget(self.plot_type_2d_button)
        self.plot_buttons_layout_row1.addWidget(self.plot_type_3d_button)
        self.plot_buttons_layout_row1.addWidget(self.configure_subplots_button)

        # Add buttons to Row 2
        self.plot_buttons_layout_row2.addWidget(self.show_data_structure_button)
        self.plot_buttons_layout_row2.addWidget(self.expand_button)
        self.plot_buttons_layout_row2.addWidget(self.save_plot_button)

        # Create a vertical layout to hold both button rows
        self.plot_buttons_vertical_layout = QVBoxLayout()
        self.plot_buttons_vertical_layout.addLayout(self.plot_buttons_layout_row1)
        self.plot_buttons_vertical_layout.addLayout(self.plot_buttons_layout_row2)

        # Add the vertical button layout to the plot_layout
        plot_layout.addLayout(self.plot_buttons_vertical_layout)

        # Create a plot_widget and set its layout
        plot_widget = QWidget()
        plot_widget.setLayout(plot_layout)

        # Add the plot_widget to the main grid layout
        self.layout.addWidget(plot_widget, 0, 2)

        # Connect signals and slots from the panels
        self.connect_signals()

        # Connect the canvas to the event handlers
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

        # Update the plot_frame stylesheet for better aesthetics
        self.plot_frame.setStyleSheet("""
            #PlotFrame {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: #ffffff;  /* Set to white */
            }
        """)

        # **Ensure the Configure Subplots icon exists and set it; otherwise, warn the user**
        configure_subplots_icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'configure_subplots_icon.png')  
        if os.path.exists(configure_subplots_icon_path):  
            self.configure_subplots_button.setIcon(QIcon(configure_subplots_icon_path))  
        else:  
            print(f"Warning: Configure Subplots icon not found at {configure_subplots_icon_path}")  


    def connect_signals(self):
        # Access panels
        #general_tab = self

        self.selected_data_panel.file_selector_button.clicked.connect(self.choose_files)
        self.selected_data_panel.add_file_button.clicked.connect(self.add_files)
        self.selected_data_panel.select_all_button.clicked.connect(self.toggle_select_all_files)
        #self.additional_text_panel.text_color_button.clicked.connect(self.choose_text_color)
        self.additional_text_panel.add_text_button.clicked.connect(self.add_text_to_plot)
        self.additional_text_panel.delete_text_button.clicked.connect(self.delete_text_from_plot)
        self.custom_annotations_panel.apply_changes_button.clicked.connect(self.apply_changes)
        self.custom_annotations_panel.calculate_distance_button.clicked.connect(self.start_distance_calculation)

    # Include all other methods (choose_files, add_files, update_plot, etc.)
    # These methods are similar to those in the original main_window.py
    # Ensure all methods are properly implemented as in the previous code
        #self.expand_button.clicked.connect(self.expand_window)


    def open_data_styles_dialog(self):
        # Create and open the DataStylesDialog
        self.data_styles_dialog = DataStylesDialog(self)
        self.data_styles_dialog.exec_()
        # After the dialog is closed, update the plot with new styles
        self.update_plot()
        # Ensure the styles dialog is updated next time it's opened
        self.data_styles_dialog = None  # Force re-creation of the dialog

    def read_numeric_data(self, file_path):
        return read_numeric_data(file_path, parent=self)

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
            self.additional_text_panel.set_text_color(self.text_color)'''

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
        print("GeneralTab: update_plot called")  # Debugging statement

        data_files = self.selected_data_panel.get_selected_files()
        plot_details = self.plot_details_panel.get_plot_details()
        axis_details = self.axis_details_panel.get_axis_details()
        plot_visuals = self.plot_visuals_panel.get_plot_visuals()

        # Ensure data_series_styles only includes current data_files
        self.data_series_styles = {k: v for k, v in self.data_series_styles.items() if k in data_files}

        # Get per-data-series styles
        data_series_styles = self.data_series_styles

        # Call the plot_data function with data_series_styles
        plot_data(
            self.figure,
            data_files,
            plot_details,
            axis_details,
            plot_visuals,
            data_series_styles=data_series_styles,
            is_3d=(self.plot_type == "3D")
        )

        # Re-add all existing text items
        ax = self.figure.gca()
        if self.plot_type == "2D":
            for text_item in self.text_items:
                ax.add_artist(text_item)

        self.canvas.draw_idle()

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



    def eventFilter(self, obj, event):
        if obj == self.canvas and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.custom_annotations_panel.apply_changes_button.click()
                return True  # Event handled
        return super(GeneralTab, self).eventFilter(obj, event)


    def expand_window(self):
        print("Expand Window button clicked.")

        if self.expanded_window is not None:
            print("Expanded window already exists, bringing it to front.")
            self.expanded_window.raise_()
            return

        # Create a new window for the expanded plot
        try:
            print("GeneralTab: Creating a new ExpandedPlotWindow.")
            self.expanded_window = ExpandedPlotWindow(self)
            self.expanded_window.closed.connect(self.on_expanded_window_closed)
            self.expanded_window.show()
        except Exception as e:
            print(f"GeneralTab: Error creating ExpandedPlotWindow: {e}")

        # Connect to the closed signal to reset the reference
        #self.expanded_window.destroyed.connect(self.on_expanded_window_closed)

    def on_expanded_window_closed(self):
            print("Expanded window closed.")
            self.expanded_window = None  # Reset the reference when the window is closed
            print("self.expanded_window has been reset to None.")
        
    def on_click(self, event):
        if event.inaxes is None:
            return

        ax = event.inaxes

        # Get annotation type from the main CustomAnnotationsPanel
        annotation_type = self.custom_annotations_panel.get_annotation_type()

        # Apply annotations to this axes (subplot or main plot)
        self.apply_annotation(ax, event, annotation_type)




    def on_mouse_move(self, event):
        if event.inaxes is None:
            return

        ax = event.inaxes

        # Get annotation type from the main CustomAnnotationsPanel
        annotation_type = self.custom_annotations_panel.get_annotation_type()

        if annotation_type not in ['Vertical Line', 'Horizontal Line']:
            return

        if self.temp_annotation:
            self.temp_annotation.remove()
            self.temp_annotation = None

        if annotation_type == 'Vertical Line':
            if event.xdata is not None:
                self.temp_annotation = ax.axvline(x=event.xdata, color='r', linestyle='--')
        elif annotation_type == 'Horizontal Line':
            if event.ydata is not None:
                self.temp_annotation = ax.axhline(y=event.ydata, color='b', linestyle='--')

        self.canvas.draw_idle()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.custom_annotations_panel.apply_changes_button.click()
            event.accept()
        else:
            super().keyPressEvent(event)


    def apply_annotation(self, ax, event, annotation_type):
        if annotation_type == "Annotation Point":
            self.add_annotation_point(ax, event)
        elif annotation_type == "Vertical Line":
            self.add_vertical_line(ax, event)
        elif annotation_type == "Horizontal Line":
            self.add_horizontal_line(ax, event)
        elif annotation_type == "None":
            self.select_line(ax, event)

    def add_annotation_point(self, ax, event):
        if event.xdata is None or event.ydata is None:
            return
        star, = ax.plot(event.xdata, event.ydata, marker='*', color='black', markersize=10)
        text = ax.text(event.xdata, event.ydata, f'({event.xdata:.2f}, {event.ydata:.2f})', fontsize=10, color='black', ha='left')
        # Store annotations per axes
        if not hasattr(ax, 'annotations'):
            ax.annotations = []
        ax.annotations.append((star, text))
        self.canvas.draw_idle()



    def add_vertical_line(self, ax, event):
        if event.xdata is None:
            return
        line = ax.axvline(x=event.xdata, color='r', linestyle='--')
        if not hasattr(ax, 'annotations'):
            ax.annotations = []
        ax.annotations.append(line)
        self.canvas.draw_idle()


    def add_horizontal_line(self, ax, event):
        if event.ydata is None:
            return
        line = ax.axhline(y=event.ydata, color='b', linestyle='--')
        if not hasattr(ax, 'annotations'):
            ax.annotations = []
        ax.annotations.append(line)
        self.canvas.draw_idle()



    def apply_changes(self):
        self.annotation_mode = None
        self.temp_annotation = None
        # Reset annotation type in the main CustomAnnotationsPanel
        self.custom_annotations_panel.annotation_type_combo.setCurrentText("None")
        self.canvas.draw_idle()


    def select_line(self, ax, event):
        if event.xdata is None or event.ydata is None:
            return

        for ann in getattr(ax, 'annotations', []):
            if isinstance(ann, plt.Line2D):
                # Check if it's a vertical line
                if np.allclose(ann.get_xdata(), [ann.get_xdata()[0]]) and ann.contains(event)[0]:
                    self.selected_lines.append(ann)
                    if len(self.selected_lines) == 2:
                        self.calculate_distance(ax)
                    break
                # Check if it's a horizontal line
                elif np.allclose(ann.get_ydata(), [ann.get_ydata()[0]]) and ann.contains(event)[0]:
                    self.selected_lines.append(ann)
                    if len(self.selected_lines) == 2:
                        self.calculate_distance(ax)
                    break

    def start_distance_calculation(self):
        self.selected_lines.clear()
        # Reset annotation type in the main CustomAnnotationsPanel
        self.custom_annotations_panel.annotation_type_combo.setCurrentText("None")

    def calculate_distance(self, ax):
        if len(self.selected_lines) < 2:
            return

        line1, line2 = self.selected_lines

        if np.allclose(line1.get_xdata(), [line1.get_xdata()[0]]) and np.allclose(line2.get_xdata(), [line2.get_xdata()[0]]):  # Both lines are vertical
            x1 = line1.get_xdata()[0]
            x2 = line2.get_xdata()[0]
            dist = abs(x2 - x1)

            # Draw a horizontal arrow between the lines
            arrow = ax.annotate(
                f'd = {dist:.2f}',
                xy=((x1 + x2) / 2, ax.get_ylim()[1] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05),
                xytext=((x1 + x2) / 2, ax.get_ylim()[1] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05),
                arrowprops=dict(facecolor='black', arrowstyle='<->', lw=1.5),
                ha='center', va='center'
            )
            ax.annotations.append(arrow)

        elif np.allclose(line1.get_ydata(), [line1.get_ydata()[0]]) and np.allclose(line2.get_ydata(), [line2.get_ydata()[0]]):  # Both lines are horizontal
            y1 = line1.get_ydata()[0]
            y2 = line2.get_ydata()[0]
            dist = abs(y2 - y1)

            # Draw a vertical arrow between the lines
            arrow = ax.annotate(
                f'd = {dist:.2f}',
                xy=(ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.05, (y1 + y2) / 2),
                xytext=(ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.05, (y1 + y2) / 2),
                arrowprops=dict(facecolor='black', arrowstyle='<->', lw=1.5),
                ha='center', va='center', rotation=90
            )
            ax.annotations.append(arrow)

        self.selected_lines.clear()
        self.canvas.draw_idle()

    def apply_style_to_axes(self, ax, style_dict):
    # Apply style parameters to the axes
        for key, value in style_dict.items():
            if key.startswith('axes.'):
                param_name = key[5:]  # Remove 'axes.' prefix
                if param_name == 'facecolor':
                    ax.set_facecolor(value)
                elif param_name == 'edgecolor':
                    for spine in ax.spines.values():
                        spine.set_edgecolor(value)
                elif param_name == 'labelcolor':
                    ax.xaxis.label.set_color(value)
                    ax.yaxis.label.set_color(value)
                elif param_name == 'titlesize':
                    ax.title.set_fontsize(value)
                elif param_name == 'titleweight':
                    ax.title.set_fontweight(value)
                # Add more axes-related styles as needed
            elif key.startswith('xtick.'):
                param_name = key[6:]  # Remove 'xtick.' prefix
                if param_name == 'color':
                    ax.tick_params(axis='x', colors=value)
                elif param_name == 'labelsize':
                    ax.tick_params(axis='x', labelsize=value)
                # Add more xtick-related styles as needed
            elif key.startswith('ytick.'):
                param_name = key[6:]  # Remove 'ytick.' prefix
                if param_name == 'color':
                    ax.tick_params(axis='y', colors=value)
                elif param_name == 'labelsize':
                    ax.tick_params(axis='y', labelsize=value)
                # Add more ytick-related styles as needed
            elif key == 'grid.color':
                ax.grid(True, color=value)
            elif key == 'grid.linestyle':
                ax.grid(True, linestyle=value)
            elif key == 'grid.linewidth':
                ax.grid(True, linewidth=value)
            elif key == 'lines.linewidth':
                pass  # Handled in plot function
            elif key == 'lines.linestyle':
                pass  # Handled in plot function
            elif key == 'text.color':
                ax.title.set_color(value)
                ax.xaxis.label.set_color(value)
                ax.yaxis.label.set_color(value)
                for text in ax.texts:
                    text.set_color(value)
            # Handle other style parameters as needed


    def apply_font_settings(self, font_family, title_font_size, axis_font_size):
        for ax in self.figure.axes:
            # Update titles
            ax.title.set_fontsize(title_font_size)
            ax.title.set_fontfamily(font_family)

            # Update axis labels
            ax.xaxis.label.set_fontsize(axis_font_size)
            ax.xaxis.label.set_fontfamily(font_family)
            ax.yaxis.label.set_fontsize(axis_font_size)
            ax.yaxis.label.set_fontfamily(font_family)

            # Update tick labels
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(axis_font_size)
                label.set_fontfamily(font_family)

            # Update legend
            legend = ax.get_legend()
            if legend:
                for text in legend.get_texts():
                    text.set_fontsize(axis_font_size)
                    text.set_fontfamily(font_family)

            # Update annotations
            for child in ax.get_children():
                if isinstance(child, matplotlib.text.Annotation):
                    child.set_fontsize(axis_font_size)
                    child.set_fontfamily(font_family)

    def save_plot_with_options(self):
        print("Save Plot button clicked.")
        dialog = SavePlotDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            width_pixels, height_pixels, quality, latex_options = dialog.get_values()
            print(f"Saving plot with width: {width_pixels}px, height: {height_pixels}px, quality: {quality}")
            self.save_plot(width_pixels, height_pixels, quality, latex_options)

    def save_plot(self, width_pixels, height_pixels, quality, latex_options):
        # Map quality to dpi
        quality_dpi_mapping = {
            "Low": 72,
            "Medium": 150,
            "High": 300,
            "Very High": 600
        }
        dpi = quality_dpi_mapping.get(quality, 150)  # Default to 150 DPI if not found

        # Convert pixels to inches (assuming 100 pixels = 1 inch for simplicity)
        width_in = width_pixels / 100
        height_in = height_pixels / 100

        # Store original figure size, DPI, and rcParams
        original_size = self.figure.get_size_inches()
        original_dpi = self.figure.get_dpi()
        original_rcparams = plt.rcParams.copy()

        try:
            # Apply LaTeX settings if provided
            if latex_options:
                selected_font = latex_options['font_family']
                print(f"Selected font: '{selected_font}'")

                # Set figure size based on LaTeX settings
                width_unit = latex_options['width_unit']
                figure_width = latex_options['figure_width']
                if width_unit == 'inches':
                    width_in_inches = figure_width
                elif width_unit == 'cm':
                    width_in_inches = figure_width / 2.54
                elif width_unit == 'mm':
                    width_in_inches = figure_width / 25.4
                elif width_unit == 'pt':
                    width_in_inches = figure_width / 72.27
                elif width_unit == 'textwidth fraction':
                    # Assume standard LaTeX textwidth is 6.5 inches
                    width_in_inches = figure_width * 6.5
                else:
                    width_in_inches = figure_width  # Default to inches

                # Set figure size and DPI
                self.figure.set_size_inches(width_in_inches, self.figure.get_size_inches()[1])
                self.figure.set_dpi(latex_options['dpi'])

                # Update rcParams for font settings
                plt.rcParams.update({
                    'font.size': latex_options['base_font_size'],
                    'font.family': selected_font,
                })

                if latex_options['use_latex']:
                    plt.rcParams.update({
                        'text.usetex': True,
                        'font.family': selected_font,
                    })
                else:
                    plt.rcParams.update({'text.usetex': False})

                # Apply font settings to plot titles and axis labels
                self.apply_font_settings(
                    selected_font,
                    latex_options['title_font_size'],
                    latex_options['axis_font_size']
                )
            else:
                # If no LaTeX settings, apply the user-specified image size and quality
                self.figure.set_size_inches(width_in, height_in)
                self.figure.set_dpi(dpi)

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
                    # Save the figure with the specified DPI
                    self.figure.savefig(file_path, dpi=dpi)
                    QMessageBox.information(self, "Save Successful", f"Plot saved successfully at:\n{file_path}")
                    print(f"Plot saved successfully at: {file_path}")
                except Exception as e:
                    QMessageBox.warning(self, "Save Failed", f"Failed to save plot:\n{e}")
                    print(f"Failed to save plot: {e}")

        finally:
            # Restore original figure size, DPI, and rcParams to keep the interactive plot unaffected
            self.figure.set_size_inches(original_size)
            self.figure.set_dpi(original_dpi)
            plt.rcParams.update(original_rcparams)

            # Redraw the canvas to reflect original settings
            self.canvas.draw_idle()
            print("Figure size, DPI, and rcParams restored to original after saving.")

        
    def open_subplots_config_dialog(self):
        self.dialog = SubplotsConfigDialog(self)
        # Connect the apply_clicked signal
        self.dialog.apply_clicked.connect(self.on_subplots_apply)
        # Connect the accepted signal
        self.dialog.accepted.connect(self.on_subplots_accepted)
        # Show the dialog (non-blocking)
        self.dialog.show()

    def on_subplots_apply(self):
        # Retrieve configurations from the dialog
        self.subplot_configs_data = self.dialog.get_subplot_configs()
        self.layout_settings = self.dialog.get_layout_settings()
        # Update the plot with subplots
        self.update_plot_with_subplots()
        
    def on_subplots_accepted(self):
        # Retrieve configurations from the dialog
        self.subplot_configs_data = self.dialog.get_subplot_configs()
        self.layout_settings = self.dialog.get_layout_settings()
        # Update the plot with subplots
        self.update_plot_with_subplots()
        # Close the dialog
        self.dialog.close()
            
    def update_plot_with_subplots(self):

        # Store current rcParams
        original_rcparams = plt.rcParams.copy()

        if not hasattr(self, 'subplot_configs_data') or not self.subplot_configs_data:
            self.update_plot()  # Use existing plotting if no subplots are configured
            return

        # Clear the existing figure
        self.figure.clear()

        # Determine the layout based on user settings
        if self.layout_settings.get('auto_layout', False):
            num_subplots = len(self.subplot_configs_data)
            cols = int(np.ceil(np.sqrt(num_subplots)))
            rows = int(np.ceil(num_subplots / cols))
        else:
            rows = self.layout_settings.get('rows', 1)
            cols = self.layout_settings.get('columns', 1)

        # Set figure size based on the number of rows and columns
        self.figure.set_size_inches(5 * cols, 4 * rows)

        # Create subplots
        try:
            axes = self.figure.subplots(rows, cols, squeeze=False)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create subplots: {e}")
            return

        # Flatten the axes array for easy iteration
        axes = axes.flatten()

        # Iterate through each subplot configuration
        for idx, config in enumerate(self.subplot_configs_data):
            if idx >= len(axes):
                break  # Prevent index out of range if more subplots are configured than available axes

            ax = axes[idx]
            try:
                # Extract advanced options
                advanced_options = config.get('advanced_options', {})
                scale_type = advanced_options.get('scale_type', 'Linear')
                plot_style = advanced_options.get('plot_style', 'default')

                # Retrieve the style dictionary
                style_dict = plt.style.library.get(plot_style, {})

                # Apply style parameters to the axes
                self.apply_style_to_axes(ax, style_dict)

                # Apply LaTeX options if they exist
                latex_options = config.get('latex_options', None)
                if latex_options:
                    self.apply_latex_compatibility_to_axes(ax, latex_options)

                # Plot datasets with specified styles
                for dataset_config in config['datasets']:
                    df = pd.read_csv(dataset_config['dataset'])
                    x = df.iloc[:, int(dataset_config.get('x_column', 0))]
                    y = df.iloc[:, int(dataset_config.get('y_column', 1))]

                    # Retrieve per-dataset styling options
                    line_style = {
                        'Solid': '-',
                        'Dashed': '--',
                        'Dash-Dot': '-.',
                        'None': 'None'
                    }.get(dataset_config.get('line_style', 'Solid'), '-')
                    point_style = {
                        "None": "",
                        "Circle": "o",
                        "Square": "s",
                        "Triangle Up": "^",
                        "Triangle Down": "v",
                        "Star": "*",
                        "Plus": "+",
                        "Cross": "x",
                        "Diamond": "D",
                        "Pentagon": "p",
                        "Hexagon": "h",
                    }.get(dataset_config.get('point_style', 'None'), '')
                    line_thickness = dataset_config.get('line_thickness', 1.0)

                    label = dataset_config.get('legend_label', os.path.basename(dataset_config['dataset']))

                    # Plot the data
                    ax.plot(
                        x, y, label=rf"{label}",
                        linestyle=line_style if line_style != 'None' else '',
                        marker=point_style if point_style != '' else None,
                        linewidth=line_thickness
                    )

                # Set axis labels with LaTeX rendering
                ax.set_xlabel(rf"{config.get('x_axis_label', '')}", fontsize=12)
                ax.set_ylabel(rf"{config.get('y_axis_label', '')}", fontsize=12)

                # Set subplot title with customizable font size and LaTeX
                ax.set_title(rf"{config.get('subplot_title', f'Subplot {idx + 1}')}", fontsize=config.get('title_font_size', 14))

                # Set scale type
                x_scale = 'linear'
                y_scale = 'linear'
                if scale_type == 'Logarithmic X-Axis':
                    x_scale = 'log'
                elif scale_type == 'Logarithmic Y-Axis':
                    y_scale = 'log'
                elif scale_type == 'Logarithmic Both Axes':
                    x_scale = 'log'
                    y_scale = 'log'
                ax.set_xscale(x_scale)
                ax.set_yscale(y_scale)

                # Enable legend if required with customizable font size
                if config.get('enable_legend'):
                    legend_location = config.get('legend_location', 'best')
                    ax.legend(loc=legend_location, fontsize=config.get('legend_font_size', 10))
                else:
                    print(f"Legend not enabled for Subplot {idx + 1}")

                # Enable grid if required
                if config.get('enable_grid'):
                    print(f"Enabling grid for Subplot {idx + 1}")
                    ax.minorticks_on()
                    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
                    # Optional: Customize minor tick appearance
                    ax.tick_params(which='minor', length=4, color='gray')
                else:
                    print(f"Grid not enabled for Subplot {idx + 1}")

                # Initialize annotations list for this subplot
                if not hasattr(ax, 'annotations'):
                    ax.annotations = []

                # Store the subplot index in the axes object for event handling (optional)
                ax.subplot_index = idx

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to plot Subplot {idx + 1}: {e}")

        # Restore original rcParams
        plt.rcParams.update(original_rcparams)

        # Hide any unused axes
        for idx in range(len(self.subplot_configs_data), len(axes)):
            self.figure.delaxes(axes[idx])

        # Adjust layout for better spacing
        try:
            self.figure.tight_layout()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to adjust layout: {e}")

        # Render the updated plot
        self.canvas.draw_idle()



class DataStylesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.general_tab = parent
        self.setWindowTitle("Customize Data Styles")
        self.setMinimumSize(600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Table to display data files and their styles
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Data File', 'Line Style', 'Point Style', 'Line Thickness'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Populate the table with current data files and styles
        self.populate_table()

        # Connect signals
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def populate_table(self):
        data_files = self.general_tab.selected_data_panel.get_selected_files()
        self.table.setRowCount(len(data_files))

        for row, file_path in enumerate(data_files):
            file_name = os.path.basename(file_path)
            # Retrieve previous styles if available
            styles = self.general_tab.data_series_styles.get(file_path, {})
            line_style = styles.get('line_style', '-')  # default to '-'
            point_style = styles.get('point_style', '')  # default to 'o'
            line_thickness = styles.get('line_thickness', 1.0)  # default to 1.0

            # Data File Name
            file_name_item = QTableWidgetItem(file_name)
            file_name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            file_name_item.setData(Qt.UserRole, file_path)
            self.table.setItem(row, 0, file_name_item)

            # Line Style ComboBox
            line_style_combo = QComboBox()
            line_style_combo.addItems(['Solid', 'Dashed', 'Dash-Dot', 'None'])
            # Map line styles to matplotlib styles
            line_style_map = {'Solid': '-', 'Dashed': '--', 'Dash-Dot': '-.', 'None': 'None'}
            # Set current text based on existing style
            current_line_style = 'None' if line_style == 'None' else next(
                (k for k, v in line_style_map.items() if v == line_style), 'Solid'
            )
            line_style_combo.setCurrentText(current_line_style)
            self.table.setCellWidget(row, 1, line_style_combo)

            # Point Style ComboBox
            point_style_combo = QComboBox()
            point_style_combo.addItems(['None', 'Circle', 'Square', 'Triangle Up', 'Triangle Down', 'Star', 'Plus', 'Cross', 'Diamond', 'Pentagon', 'Hexagon'])
            # Map point styles to matplotlib styles
            point_style_map = {
                "None": "",
                "Circle": "o",
                "Square": "s",
                "Triangle Up": "^",
                "Triangle Down": "v",
                "Star": "*",
                "Plus": "+",
                "Cross": "x",
                "Diamond": "D",
                "Pentagon": "p",
                "Hexagon": "h",
            }
            # Set current text based on existing style
            current_point_style = 'None' if point_style == 'None' else next(
                (k for k, v in point_style_map.items() if v == point_style), 'Circle'
            )
            point_style_combo.setCurrentText(current_point_style)
            self.table.setCellWidget(row, 2, point_style_combo)

            # Line Thickness SpinBox
            line_thickness_spin = QDoubleSpinBox()
            line_thickness_spin.setRange(0.1, 10.0)
            line_thickness_spin.setSingleStep(0.1)
            line_thickness_spin.setValue(line_thickness)
            self.table.setCellWidget(row, 3, line_thickness_spin)

    def accept(self):
        # Update the styles in the GeneralTab
        for row in range(self.table.rowCount()):
            file_name_item = self.table.item(row, 0)
            if file_name_item is None:
                continue
            file_path = file_name_item.data(Qt.UserRole)

            # Get widgets
            line_style_combo = self.table.cellWidget(row, 1)
            point_style_combo = self.table.cellWidget(row, 2)
            line_thickness_spin = self.table.cellWidget(row, 3)

            # Get values
            selected_line_style = line_style_combo.currentText()
            line_style_map = {'Solid': '-', 'Dashed': '--', 'Dash-Dot': '-.', 'None': 'None'}
            line_style = line_style_map.get(selected_line_style, '-')

            selected_point_style = point_style_combo.currentText()
            point_style_map = {
                "None": "",
                "Circle": "o",
                "Square": "s",
                "Triangle Up": "^",
                "Triangle Down": "v",
                "Star": "*",
                "Plus": "+",
                "Cross": "x",
                "Diamond": "D",
                "Pentagon": "p",
                "Hexagon": "h",
            }
            point_style = point_style_map.get(selected_point_style, 'o')

            line_thickness = line_thickness_spin.value()

            # Update styles in GeneralTab
            self.general_tab.data_series_styles[file_path] = {
                'line_style': line_style,
                'point_style': point_style,
                'line_thickness': line_thickness
            }

        super().accept()  # Close the dialog

# gui/panels.py

import os
from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QScrollArea, QCheckBox, QSpinBox, QComboBox, QHBoxLayout,
    QListWidgetItem, QColorDialog, QMessageBox, QFileDialog, QWidget, QMenu, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from utils import read_numeric_data  # Ensure this import is correct
import h5py
import pandas as pd

class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.MultiSelection)  # Enable multi-selection
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

    def keyPressEvent(self, event):
        """
        Handle key press events. If the Delete key is pressed, remove selected items.
        """
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
        else:
            super().keyPressEvent(event)

    def delete_selected_items(self):
        """
        Delete all selected items from the list after confirmation.
        """
        selected_items = self.selectedItems()
        if not selected_items:
            return
        reply = QMessageBox.question(
            self, 'Confirm Deletion',
            f"Are you sure you want to delete the selected {len(selected_items)} file(s)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for item in selected_items:
                self.takeItem(self.row(item))
            QMessageBox.information(self, "Deletion Successful", f"Deleted {len(selected_items)} file(s).")

    def open_context_menu(self, position):
        """
        Create a context menu with a 'Delete' option on right-click.
        """
        context_menu = QMenu(self)
        delete_action = context_menu.addAction("Delete")
        action = context_menu.exec_(self.mapToGlobal(position))
        if action == delete_action:
            self.delete_selected_items()

    def dragEnterEvent(self, event):
        """
        Accept the drag event if it contains URLs (files).
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """
        Accept the drag move event if it contains URLs (files).
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Handle the drop event by adding the dropped files to the list.
        """
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    self.add_file_to_panel(file_path)
            event.acceptProposedAction()
        else:
            event.ignore()

    def add_file_to_panel(self, file_path):
        """
        Add a single file to the Selected Data Panel.
        Avoid adding duplicates.
        """
        file_name = os.path.basename(file_path)
        # Avoid adding duplicates
        existing_files = [self.item(i).data(Qt.UserRole) for i in range(self.count())]
        if file_path in existing_files:
            return
        item = QListWidgetItem(file_name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Unchecked)
        item.setData(Qt.UserRole, file_path)
        self.addItem(item)


class SelectedDataPanel(QGroupBox):
    def __init__(self, include_retract_button=False, parent=None):
        super().__init__("Selected Data", parent)
        self.last_directory = os.path.expanduser("~")  # Initialize to user's home directory
        self.all_selected = False  # Initialize selection state
        self.init_ui(include_retract_button)

    def init_ui(self, include_retract_button):
        self.layout = QVBoxLayout()

        # Buttons for file operations
        self.file_selector_button = QPushButton("Choose Files")
        self.add_file_button = QPushButton("Add Files")
        self.select_all_button = QPushButton("Select All")
        self.remove_selected_button = QPushButton("Remove Selected")  # Optional Remove Button

        # Tooltips for better UX
        self.file_selector_button.setToolTip("Click to choose and add files to the Selected Data panel.")
        self.add_file_button.setToolTip("Click to add more files to the Selected Data panel.")
        self.select_all_button.setToolTip("Click to select or deselect all files.")
        self.remove_selected_button.setToolTip("Click to remove selected files from the Selected Data panel.")

        # Optional Retract Button
        if include_retract_button:
            self.retract_button = QPushButton("Retract from General")
            self.layout.addWidget(self.retract_button)

        # Draggable and Selectable List Widget
        self.selected_files_list = DraggableListWidget()

        # Scroll Area for the List Widget
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.selected_files_list)

        # Add buttons to the layout
        self.layout.addWidget(self.file_selector_button)
        self.layout.addWidget(self.add_file_button)
        self.layout.addWidget(self.select_all_button)
        self.layout.addWidget(self.remove_selected_button)  # Add Remove Button

        # Add the scroll area containing the list widget
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

        # Connect buttons to their respective functions
        self.file_selector_button.clicked.connect(self.choose_files)
        self.add_file_button.clicked.connect(self.add_files)
        self.select_all_button.clicked.connect(self.toggle_select_all)
        self.remove_selected_button.clicked.connect(self.remove_selected_files)  # Connect Remove Button

    def choose_files(self):
        """
        Open a file dialog to select multiple files and add them to the panel.
        """
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            self.last_directory,  # Open the last used directory
            "All Files (*)"
        )
        if file_paths:
            self.add_file_to_panel(file_paths)
            # Update last_directory to the directory of the last selected file
            self.last_directory = os.path.dirname(file_paths[-1])

    def add_files(self):
        """
        Alias for choose_files to maintain consistency.
        """
        self.choose_files()

    def toggle_select_all(self):
        """
        Toggle between selecting all files and deselecting all files.
        """
        if not self.all_selected:
            # Select all
            for index in range(self.selected_files_list.count()):
                item = self.selected_files_list.item(index)
                item.setCheckState(Qt.Checked)
            self.select_all_button.setText("Deselect All")
            self.all_selected = True
        else:
            # Deselect all
            for index in range(self.selected_files_list.count()):
                item = self.selected_files_list.item(index)
                item.setCheckState(Qt.Unchecked)
            self.select_all_button.setText("Select All")
            self.all_selected = False

    def get_selected_files(self):
        """
        Retrieve a list of file paths that are currently selected (checked).
        """
        selected_items = [
            item for item in self.selected_files_list.findItems("*", Qt.MatchWildcard)
            if item.checkState() == Qt.Checked
        ]
        return [item.data(Qt.UserRole) for item in selected_items]

    def add_file_to_panel(self, file_paths):
        """
        Add one or multiple files to the Selected Data Panel.
        """
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        for file_path in file_paths:
            self.selected_files_list.add_file_to_panel(file_path)

    def select_files(self, file_paths):
        """
        Programmatically select and add multiple files to the panel.
        """
        self.add_file_to_panel(file_paths)

    def remove_selected_files(self):
        """
        Remove selected files from the Selected Data Panel.
        """
        selected_items = self.selected_files_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "No files selected to remove.")
            return
        reply = QMessageBox.question(
            self, 'Confirm Removal',
            f"Are you sure you want to remove the selected {len(selected_items)} file(s)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for item in selected_items:
                self.selected_files_list.takeItem(self.selected_files_list.row(item))
            QMessageBox.information(self, "Removal Successful", f"Removed {len(selected_items)} file(s).")

    # Optional Retract Functionality
    def retract_from_general(self):
        # Implementation as per your application logic
        pass


class H5DataHandlingPanel(QGroupBox):
    def __init__(self, selected_data_panel, parent=None):
        super().__init__("H5 Data Handling", parent)
        self.selected_data_panel = selected_data_panel
        self.parent_widget = parent  # Reference to DataHandlingTab
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Collapsible Local Processing Section
        self.local_processing_group = QGroupBox("Local Processing Selected H5 Files")
        self.local_processing_group.setCheckable(True)
        self.local_processing_group.setChecked(True)
        local_layout = QVBoxLayout()
        self.local_processing_group.setLayout(local_layout)

        # Select H5 Files Button
        self.select_h5_files_button = QPushButton("Select H5 Files")
        self.select_h5_files_button.setIcon(QIcon('gui/resources/select_h5_icon.png'))  # Ensure the icon exists
        self.select_h5_files_button.clicked.connect(self.select_h5_files)
        local_layout.addWidget(self.select_h5_files_button)

        # List of Selected H5 Files
        self.h5_files_list = QListWidget()
        local_layout.addWidget(self.h5_files_list)

        # Select Datasets Button
        self.select_datasets_button = QPushButton("Select Datasets")
        self.select_datasets_button.setIcon(QIcon('gui/resources/select_datasets_icon.png'))  # Ensure the icon exists
        self.select_datasets_button.clicked.connect(self.select_datasets)
        local_layout.addWidget(self.select_datasets_button)

        # List of Selected Datasets
        self.selected_datasets_list = QListWidget()
        local_layout.addWidget(self.selected_datasets_list)

        # Combine and Export Button
        self.combine_export_button = QPushButton("Combine and Export")
        self.combine_export_button.setIcon(QIcon('gui/resources/combine_export_icon.png'))  # Ensure the icon exists
        self.combine_export_button.clicked.connect(self.combine_and_export)
        self.combine_export_button.setEnabled(False)  # Disabled until datasets are selected
        local_layout.addWidget(self.combine_export_button)

        # Generated CSV Files Label and List
        self.csv_files_label = QLabel("Generated CSV Files:")
        local_layout.addWidget(self.csv_files_label)
        #self.csv_files_list = QListWidget()
        #local_layout.addWidget(self.csv_files_list)

        # Send to Local Tabs Section
        self.send_to_tabs_group = QGroupBox("Send to Local Tabs")
        send_to_tabs_layout = QHBoxLayout()
        self.send_to_tabs_group.setLayout(send_to_tabs_layout)

        self.general_tab_checkbox = QCheckBox("General Tab")
        self.normalization_tab_checkbox = QCheckBox("Normalization Tab")
        send_to_tabs_layout.addWidget(self.general_tab_checkbox)
        send_to_tabs_layout.addWidget(self.normalization_tab_checkbox)

        local_layout.addWidget(self.send_to_tabs_group)

        # Apply Button for Sending CSV Files
        self.apply_send_button = QPushButton("Send to Selected Tabs")
        self.apply_send_button.clicked.connect(self.send_csv_files_to_tabs)
        self.apply_send_button.setEnabled(False)  # Disabled until CSV files are generated
        local_layout.addWidget(self.apply_send_button)

        # Add the Local Processing section to the main layout
        self.layout.addWidget(self.local_processing_group)

        # Collapsible Batch Processing Section
        self.batch_processing_group = QGroupBox("Batch Processing H5 Files")
        self.batch_processing_group.setCheckable(True)
        self.batch_processing_group.setChecked(False)
        batch_layout = QVBoxLayout()
        self.batch_processing_group.setLayout(batch_layout)

        # Select Directory Button
        self.select_directory_button = QPushButton("Select Directory")
        self.select_directory_button.setIcon(QIcon('gui/resources/select_directory_icon.png'))  # Ensure the icon exists
        self.select_directory_button.clicked.connect(self.select_directory)
        batch_layout.addWidget(self.select_directory_button)

        # Directory Label
        self.directory_label = QLabel("No directory selected.")
        batch_layout.addWidget(self.directory_label)

        # Include All Subfolders Checkbox
        self.include_subfolders_checkbox = QCheckBox("Include All Subfolders")
        batch_layout.addWidget(self.include_subfolders_checkbox)

        # Select Datasets Button
        self.batch_select_datasets_button = QPushButton("Select Datasets")
        self.batch_select_datasets_button.setIcon(QIcon('gui/resources/select_datasets_icon.png'))  # Ensure the icon exists
        self.batch_select_datasets_button.clicked.connect(self.batch_select_datasets)
        batch_layout.addWidget(self.batch_select_datasets_button)

        # Combine and Export Button for Batch Processing
        self.batch_combine_export_button = QPushButton("Combine and Export")
        self.batch_combine_export_button.setIcon(QIcon('gui/resources/combine_export_icon.png'))  # Ensure the icon exists
        self.batch_combine_export_button.clicked.connect(self.batch_combine_and_export)
        self.batch_combine_export_button.setEnabled(False)  # Disabled until datasets are selected
        batch_layout.addWidget(self.batch_combine_export_button)

        # Add the Batch Processing section to the main layout
        self.layout.addWidget(self.batch_processing_group)

        self.setLayout(self.layout)

    # ----------------- Local Processing Methods -----------------

    def select_h5_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select H5 Files", "", "H5 Files (*.h5 *.hdf5);;All Files (*)")
        if files:
            self.h5_files_list.clear()
            for file in files:
                item = QListWidgetItem(os.path.basename(file))
                item.setData(Qt.UserRole, file)
                self.h5_files_list.addItem(item)
            self.combine_export_button.setEnabled(True)

    def select_datasets(self):
        # Get selected H5 files
        h5_files = [self.h5_files_list.item(i).data(Qt.UserRole) for i in range(self.h5_files_list.count())]
        if not h5_files:
            QMessageBox.warning(self, "No H5 Files Selected", "Please select H5 files first.")
            return

        # Assume structural consistency and select datasets from the first file
        try:
            with h5py.File(h5_files[0], 'r') as h5_file:
                structure = self.get_h5_structure(h5_file)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read H5 file {h5_files[0]}:\n{e}")
            return

        # Open a dialog to select datasets
        selected_datasets = self.show_structure_and_get_datasets(structure)
        if selected_datasets:
            self.selected_datasets_list.clear()
            for dataset in selected_datasets:
                item = QListWidgetItem(dataset)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setCheckState(Qt.Checked)
                self.selected_datasets_list.addItem(item)
            self.combine_export_button.setEnabled(True)
        else:
            self.selected_datasets_list.clear()
            self.combine_export_button.setEnabled(False)

    def show_structure_and_get_datasets(self, structure):
        # Display the structure and allow the user to select datasets
        dialog = DatasetSelectionDialog(structure, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_datasets = dialog.get_selected_datasets()
            return selected_datasets
        else:
            return []

    def combine_and_export(self):
        # Get selected datasets from the list
        selected_datasets = [
            self.selected_datasets_list.item(i).text()
            for i in range(self.selected_datasets_list.count())
            if self.selected_datasets_list.item(i).checkState() == Qt.Checked
        ]

        if not selected_datasets:
            QMessageBox.warning(self, "No Datasets Selected", "Please select at least one dataset to combine.")
            return

        # Get selected H5 files
        h5_files = [self.h5_files_list.item(i).data(Qt.UserRole) for i in range(self.h5_files_list.count())]
        if not h5_files:
            QMessageBox.warning(self, "No H5 Files Selected", "Please select H5 files first.")
            return

        # Initialize list to store CSV file paths
        csv_files = []

        # Process each H5 file
        for file in h5_files:
            try:
                with h5py.File(file, 'r') as h5_file:
                    data = self.extract_datasets(h5_file, selected_datasets)
                
                # Combine datasets into a single CSV
                combined_csv = self.combine_datasets_to_csv(data, file)
                csv_files.append(combined_csv)
                
                # Add generated CSV to the CSV Files List
                #self.csv_files_list.add_item(combined_csv)
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to process H5 file {file}:\n{e}")
                continue  # Proceed to next file

        if csv_files:
            QMessageBox.information(self, "Export Complete", "Selected datasets have been combined and exported as CSV files.")
            self.apply_send_button.setEnabled(True)
        else:
            QMessageBox.warning(self, "No CSV Created", "No CSV files were created.")

    def extract_datasets(self, h5_file, datasets):
        # Extract selected datasets
        data = {}
        for dataset_name in datasets:
            if dataset_name in h5_file:
                data[dataset_name] = h5_file[dataset_name][:]
            else:
                raise KeyError(f"Dataset {dataset_name} not found in H5 file.")
        return data

    def combine_datasets_to_csv(self, data, h5_file_path):
        # Combine datasets into a DataFrame
        df = pd.DataFrame()
        for dataset_name, values in data.items():
            # Handle datasets based on dimensions
            if values.ndim == 1:
                df[dataset_name] = values
            elif values.ndim == 2:
                # For 2D datasets, flatten columns
                for i in range(values.shape[1]):
                    col_name = f"{dataset_name}_{i}"
                    df[col_name] = values[:, i]
            else:
                # Skip datasets with higher dimensions
                continue

        # Define the CSV file path
        base_name = os.path.splitext(os.path.basename(h5_file_path))[0]
        csv_file_name = f"{base_name}_combined.csv"
        csv_file_path = os.path.join(os.path.dirname(h5_file_path), csv_file_name)

        # Save DataFrame to CSV
        df.to_csv(csv_file_path, index=False)
        return csv_file_path

    def add_item(self, csv_file_path):
        """
        Add a CSV file to the CSV Files List.
        """
        file_name = os.path.basename(csv_file_path)
        item = QListWidgetItem(file_name)
        item.setData(Qt.UserRole, csv_file_path)
        item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.csv_files_list.addItem(item)

    def delete_selected_csv_files(self):
        """
        Delete selected CSV files from the list.
        """
        selected_items = self.csv_files_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "No CSV files selected to delete.")
            return
        reply = QMessageBox.question(
            self, 'Confirm Deletion',
            f"Are you sure you want to delete the selected {len(selected_items)} CSV file(s)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for item in selected_items:
                csv_file_path = item.data(Qt.UserRole)
                try:
                    os.remove(csv_file_path)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to delete {csv_file_path}:\n{e}")
                    continue
                self.csv_files_list.takeItem(self.csv_files_list.row(item))
            QMessageBox.information(self, "Deletion Successful", f"Deleted {len(selected_items)} CSV file(s).")

    def send_csv_files_to_tabs(self):
        selected_items = self.csv_files_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No CSV Files Selected", "Please select CSV files to send.")
            return

        target_tabs = []
        if self.general_tab_checkbox.isChecked():
            target_tabs.append(self.parent_widget.parent().general_tab)  # Adjust according to your tab structure
        if self.normalization_tab_checkbox.isChecked():
            target_tabs.append(self.parent_widget.parent().normalization_tab)  # Adjust accordingly

        if not target_tabs:
            QMessageBox.warning(self, "No Tabs Selected", "Please select at least one tab to send files to.")
            return

        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            for tab in target_tabs:
                tab.selected_data_panel.add_file_to_panel([file_path])

        QMessageBox.information(self, "Send Successful", "Selected CSV files have been sent to the chosen tabs.")

    # ----------------- Batch Processing Methods -----------------

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory Containing H5 Files")
        if directory:
            self.selected_directory = directory
            self.directory_label.setText(f"Selected Directory: {directory}")
            self.batch_combine_export_button.setEnabled(True)
        else:
            self.selected_directory = None
            self.directory_label.setText("No directory selected.")
            self.batch_combine_export_button.setEnabled(False)

    def batch_select_datasets(self):
        if not hasattr(self, 'selected_directory') or not self.selected_directory:
            QMessageBox.warning(self, "No Directory Selected", "Please select a directory first.")
            return

        # Collect all H5 files in the directory (and subdirectories if checked)
        include_subfolders = self.include_subfolders_checkbox.isChecked()
        h5_files = []
        if include_subfolders:
            for root, dirs, files in os.walk(self.selected_directory):
                for file in files:
                    if file.endswith('.h5') or file.endswith('.hdf5'):
                        h5_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(self.selected_directory):
                if file.endswith('.h5') or file.endswith('.hdf5'):
                    h5_files.append(os.path.join(self.selected_directory, file))

        if not h5_files:
            QMessageBox.warning(self, "No H5 Files Found", "No H5 files found in the selected directory.")
            return

        # Assume structural consistency and select datasets from the first file
        try:
            with h5py.File(h5_files[0], 'r') as h5_file:
                structure = self.get_h5_structure(h5_file)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read H5 file {h5_files[0]}:\n{e}")
            return

        # Open a dialog to select datasets
        selected_datasets = self.show_structure_and_get_datasets(structure)
        if selected_datasets:
            self.selected_datasets_list.clear()
            for dataset in selected_datasets:
                item = QListWidgetItem(dataset)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setCheckState(Qt.Checked)
                self.selected_datasets_list.addItem(item)
            self.batch_combine_export_button.setEnabled(True)
        else:
            self.selected_datasets_list.clear()
            self.batch_combine_export_button.setEnabled(False)

    def batch_combine_and_export(self):
        # Get selected datasets from the list
        selected_datasets = [
            self.selected_datasets_list.item(i).text()
            for i in range(self.selected_datasets_list.count())
            if self.selected_datasets_list.item(i).checkState() == Qt.Checked
        ]

        if not selected_datasets:
            QMessageBox.warning(self, "No Datasets Selected", "Please select at least one dataset to combine.")
            return

        if not hasattr(self, 'selected_directory') or not self.selected_directory:
            QMessageBox.warning(self, "No Directory Selected", "Please select a directory first.")
            return

        # Collect all H5 files
        include_subfolders = self.include_subfolders_checkbox.isChecked()
        h5_files = []
        if include_subfolders:
            for root, dirs, files in os.walk(self.selected_directory):
                for file in files:
                    if file.endswith('.h5') or file.endswith('.hdf5'):
                        h5_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(self.selected_directory):
                if file.endswith('.h5') or file.endswith('.hdf5'):
                    h5_files.append(os.path.join(self.selected_directory, file))

        if not h5_files:
            QMessageBox.warning(self, "No H5 Files Found", "No H5 files found in the selected directory.")
            return

        # Initialize list to store CSV file paths
        csv_files = []

        # Process each H5 file
        for file in h5_files:
            try:
                with h5py.File(file, 'r') as h5_file:
                    data = self.extract_datasets(h5_file, selected_datasets)
                
                # Combine datasets into a single CSV
                combined_csv = self.combine_datasets_to_csv(data, file)
                csv_files.append(combined_csv)
                
                # Add generated CSV to the CSV Files List
                self.csv_files_list.add_item(combined_csv)
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to process H5 file {file}:\n{e}")
                continue  # Proceed to next file

        if csv_files:
            QMessageBox.information(self, "Export Complete", "Selected datasets have been combined and exported as CSV files.")
            self.apply_send_button.setEnabled(True)
        else:
            QMessageBox.warning(self, "No CSV Created", "No CSV files were created.")

    # ----------------- Common Methods -----------------

    def get_h5_structure(self, h5_file):
        # Recursively get the structure of the H5 file
        structure = {}
        
        def visitor(name, node):
            if isinstance(node, h5py.Dataset):
                structure[name] = node.shape  # Store dataset name and shape
        
        h5_file.visititems(visitor)
        return structure

    # ----------------- CSV Management Methods -----------------

    def combine_and_export(self):
        # This method is already implemented above
        pass

    def batch_combine_and_export(self):
        # This method is already implemented above
        pass


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
            # Optionally, update button color to reflect selection
            self.text_color_button.setStyleSheet(f"background-color: {color.name()}")
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
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setDirectory(os.path.dirname(self.reference_spectrum_button.text()) if hasattr(self, 'reference_spectrum_button') else os.path.expanduser("~"))
        file_path, _ = file_dialog.getOpenFileName(self, "Select Reference Spectrum", self.parent().selected_data_panel.last_directory, "CSV Files (*.csv);;All Files (*)")
        if file_path:
            self.reference_spectrum_file = file_path
            self.reference_spectrum_button.setText(os.path.basename(file_path))
            # Update last_directory
            self.parent().selected_data_panel.last_directory = os.path.dirname(file_path)

    def choose_baseline_file(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setDirectory(os.path.dirname(self.baseline_file_button.text()) if hasattr(self, 'baseline_file_button') else os.path.expanduser("~"))
        file_path, _ = file_dialog.getOpenFileName(self, "Select Baseline File", self.parent().selected_data_panel.last_directory, "CSV Files (*.csv);;All Files (*)")
        if file_path:
            self.baseline_file = file_path
            self.baseline_file_button.setText(os.path.basename(file_path))
            # Update last_directory
            self.parent().selected_data_panel.last_directory = os.path.dirname(file_path)

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

class GeneratedCSVFilesPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Generated CSV Files", parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Draggable and Selectable List Widget for CSV Files
        self.csv_files_list = DraggableListWidget()
        self.layout.addWidget(self.csv_files_list)

        # Buttons for Managing CSV Files
        buttons_layout = QHBoxLayout()
        self.delete_csv_button = QPushButton("Delete Selected CSV Files")
        self.delete_csv_button.setIcon(QIcon('gui/resources/delete_icon.png'))  # Ensure the icon exists
        self.delete_csv_button.clicked.connect(self.delete_selected_csv_files)
        buttons_layout.addWidget(self.delete_csv_button)
        buttons_layout.addStretch()
        self.layout.addLayout(buttons_layout)

    def add_csv_file(self, csv_file_path):
        file_name = os.path.basename(csv_file_path)
        item = QListWidgetItem(file_name)
        item.setData(Qt.UserRole, csv_file_path)
        item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.csv_files_list.add_file_to_panel(csv_file_path)

    def get_selected_csv_files(self):
        selected_items = [
            item for item in self.csv_files_list.findItems("*", Qt.MatchWildcard)
            if item.checkState() == Qt.Checked
        ]
        return [item.data(Qt.UserRole) for item in selected_items]

    def delete_selected_csv_files(self):
        selected_items = self.csv_files_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "No CSV files selected to delete.")
            return
        reply = QMessageBox.question(
            self, 'Confirm Deletion',
            f"Are you sure you want to delete the selected {len(selected_items)} CSV file(s)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for item in selected_items:
                csv_file_path = item.data(Qt.UserRole)
                try:
                    os.remove(csv_file_path)
                except Exception as e:
                    QMessageBox.warning(self, "Deletion Error", f"Failed to delete {csv_file_path}:\n{e}")
                    continue
                self.csv_files_list.takeItem(self.csv_files_list.row(item))
            QMessageBox.information(self, "Deletion Successful", f"Deleted {len(selected_items)} CSV file(s).")

class DatasetSelectionExportPanel(QGroupBox):
    def __init__(self, selected_data_panel, h5_handling_panel, parent=None):
        super().__init__("Dataset Selection and Export", parent)
        self.selected_data_panel = selected_data_panel
        self.h5_handling_panel = h5_handling_panel
        self.init_ui()
        self.selected_datasets = []

    def init_ui(self):
        layout = QVBoxLayout()

        # Instruction Label
        instruction_label = QLabel("Select Datasets to Combine into CSV:")
        layout.addWidget(instruction_label)

        # Select Datasets Button
        self.select_datasets_button = QPushButton("Select Datasets")
        self.select_datasets_button.setIcon(QIcon('gui/resources/select_datasets_icon.png'))  # Ensure the icon exists
        layout.addWidget(self.select_datasets_button)

        # Combine and Export Button
        self.combine_export_button = QPushButton("Combine and Export")
        self.combine_export_button.setIcon(QIcon('gui/resources/combine_export_icon.png'))  # Ensure the icon exists
        self.combine_export_button.setEnabled(False)  # Disabled until datasets are selected
        layout.addWidget(self.combine_export_button)

        # Add to Selected Data Panel Checkbox
        self.add_to_selected_checkbox = QCheckBox("Add CSV to Selected Data Panel")
        self.add_to_selected_checkbox.setChecked(True)
        layout.addWidget(self.add_to_selected_checkbox)

        # Spacer
        layout.addStretch()

        self.setLayout(layout)

        # Connections
        self.select_datasets_button.clicked.connect(self.open_dataset_selection_dialog)
        self.combine_export_button.clicked.connect(self.combine_and_export_datasets)

    def open_dataset_selection_dialog(self):
        # Ensure that H5 files have been processed
        if not hasattr(self.h5_handling_panel, 'h5_files') or not self.h5_handling_panel.h5_files:
            QMessageBox.warning(self, "No H5 Files Processed", "Please process H5 files before selecting datasets.")
            return

        # Use the structure from the first H5 file (since all are consistent)
        structure = self.h5_handling_panel.structures[0]

        # Show the structure and get selected datasets
        selected_datasets = self.show_structure_and_get_datasets(structure)
        if selected_datasets:
            self.selected_datasets = selected_datasets
            self.combine_export_button.setEnabled(True)
        else:
            self.selected_datasets = []
            self.combine_export_button.setEnabled(False)

    def show_structure_and_get_datasets(self, structure):
        # Display the structure and allow the user to select datasets
        dialog = DatasetSelectionDialog(structure, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_datasets = dialog.get_selected_datasets()
            return selected_datasets
        else:
            return []

    def combine_and_export_datasets(self):
        if not self.selected_datasets:
            QMessageBox.warning(self, "No Datasets Selected", "Please select at least one dataset to combine.")
            return

        # Get H5 files to process
        h5_files = self.h5_handling_panel.h5_files
        if not h5_files:
            QMessageBox.warning(self, "No H5 Files Processed", "Please process H5 files before exporting datasets.")
            return

        # Initialize list to store CSV file paths
        csv_files = []

        # Process each H5 file
        for file in h5_files:
            try:
                with h5py.File(file, 'r') as h5_file:
                    data = self.extract_datasets(h5_file, self.selected_datasets)

                # Combine datasets into a single CSV
                combined_csv = self.combine_datasets_to_csv(data, file)
                csv_files.append(combined_csv)

                # If add to selected data panel is checked, add CSV to the panel
                if self.add_to_selected_checkbox.isChecked():
                    self.selected_data_panel.add_file_to_panel([combined_csv])

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to process H5 file {file}:\n{e}")
                continue  # Proceed to next file

        if csv_files:
            QMessageBox.information(self, "Export Complete", "Selected datasets have been combined and exported as CSV files.")
            # Optionally, enable sending to tabs
            self.parent().send_to_tabs_group.setEnabled(True)
        else:
            QMessageBox.warning(self, "No CSV Created", "No CSV files were created.")

    def extract_datasets(self, h5_file, datasets):
        # Extract selected datasets
        data = {}
        for dataset_name in datasets:
            data[dataset_name] = h5_file[dataset_name][:]
        return data

    def combine_datasets_to_csv(self, data, h5_file_path):
        # Combine datasets into a DataFrame
        df = pd.DataFrame()
        for dataset_name, values in data.items():
            # Handle datasets based on dimensions
            if values.ndim == 1:
                df[dataset_name] = values
            elif values.ndim == 2:
                # For 2D datasets, flatten columns
                for i in range(values.shape[1]):
                    col_name = f"{dataset_name}_{i}"
                    df[col_name] = values[:, i]
            else:
                # Skip datasets with higher dimensions
                continue

        # Define the CSV file path
        base_name = os.path.splitext(os.path.basename(h5_file_path))[0]
        csv_file_name = f"{base_name}_combined.csv"
        csv_file_path = os.path.join(os.path.dirname(h5_file_path), csv_file_name)

        # Save DataFrame to CSV
        df.to_csv(csv_file_path, index=False)
        return csv_file_path

    def extract_datasets(self, h5_file, datasets):
        # Extract selected datasets
        data = {}
        for dataset_name in datasets:
            if dataset_name in h5_file:
                data[dataset_name] = h5_file[dataset_name][:]
            else:
                raise KeyError(f"Dataset {dataset_name} not found in H5 file.")
        return data
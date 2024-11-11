# batch_processing_panels.py
import os
import sys
import shutil
import pandas as pd
import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QLineEdit, QTableView, QTreeView, QAbstractItemView, QHeaderView,
    QProgressBar, QMessageBox, QCalendarWidget, QDateEdit, QDialog, QFormLayout,
    QGroupBox, QScrollArea, QDateTimeEdit, QGridLayout, QApplication,QDirModel,QCheckBox,QComboBox
)
from PyQt5.QtCore import pyqtSignal, Qt, QAbstractTableModel, QModelIndex, QDir, QDateTime
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QIcon
import yaml
import datetime

def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def is_subdirectory(child, parent):
    child = os.path.realpath(child)
    parent = os.path.realpath(parent)
    if child == parent:
        return False
    return os.path.commonpath([parent, child]) == parent

class BatchDataHandlingPanel(QWidget):
    data_processed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Example content for Batch Data Handling
        layout.addWidget(QLabel("Batch Data Handling Panel"))
        self.process_data_button = QPushButton("Process Data")
        self.process_data_button.clicked.connect(self.process_data)
        layout.addWidget(self.process_data_button)

        self.setLayout(layout)

    def process_data(self):
        # Placeholder for processing data
        print("Processing data...")
        self.data_processed.emit()

#################################################################################
#################################################################################

class CriteriaGroup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        group_layout = QVBoxLayout()
        self.setLayout(group_layout)

        # Logic selection for this group
        logic_layout = QHBoxLayout()
        logic_label = QLabel("Combine Within Group Using:")
        self.logic_combo_box = QComboBox()
        self.logic_combo_box.addItems(["AND", "OR"])
        logic_layout.addWidget(logic_label)
        logic_layout.addWidget(self.logic_combo_box)
        group_layout.addLayout(logic_layout)

        # Input fields for criteria
        self.input_fields_layout = QVBoxLayout()
        group_layout.addLayout(self.input_fields_layout)

        # Add initial input field
        self.add_input_field()

        # Add button to add more input fields
        self.add_input_button = QPushButton("Add Criterion")
        self.add_input_button.setIcon(QIcon(resource_path('gui/resources/add2.png')))
        self.add_input_button.clicked.connect(self.add_input_field)
        group_layout.addWidget(self.add_input_button)

        # Remove group button
        self.remove_group_button = QPushButton("Remove Group")
        self.remove_group_button.setIcon(QIcon(resource_path('gui/resources/remove2.png')))
        self.remove_group_button.clicked.connect(self.remove_group)
        group_layout.addWidget(self.remove_group_button)

        # Add a line separator
        separator = QLabel()
        separator.setFrameStyle(QLabel.HLine | QLabel.Plain)
        group_layout.addWidget(separator)

    def add_input_field(self):
        input_field_layout = QHBoxLayout()
        input_line_edit = QLineEdit()
        remove_button = QPushButton("Remove")
        remove_button.setIcon(QIcon(resource_path('gui/resources/remove.png')))
        remove_button.clicked.connect(lambda: self.remove_input_field(input_field_layout))
        input_field_layout.addWidget(QLabel("Contains:"))
        input_field_layout.addWidget(input_line_edit)
        input_field_layout.addWidget(remove_button)
        self.input_fields_layout.addLayout(input_field_layout)

    def remove_input_field(self, layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.input_fields_layout.removeItem(layout)

    def remove_group(self):
        self.setParent(None)
        self.deleteLater()

    def get_criteria(self):
        criteria_list = []
        for i in range(self.input_fields_layout.count()):
            layout = self.input_fields_layout.itemAt(i)
            if isinstance(layout, QHBoxLayout):
                line_edit = layout.itemAt(1).widget()
                if isinstance(line_edit, QLineEdit):
                    text = line_edit.text()
                    if text:
                        criteria_list.append(text.strip())
        return criteria_list
    
class FileNameHandlingDialog(QDialog):
    def __init__(self, metadata_df, root_folder, parent=None):
        super().__init__(parent)
        self.metadata_df = metadata_df
        self.root_folder = root_folder
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("File Name Handling")
        self.setMinimumSize(800, 600)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Left side: Input fields and options
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)

        # Input fields group
        input_groupbox = QGroupBox("Replacement Criteria")
        input_layout = QVBoxLayout()
        input_groupbox.setLayout(input_layout)
        left_layout.addWidget(input_groupbox)

        # Scroll area for replacement fields
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.replacement_fields_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        input_layout.addWidget(scroll_area)

        # Add first replacement field
        self.add_replacement_field()
        self.replacement_fields_layout.setAlignment(Qt.AlignTop)

        # Add button to add more replacement fields
        self.add_replacement_button = QPushButton("Add Replacement")
        self.add_replacement_button.setIcon(QIcon(resource_path('gui/resources/add.png')))
        self.add_replacement_button.clicked.connect(self.add_replacement_field)
        input_layout.addWidget(self.add_replacement_button)

        # Partial matching checkbox
        self.partial_matching_checkbox = QCheckBox("Enable Partial Matching in File Name")
        self.partial_matching_checkbox.setChecked(True)
        left_layout.addWidget(self.partial_matching_checkbox)

        # Data type selection
        data_type_layout = QHBoxLayout()

        data_type_label = QLabel("File Type:")
        self.data_type_combo_box = QComboBox()

        # Extract unique file extensions from the metadata DataFrame
        self.unique_extensions = sorted(
            self.metadata_df['File Name']
            .apply(lambda x: os.path.splitext(x)[1].lower())
            .dropna()
            .unique()
        )

        # Populate the combo box
        self.data_type_combo_box.addItem("All")  # Default option
        for ext in self.unique_extensions:
            # Ensure extensions start with a dot
            if not ext.startswith('.'):
                ext = '.' + ext
            self.data_type_combo_box.addItem(ext)
        data_type_layout.addWidget(data_type_label)
        data_type_layout.addWidget(self.data_type_combo_box)
        left_layout.addLayout(data_type_layout)

        # Include subfolders checkbox
        self.include_subfolders_checkbox = QCheckBox("Include Subfolders")
        self.include_subfolders_checkbox.setChecked(True)
        left_layout.addWidget(self.include_subfolders_checkbox)

        # Destination folder selection
        dest_folder_layout = QHBoxLayout()
        self.dest_folder_line_edit = QLineEdit()
        self.dest_folder_line_edit.setReadOnly(True)
        self.select_dest_folder_button = QPushButton("Select Destination Folder")
        self.select_dest_folder_button.setIcon(QIcon(resource_path('gui/resources/select_folder_icon.png')))
        self.select_dest_folder_button.clicked.connect(self.select_destination_folder)
        dest_folder_layout.addWidget(QLabel("Destination Folder:"))
        dest_folder_layout.addWidget(self.dest_folder_line_edit)
        dest_folder_layout.addWidget(self.select_dest_folder_button)
        left_layout.addLayout(dest_folder_layout)

        # Execute button
        self.execute_button = QPushButton("Execute Rename")
        self.execute_button.setIcon(QIcon(resource_path('gui/resources/execute_icon.png')))
        self.execute_button.clicked.connect(self.execute_renaming)
        left_layout.addWidget(self.execute_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        left_layout.addWidget(self.progress_bar)

        # Right side: Folder/file tree
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)

        self.folder_tree = QTreeView()
        self.dir_model = QDirModel()
        self.folder_tree.setModel(self.dir_model)
        self.folder_tree.setRootIndex(self.dir_model.index(self.root_folder))
        self.folder_tree.setSortingEnabled(True)
        right_layout.addWidget(QLabel("Current Folder Structure:"))
        right_layout.addWidget(self.folder_tree)

    def add_replacement_field(self):
        replacement_field_layout = QHBoxLayout()
        from_line_edit = QLineEdit()
        to_line_edit = QLineEdit()
        remove_button = QPushButton("Remove")
        remove_button.setIcon(QIcon(resource_path('gui/resources/remove.png')))
        remove_button.clicked.connect(lambda: self.remove_replacement_field(replacement_field_layout))
        replacement_field_layout.addWidget(QLabel("From:"))
        replacement_field_layout.addWidget(from_line_edit)
        replacement_field_layout.addWidget(QLabel("To:"))
        replacement_field_layout.addWidget(to_line_edit)
        replacement_field_layout.addWidget(remove_button)
        self.replacement_fields_layout.addLayout(replacement_field_layout)

    def remove_replacement_field(self, layout):
        # Remove widgets from the layout
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        # Remove the layout itself
        self.replacement_fields_layout.removeItem(layout)
        
    def select_destination_folder(self):
        options = QFileDialog.Options()
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Destination Folder",
            "",
            options=options
        )
        if folder:
            self.dest_folder_line_edit.setText(folder)


    def execute_renaming(self):
        # Get replacement criteria from input fields
        replacement_list = []
        for i in range(self.replacement_fields_layout.count()):
            layout = self.replacement_fields_layout.itemAt(i)
            if isinstance(layout, QHBoxLayout):
                from_line_edit = layout.itemAt(1).widget()
                to_line_edit = layout.itemAt(3).widget()
                if isinstance(from_line_edit, QLineEdit) and isinstance(to_line_edit, QLineEdit):
                    from_text = from_line_edit.text()
                    to_text = to_line_edit.text()
                    if from_text:
                        replacement_list.append((from_text, to_text))

        if not replacement_list:
            QMessageBox.warning(self, "No Replacement Criteria", "Please add at least one replacement criterion.")
            return

        # Determine if partial matching is enabled
        partial_matching = self.partial_matching_checkbox.isChecked()

        # Get destination folder
        dest_folder = self.dest_folder_line_edit.text()
        if not dest_folder:
            QMessageBox.warning(self, "No Destination Folder", "Please select a destination folder.")
            return

        # Include subfolders option
        include_subfolders = self.include_subfolders_checkbox.isChecked()

        # Get data type handling selection
        data_type_selection = self.data_type_combo_box.currentText()

        # Build folder name based on replacements
        folder_name_parts = []
        for from_text, to_text in replacement_list:
            folder_name_parts.append(f"{from_text}_to_{to_text}")
        base_folder_name = "_".join(folder_name_parts)

        # Append file type to folder name if not "All"
        if data_type_selection != "All":
            ext_without_dot = data_type_selection[1:] if data_type_selection.startswith('.') else data_type_selection
            base_folder_name = f"{base_folder_name}_{ext_without_dot}"

        # Prepare destination folder path
        dest_folder_path = os.path.join(dest_folder, base_folder_name)
        os.makedirs(dest_folder_path, exist_ok=True)

        # Filter files based on file type
        selected_files_df = self.metadata_df.copy()

        if data_type_selection != "All":
            selected_files_df = selected_files_df[
                selected_files_df['File Name'].str.lower().str.endswith(data_type_selection.lower())
            ]

        if selected_files_df.empty:
            QMessageBox.information(self, "No Files Found", f"No files with extension {data_type_selection} found.")
            return

        # Prepare to copy files
        total_files = len(selected_files_df)
        self.progress_bar.setMaximum(total_files)
        self.progress_bar.setValue(0)

        # Confirm action
        reply = QMessageBox.question(
            self,
            "Confirm Rename",
            f"Are you sure you want to rename and copy {total_files} files to '{dest_folder_path}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # Prepare a log for the replacements
        replacement_log = []

        # Copy and rename files
        for idx, row in selected_files_df.iterrows():
            src_file = row['File Path']
            relative_path = os.path.relpath(src_file, self.root_folder)
            if not include_subfolders:
                # If not including subfolders, skip files not in root folder
                if os.path.dirname(relative_path) != '':
                    continue
            original_file_name = row['File Name']
            new_file_name = original_file_name
            # Apply replacements
            for from_text, to_text in replacement_list:
                if partial_matching:
                    new_file_name = new_file_name.replace(from_text, to_text)
                else:
                    # Use regex for exact matching
                    pattern = re.escape(from_text)
                    new_file_name = re.sub(r'(?<![a-zA-Z0-9])' + pattern + r'(?![a-zA-Z0-9])', to_text, new_file_name)
            if new_file_name != original_file_name:
                replacement_log.append(f"{original_file_name} -> {new_file_name}")
            dst_file = os.path.join(dest_folder_path, new_file_name)
            try:
                shutil.copy2(src_file, dst_file)
            except Exception as e:
                QMessageBox.warning(self, "Error Copying File", f"Failed to copy {src_file}:\n{e}")
                continue

            # Update progress bar
            self.progress_bar.setValue(self.progress_bar.value() + 1)
            QApplication.processEvents()

        # Write the replacement log to .txt and .yaml files
        log_file_txt = os.path.join(dest_folder_path, "replacement_log.txt")
        log_file_yaml = os.path.join(dest_folder_path, "replacement_log.yaml")
        with open(log_file_txt, 'w') as f_txt, open(log_file_yaml, 'w') as f_yaml:
            for line in replacement_log:
                f_txt.write(line + '\n')
                # For YAML, write as a list

            yaml.dump(replacement_log, f_yaml)

        QMessageBox.information(self, "Renaming Complete", "Files have been renamed and copied successfully.")
        self.progress_bar.setValue(0)

        # Refresh folder tree
        self.dir_model.refresh()

class FileMetadataModel(QAbstractTableModel):
    """A model to interface between the DataFrame and the QTableView."""
    def __init__(self, data_frame=None):
        super().__init__()
        self._data_frame = data_frame if data_frame is not None else pd.DataFrame()

    def rowCount(self, parent=QModelIndex()):
        return len(self._data_frame)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data_frame.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        value = self._data_frame.iloc[index.row(), index.column()]
        if role == Qt.DisplayRole:
            return str(value)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return str(self._data_frame.columns[section])
        else:
            return str(self._data_frame.index[section])

    def sort(self, column, order):
        colname = self._data_frame.columns[column]
        self.layoutAboutToBeChanged.emit()
        self._data_frame.sort_values(
            by=colname, ascending=order == Qt.AscendingOrder, inplace=True
        )
        self.layoutChanged.emit()

class BatchFileHandlingPanel(QWidget):
    files_processed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.metadata_df = pd.DataFrame()

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Left side: File metadata table
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)

        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_path_line_edit = QLineEdit()
        self.folder_path_line_edit.setReadOnly(True)
        self.select_folder_button = QPushButton("Select Root Folder")
        self.select_folder_button.setIcon(QIcon(resource_path('gui/resources/select_folder_icon.png')))  # Icon added here

        self.select_folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(QLabel("Root Folder:"))
        folder_layout.addWidget(self.folder_path_line_edit)
        folder_layout.addWidget(self.select_folder_button)
        left_layout.addLayout(folder_layout)

        # File metadata display
        self.metadata_table = QTableView()
        self.metadata_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.metadata_table.setSortingEnabled(True)
        self.metadata_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        left_layout.addWidget(self.metadata_table)

        # New "File Name Handling" button
        self.file_name_handling_button = QPushButton("File Name Handling")
        self.file_name_handling_button.setIcon(QIcon(resource_path('gui/resources/file_name_handling_icon.png')))
        self.file_name_handling_button.clicked.connect(self.open_file_name_handling_window)
        left_layout.addWidget(self.file_name_handling_button)

        # Restructuring button
        self.restructure_button = QPushButton("Files and Folders Restructuring")
        self.restructure_button.setIcon(QIcon(resource_path('gui/resources/restructuring_icon.png')))  # Icon added here
        self.restructure_button.clicked.connect(self.open_restructuring_window)
        left_layout.addWidget(self.restructure_button)

        # Right side: Folder/file tree view
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)

        self.folder_tree = QTreeView()
        self.dir_model = QDirModel()
        self.folder_tree.setModel(self.dir_model)
        self.folder_tree.setRootIndex(self.dir_model.index(QDir.rootPath()))
        self.folder_tree.setSortingEnabled(True)
        right_layout.addWidget(QLabel("Folder Structure:"))
        right_layout.addWidget(self.folder_tree)

    def open_file_name_handling_window(self):
        if self.folder_path_line_edit.text() == '':
            QMessageBox.warning(self, "No Root Folder Selected", "Please select a root folder first.")
            return

        self.file_name_handling_dialog = FileNameHandlingDialog(
            self.metadata_df, self.folder_path_line_edit.text(), self)
        self.file_name_handling_dialog.exec_()
        # After renaming, update the folder tree
        self.dir_model.refresh()

    def select_folder(self):
        options = QFileDialog.Options()
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Root Folder",
            "",
            options=options
        )
        if folder:
            self.folder_path_line_edit.setText(folder)
            self.scan_folder(folder)
            # Update the folder tree view
            self.folder_tree.setRootIndex(self.dir_model.index(folder))

    def scan_folder(self, root_folder):
        # Scan folders and extract metadata
        file_list = []
        for dirpath, dirnames, filenames in os.walk(root_folder):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                file_list.append(file_path)

        # Initialize metadata DataFrame
        self.metadata_df = pd.DataFrame({
            'File Path': file_list
        })
        # Extract metadata
        self.metadata_df['File Name'] = self.metadata_df['File Path'].apply(os.path.basename)
        self.metadata_df['Folder Path'] = self.metadata_df['File Path'].apply(os.path.dirname)
        self.metadata_df['Modification Date'] = self.metadata_df['File Path'].apply(
            lambda x: datetime.datetime.fromtimestamp(os.path.getmtime(x)))
        self.metadata_df['Creation Date'] = self.metadata_df['File Path'].apply(
            lambda x: datetime.datetime.fromtimestamp(os.path.getctime(x)))
        self.metadata_df['File Size'] = self.metadata_df['File Path'].apply(os.path.getsize)

        # Display metadata in the table
        self.display_metadata()

    def display_metadata(self):
        # Select columns to display
        display_df = self.metadata_df[[
            'File Path', 'File Name', 'Modification Date', 'Creation Date', 'File Size'
        ]]
        self.model = FileMetadataModel(display_df)
        self.metadata_table.setModel(self.model)

        # Set the resize mode to Interactive to allow manual resizing
        self.metadata_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)


    def open_restructuring_window(self):
        if self.folder_path_line_edit.text() == '':
            QMessageBox.warning(self, "No Root Folder Selected", "Please select a root folder first.")
            return

        self.restructuring_dialog = RestructuringDialog(
            self.metadata_df, self.folder_path_line_edit.text(), self)
        self.restructuring_dialog.exec_()
        # After restructuring, update the folder tree
        self.dir_model.refresh()
class RestructuringDialog(QDialog):
    def __init__(self, metadata_df, root_folder, parent=None):
        super().__init__(parent)
        self.metadata_df = metadata_df
        self.root_folder = root_folder
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Files and Folders Restructuring")
        self.setMinimumSize(900, 700)  # Increased size for better UI

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Left side: Input fields and options
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)

        # Input fields group
        input_groupbox = QGroupBox("Criteria for File Selection")
        input_layout = QVBoxLayout()
        input_groupbox.setLayout(input_layout)
        left_layout.addWidget(input_groupbox)

        # Scroll area for criteria groups
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.criteria_groups_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        input_layout.addWidget(scroll_area)

        # Add initial criteria group
        self.add_criteria_group()

        # Button to add more criteria groups
        self.add_group_button = QPushButton("Add Criteria Group")
        self.add_group_button.setIcon(QIcon(resource_path('gui/resources/add.png')))
        self.add_group_button.clicked.connect(self.add_criteria_group)
        input_layout.addWidget(self.add_group_button)

        # Partial matching checkbox
        self.partial_matching_checkbox = QCheckBox("Enable Partial Matching in File Name")
        self.partial_matching_checkbox.setChecked(True)
        left_layout.addWidget(self.partial_matching_checkbox)

        # Data type selection
        data_type_layout = QHBoxLayout()

        data_type_label = QLabel("Data Type Handling:")
        self.data_type_combo_box = QComboBox()

        # Extract unique file extensions from the metadata DataFrame
        self.unique_extensions = sorted(
            self.metadata_df['File Name']
            .apply(lambda x: os.path.splitext(x)[1].lower())
            .dropna()
            .unique()
        )

        # Populate the combo box
        self.data_type_combo_box.addItem("All")  # Default option
        for ext in self.unique_extensions:
            # Ensure extensions start with a dot
            if not ext.startswith('.'):
                ext = '.' + ext
            self.data_type_combo_box.addItem(ext)
        self.data_type_combo_box.addItem("Each Separately")

        data_type_layout.addWidget(data_type_label)
        data_type_layout.addWidget(self.data_type_combo_box)
        left_layout.addLayout(data_type_layout)

        # Date range selection for Creation Date
        creation_date_groupbox = QGroupBox("Creation Date Range Selection (Optional)")
        creation_date_layout = QFormLayout()
        creation_date_groupbox.setLayout(creation_date_layout)

        self.creation_start_date_edit = QDateTimeEdit()
        self.creation_start_date_edit.setCalendarPopup(True)
        self.creation_start_date_edit.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.creation_start_date_edit.setDateTime(QDateTime.currentDateTime().addYears(-1))

        self.creation_end_date_edit = QDateTimeEdit()
        self.creation_end_date_edit.setCalendarPopup(True)
        self.creation_end_date_edit.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.creation_end_date_edit.setDateTime(QDateTime.currentDateTime())

        creation_date_layout.addRow("Start Date and Time:", self.creation_start_date_edit)
        creation_date_layout.addRow("End Date and Time:", self.creation_end_date_edit)

        # Add checkbox to include creation date in folder name and activate filtering
        self.include_creation_date_in_name_checkbox = QCheckBox("Include Creation Date in Folder Name and Filter")
        self.include_creation_date_in_name_checkbox.setChecked(False)
        creation_date_layout.addRow(self.include_creation_date_in_name_checkbox)

        # Connect checkbox to toggle date filters
        self.include_creation_date_in_name_checkbox.stateChanged.connect(
            self.toggle_creation_date_filters
        )

        left_layout.addWidget(creation_date_groupbox)

        # Date range selection for Modification Date
        modification_date_groupbox = QGroupBox("Modification Date Range Selection (Optional)")
        modification_date_layout = QFormLayout()
        modification_date_groupbox.setLayout(modification_date_layout)

        self.modification_start_date_edit = QDateTimeEdit()
        self.modification_start_date_edit.setCalendarPopup(True)
        self.modification_start_date_edit.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.modification_start_date_edit.setDateTime(QDateTime.currentDateTime().addYears(-1))

        self.modification_end_date_edit = QDateTimeEdit()
        self.modification_end_date_edit.setCalendarPopup(True)
        self.modification_end_date_edit.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.modification_end_date_edit.setDateTime(QDateTime.currentDateTime())

        modification_date_layout.addRow("Start Date and Time:", self.modification_start_date_edit)
        modification_date_layout.addRow("End Date and Time:", self.modification_end_date_edit)

        # Add checkbox to include modification date in folder name and activate filtering
        self.include_modification_date_in_name_checkbox = QCheckBox("Include Modification Date in Folder Name and Filter")
        self.include_modification_date_in_name_checkbox.setChecked(False)
        modification_date_layout.addRow(self.include_modification_date_in_name_checkbox)

        # Connect checkbox to toggle date filters
        self.include_modification_date_in_name_checkbox.stateChanged.connect(
            self.toggle_modification_date_filters
        )

        left_layout.addWidget(modification_date_groupbox)

        # Destination folder selection
        dest_folder_layout = QHBoxLayout()
        self.dest_folder_line_edit = QLineEdit()
        self.dest_folder_line_edit.setReadOnly(True)
        self.select_dest_folder_button = QPushButton("Select Destination Folder")
        self.select_dest_folder_button.setIcon(QIcon(resource_path('gui/resources/select_folder_icon.png')))
        self.select_dest_folder_button.clicked.connect(self.select_destination_folder)
        dest_folder_layout.addWidget(QLabel("Destination Folder:"))
        dest_folder_layout.addWidget(self.dest_folder_line_edit)
        dest_folder_layout.addWidget(self.select_dest_folder_button)
        left_layout.addLayout(dest_folder_layout)

        # Restructure button
        self.execute_button = QPushButton("Execute Restructuring")
        self.execute_button.setIcon(QIcon(resource_path('gui/resources/execute_icon.png')))
        self.execute_button.clicked.connect(self.execute_restructuring)
        left_layout.addWidget(self.execute_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        left_layout.addWidget(self.progress_bar)

        # Right side: Folder/file tree
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)

        self.folder_tree = QTreeView()
        self.dir_model = QDirModel()
        self.folder_tree.setModel(self.dir_model)
        self.folder_tree.setRootIndex(self.dir_model.index(self.root_folder))
        self.folder_tree.setSortingEnabled(True)
        right_layout.addWidget(QLabel("Current Folder Structure:"))
        right_layout.addWidget(self.folder_tree)

        # Initially disable date filters
        self.toggle_creation_date_filters(self.include_creation_date_in_name_checkbox.isChecked())
        self.toggle_modification_date_filters(self.include_modification_date_in_name_checkbox.isChecked())

    def toggle_creation_date_filters(self, state):
        """Enable or disable creation date/time filters based on checkbox state."""
        is_checked = state == Qt.Checked
        self.creation_start_date_edit.setEnabled(is_checked)
        self.creation_end_date_edit.setEnabled(is_checked)

    def toggle_modification_date_filters(self, state):
        """Enable or disable modification date/time filters based on checkbox state."""
        is_checked = state == Qt.Checked
        self.modification_start_date_edit.setEnabled(is_checked)
        self.modification_end_date_edit.setEnabled(is_checked)

    def add_criteria_group(self):
        criteria_group = CriteriaGroup()
        self.criteria_groups_layout.addWidget(criteria_group)

    def select_destination_folder(self):
        options = QFileDialog.Options()
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Destination Folder",
            "",
            options=options
        )
        if folder:
            if is_subdirectory(folder, self.root_folder):
                QMessageBox.warning(self, "Invalid Destination Folder", "The destination folder cannot be inside the root folder.")
                return
            self.dest_folder_line_edit.setText(folder)

    def execute_restructuring(self):
        # Determine if partial matching is enabled
        partial_matching = self.partial_matching_checkbox.isChecked()

        # Get data type handling selection
        data_type_selection = self.data_type_combo_box.currentText()

        # Get destination folder
        dest_folder = self.dest_folder_line_edit.text()
        if not dest_folder:
            QMessageBox.warning(self, "No Destination Folder", "Please select a destination folder.")
            return

        # Build folder name based on criteria and date ranges
        folder_name_parts = []

        # Collect folder name parts from criteria groups
        criteria_folder_name_parts = []
        for i in range(self.criteria_groups_layout.count()):
            group_widget = self.criteria_groups_layout.itemAt(i).widget()
            if isinstance(group_widget, CriteriaGroup):
                group_criteria = group_widget.get_criteria()
                if group_criteria:
                    criteria_folder_name_parts.append("_".join(group_criteria))
        if criteria_folder_name_parts:
            folder_name_parts.append("_".join(criteria_folder_name_parts))

        # Start with all files
        selected_files_df = self.metadata_df.copy()

        # Process criteria groups
        for i in range(self.criteria_groups_layout.count()):
            group_widget = self.criteria_groups_layout.itemAt(i).widget()
            if isinstance(group_widget, CriteriaGroup):
                group_logic = group_widget.logic_combo_box.currentText()
                group_criteria_list = group_widget.get_criteria()

                if not group_criteria_list:
                    continue  # Skip empty groups

                # Compile regex patterns for group criteria
                regex_patterns = []
                for criteria in group_criteria_list:
                    escaped_criteria = re.escape(criteria)
                    if partial_matching:
                        pattern = escaped_criteria
                    else:
                        pattern = r'\b' + escaped_criteria + r'\b'
                    # Use custom word boundaries to avoid matching within words or numbers
                    pattern = r'(?<![a-zA-Z0-9])' + pattern + r'(?![a-zA-Z0-9])'
                    regex_patterns.append(pattern)

                # Filter files based on group logic
                if group_logic == "AND":
                    # Files must match all criteria in the group
                    for pattern in regex_patterns:
                        selected_files_df = selected_files_df[
                            selected_files_df['File Name'].str.contains(
                                pattern,
                                flags=re.IGNORECASE,
                                regex=True
                            )
                        ]
                elif group_logic == "OR":
                    # Files must match at least one criterion in the group
                    combined_pattern = '|'.join(regex_patterns)
                    selected_files_df = selected_files_df[
                        selected_files_df['File Name'].str.contains(
                            combined_pattern,
                            flags=re.IGNORECASE,
                            regex=True
                        )
                    ]
                else:
                    continue  # Unknown logic, skip

        # Add date ranges to folder name if applicable and if user chose to include them
        date_parts = []

        # Filter and include Creation Date if checkbox is checked
        if self.include_creation_date_in_name_checkbox.isChecked():
            creation_start_datetime = self.creation_start_date_edit.dateTime().toPyDateTime()
            creation_end_datetime = self.creation_end_date_edit.dateTime().toPyDateTime()
            # Filter based on creation date range
            selected_files_df = selected_files_df[
                (selected_files_df['Creation Date'] >= creation_start_datetime) &
                (selected_files_df['Creation Date'] <= creation_end_datetime)
            ]
            # Include date and time in folder name
            creation_start_str = creation_start_datetime.strftime('%d%b%Y_%H-%M-%S')
            creation_end_str = creation_end_datetime.strftime('%d%b%Y_%H-%M-%S')
            date_parts.append(f"Created_{creation_start_str}-{creation_end_str}")

        # Filter and include Modification Date if checkbox is checked
        if self.include_modification_date_in_name_checkbox.isChecked():
            modification_start_datetime = self.modification_start_date_edit.dateTime().toPyDateTime()
            modification_end_datetime = self.modification_end_date_edit.dateTime().toPyDateTime()
            # Filter based on modification date range
            selected_files_df = selected_files_df[
                (selected_files_df['Modification Date'] >= modification_start_datetime) &
                (selected_files_df['Modification Date'] <= modification_end_datetime)
            ]
            # Include date and time in folder name
            modification_start_str = modification_start_datetime.strftime('%d%b%Y_%H-%M-%S')
            modification_end_str = modification_end_datetime.strftime('%d%b%Y_%H-%M-%S')
            date_parts.append(f"Modified_{modification_start_str}-{modification_end_str}")

        if date_parts:
            folder_name_parts.append("_".join(date_parts))

        # Base folder name without extension
        base_folder_name = "_".join(folder_name_parts) if folder_name_parts else "Selected_Files"

        if selected_files_df.empty:
            QMessageBox.information(self, "No Files Found", "No files match the given criteria.")
            return

        # Handle data type selection
        if data_type_selection == "All":
            # Handle all data types together (no additional filtering)
            dest_folder_path = os.path.join(dest_folder, base_folder_name)
            os.makedirs(dest_folder_path, exist_ok=True)

        elif data_type_selection == "Each Separately":
            # Handle each data type separately
            # Iterate through each unique extension and copy files accordingly
            for ext in self.unique_extensions:
                # Filter files with the current extension
                files_with_ext = selected_files_df[selected_files_df['File Name'].str.lower().str.endswith(ext.lower())]

                if files_with_ext.empty:
                    continue  # Skip if no files with this extension

                # Construct folder name with extension
                # Remove the dot from extension for folder naming
                ext_without_dot = ext[1:] if ext.startswith('.') else ext
                folder_name = f"{base_folder_name}_{ext_without_dot}"
                dest_folder_path_ext = os.path.join(dest_folder, folder_name)
                os.makedirs(dest_folder_path_ext, exist_ok=True)

                # Confirm action for each extension
                reply = QMessageBox.question(
                    self,
                    "Confirm Restructuring",
                    f"Are you sure you want to copy {len(files_with_ext)} '{ext}' files to '{dest_folder_path_ext}'?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    continue  # Skip this extension if not confirmed

                # Prepare to copy files
                total_files_ext = len(files_with_ext)
                self.progress_bar.setMaximum(total_files_ext)
                self.progress_bar.setValue(0)

                # Prepare a log for the replacements
                replacement_log = []

                # Copy files
                for idx, row in files_with_ext.iterrows():
                    src_file = row['File Path']
                    dst_file = os.path.join(dest_folder_path_ext, row['File Name'])
                    try:
                        shutil.copy2(src_file, dst_file)
                        replacement_log.append(f"Copied: {row['File Name']}")
                    except Exception as e:
                        QMessageBox.warning(self, "Error Copying File", f"Failed to copy {src_file}:\n{e}")
                        continue

                    # Update progress bar
                    self.progress_bar.setValue(self.progress_bar.value() + 1)
                    QApplication.processEvents()

                # Write the replacement log to .txt and .yaml files
                log_file_txt = os.path.join(dest_folder_path_ext, "replacement_log.txt")
                log_file_yaml = os.path.join(dest_folder_path_ext, "replacement_log.yaml")
                try:
                    with open(log_file_txt, 'w') as f_txt:
                        for line in replacement_log:
                            f_txt.write(line + '\n')

                    with open(log_file_yaml, 'w') as f_yaml:
                        yaml.dump(replacement_log, f_yaml, default_flow_style=False)
                except Exception as e:
                    QMessageBox.warning(self, "Error Writing Logs", f"Failed to write log files:\n{e}")

                QMessageBox.information(self, "Restructuring Complete", f"Copied {total_files_ext} '{ext}' files successfully.")
                self.progress_bar.setValue(0)

            QMessageBox.information(self, "Restructuring Complete", "All selected files have been copied successfully.")
            self.progress_bar.setValue(0)
            return  # Exit the method after handling "Each Separately"

        else:
            # Handle specific data type
            # Filter files with the selected extension
            selected_files_df = selected_files_df[selected_files_df['File Name'].str.lower().str.endswith(data_type_selection.lower())]

            if selected_files_df.empty:
                QMessageBox.information(self, "No Files Found", f"No files with extension {data_type_selection} match the given criteria.")
                return

            # Append the extension to the folder name
            ext_without_dot = data_type_selection[1:] if data_type_selection.startswith('.') else data_type_selection
            folder_name = f"{base_folder_name}_{ext_without_dot}"
            dest_folder_path = os.path.join(dest_folder, folder_name)
            os.makedirs(dest_folder_path, exist_ok=True)

        # Confirm action
        reply = QMessageBox.question(
            self,
            "Confirm Restructuring",
            f"Are you sure you want to copy {len(selected_files_df)} files to '{dest_folder_path}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # Prepare to copy files
        total_files = len(selected_files_df)
        self.progress_bar.setMaximum(total_files)
        self.progress_bar.setValue(0)

        # Prepare a log for the replacements
        replacement_log = []

        # Copy files
        for idx, row in selected_files_df.iterrows():
            src_file = row['File Path']
            dst_file = os.path.join(dest_folder_path, row['File Name'])
            try:
                shutil.copy2(src_file, dst_file)
                replacement_log.append(f"Copied: {row['File Name']}")
            except Exception as e:
                QMessageBox.warning(self, "Error Copying File", f"Failed to copy {src_file}:\n{e}")
                continue

            # Update progress bar
            self.progress_bar.setValue(self.progress_bar.value() + 1)
            QApplication.processEvents()

        # Write the replacement log to .txt and .yaml files
        log_file_txt = os.path.join(dest_folder_path, "replacement_log.txt")
        log_file_yaml = os.path.join(dest_folder_path, "replacement_log.yaml")
        try:
            with open(log_file_txt, 'w') as f_txt:
                for line in replacement_log:
                    f_txt.write(line + '\n')

            with open(log_file_yaml, 'w') as f_yaml:
                yaml.dump(replacement_log, f_yaml, default_flow_style=False)
        except Exception as e:
            QMessageBox.warning(self, "Error Writing Logs", f"Failed to write log files:\n{e}")

        QMessageBox.information(self, "Restructuring Complete", "Files have been copied successfully.")
        self.progress_bar.setValue(0)

        # Refresh folder tree
        self.dir_model.refresh()


#################################################################################
#################################################################################

class BatchMetaDataHandlingPanel(QWidget):
    metadata_processed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Example content for Batch Meta Data Handling
        layout.addWidget(QLabel("Batch Meta Data Handling Panel"))
        self.process_metadata_button = QPushButton("Process Meta Data")
        self.process_metadata_button.clicked.connect(self.process_metadata)
        layout.addWidget(self.process_metadata_button)

        self.setLayout(layout)

    def process_metadata(self):
        # Placeholder for processing metadata
        print("Processing metadata...")
        self.metadata_processed.emit()

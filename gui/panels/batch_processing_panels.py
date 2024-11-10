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
    QGroupBox, QScrollArea, QDateTimeEdit, QGridLayout, QApplication,QDirModel,QCheckBox
)
from PyQt5.QtCore import pyqtSignal, Qt, QAbstractTableModel, QModelIndex, QDir, QDateTime
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QIcon

def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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
            lambda x: pd.to_datetime(os.path.getmtime(x), unit='s'))
        self.metadata_df['Creation Date'] = self.metadata_df['File Path'].apply(
            lambda x: pd.to_datetime(os.path.getctime(x), unit='s'))
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
        self.setMinimumSize(800, 600)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Left side: Input fields
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)

        # Input fields group
        input_groupbox = QGroupBox("Criteria for File Selection")
        input_layout = QVBoxLayout()
        input_groupbox.setLayout(input_layout)

        # Scroll area for input fields
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.input_fields_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        input_layout.addWidget(scroll_area)

        # Add first input field
        self.add_input_field()

        # Add button to add more input fields
        self.add_input_button = QPushButton("Add Criteria")
        self.add_input_button.setIcon(QIcon(resource_path('gui/resources/add.png')))  # Icon added here
        self.add_input_button.clicked.connect(self.add_input_field)
        input_layout.addWidget(self.add_input_button)

        # Add partial matching checkbox
        self.partial_matching_checkbox = QCheckBox("Enable Partial Matching in File Name")
        self.partial_matching_checkbox.setChecked(True)  # Preselect the checkbox
        input_layout.addWidget(self.partial_matching_checkbox)

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

        creation_date_layout.addRow("Start Date:", self.creation_start_date_edit)
        creation_date_layout.addRow("End Date:", self.creation_end_date_edit)

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

        modification_date_layout.addRow("Start Date:", self.modification_start_date_edit)
        modification_date_layout.addRow("End Date:", self.modification_end_date_edit)

        left_layout.addWidget(input_groupbox)
        left_layout.addWidget(creation_date_groupbox)
        left_layout.addWidget(modification_date_groupbox)

        # Destination folder selection
        dest_folder_layout = QHBoxLayout()
        self.dest_folder_line_edit = QLineEdit()
        self.dest_folder_line_edit.setReadOnly(True)
        self.select_dest_folder_button = QPushButton("Select Destination Folder")
        self.select_dest_folder_button.setIcon(QIcon(resource_path('gui/resources/select_folder_icon.png')))  # Icon added here
        self.select_dest_folder_button.clicked.connect(self.select_destination_folder)
        dest_folder_layout.addWidget(QLabel("Destination Folder:"))
        dest_folder_layout.addWidget(self.dest_folder_line_edit)
        dest_folder_layout.addWidget(self.select_dest_folder_button)
        left_layout.addLayout(dest_folder_layout)

        # Restructure button
        self.execute_button = QPushButton("Execute Restructuring")
        self.execute_button.setIcon(QIcon(resource_path('gui/resources/execute_icon.png')))  # Icon added here
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

    def add_input_field(self):
        input_field_layout = QHBoxLayout()
        input_line_edit = QLineEdit()
        remove_button = QPushButton("Remove")
        remove_button.setIcon(QIcon(resource_path('gui/resources/remove.png')))  # Icon added here

        remove_button.clicked.connect(lambda: self.remove_input_field(input_field_layout))
        input_field_layout.addWidget(QLabel("Contains:"))
        input_field_layout.addWidget(input_line_edit)
        input_field_layout.addWidget(remove_button)
        self.input_fields_layout.addLayout(input_field_layout)

    def remove_input_field(self, layout):
        # Remove widgets from the layout
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        # Remove the layout itself
        self.input_fields_layout.removeItem(layout)

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

    def execute_restructuring(self):
        # Get criteria from input fields
        criteria_list = []
        for i in range(self.input_fields_layout.count()):
            layout = self.input_fields_layout.itemAt(i)
            if isinstance(layout, QHBoxLayout):
                line_edit = layout.itemAt(1).widget()
                if isinstance(line_edit, QLineEdit):
                    text = line_edit.text()
                    if text:
                        criteria_list.append(text.strip())

        # Determine if partial matching is enabled
        partial_matching = self.partial_matching_checkbox.isChecked()

        # Get date ranges
        creation_start_datetime = self.creation_start_date_edit.dateTime().toPyDateTime()
        creation_end_datetime = self.creation_end_date_edit.dateTime().toPyDateTime()
        modification_start_datetime = self.modification_start_date_edit.dateTime().toPyDateTime()
        modification_end_datetime = self.modification_end_date_edit.dateTime().toPyDateTime()

        # Get destination folder
        dest_folder = self.dest_folder_line_edit.text()
        if not dest_folder:
            QMessageBox.warning(self, "No Destination Folder", "Please select a destination folder.")
            return

        # Build folder name
        folder_name_parts = []
        if criteria_list:
            folder_name_parts.append("_".join(criteria_list))
        if not criteria_list and (creation_start_datetime or creation_end_datetime or modification_start_datetime or modification_end_datetime):
            date_parts = []
            if creation_start_datetime and creation_end_datetime:
                date_parts.append(f"Created_{creation_start_datetime.strftime('%d%b%Y')}-{creation_end_datetime.strftime('%d%b%Y')}")
            if modification_start_datetime and modification_end_datetime:
                date_parts.append(f"Modified_{modification_start_datetime.strftime('%d%b%Y')}-{modification_end_datetime.strftime('%d%b%Y')}")
            folder_name_parts.append("_".join(date_parts))
        if not folder_name_parts:
            QMessageBox.warning(self, "No Criteria", "Please provide criteria for file selection.")
            return

        folder_name = "_".join(folder_name_parts)
        dest_folder_path = os.path.join(dest_folder, folder_name)
        os.makedirs(dest_folder_path, exist_ok=True)

        # Filter files based on criteria
        selected_files_df = self.metadata_df.copy()

        if criteria_list:
            # Compile regular expressions for criteria
            regex_patterns = []
            for criteria in criteria_list:
                # Escape special characters in criteria
                escaped_criteria = re.escape(criteria)
                if partial_matching:
                    # Partial matching without word boundaries
                    pattern = escaped_criteria
                else:
                    # Exact matching with word boundaries
                    pattern = r'\b' + escaped_criteria + r'\b'
                regex_patterns.append(re.compile(pattern, re.IGNORECASE))

            # Filter files where all criteria match
            for regex in regex_patterns:
                selected_files_df = selected_files_df[
                    selected_files_df['File Name'].apply(lambda x: bool(regex.search(x)))
                ]

        # Filter based on creation date range
        if self.creation_start_date_edit.dateTime() and self.creation_end_date_edit.dateTime():
            selected_files_df = selected_files_df[
                (selected_files_df['Creation Date'] >= creation_start_datetime) &
                (selected_files_df['Creation Date'] <= creation_end_datetime)
            ]

        # Filter based on modification date range
        if self.modification_start_date_edit.dateTime() and self.modification_end_date_edit.dateTime():
            selected_files_df = selected_files_df[
                (selected_files_df['Modification Date'] >= modification_start_datetime) &
                (selected_files_df['Modification Date'] <= modification_end_datetime)
            ]

        if selected_files_df.empty:
            QMessageBox.information(self, "No Files Found", "No files match the given criteria.")
            return

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

        # Copy files
        for idx, row in selected_files_df.iterrows():
            src_file = row['File Path']
            dst_file = os.path.join(dest_folder_path, row['File Name'])
            try:
                shutil.copy2(src_file, dst_file)
            except Exception as e:
                QMessageBox.warning(self, "Error Copying File", f"Failed to copy {src_file}:\n{e}")
                continue

            # Update progress bar
            self.progress_bar.setValue(idx + 1)
            QApplication.processEvents()

        QMessageBox.information(self, "Restructuring Complete", "Files have been copied successfully.")
        self.progress_bar.setValue(0)

        # Refresh folder tree
        self.dir_model.refresh()

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

# batch_metadata_handling_panels.py

import os
import sys
import re
import yaml
import json
import shutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QTreeView, QAbstractItemView, QMessageBox, QLabel, QLineEdit,
    QScrollArea, QFormLayout, QComboBox, QTextEdit, QInputDialog,
    QMenu, QAction, QApplication, QProgressBar, QDirModel, QGroupBox, QProgressBar,QShortcut

)
from PyQt5.QtCore import (
    Qt, QDir, pyqtSignal
)
from PyQt5.QtGui import QIcon, QKeySequence

def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MetadataField(QWidget):
    def __init__(self, key='', value='', parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.key_edit = QLineEdit(key)
        self.value_edit = QLineEdit(value)
        self.remove_button = QPushButton('Remove')
        self.remove_button.setFixedWidth(60)
        self.layout.addWidget(self.key_edit)
        self.layout.addWidget(self.value_edit)
        self.layout.addWidget(self.remove_button)
        self.setLayout(self.layout)
        self.remove_button.clicked.connect(self.remove_self)

    def remove_self(self):
        self.setParent(None)

    def get_data(self):
        return self.key_edit.text(), self.value_edit.text()

class BatchMetaDataHandlingPanel(QWidget):
    metadata_processed = pyqtSignal()  # Signal to indicate metadata processing is done

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_metadata_type = None  # 'Investigation', 'Study', 'Assay'
        self.current_folder_path = None
        self.navigation_history = []  # Stack to keep track of navigation
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Left Panel
        left_panel = QVBoxLayout()

        # **1. Select Root Folder Button and Root Path Display at the Top**
        navigation_layout = QHBoxLayout()

        # Label for Root Folder
        root_label = QLabel("Root Folder:")
        navigation_layout.addWidget(root_label)

        # Read-only Line Edit to Display Root Path
        self.root_path_line_edit = QLineEdit()
        self.root_path_line_edit.setReadOnly(True)
        navigation_layout.addWidget(self.root_path_line_edit)

        # Select Root Folder Button
        self.select_folder_button = QPushButton('Select Root Folder')
        self.select_folder_button.setIcon(QIcon(resource_path('gui/resources/select_folder_icon.png')))  # Ensure the icon exists
        self.select_folder_button.clicked.connect(self.select_root_folder)
        navigation_layout.addWidget(self.select_folder_button)

        left_panel.addLayout(navigation_layout)


        # Scroll Area for Metadata Fields
        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.scroll_layout = QFormLayout()
        self.scroll_area_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget)
        left_panel.addWidget(self.scroll_area)

        # Buttons below scroll area
        button_layout = QHBoxLayout()
        self.add_investigation_button = QPushButton('Add Investigation')
        self.add_study_button = QPushButton('Add Study')
        self.add_assay_button = QPushButton('Add Assay')
        button_layout.addWidget(self.add_investigation_button)
        button_layout.addWidget(self.add_study_button)
        button_layout.addWidget(self.add_assay_button)
        left_panel.addLayout(button_layout)

        # Save and Export buttons
        save_export_layout = QHBoxLayout()
        self.save_metadata_button = QPushButton('Save Metadata')
        self.export_metadata_button = QPushButton('Export Metadata')
        self.extract_metadata_button = QPushButton('Extract Metadata from Data Points')
        save_export_layout.addWidget(self.save_metadata_button)
        save_export_layout.addWidget(self.export_metadata_button)
        save_export_layout.addWidget(self.extract_metadata_button)
        left_panel.addLayout(save_export_layout)
        self.extract_metadata_button.hide()  # Initially hidden

        # Add a progress bar below the Save and Export buttons
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)  # Initially hidden
        left_panel.addWidget(self.progress_bar)

        main_layout.addLayout(left_panel)

        # **Right Panel - Vertical Layout with Back Button and Hierarchy Tree**
        right_panel = QVBoxLayout()

        # **1. Back Button at the Top of the Hierarchy Tree**
        self.back_button = QPushButton('Back')
        self.back_button.setIcon(QIcon(resource_path('gui/resources/back_icon.png')))  # Ensure you have a back icon
        self.back_button.clicked.connect(self.navigate_back)
        self.back_button.setEnabled(False)  # Initially disabled
        right_panel.addWidget(self.back_button)

        # **2. Hierarchy Tree Below the Back Button**
        self.tree_view = QTreeView()
        self.tree_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Prevent editing by default
        self.dir_model = QDirModel()
        self.dir_model.setReadOnly(False)
        self.tree_view.setModel(self.dir_model)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.open_context_menu)
        self.tree_view.doubleClicked.connect(self.on_tree_item_double_clicked)
        right_panel.addWidget(self.tree_view)

        main_layout.addLayout(right_panel)

        # **3. Keyboard Shortcut for Back (Left Arrow Key)**
        self.back_shortcut = QShortcut(QKeySequence(Qt.Key_Backspace), self.tree_view)
        self.back_shortcut.activated.connect(self.navigate_back)

        # Connect buttons
        self.add_investigation_button.clicked.connect(self.add_investigation)
        self.add_study_button.clicked.connect(self.add_study)
        self.add_assay_button.clicked.connect(self.add_assay)
        self.save_metadata_button.clicked.connect(self.save_metadata)
        self.export_metadata_button.clicked.connect(self.export_metadata)
        self.extract_metadata_button.clicked.connect(self.extract_metadata)

        # Initialize variables
        self.metadata_fields = []
        self.root_folder_path = None

    def select_root_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Root Folder")
        if folder_path:
            self.root_folder_path = folder_path
            self.root_path_line_edit.setText(folder_path)  # Display the root path
            self.populate_tree_view()
            self.navigation_history.clear()  # Clear history when a new root is selected
            self.back_button.setEnabled(False)
        else:
            QMessageBox.warning(self, 'No Folder Selected', 'Please select a root folder to proceed.')


    def populate_tree_view(self):
        if self.root_folder_path:
            index = self.dir_model.index(self.root_folder_path)
            self.tree_view.setRootIndex(index)
            self.tree_view.collapseAll()  # Ensure all nodes are collapsed
       


    def navigate_back(self):
        if self.navigation_history:
            previous_folder = self.navigation_history.pop()
            self.root_folder_path = previous_folder
            self.populate_tree_view()
            if not self.navigation_history:
                self.back_button.setEnabled(False)
        else:
            self.back_button.setEnabled(False)

    def open_context_menu(self, position):
        indexes = self.tree_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            path = self.dir_model.filePath(index)
            menu = QMenu()

            rename_action = QAction(QIcon(resource_path('gui/resources/rename_icon.png')), 'Rename', self)
            delete_action = QAction(QIcon(resource_path('gui/resources/delete_icon.png')), 'Delete', self)
            new_folder_action = QAction(QIcon(resource_path('gui/resources/new_folder_icon.png')), 'New Folder', self)
            menu.addAction(rename_action)
            menu.addAction(delete_action)
            menu.addAction(new_folder_action)

            action = menu.exec_(self.tree_view.viewport().mapToGlobal(position))
            if action == rename_action:
                self.tree_view.edit(index)
            elif action == delete_action:
                self.delete_item(index)
            elif action == new_folder_action:
                self.create_new_folder(index)

    def delete_item(self, index):
        path = self.dir_model.filePath(index)
        if os.path.isdir(path):
            try:
                shutil.rmtree(path)
            except Exception as e:
                QMessageBox.warning(self, 'Delete Error', f'Cannot delete folder: {e}')
                return
        else:
            try:
                os.remove(path)
            except Exception as e:
                QMessageBox.warning(self, 'Delete Error', f'Cannot delete file: {e}')
                return
        # Refresh the model
        self.dir_model.refresh()

    def create_new_folder(self, index):
        path = self.dir_model.filePath(index)
        folder_name, ok = QInputDialog.getText(self, 'New Folder', 'Folder Name:')
        if ok and folder_name:
            new_folder_path = os.path.join(path, folder_name)
            try:
                os.mkdir(new_folder_path)
                self.dir_model.refresh()
            except Exception as e:
                QMessageBox.warning(self, 'Folder Creation Error', f'Cannot create folder: {e}')

    def on_tree_item_double_clicked(self, index):
        path = self.dir_model.filePath(index)
        if os.path.isdir(path):
            # Push current root to history before navigating
            if self.root_folder_path:
                self.navigation_history.append(self.root_folder_path)
                self.back_button.setEnabled(True)
            self.root_folder_path = path
            self.populate_tree_view()



    def clear_scroll_area(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.metadata_fields = []

    def add_investigation(self):
        if not self.root_folder_path:
            QMessageBox.warning(self, 'No Root Folder', 'Please select a root folder first.')
            return
        self.clear_scroll_area()
        self.current_metadata_type = 'Investigation'
        self.current_folder_path = self.root_folder_path
        # Default fields
        fields = [
            ('Title', ''),
            ('Description', ''),
            ('Project ID', ''),
            ('Authors/Researchers', ''),
            ('Institution', ''),
            ('Funding Information', ''),
            ('Keywords', ''),
            ('Study Design', ''),
            ('Start Date', ''),
            ('End Date', ''),
            ('DOI', ''),
            ('Associated Publications', ''),
            ('Project Website', '')
        ]
        for key, value in fields:
            self.add_metadata_field(key, value)
        # Button to add additional fields
        self.add_field_button = QPushButton('Add Field')
        self.add_field_button.setIcon(QIcon(resource_path('gui/resources/add_field_icon.png')))  # Optional: add icon
        self.add_field_button.clicked.connect(self.add_empty_field)
        self.scroll_layout.addRow(self.add_field_button)
        self.extract_metadata_button.hide()

    def add_study(self):
        selected_folder = self.get_selected_folder()
        if selected_folder:
            self.clear_scroll_area()
            self.current_metadata_type = 'Study'
            self.current_folder_path = selected_folder
            # Default fields
            fields = [
                ('Title', ''),
                ('Description', ''),
                ('Study ID', ''),
                ('Procedure Description', ''),
                ('Equipment and Software', ''),
                ('Date of Study', ''),
                ('Collaborating Labs/Institutions', ''),
                ('Data Collection Instruments', ''),
                ('Keywords', '')
            ]
            for key, value in fields:
                self.add_metadata_field(key, value)
            # Button to add additional fields
            self.add_field_button = QPushButton('Add Field')
            self.add_field_button.setIcon(QIcon(resource_path('gui/resources/add_field_icon.png')))  # Optional: add icon
            self.add_field_button.clicked.connect(self.add_empty_field)
            self.scroll_layout.addRow(self.add_field_button)
            self.extract_metadata_button.hide()
        else:
            QMessageBox.warning(self, 'No Folder Selected', 'Please select a folder in the hierarchy tree to add Study metadata.')

    def add_assay(self):
        selected_item = self.get_selected_item()
        if selected_item:
            self.clear_scroll_area()
            self.current_metadata_type = 'Assay'
            self.current_folder_path = selected_item['path']
            # Default fields
            fields = [
                ('Title', os.path.basename(selected_item['path']) if selected_item['type'] == 'file' else ''),
                ('Assay ID', ''),
                ('Measurement Type', ''),
                ('Data File Link', selected_item['path'] if selected_item['type'] == 'file' else ''),
                ('Method/Protocol', ''),
                ('Contributor', ''),
                ('Processing Date', '')
            ]
            for key, value in fields:
                self.add_metadata_field(key, value)
            # Button to add additional fields
            self.add_field_button = QPushButton('Add Field')
            self.add_field_button.setIcon(QIcon(resource_path('gui/resources/add_field_icon.png')))  # Optional: add icon
            self.add_field_button.clicked.connect(self.add_empty_field)
            self.scroll_layout.addRow(self.add_field_button)
            self.extract_metadata_button.show()
        else:
            QMessageBox.warning(self, 'No Item Selected', 'Please select a folder or data file in the hierarchy tree to add Assay metadata.')

    def add_metadata_field(self, key='', value=''):
        field_widget = MetadataField(key, value)
        self.scroll_layout.addRow(field_widget)
        self.metadata_fields.append(field_widget)

    def add_empty_field(self):
        self.add_metadata_field()

    def get_selected_folder(self):
        selected_item = self.get_selected_item()
        if selected_item and selected_item['type'] == 'folder':
            return selected_item['path']
        return None

    def get_selected_file(self):
        selected_item = self.get_selected_item()
        if selected_item and selected_item['type'] == 'file':
            return selected_item['path']
        return None

    def get_selected_item(self):
        indexes = self.tree_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            path = self.dir_model.filePath(index)
            if os.path.isdir(path):
                return {'type': 'folder', 'path': path}
            elif os.path.isfile(path):
                return {'type': 'file', 'path': path}
        return None

    def save_metadata(self):
        if not self.current_metadata_type:
            QMessageBox.warning(self, 'No Metadata', 'Please add metadata first.')
            return

        data = {}
        for field in self.metadata_fields:
            key, value = field.get_data()
            data[key] = value

        format_options = ['YAML', 'JSON', 'TXT']
        format_choice, ok = QInputDialog.getItem(self, 'Select Format', 'Choose metadata format:', format_options, 0, False)
        if ok:
            if format_choice == 'YAML':
                file_extension = '.yaml'
                content = yaml.dump(data)
            elif format_choice == 'JSON':
                file_extension = '.json'
                content = json.dumps(data, indent=2)
            elif format_choice == 'TXT':
                file_extension = '.txt'
                content = '\n'.join(f'{k}: {v}' for k, v in data.items())
            else:
                return

            if self.current_metadata_type == 'Assay':
                selected_item = self.get_selected_item()
                if selected_item and selected_item['type'] == 'file':
                    default_name = os.path.splitext(os.path.basename(selected_item['path']))[0] + '_metadata' + file_extension
                    save_folder = os.path.dirname(selected_item['path'])
                else:
                    default_name = 'assay_metadata' + file_extension
                    save_folder = self.current_folder_path
            elif self.current_metadata_type == 'Study':
                default_name = 'study_metadata' + file_extension
                save_folder = self.current_folder_path
            elif self.current_metadata_type == 'Investigation':
                default_name = 'investigation_metadata' + file_extension
                save_folder = self.current_folder_path
            else:
                default_name = 'metadata' + file_extension
                save_folder = self.current_folder_path

            save_path = os.path.join(save_folder, default_name)
            try:
                with open(save_path, 'w') as f:
                    f.write(content)
                QMessageBox.information(self, 'Metadata Saved', f'Metadata saved to {save_path}')
                self.metadata_processed.emit()  # Emit signal after saving metadata
            except Exception as e:
                QMessageBox.warning(self, 'Save Error', f'Failed to save metadata:\n{e}')
        else:
            QMessageBox.warning(self, 'Format Not Selected', 'Please select a format to save metadata.')

    def export_metadata(self):
        # Implement export functionality as needed
        QMessageBox.information(self, 'Export Metadata', 'Export functionality is not implemented yet.')

    def extract_metadata(self):
        selected_folder = self.get_selected_folder()
        if selected_folder:
            self.current_metadata_type = 'Assay'
            self.current_folder_path = selected_folder

            # Check if token mapping fields already exist to prevent duplication
            if hasattr(self, 'token_mapping_group'):
                QMessageBox.information(self, 'Token Mapping Exists', 'Token mapping fields are already present.')
                return

            # Create a group box for token mapping
            self.token_mapping_group = QGroupBox("Token Mapping")
            token_mapping_layout = QFormLayout()
            self.token_mapping_group.setLayout(token_mapping_layout)
            self.scroll_layout.addRow(self.token_mapping_group)

            # Get list of files to determine the number of tokens
            try:
                files = [f for f in os.listdir(selected_folder) if os.path.isfile(os.path.join(selected_folder, f))]
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to list files in the selected folder:\n{e}')
                return

            if not files:
                QMessageBox.warning(self, 'No Files', 'No files found in the selected folder.')
                return

            # Use the first file name to determine tokens
            sample_file = files[0]
            tokens = re.split(r'[_\-\s]+', sample_file)

            # Create input fields for each token (only key names)
            self.token_fields = []
            for i, token in enumerate(tokens):
                key_field = QLineEdit(f'Metadata Key {i+1}')
                token_mapping_layout.addRow(f'Token {i+1}:', key_field)
                self.token_fields.append(key_field)

            # Button to apply mapping
            self.apply_button = QPushButton('Apply for all')
            self.apply_button.setIcon(QIcon(resource_path('gui/resources/apply_icon.png')))  # Optional: add icon
            self.apply_button.clicked.connect(self.apply_token_mapping)
            self.scroll_layout.addRow(self.apply_button)
        else:
            QMessageBox.warning(self, 'No Folder Selected', 'Please select a folder in the hierarchy tree to extract metadata.')

    def apply_token_mapping(self):
        selected_folder = self.current_folder_path
        try:
            files = [f for f in os.listdir(selected_folder) if os.path.isfile(os.path.join(selected_folder, f))]
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to list files in the selected folder:\n{e}')
            return

        if not files:
            QMessageBox.warning(self, 'No Files', 'No files found in the selected folder.')
            return

        # Gather metadata keys from token mapping fields
        metadata_keys = []
        for key_field in self.token_fields:
            key = key_field.text().strip()
            if not key:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter all metadata keys.')
                return
            metadata_keys.append(key)

        # Confirm the number of tokens matches the number of metadata keys
        sample_file = files[0]
        tokens = re.split(r'[_\-\s]+', sample_file)
        if len(tokens) != len(metadata_keys):
            QMessageBox.warning(self, 'Mismatch', 'The number of tokens does not match the number of metadata keys.')
            return

        format_options = ['YAML', 'JSON', 'TXT']
        format_choice, ok = QInputDialog.getItem(self, 'Select Format', 'Choose metadata format:', format_options, 0, False)
        if not ok:
            QMessageBox.warning(self, 'Format Not Selected', 'Please select a format to save metadata.')
            return

        # Prepare to save metadata for each file
        total_files = len(files)
        self.progress_bar.setMaximum(total_files)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)  # Show the progress bar

        for file_name in files:
            tokens = re.split(r'[_\-\s]+', file_name)
            if len(tokens) != len(metadata_keys):
                QMessageBox.warning(self, 'Token Mismatch', f'File "{file_name}" does not have the expected number of tokens.')
                continue

            data = {}
            for key, token in zip(metadata_keys, tokens):
                data[key] = token.strip()

            # Add static fields if any (if you want to include additional metadata beyond tokens)
            for field in self.metadata_fields:
                key, value = field.get_data()
                if key:
                    data[key] = value

            # Determine file extension and content
            if format_choice == 'YAML':
                file_extension = '.yaml'
                content = yaml.dump(data)
            elif format_choice == 'JSON':
                file_extension = '.json'
                content = json.dumps(data, indent=2)
            elif format_choice == 'TXT':
                file_extension = '.txt'
                content = '\n'.join(f'{k}: {v}' for k, v in data.items())
            else:
                continue

            # Save metadata file
            base_name = os.path.splitext(file_name)[0]
            save_path = os.path.join(selected_folder, base_name + '_metadata' + file_extension)
            try:
                with open(save_path, 'w') as f:
                    f.write(content)
            except Exception as e:
                QMessageBox.warning(self, 'Save Error', f'Failed to save metadata for {file_name}:\n{e}')
                continue

            # Update progress bar
            self.progress_bar.setValue(self.progress_bar.value() + 1)
            QApplication.processEvents()

        QMessageBox.information(self, 'Metadata Extraction', 'Metadata extracted and saved for all files.')
        self.metadata_processed.emit()  # Emit signal after processing metadata
        self.progress_bar.setVisible(False)  # Hide the progress bar after completion
        self.progress_bar.setValue(0)  # Reset progress bar value

    def navigate_back(self):
        if self.navigation_history:
            previous_folder = self.navigation_history.pop()
            self.root_folder_path = previous_folder
            self.populate_tree_view()
            if not self.navigation_history:
                self.back_button.setEnabled(False)
        else:
            self.back_button.setEnabled(False)

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
    QMenu, QAction, QApplication, QProgressBar, QDirModel, QGroupBox, QProgressBar,QShortcut, QSizePolicy

)
from PyQt5.QtCore import (
    Qt, QDir, pyqtSignal,QItemSelectionModel
)
from PyQt5.QtGui import QIcon, QKeySequence
from collections import OrderedDict
from gui.dialogs.help_dialog import HelpDialog 
from gui.utils.help_content import METADATA_HELP

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
        
        # Create input fields
        self.key_edit = QLineEdit(key)
        self.value_edit = QLineEdit(value)
        
        # Create remove button with icon and fixed size
        self.remove_button = QPushButton()
        self.remove_button.setIcon(QIcon(resource_path('gui/resources/remove.png')))  # Ensure the icon exists
        self.remove_button.setFixedSize(24, 24)  # Set fixed size for the remove button
        self.remove_button.setToolTip('Remove this field')
        
        # Adjust size policies
        self.key_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.value_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.remove_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        # Add widgets to the layout with stretch factors
        self.layout.addWidget(self.key_edit, 2)
        self.layout.addWidget(self.value_edit, 3)
        self.layout.addWidget(self.remove_button)
        
        # Set layout margins and spacing
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
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
        self.select_folder_button.setToolTip('Click to select the root folder for metadata handling.')

        self.select_folder_button.setIcon(QIcon(resource_path('gui/resources/select_folder_icon.png')))  # Ensure the icon exists
        self.select_folder_button.clicked.connect(self.select_root_folder)
        navigation_layout.addWidget(self.select_folder_button)

        left_panel.addLayout(navigation_layout)


        # Group box for metadata fields
        self.metadata_group_box = QGroupBox('Metadata Fields')
        self.metadata_group_layout = QVBoxLayout()
        self.metadata_group_box.setLayout(self.metadata_group_layout)

        # Scroll Area for Metadata Fields
        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.scroll_layout = QFormLayout()
        self.scroll_area_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.metadata_group_layout.addWidget(self.scroll_area)

        self.metadata_group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid gray;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
        """)
        left_panel.addWidget(self.metadata_group_box)

  
        # Buttons below scroll area
        button_layout = QHBoxLayout()
        self.add_investigation_button = QPushButton('Add Investigation')
        self.add_investigation_button.setIcon(QIcon(resource_path('gui/resources/investigation_icon.png')))  # Ensure the icon exists
        self.add_investigation_button.setToolTip('Add metadata for an Investigation.')

        self.add_study_button = QPushButton('Add Study')
        self.add_study_button.setIcon(QIcon(resource_path('gui/resources/study_icon.png')))  # Ensure the icon exists
        self.add_study_button.setToolTip('Add metadata for a Study.')

        self.add_assay_button = QPushButton('Add Assay')
        self.add_assay_button.setIcon(QIcon(resource_path('gui/resources/assay_icon.png')))  # Ensure the icon exists
        self.add_assay_button.setToolTip('Add metadata for an Assay.')
        button_layout.addWidget(self.add_investigation_button)
        
        button_layout.addWidget(self.add_study_button)
        button_layout.addWidget(self.add_assay_button)
        left_panel.addLayout(button_layout)

        # Save and Export buttons
        save_export_layout = QHBoxLayout()
        self.save_metadata_button = QPushButton('Save Metadata')
        self.save_metadata_button.setIcon(QIcon(resource_path('gui/resources/save_icon.png')))  # Ensure the icon exists
        self.save_metadata_button.setToolTip('Save the current metadata.')

        self.export_metadata_button = QPushButton('Export Metadata')
        self.export_metadata_button.setIcon(QIcon(resource_path('gui/resources/export_icon.png')))  # Ensure the icon exists
        self.export_metadata_button.setToolTip('Export the current metadata.')

        self.extract_metadata_button = QPushButton('Extract Metadata from Data Points')
        self.extract_metadata_button.setIcon(QIcon(resource_path('gui/resources/extract_icon.png')))  # Ensure the icon exists
        self.extract_metadata_button.setToolTip('Extract metadata from data points based on token mapping.')

        # **New: Help Button Layout**
        help_button_layout = QHBoxLayout()
        self.help_button = QPushButton('Help')
        self.help_button.setIcon(QIcon(resource_path('gui/resources/help_icon.png')))  # Optional: add a help icon
        self.help_button.setToolTip('Click for help and instructions.')
        self.help_button.clicked.connect(self.show_help)

        save_export_layout.addWidget(self.save_metadata_button)
        save_export_layout.addWidget(self.export_metadata_button)
        save_export_layout.addWidget(self.extract_metadata_button)
        save_export_layout.addWidget(self.help_button)

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
        self.back_button.setToolTip('Navigate to the previous folder in the hierarchy.')
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

        # Set the default column width for the "Name" column
        self.tree_view.setColumnWidth(0, 250)  # Adjust the width as desired

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

    def get_expanded_paths(self):
        expanded_paths = []

        def recurse(index):
            if not index.isValid():
                return
            if self.tree_view.isExpanded(index):
                path = self.dir_model.filePath(index)
                expanded_paths.append(path)
                # Recurse into children
                for i in range(self.dir_model.rowCount(index)):
                    child_index = self.dir_model.index(i, 0, index)
                    recurse(child_index)

        root_index = self.tree_view.rootIndex()
        recurse(root_index)
        return expanded_paths

    def get_selected_path(self):
        indexes = self.tree_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            path = self.dir_model.filePath(index)
            return path
        return None

    def set_expanded_paths(self, expanded_paths):
        valid_paths = []
        for path in expanded_paths:
            index = self.dir_model.index(path)
            if index.isValid():
                valid_paths.append(path)
        for path in valid_paths:
            index = self.dir_model.index(path)
            self.tree_view.expand(index)

    def set_selected_path(self, selected_path):
        index = self.dir_model.index(selected_path)
        if index.isValid():
            self.tree_view.selectionModel().select(
                index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
            self.tree_view.scrollTo(index)
        else:
            # If the selected path no longer exists, select the parent directory
            parent_path = os.path.dirname(selected_path)
            parent_index = self.dir_model.index(parent_path)
            if parent_index.isValid():
                self.tree_view.selectionModel().select(
                    parent_index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
                self.tree_view.scrollTo(parent_index)

    def refresh_tree_view(self, expanded_paths=None, selected_path=None):
        """Refresh the QDirModel by re-instantiating it and reassigning it to the QTreeView."""
        if self.root_folder_path:
            if expanded_paths is None:
                expanded_paths = self.get_expanded_paths()
            if selected_path is None:
                selected_path = self.get_selected_path()

            # Re-instantiate the model
            self.dir_model = QDirModel()
            self.dir_model.setReadOnly(False)
            self.dir_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)
            # Reassign the model to the tree view
            self.tree_view.setModel(self.dir_model)
            index = self.dir_model.index(self.root_folder_path)
            self.tree_view.setRootIndex(index)

            # Restore expanded paths and selection
            self.set_expanded_paths(expanded_paths)
            self.set_selected_path(selected_path)


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
            # Set up the model and view
            self.dir_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)
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
        # Save expanded paths and selected path before deletion
        expanded_paths = self.get_expanded_paths()
        selected_path = self.get_selected_path()

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

        # Remove deleted path from expanded_paths if present
        if path in expanded_paths:
            expanded_paths.remove(path)

        # Refresh the hierarchy tree
        self.refresh_tree_view(expanded_paths=expanded_paths, selected_path=selected_path)


    def create_new_folder(self, index):
        # Save expanded paths and selected path before creating the folder
        expanded_paths = self.get_expanded_paths()
        selected_path = self.get_selected_path()

        path = self.dir_model.filePath(index)
        folder_name, ok = QInputDialog.getText(self, 'New Folder', 'Folder Name:')
        if ok and folder_name:
            new_folder_path = os.path.join(path, folder_name)
            try:
                os.mkdir(new_folder_path)
                # Refresh the hierarchy tree
                self.refresh_tree_view(expanded_paths=expanded_paths, selected_path=selected_path)
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
        selected_folder = self.get_selected_folder()
        if not selected_folder:
            QMessageBox.warning(
                self,
                'No Folder Selected',
                'Please select a folder in the hierarchy tree to add Investigation metadata.'
            )
            return
        self.clear_scroll_area()
        self.current_metadata_type = 'Investigation'
        self.current_folder_path = selected_folder
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
        self.add_field_button.setIcon(QIcon(resource_path('gui/resources/add2.png')))  # Optional: add icon
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
            self.add_field_button.setIcon(QIcon(resource_path('gui/resources/add2.png')))  # Optional: add icon
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
            self.add_field_button.setIcon(QIcon(resource_path('gui/resources/add2.png')))  # Optional: add icon
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

        data = OrderedDict()
        for field in self.metadata_fields:
            key, value = field.get_data()
            data[key] = value

        format_options = ['YAML', 'JSON', 'TXT']
        format_choice, ok = QInputDialog.getItem(self, 'Select Format', 'Choose metadata format:', format_options, 0, False)
        if ok:
            if format_choice == 'YAML':
                file_extension = '.yaml'
                content = yaml.dump(data, default_flow_style=False)
            elif format_choice == 'JSON':
                file_extension = '.json'
                content = json.dumps(data, indent=2, sort_keys=False)
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

            # Save expanded paths and selected path before saving
            expanded_paths = self.get_expanded_paths()
            selected_path = self.get_selected_path()

            try:
                with open(save_path, 'w') as f:
                    f.write(content)
                QMessageBox.information(self, 'Metadata Saved', f'Metadata saved to {save_path}')
                self.metadata_processed.emit()  # Emit signal after saving metadata

                # Refresh the hierarchy tree to reflect the new metadata file
                self.refresh_tree_view(expanded_paths=expanded_paths, selected_path=selected_path)

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
            self.apply_button.setToolTip('Apply the token mappings to all files in the selected folder.')
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

        format_options = ['YAML', 'JSON', 'TXT']
        format_choice, ok = QInputDialog.getItem(self, 'Select Format', 'Choose metadata format:', format_options, 0, False)
        if not ok:
            QMessageBox.warning(self, 'Format Not Selected', 'Please select a format to save metadata.')
            return

        # Save expanded paths and selected path before processing
        expanded_paths = self.get_expanded_paths()
        selected_path = self.get_selected_path()

        # Prepare to save metadata for each file
        total_files = len(files)
        self.progress_bar.setMaximum(total_files)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)  # Show the progress bar

        skipped_files = []  # Collect skipped files

        # Build ordered list of metadata keys
        ordered_keys = []

        # Add keys from static fields (metadata_fields)
        for field in self.metadata_fields:
            key, value = field.get_data()
            if key:
                ordered_keys.append(key)

        # Add keys from token mapping fields (token_fields)
        for key in metadata_keys:
            ordered_keys.append(key)

        for file_name in files:
            tokens = re.split(r'[_\-\s]+', file_name)
            if len(tokens) != len(metadata_keys):
                skipped_files.append(file_name)
                continue

            data = OrderedDict()

            # Collect values for static fields
            static_field_values = OrderedDict()
            for field in self.metadata_fields:
                key, value = field.get_data()
                if key:
                    static_field_values[key] = value

            # Collect values for token-mapped fields
            token_field_values = OrderedDict()
            for key, token in zip(metadata_keys, tokens):
                token_field_values[key] = token.strip()

            # Build data in order
            for key in ordered_keys:
                if key in static_field_values:
                    data[key] = static_field_values[key]
                elif key in token_field_values:
                    data[key] = token_field_values[key]
                else:
                    data[key] = ''  # or None

            # Determine file extension and content
            if format_choice == 'YAML':
                file_extension = '.yaml'
                content = yaml.dump(data, default_flow_style=False)
            elif format_choice == 'JSON':
                file_extension = '.json'
                content = json.dumps(data, indent=2, sort_keys=False)
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

        # After processing all files
        if skipped_files:
            skipped_files_str = '\n'.join(skipped_files)
            QMessageBox.information(
                self,
                'Skipped Files',
                f'The following files were skipped due to token mismatch:\n{skipped_files_str}'
            )

        QMessageBox.information(self, 'Metadata Extraction', 'Metadata extracted and saved for all files.')
        self.metadata_processed.emit()  # Emit signal after processing metadata
        self.progress_bar.setVisible(False)  # Hide the progress bar after completion
        self.progress_bar.setValue(0)  # Reset progress bar value

        # Refresh the hierarchy tree to show new metadata files
        self.refresh_tree_view(expanded_paths=expanded_paths, selected_path=selected_path)

    def navigate_back(self):
        if self.navigation_history:
            previous_folder = self.navigation_history.pop()
            self.root_folder_path = previous_folder
            self.populate_tree_view()
            if not self.navigation_history:
                self.back_button.setEnabled(False)
        else:
            self.back_button.setEnabled(False)

    def show_help(self):
        help_content = METADATA_HELP
        dialog = HelpDialog("Metadata Help Content", help_content, self)
        dialog.exec_()

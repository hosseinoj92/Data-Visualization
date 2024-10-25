import os
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QApplication, QMenu, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt, QUrl, QMimeData
import sys

def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
############################################################

class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.MultiSelection)  # Enable multi-selection
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
        elif event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            self.copy_selected_items()
        elif event.key() == Qt.Key_V and event.modifiers() & Qt.ControlModifier:
            self.paste_items()
        else:
            super().keyPressEvent(event)

    def copy_selected_items(self):
        selected_items = self.selectedItems()
        if not selected_items:
            return
        file_paths = [item.data(Qt.UserRole) for item in selected_items]
        mime_data = QMimeData()
        urls = [QUrl.fromLocalFile(file_path) for file_path in file_paths]
        mime_data.setUrls(urls)
        QApplication.clipboard().setMimeData(mime_data)
        
    def paste_items(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if mime_data.hasUrls():
            urls = mime_data.urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path and os.path.isfile(file_path):
                    self.add_file_to_panel(file_path)

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
        Create a context menu with 'Delete' and 'Rename' options on right-click.
        """
        context_menu = QMenu(self)
        delete_action = context_menu.addAction("Delete")
        rename_action = context_menu.addAction("Rename")
        action = context_menu.exec_(self.mapToGlobal(position))
        if action == delete_action:
            self.delete_selected_items()
        elif action == rename_action:
            self.rename_selected_item()

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
        Add a single file to the list.
        Avoid adding duplicates.
        """
        file_name = os.path.basename(file_path)
        # Avoid adding duplicates
        existing_files = [os.path.abspath(self.item(i).data(Qt.UserRole)) for i in range(self.count())]
        if os.path.abspath(file_path) in existing_files:
            return
        item = QListWidgetItem(file_name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Unchecked)
        item.setData(Qt.UserRole, file_path)
        self.addItem(item)

    def rename_selected_item(self):
        """
        Rename the selected item in the list.
        """
        selected_items = self.selectedItems()
        if len(selected_items) != 1:
            QMessageBox.warning(self, "Rename Error", "Please select a single file to rename.")
            return
        
        item = selected_items[0]
        current_name = item.text()
        file_path = item.data(Qt.UserRole)
        new_name, ok = QInputDialog.getText(self, "Rename File", "Enter new name:", text=current_name)
        
        if ok and new_name:
            # Validate the new name (e.g., no forbidden characters)
            if any(c in new_name for c in r'\/:*?"<>|'):
                QMessageBox.warning(self, "Invalid Name", "The file name contains invalid characters.")
                return
            
            # Check for duplicate names
            existing_names = [self.item(i).text() for i in range(self.count())]
            if new_name in existing_names:
                QMessageBox.warning(self, "Duplicate Name", "A file with this name already exists in the list.")
                return
            
            # Optionally, preserve the file extension
            _, ext = os.path.splitext(current_name)
            if not os.path.splitext(new_name)[1]:
                new_name += ext  # Append the original extension if not provided
            
            item.setText(new_name)
            QMessageBox.information(self, "Rename Successful", f"File renamed to {new_name}.")
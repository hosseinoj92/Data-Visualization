# batch_data_handling_panels.py
import os
import sys
import shutil
import pandas as pd
import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QLineEdit, QTableView, QTreeView, QAbstractItemView, QHeaderView,
    QProgressBar, QMessageBox, QCalendarWidget, QDateEdit, QDialog, QFormLayout,
    QGroupBox, QScrollArea, QDateTimeEdit, QGridLayout, 
    QApplication,QDirModel,QCheckBox,QComboBox, QTextEdit,QTabWidget
)
from PyQt5.QtCore import pyqtSignal, Qt, QAbstractTableModel, QModelIndex, QDir, QDateTime
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QIcon
import yaml
import datetime
from PyQt5.QtCore import pyqtSignal

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas



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

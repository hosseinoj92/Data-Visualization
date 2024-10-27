# gui/tabs/data_fitting_tab.py

from PyQt5.QtWidgets import QWidget, QHBoxLayout

class DataFittingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        # Create an empty layout
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        # No widgets are added to the layout, so the tab will be empty

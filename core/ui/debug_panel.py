from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QHeaderView, QLabel, QSplitter
)
from PyQt6.QtCore import Qt
from core.ui.theme import COLORS

class DebugPanel(QWidget):
    """
    Sidebar panel for debugger data visualization.
    Contains sections for Variables, Watch, Call Stack, and Breakpoints.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_secondary']};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Variables Tree
        self.variables_tree = self._create_section("VARIABLES")
        splitter.addWidget(self.variables_tree)
        
        # Call Stack
        self.call_stack_tree = self._create_section("CALL STACK")
        splitter.addWidget(self.call_stack_tree)
        
        # Breakpoints
        self.breakpoints_tree = self._create_section("BREAKPOINTS")
        splitter.addWidget(self.breakpoints_tree)
        
        layout.addWidget(splitter)

    def _create_section(self, title):
        container = QWidget()
        v_layout = QVBoxLayout(container)
        v_layout.setContentsMargins(5, 5, 5, 5)
        
        label = QLabel(title)
        label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: bold; font-size: 8pt;")
        v_layout.addWidget(label)
        
        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        tree.setStyleSheet(f"background-color: transparent; border: none;")
        v_layout.addWidget(tree)
        
        return container

    def update_variables(self, vars):
        # Implementation to populate variables_tree
        pass

    def update_stack(self, stack):
        # Implementation to populate call_stack_tree
        pass

from PySide6.QtWidgets import QTreeView, QMenu
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide6.QtCore import Qt, QPoint

def add_file_view(parent):
    from ui.main_window import refresh_ui, get_registry
    from PySide6.QtWidgets import QMenu
    from PySide6.QtCore import QPoint
    
    file_list = QTreeView(parent)
    file_list.setAlternatingRowColors(True)
    file_list.setSelectionMode(QTreeView.ExtendedSelection)
    file_list.setContextMenuPolicy(Qt.CustomContextMenu)
    
    def open_context_menu(position: QPoint):
        menu = QMenu()
        from ui.toolbar import toolbar_actions_ref
        
        if toolbar_actions_ref:
            # Grouping actions: [Add], [Extract, Copy], [Delete]
            for text, callback in toolbar_actions_ref:
                if text in ["Add", "Extract", "Copy", "Delete"]:
                    if text == "Extract": menu.addSeparator()
                    if text == "Delete": menu.addSeparator()
                    
                    action = menu.addAction(text)
                    action.triggered.connect(callback)
                    
        menu.exec(file_list.viewport().mapToGlobal(position))

    file_list.customContextMenuRequested.connect(open_context_menu)
    
    # Model with columns: Name, Size, Type, Modified
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Name", "Size", "Type", "Modified"])
    file_list.setModel(model)
    file_list.setColumnWidth(0, 250)
    
    return file_list

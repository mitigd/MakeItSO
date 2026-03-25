from PySide6.QtWidgets import QTreeView
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon

def refresh_sidebar():
    """Refresh the sidebar directory tree."""
    from core.iso import get_state
    from ui.main_window import get_registry
    from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
    
    state = get_state()
    reg = get_registry()
    
    model = reg['sidebar'].model()
    model.removeRows(0, model.rowCount())
    
    if not state['is_loaded']:
        return
        
    root_node = QStandardItem(QIcon.fromTheme("folder"), "/")
    model.appendRow(root_node)
    
    # Simple recursive function to build the tree (Simplified for now)
    # In a full app, we'd traverse the ISO structure
    
    reg['sidebar'].expandAll()

def add_sidebar(parent):
    tree_view = QTreeView(parent)
    tree_view.setHeaderHidden(True)
    
    model = QStandardItemModel()
    tree_view.setModel(model)
    
    return tree_view

from PySide6.QtWidgets import QTreeView
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon

def refresh_sidebar():
    """Refresh the sidebar directory tree."""
    from core.iso import get_state, get_dir_tree, set_current_dir
    from ui.main_window import get_registry, refresh_ui
    from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
    
    state = get_state()
    reg = get_registry()
    
    view = reg['sidebar']
    model = view.model()
    model.removeRows(0, model.rowCount())
    
    if not state['is_loaded']:
        return
        
    all_dirs = get_dir_tree()
    nodes = {} # path -> QStandardItem
    
    for path in all_dirs:
        name = path.split('/')[-1] or "/"
        item = QStandardItem(QIcon.fromTheme("folder"), name)
        item.setData(path) # Store the full path in data
        nodes[path] = item
        
        if path == '/':
            model.appendRow(item)
        else:
            parent_path = '/'.join(path.split('/')[:-1]) or '/'
            if parent_path in nodes:
                nodes[parent_path].appendRow(item)

    def on_sidebar_clicked(index):
        path = model.itemFromIndex(index).data()
        print(f"Sidebar clicked: {path}")
        set_current_dir(path)
        refresh_ui()
        
    # Re-connect (Disconnect only if same view)
    view.clicked.connect(on_sidebar_clicked)
    
    view.expandAll()

def add_sidebar(parent):
    tree_view = QTreeView(parent)
    tree_view.setHeaderHidden(True)
    tree_view.setMinimumWidth(200)
    
    model = QStandardItemModel()
    tree_view.setModel(model)
    
    return tree_view

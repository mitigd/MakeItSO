from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt
from ui.toolbar import add_toolbar
from ui.sidebar import add_sidebar
from ui.file_view import add_file_view
from ui.status_bar import add_status_bar

# Global UI registry to keep track of widgets for updates
ui_registry = {
    'window': None,
    'sidebar': None,
    'file_view': None,
    'status_label': None,
    'progress_bar': None
}

def get_registry():
    return ui_registry

def refresh_ui():
    """Refresh the entire UI based on the current ISO state."""
    from core.iso import get_state, list_dir
    from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
    from ui.sidebar import refresh_sidebar
    
    state = get_state()
    reg = get_registry()
    
    if not state['is_loaded']:
        reg['window'].setWindowTitle("MakeSo - [No ISO]")
        return

    # Update title
    title = f"MakeSo - [{state['path'] if state['path'] else 'Unsaved ISO'}]"
    reg['window'].setWindowTitle(title)
    
    # Refresh Sidebar
    refresh_sidebar()
    
    # Refresh File View
    model = reg['file_view'].model()
    model.removeRows(0, model.rowCount())
    
    items = list_dir()
    total_size = 0
    for item in items:
        row = [
            QStandardItem(QIcon.fromTheme("folder" if item['is_dir'] else "text-x-generic"), item['name']),
            QStandardItem(f"{item['size'] / 1024:.1f} KB" if item['size'] > 0 else "0"),
            QStandardItem("Folder" if item['is_dir'] else "File"),
            QStandardItem(item['modified'])
        ]
        model.appendRow(row)
        total_size += item['size']
        
    # Update Status
    if reg['status_label']:
        reg['status_label'].setText(f"Total: {len(items)} objects, {total_size / 1024:.1f} KB")

def create_main_window():
    window = QMainWindow()
    window.setWindowTitle("MakeSo - [New ISO]")
    window.resize(1000, 700)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    
    # Header area (Toolbar)
    add_toolbar(window)
    
    # Navigation Bar (Simplified for now)
    nav_bar = QWidget()
    nav_bar.setObjectName("navBar")
    nav_bar.setFixedHeight(40)
    nav_layout = QHBoxLayout(nav_bar)
    nav_layout.setContentsMargins(10, 0, 10, 0)
    main_layout.addWidget(nav_bar)
    
    # Splitter for Sidebar and File View
    splitter = QSplitter(Qt.Horizontal)
    
    sidebar = add_sidebar(splitter)
    file_view = add_file_view(splitter)
    
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 4)
    
    main_layout.addWidget(splitter)
    
    # Footer area (Status Bar)
    status_bar, status_label, progress_bar = add_status_bar(window)
    
    ui_registry['window'] = window
    ui_registry['sidebar'] = sidebar
    ui_registry['file_view'] = file_view
    ui_registry['status_label'] = status_label
    ui_registry['progress_bar'] = progress_bar
    
    return window

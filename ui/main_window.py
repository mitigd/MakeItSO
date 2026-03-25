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
        reg['window'].setWindowTitle("MakeItSO - [No ISO]")
        return

    # Update title and path bar
    title = f"MakeItSO - [{state['path'] if state['path'] else 'Unsaved ISO'}]"
    reg['window'].setWindowTitle(title)
    if reg['path_edit']:
        reg['path_edit'].setText(state['current_dir'])
    
    # Refresh Sidebar
    refresh_sidebar()
    
    # Refresh File View
    model = reg['file_view'].model()
    model.removeRows(0, model.rowCount())
    
    items = list_dir()
    # Sort: Folders first, then Name
    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    
    # Prepend '..' if not in root
    current_dir = state['current_dir'].rstrip('/')
    if current_dir != "" and state['current_dir'] != "/":
        up_row = [
            QStandardItem(QIcon.fromTheme("go-up"), ".."),
            QStandardItem(""),
            QStandardItem("Folder"),
            QStandardItem("")
        ]
        model.appendRow(up_row)
    
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
        
    # Refresh Status Bar Usage
    from core.iso import get_total_size
    total_bytes = get_total_size()
    total_mb = total_bytes / (1024 * 1024)
    print(f"DEBUG: Total Bytes: {total_bytes}, Total MB: {total_mb:.2f}")
    
    # Dynamic capacity tiering
    if total_mb <= 700: max_mb = 700
    elif total_mb <= 4700: max_mb = 4700
    elif total_mb <= 8500: max_mb = 8500
    else: max_mb = 25000
    
    # Count objects in current dir
    count = len([i for i in items if i['name'] != '..'])
    
    status_text = f"Total: {count} objects, {total_mb:.2f} MB / {max_mb} MB"
    if reg['status_label']:
        reg['status_label'].setText(status_text)
    
    if reg['progress_bar']:
        percent = int((total_mb / max_mb) * 100)
        reg['progress_bar'].setValue(min(percent, 100))
        reg['progress_bar'].setToolTip(f"{percent}% of {max_mb} MB used")
        # Color based on usage (Premium touch)
        if percent > 90:
            reg['progress_bar'].setStyleSheet("QProgressBar::chunk { background-color: #e81123; }") # Red
        elif percent > 75:
            reg['progress_bar'].setStyleSheet("QProgressBar::chunk { background-color: #ffb900; }") # Yellow
        else:
            reg['progress_bar'].setStyleSheet("QProgressBar::chunk { background-color: #007acc; }") # Blue

def create_main_window():
    window = QMainWindow()
    window.setWindowTitle("MakeItSO - [No ISO]")
    window.setMinimumSize(1000, 680)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    
    # Header area (Toolbar)
    add_toolbar(window)
    
    # Navigation Bar
    nav_bar = QWidget()
    nav_bar.setObjectName("navBar")
    nav_bar.setFixedHeight(40)
    nav_layout = QHBoxLayout(nav_bar)
    nav_layout.setContentsMargins(10, 0, 10, 0)
    
    from PySide6.QtWidgets import QPushButton, QLineEdit
    from core.iso import go_up, go_back, go_forward
    
    back_btn = QPushButton("<")
    back_btn.setFixedWidth(30)
    back_btn.clicked.connect(lambda: [go_back(), refresh_ui()])
    nav_layout.addWidget(back_btn)
    
    fwd_btn = QPushButton(">")
    fwd_btn.setFixedWidth(30)
    fwd_btn.clicked.connect(lambda: [go_forward(), refresh_ui()])
    nav_layout.addWidget(fwd_btn)
    
    up_btn = QPushButton("Up")
    up_btn.setFixedWidth(50)
    up_btn.clicked.connect(lambda: [go_up(), refresh_ui()])
    nav_layout.addWidget(up_btn)
    
    path_edit = QLineEdit("/")
    path_edit.setObjectName("pathEdit")
    path_edit.setReadOnly(True)
    nav_layout.addWidget(path_edit)
    ui_registry['path_edit'] = path_edit
    
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
    
    # Actions
    def on_double_click(index):
        from core.iso import get_state, set_current_dir, go_up
        model = file_view.model()
        name = model.item(index.row(), 0).text()
        
        if name == "..":
            go_up()
            refresh_ui()
            return

        type_str = model.item(index.row(), 2).text()
        if type_str == "Folder":
            state = get_state()
            new_path = f"{state['current_dir'].rstrip('/')}/{name}"
            set_current_dir(new_path)
            refresh_ui()
            
    file_view.doubleClicked.connect(on_double_click)
    
    return window

import os
from PySide6.QtWidgets import QToolBar, QToolButton, QFileDialog
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, QSize
import core.iso as iso

def add_toolbar(window):
    from ui.main_window import refresh_ui
    
    toolbar = QToolBar("Main Toolbar")
    toolbar.setIconSize(QSize(32, 32))
    toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
    window.addToolBar(toolbar)
    
    def on_new():
        iso.new_iso()
        refresh_ui()
        
    def on_open():
        file_path, _ = QFileDialog.getOpenFileName(window, "Open ISO", "", "ISO Files (*.iso)")
        if file_path:
            if iso.open_iso(file_path):
                refresh_ui()

    def on_save():
        state = iso.get_state()
        if not state['path']:
            on_save_as()
        else:
            iso.save_iso(state['path'])
            refresh_ui()

    def on_save_as():
        file_path, _ = QFileDialog.getSaveFileName(window, "Save ISO As", "image.iso", "ISO Files (*.iso)")
        if file_path:
            iso.save_iso(file_path)
            refresh_ui()

    def on_add():
        file_paths, _ = QFileDialog.getOpenFileNames(window, "Add Files", "", "All Files (*.*)")
        if file_paths:
            for fp in file_paths:
                name = os.path.basename(fp)
                iso.add_file(fp, f"/{name}")
            refresh_ui()

    def on_delete():
        reg = get_registry()
        view = reg['file_view']
        indices = view.selectionModel().selectedRows()
        if indices:
            model = view.model()
            for index in sorted(indices, reverse=True):
                name = model.item(index.row(), 0).text()
                # Determine if it's a dir (Simplified)
                iso.remove_item(f"/{name}")
            refresh_ui()

    def on_extract():
        reg = get_registry()
        view = reg['file_view']
        indices = view.selectionModel().selectedRows()
        if indices:
            model = view.model()
            save_dir = QFileDialog.getExistingDirectory(window, "Extract to Directory")
            if save_dir:
                for index in indices:
                    name = model.item(index.row(), 0).text()
                    # In pycdlib, we need to extract to a local file
                    local_path = os.path.join(save_dir, name)
                    # Simplified extraction logic
                    # This would need more robust handling in a real app
                    try:
                        iso.get_state()['iso'].get_file_from_joliet_path(local_path, joliet_path=f"/{name}")
                    except:
                        pass
                refresh_ui()

    # Actions
    actions = [
        ("New", "document-new", on_new),
        ("Open", "document-open", on_open),
        ("Save", "document-save", on_save),
        ("Save As", "document-save-as", on_save_as),
        (None, None, None), # Separator
        ("Add", "list-add", on_add),
        ("Extract", "document-export", on_extract),
        ("Delete", "list-remove", on_delete),
        (None, None, None),
        ("Copy", "edit-copy", None),
        ("Compress", "package-x-generic", None),
        ("Burn", "media-optical-burn", None),
        ("Mount", "media-mount", None),
        (None, None, None),
        ("Help", "help-browser", None)
    ]
    
    for text, icon_name, callback in actions:
        if text is None:
            toolbar.addSeparator()
            continue
            
        icon = QIcon.fromTheme(icon_name)
        action = toolbar.addAction(icon, text)
        if callback:
            action.triggered.connect(callback)
            
    return toolbar

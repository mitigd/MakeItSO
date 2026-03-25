from PySide6.QtWidgets import QToolBar, QToolButton, QFileDialog, QApplication
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, QSize
import core.iso as iso

# Global reference for context menus
toolbar_actions_ref = []

def add_toolbar(window):
    from ui.main_window import refresh_ui, get_registry
    global toolbar_actions_ref
    toolbar_actions_ref.clear()
    
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
        from PySide6.QtWidgets import QProgressDialog
        reg = get_registry()
        view = reg['file_view']
        indices = view.selectionModel().selectedRows()
        
        save_dir = QFileDialog.getExistingDirectory(window, "Extract to Directory")
        if not save_dir:
            return
            
        progress = QProgressDialog("Extracting files...", "Cancel", 0, 100, window)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()

        def update_progress(name):
            progress.setLabelText(f"Extracting: {name}")
            QApplication.processEvents()

        if not indices:
            # Extract everything
            iso.extract_all(save_dir, progress_callback=update_progress)
        else:
            # Extract selected indices
            model = view.model()
            state = iso.get_state()
            for i, index in enumerate(indices):
                if progress.wasCanceled(): break
                name = model.item(index.row(), 0).text()
                iso_path = f"{state['current_dir'].rstrip('/')}/{name}"
                dest_path = os.path.join(save_dir, name)
                iso.extract_item(iso_path, dest_path)
                update_progress(name)
                progress.setValue(int((i+1)/len(indices) * 100))
        
        progress.setValue(100)
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
            toolbar_actions_ref.append((text, callback))
            
    return toolbar

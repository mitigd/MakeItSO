from PySide6.QtWidgets import QStatusBar, QProgressBar, QLabel, QWidget, QHBoxLayout

def add_status_bar(window):
    status_bar = QStatusBar()
    window.setStatusBar(status_bar)
    
    # Progress bar area
    progress_container = QWidget()
    progress_layout = QHBoxLayout(progress_container)
    progress_layout.setContentsMargins(0, 0, 0, 0)
    
    label = QLabel("Total: 0 objects, 0 KB")
    progress_layout.addWidget(label)
    
    progress = QProgressBar()
    progress.setValue(0)
    progress.setToolTip("ISO Space Usage")
    progress.setFixedWidth(200)
    progress_layout.addWidget(progress)
    
    status_bar.addPermanentWidget(progress_container)
    
    return status_bar, label, progress

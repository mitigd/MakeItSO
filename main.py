import sys
import os
from PySide6.QtWidgets import QApplication
from ui.main_window import create_main_window

def main():
    app = QApplication(sys.argv)
    
    # Load styles
    style_path = os.path.join(os.path.dirname(__file__), "assets", "styles.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
            
    window = create_main_window()
    window.show()
    
    # Initialize with a new ISO by default
    import core.iso as iso
    from ui.main_window import refresh_ui
    iso.new_iso()
    refresh_ui()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

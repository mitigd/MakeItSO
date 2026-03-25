from PySide6.QtWidgets import QTreeView
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon

def add_file_view(parent):
    file_list = QTreeView(parent)
    file_list.setAlternatingRowColors(True)
    file_list.setSelectionMode(QTreeView.ExtendedSelection)
    
    # Model with columns: Name, Size, Type, Modified
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Name", "Size", "Type", "Modified"])
    
    # Mock row
    row = [
        QStandardItem(QIcon.fromTheme("text-x-generic"), "readme.txt"),
        QStandardItem("12 KB"),
        QStandardItem("TXT File"),
        QStandardItem("2024-03-25 10:00")
    ]
    model.appendRow(row)
    
    file_list.setModel(model)
    file_list.setColumnWidth(0, 250)
    
    return file_list

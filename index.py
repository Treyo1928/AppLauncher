import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QLabel, QGridLayout, QLineEdit, QDialog, QMessageBox, 
                             QTabWidget, QComboBox)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize

class App:
    def __init__(self, name, path, icon_path=""):
        self.name = name
        self.path = path
        self.icon_path = icon_path

    def launch(self):
        os.startfile(self.path)

class AppLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.load_apps()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()

        # Home Tab
        self.home_tab = QWidget()
        self.home_layout = QGridLayout(self.home_tab)  # Changed to QGridLayout
        self.update_ui()
        self.tab_widget.addTab(self.home_tab, "Home")

        # Edit Tab
        self.edit_tab = QWidget()
        self.edit_layout = QVBoxLayout()

        self.app_selector = QComboBox()
        self.update_app_selector()

        self.app_selector.currentIndexChanged.connect(self.populate_app_details)
        
        self.edit_layout.addWidget(self.app_selector)

        # Fields to edit app details
        self.edit_name = QLineEdit()
        self.edit_path = QLineEdit()
        self.edit_icon_path = QLineEdit()

        # Browse button for app path
        browse_path_button = QPushButton("Browse")
        browse_path_button.clicked.connect(lambda: self.edit_path.setText(QFileDialog.getOpenFileName()[0]))

        # Browse button for icon path
        browse_icon_button = QPushButton("Browse")
        browse_icon_button.clicked.connect(lambda: self.edit_icon_path.setText(QFileDialog.getOpenFileName()[0]))

        edit_button = QPushButton("Edit App")
        edit_button.clicked.connect(self.edit_app)

        delete_button = QPushButton("Delete App")
        delete_button.clicked.connect(self.delete_app)

        # Name
        self.edit_layout.addWidget(QLabel("Name:"))
        self.edit_layout.addWidget(self.edit_name)

        # Path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Path:"))
        path_layout.addWidget(self.edit_path)
        path_layout.addWidget(browse_path_button)
        self.edit_layout.addLayout(path_layout)

        # Icon Path
        icon_path_layout = QHBoxLayout()
        icon_path_layout.addWidget(QLabel("Icon Path:"))
        icon_path_layout.addWidget(self.edit_icon_path)
        icon_path_layout.addWidget(browse_icon_button)
        self.edit_layout.addLayout(icon_path_layout)
        self.edit_layout.addWidget(edit_button)
        self.edit_layout.addWidget(delete_button)

        self.edit_tab.setLayout(self.edit_layout)
        self.tab_widget.addTab(self.edit_tab, "Edit")

        # Add tab widget to main layout
        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)

    def populate_app_details(self, index):
        app = self.app_selector.itemData(index)
        if app:
            self.edit_name.setText(app.name)
            self.edit_path.setText(app.path)
            self.edit_icon_path.setText(app.icon_path)

    def load_apps(self):
        self.apps = []
        if os.path.exists("apps.json"):
            with open("apps.json", "r") as f:
                data = json.load(f)
                for app_data in data:
                    self.apps.append(App(app_data['name'], app_data['path'], app_data['icon_path']))

    def save_apps(self):
        with open("apps.json", "w") as f:
            data = [{"name": app.name, "path": app.path, "icon_path": app.icon_path} for app in self.apps]
            json.dump(data, f)

    def update_ui(self):
        # Clear the current items in the layout
        for i in reversed(range(self.home_layout.count())):
            widget = self.home_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        for i, app in enumerate(self.apps):
            button = QPushButton(app.name)
            button.setFixedWidth(150)  # Ensure all buttons have the same width
            if app.icon_path:
                button.setIcon(QIcon(app.icon_path))
                button.setIconSize(QSize(64, 64))
            button.clicked.connect(app.launch)
            self.home_layout.addWidget(button, i // 3, i % 3)

        reload_button = QPushButton('Reload AppLauncher')
        reload_button.clicked.connect(self.update_ui)
        add_button = QPushButton('Add App')
        add_button.clicked.connect(self.add_app_dialog)

        self.home_layout.addWidget(reload_button, len(self.apps) // 3 + 1, 0, 1, 3)  # Span through all columns
        self.home_layout.addWidget(add_button, len(self.apps) // 3 + 2, 0, 1, 3)  # Span through all columns


    def update_app_selector(self):
        self.app_selector.clear()
        for app in self.apps:
            self.app_selector.addItem(app.name, app)

    def edit_app(self):
        app = self.app_selector.currentData()
        if app:
            app.name = self.edit_name.text()
            app.path = self.edit_path.text()
            app.icon_path = self.edit_icon_path.text()
            self.save_apps()
            self.update_ui()
            self.update_app_selector()

    def delete_app(self):
        app = self.app_selector.currentData()
        if app and QMessageBox.question(self, "Delete App", "Are you sure you want to delete this app?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.apps.remove(app)
            self.save_apps()
            self.update_ui()
            self.update_app_selector()

    def add_app_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add App")

        layout = QVBoxLayout()
        name_label = QLabel("App Name:")
        layout.addWidget(name_label)

        name_edit = QLineEdit()
        layout.addWidget(name_edit)

        path_label = QLabel("App Path:")
        layout.addWidget(path_label)

        path_edit = QLineEdit()
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(lambda: path_edit.setText(QFileDialog.getOpenFileName()[0]))
        layout.addWidget(path_edit)
        layout.addWidget(browse_button)

        icon_path_label = QLabel("Icon Path (optional):")
        layout.addWidget(icon_path_label)

        icon_path_edit = QLineEdit()
        browse_icon_button = QPushButton("Browse")
        browse_icon_button.clicked.connect(lambda: icon_path_edit.setText(QFileDialog.getOpenFileName()[0]))
        layout.addWidget(icon_path_edit)
        layout.addWidget(browse_icon_button)

        add_button = QPushButton("Add App")
        add_button.clicked.connect(lambda: self.add_app(name_edit.text(), path_edit.text(), icon_path_edit.text()))
        layout.addWidget(add_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def add_app(self, name, path, icon_path=""):
        if not name or not path:
            QMessageBox.critical(self, "Error", "Name and Path are required!")
            return

        if not os.path.exists(path):
            QMessageBox.critical(self, "Error", "Provided path does not exist!")
            return

        new_app = App(name, path, icon_path)
        self.apps.append(new_app)
        self.update_ui()
        self.save_apps()
        self.update_app_selector()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AppLauncher()
    ex.show()
    sys.exit(app.exec_())

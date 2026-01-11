import sys
import json
import random
import os
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QDialog, QVBoxLayout, 
                               QLabel, QPushButton, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon

def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)

# --- Constants ---
JSON_FILE = "orders.json"

# --- The "Card" Pop-up Window ---
class OrderCard(QDialog):
    def __init__(self, order_text):
        super().__init__()
        self.setWindowTitle("New Order Received")
        self.setFixedSize(400, 500)
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        # Apply "Card" Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                border: 2px solid #FFFFFF; /* Gold border */
                border-radius: 15px;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Footlight MT';
            }
            QPushButton {
                background-color: rgb(13, 13, 13);
                color: #FFFFFF;
                border: 1px solid rgb(31, 31, 31);
                padding: 8px;
                border-radius: 5px;
                font-size: 20px;
                font-family: 'Footlight MT';
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("【 ORDER ARRIVED 】")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 30px; color: #FFFFFF; font-family: 'Footlight MT'")
        layout.addWidget(title)

        # The Order Text
        self.lbl_order = QLabel(order_text)
        self.lbl_order.setAlignment(Qt.AlignCenter)
        self.lbl_order.setWordWrap(True)
        self.lbl_order.setStyleSheet("font-size: 28px; padding: 20px;")
        layout.addWidget(self.lbl_order)

        # Close Button
        btn_close = QPushButton("Acknowledge")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.accept) # Closes the window
        layout.addWidget(btn_close)

# --- The Main App ---
class IndexOrderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load UI
        loader = QUiLoader()

        self.ui = loader.load(resource_path("app_ui.ui"), None)
        self.ui.setWindowIcon(QIcon(resource_path("indexorderico.png")))
        self.ui.show()

        self.ui.tabWidget.setCurrentIndex(0)

        # Connect Tab 1 (Home) Buttons
        self.ui.btn_generate.clicked.connect(self.generate_random_order)

        # Connect Tab 2 (Orders) Buttons
        self.ui.btn_add.clicked.connect(self.add_order)
        self.ui.btn_delete.clicked.connect(self.delete_order)

        # Initial Load
        self.orders = []
        self.load_orders()

    def load_orders(self):
        """Loads orders from JSON into the list widget and memory."""
        self.ui.list_orders.clear()
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r") as f:
                try:
                    self.orders = json.load(f)
                except json.JSONDecodeError:
                    self.orders = []
        
        # Add to the List Widget in Tab 2
        for order in self.orders:
            self.ui.list_orders.addItem(order)

    def save_orders(self):
        """Saves current memory list to JSON."""
        with open(JSON_FILE, "w") as f:
            json.dump(self.orders, f, indent=4)

    def add_order(self):
        """Adds text from input box to the list."""
        text = self.ui.input_new_order.text().strip()
        if text:
            self.orders.append(text)
            self.ui.list_orders.addItem(text)
            self.ui.input_new_order.clear()
            self.save_orders()

    def delete_order(self):
        """Deletes the selected item from the list."""
        selected_items = self.ui.list_orders.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            # Remove from Memory
            self.orders.remove(item.text())
            # Remove from UI
            self.ui.list_orders.takeItem(self.ui.list_orders.row(item))
        
        self.save_orders()

    def generate_random_order(self):
        """Picks a random order and shows the Card Window."""
        if not self.orders:
            QMessageBox.warning(self.ui, "Empty Deck", "There are no orders in the list!\nGo to the Orders tab to add some.")
            return

        # 1. Pick Random
        chosen_order = random.choice(self.orders)

        # 2. Show Custom Card Window
        card_window = OrderCard(chosen_order)
        card_window.exec()  # .exec() pauses the main app until card is closed

if __name__ == "__main__":
    myappid = 'dnd.indexorders.app.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)

    icon_path = resource_path("indexorderico.png")
    app.setWindowIcon(QIcon(icon_path))

    window = IndexOrderApp()
    sys.exit(app.exec())
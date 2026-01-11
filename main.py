import sys
import json
import random
import os
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QDialog, QVBoxLayout, 
                               QLabel, QPushButton, QMessageBox, QListWidgetItem) # <--- Added QListWidgetItem
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
                border: 2px solid #FFFFFF; 
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
        btn_close.clicked.connect(self.accept) 
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
        self.orders = {"combat": [], "narrative": []}
        self.load_orders()

    def load_orders(self):
        """Loads orders and safely converts old lists to the new dictionary format."""
        self.ui.list_orders.clear()
        
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r") as f:
                try:
                    loaded_data = json.load(f)
                    
                    if isinstance(loaded_data, list):
                        # MIGRATION: Old list detected
                        self.orders["narrative"] = loaded_data
                        self.orders["combat"] = []
                        self.save_orders() 
                    elif isinstance(loaded_data, dict):
                        # Correct format detected
                        self.orders = loaded_data
                        
                except json.JSONDecodeError:
                    pass
        
        # Populate List
        if "combat" in self.orders:
            for text in self.orders["combat"]:
                self.add_item_to_list(text, "combat")
            
        if "narrative" in self.orders:
            for text in self.orders["narrative"]:
                self.add_item_to_list(text, "narrative")

    def save_orders(self):
        """Saves current memory list to JSON."""
        with open(JSON_FILE, "w") as f:
            json.dump(self.orders, f, indent=4)

    # --- LOVELY HELPER FUNCTION RESTORED ---
    def add_item_to_list(self, text, category):
        """Creates a list item with a visual tag and hidden data for logic."""
        # Visual Tag
        if category == "combat":
            display_text = f"[COMBAT] {text}"
        else:
            display_text = f"[STORY] {text}"
        
        item = QListWidgetItem(display_text)
        
        # HIDDEN DATA (Crucial for Deleting!)
        # We store the original text and category inside the item itself
        item.setData(Qt.UserRole, {"text": text, "category": category})
        
        self.ui.list_orders.addItem(item)

    def add_order(self):
        """Adds text from input box to the selected category."""
        text = self.ui.input_new_order.text().strip()
        if not text:
            return

        # Get Category from Dropdown
        category_text = self.ui.combo_add_mode.currentText().lower() 
        
        # Add to memory
        if category_text not in self.orders:
            self.orders[category_text] = []
        self.orders[category_text].append(text)
        
        # Add to UI
        self.add_item_to_list(text, category_text)
        
        # Clear and Save
        self.ui.input_new_order.clear()
        self.save_orders()

    def delete_order(self):
        """Deletes the selected item using Hidden Data."""
        selected_items = self.ui.list_orders.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            # 1. Retrieve the hidden data
            data = item.data(Qt.UserRole)
            
            # If for some reason data is missing (old items), skip
            if not data:
                continue

            real_text = data["text"]
            category = data["category"]

            # 2. Remove from the Dictionary (Memory)
            if category in self.orders and real_text in self.orders[category]:
                self.orders[category].remove(real_text)
            
            # 3. Remove from UI
            self.ui.list_orders.takeItem(self.ui.list_orders.row(item))
        
        self.save_orders()

    def generate_random_order(self):
        """Picks a random order based on dropdown selection."""
        
        mode = self.ui.combo_gen_mode.currentText() # "Any", "Combat", "Narrative"
        
        pool = []
        
        if mode == "Any":
            pool.extend(self.orders.get("combat", []))
            pool.extend(self.orders.get("narrative", []))
            
        elif mode == "Combat":
            pool.extend(self.orders.get("combat", []))
            
        elif mode == "Narrative":
            pool.extend(self.orders.get("narrative", []))

        if not pool:
            QMessageBox.warning(self.ui, "Empty Deck", f"No {mode} cards found!\nGo to the Prescripts tab and add some.")
            return

        chosen_order = random.choice(pool)
        card_window = OrderCard(chosen_order)
        card_window.exec()

if __name__ == "__main__":
    myappid = 'dnd.indexorders.app.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)

    icon_path = resource_path("indexorderico.png")
    app.setWindowIcon(QIcon(icon_path))

    window = IndexOrderApp()
    sys.exit(app.exec())
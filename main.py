import sys
import json
import random
import os
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QDialog, QVBoxLayout, 
                               QLabel, QPushButton, QMessageBox, QListWidgetItem,
                               QListView)
from PySide6.QtCore import Qt, QObject, QEvent
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# --- HELPER CLASS: DRAG FILTER ---
class DragFilter(QObject):
    def __init__(self, target_window):
        super().__init__()
        self.target = target_window
        self.drag_start_pos = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                # Only allow drag if clicking the TOP area (Header) suggests < 60px
                if event.pos().y() < 60: 
                    self.drag_start_pos = event.globalPosition().toPoint() - self.target.frameGeometry().topLeft()
                    return False 
        elif event.type() == QEvent.MouseMove:
            if self.drag_start_pos and event.buttons() == Qt.LeftButton:
                self.target.move(event.globalPosition().toPoint() - self.drag_start_pos)
                return True
        elif event.type() == QEvent.MouseButtonRelease:
            self.drag_start_pos = None
        return False

# --- Constants ---
JSON_FILE = "orders.json"

# --- The "Card" Pop-up Window ---
class OrderCard(QDialog):
    def __init__(self, order_text):
        super().__init__()
        self.setWindowTitle("New Order Received")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                border: 2px solid #FFFFFF; 
                border-radius: 20px; /* All corners rounded for the card */
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
                background-color: #ffffff;
                color: #000000;
            }
        """)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("【 ORDER ARRIVED 】")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 30px; color: #FFFFFF; font-family: 'Footlight MT'; border: none;")
        layout.addWidget(title)

        self.lbl_order = QLabel(order_text)
        self.lbl_order.setAlignment(Qt.AlignCenter)
        self.lbl_order.setWordWrap(True)
        self.lbl_order.setStyleSheet("font-size: 28px; padding: 20px; border: none;")
        layout.addWidget(self.lbl_order)

        btn_close = QPushButton("Acknowledge")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.accept) 
        layout.addWidget(btn_close)

# --- The Main App ---
class IndexOrderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        loader = QUiLoader()
        self.ui = loader.load(resource_path("app_ui.ui"), None)
        self.ui.setWindowIcon(QIcon(resource_path("indexorderico.png")))
        
        # --- 1. FRAMELESS & SHAPE SETUP ---
        self.ui.setWindowFlags(Qt.FramelessWindowHint)
        # Turn translucency back ON so the square corners are invisible
        self.ui.setAttribute(Qt.WA_TranslucentBackground)

        # --- 2. INSTALL DRAG FILTER ---
        self.drag_filter = DragFilter(self.ui)
        self.ui.tabWidget.installEventFilter(self.drag_filter)
        self.ui.tabWidget.tabBar().installEventFilter(self.drag_filter)

        # --- 3. CUSTOM CLOSE BUTTON ---
        self.btn_close_app = QPushButton("✕")
        self.btn_close_app.setFixedSize(40, 30)
        self.btn_close_app.setCursor(Qt.PointingHandCursor)
        self.btn_close_app.clicked.connect(self.ui.close)
        
        self.btn_close_app.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888; font-weight: bold; font-size: 16px; border: none;
                 /* Adjust padding to fit the rounded top-right corner nicer */
                padding-right: 10px;
            }
            QPushButton:hover { color: white; }
        """)
        
        self.ui.tabWidget.setCornerWidget(self.btn_close_app, Qt.TopRightCorner)

        # --- 4. UI SETUP ---
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.btn_generate.clicked.connect(self.generate_random_order)
        self.ui.btn_add.clicked.connect(self.add_order)
        self.ui.btn_delete.clicked.connect(self.delete_order)

        # List Widget Fixes
        self.ui.list_orders.setWordWrap(True)
        self.ui.list_orders.setWrapping(False)
        self.ui.list_orders.setResizeMode(QListView.Adjust)

        # --- 5. DATA LOAD ---
        self.orders = {"combat": [], "narrative": []}
        self.load_orders()
        
        self.ui.show()

    # --- DATA LOGIC ---
    def load_orders(self):
        self.ui.list_orders.clear()
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r") as f:
                try:
                    loaded_data = json.load(f)
                    if isinstance(loaded_data, list):
                        self.orders["narrative"] = loaded_data
                        self.orders["combat"] = []
                        self.save_orders() 
                    elif isinstance(loaded_data, dict):
                        self.orders = loaded_data
                except json.JSONDecodeError: pass
        
        if "combat" in self.orders:
            for text in self.orders["combat"]: self.add_item_to_list(text, "combat")
        if "narrative" in self.orders:
            for text in self.orders["narrative"]: self.add_item_to_list(text, "narrative")

    def save_orders(self):
        with open(JSON_FILE, "w") as f: json.dump(self.orders, f, indent=4)

    def add_item_to_list(self, text, category):
        prefix = "[COMBAT]" if category == "combat" else "[STORY]"
        item = QListWidgetItem(f"{prefix} {text}")
        item.setData(Qt.UserRole, {"text": text, "category": category})
        self.ui.list_orders.addItem(item)

    def add_order(self):
        text = self.ui.input_new_order.text().strip()
        if not text: return
        category_text = self.ui.combo_add_mode.currentText().lower() 
        if category_text not in self.orders: self.orders[category_text] = []
        self.orders[category_text].append(text)
        self.add_item_to_list(text, category_text)
        self.ui.input_new_order.clear()
        self.save_orders()

    def delete_order(self):
        selected_items = self.ui.list_orders.selectedItems()
        if not selected_items: return
        for item in selected_items:
            data = item.data(Qt.UserRole)
            if not data: continue
            if data["text"] in self.orders.get(data["category"], []):
                self.orders[data["category"]].remove(data["text"])
            self.ui.list_orders.takeItem(self.ui.list_orders.row(item))
        self.save_orders()

    def generate_random_order(self):
        mode = self.ui.combo_gen_mode.currentText()
        pool = []
        if mode == "Any":
            pool.extend(self.orders.get("combat", []))
            pool.extend(self.orders.get("narrative", []))
        elif mode == "Combat": pool.extend(self.orders.get("combat", []))
        elif mode == "Narrative": pool.extend(self.orders.get("narrative", []))

        if not pool:
            QMessageBox.warning(self.ui, "Empty Deck", f"No {mode} cards found!")
            return
        OrderCard(random.choice(pool)).exec()

if __name__ == "__main__":
    myappid = 'dnd.indexorders.app.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("indexorderico.png")))
    window = IndexOrderApp()
    sys.exit(app.exec())
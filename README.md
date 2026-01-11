# 【 Index Order 】 Application

## Overview
Index Order is a desktop application developed using Python and PySide6 (Qt). It functions as a randomized generator and management tool for "Prescripts" (Orders), designed for tabletop narrative or combat scenarios. The application features a custom, frameless user interface with persistent JSON data storage.

## Features

### Core Functionality
* **Random Generation:** Generates random orders based on user-selected categories (Combat, Narrative, or Any).
* **Data Management:** Provides a CRUD (Create, Read, Update, Delete) interface to manage the database of orders.
* **Persistence:** Automatically saves and loads data using a local `orders.json` file.
* **Categorization:** distinct handling for separate data pools ("Combat" vs. "Narrative").

### User Interface
* **Frameless Design:** Custom window rendering.
* **Custom Window Controls:** Implements a custom drag-and-drop event filter for window movement and a custom close button.
* **Theming:** High-contrast dark mode styling using embedded CSS stylesheets and "Footlight MT" typography.
* **Modal Notifications:** Custom "Order Card" popup dialogs for displaying generated results.

## Technical Architecture

### Tech Stack
* **Language:** Python 3.x
* **GUI Framework:** PySide6 (Qt for Python)
* **UI Loading:** Uses `QUiLoader` to dynamically load the interface from an external `app_ui.ui` file.
* **Windows Integration:** Uses `ctypes` to set the App User Model ID for correct taskbar icon grouping on Windows.

### Key Components
* **`IndexOrderApp` (Main Class):** Handles the main window logic, UI initialization, and event connections.
* **`DragFilter`:** A custom `QObject` event filter that overrides mouse events to allow dragging a frameless window via the header area.
* **`OrderCard`:** A custom `QDialog` class that renders the generated order in a stylized modal window.
* **`resource_path`:** A utility function ensuring asset path resolution works in both development environments and PyInstaller frozen executables (`sys._MEIPASS`).

## Prerequisites

* Python 3.8+
* PySide6

## Installation and Usage

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install Dependencies**
    ```bash
    pip install PySide6
    ```

3.  **Project Structure**
    Ensure the following files are in the root directory:
    * `main.py` (The application logic)
    * `app_ui.ui` (The XML interface definition)
    * `indexorderico.png` (Application icon)

4.  **Run the Application**
    ```bash
    python main.py
    ```

## Data Structure
The application generates an `orders.json` file in the root directory upon the first save operation. The structure is as follows:

```json
{
    "combat": [
        "Order text 1",
        "Order text 2"
    ],
    "narrative": [
        "Order text 3",
        "Order text 4"
    ]
}
```
## Compilation
This application is compatible with PyInstaller. The `resource_path` function is pre-configured to handle relative paths within a bundled executable.
```
pyinstaller --noconsole --onefile --add-data "app_ui.ui;." --add-data "indexorderico.png;." main.py
```

## License
---

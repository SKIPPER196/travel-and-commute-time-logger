# Travel & Commute Time Logger

---

## Proponent

**Ymman Neil P. Geolamen** – BSCS

---

## Project Overview

The Travel & Commute Time Logger is a desktop application designed to help users track and analyze their travel and commute times. It allows users to log journeys with details such as origin, destination, transportation mode, and timestamps. The application calculates total and average duration times, providing valuable insights for time management and travel planning. Developed using Python with PyQt6 for the GUI and SQLite for data storage, this tool is useful for commuters, frequent travelers, and anyone interested in monitoring their travel patterns.

---

## Features

- **Create, rename, and delete log tables** for organizing different types of travels
- **Add, edit, and delete travel logs** with comprehensive details
- **Automatic duration calculation** between start and end times
- **Total and average duration statistics** for all logs in a table
- **Sortable table view** with formatted date/time display
- **Multiple transportation modes** with custom "Other" option
- **Data validation** with user-friendly error messages
- **Persistent data storage** using SQLite database
- **Real-time input validation** for date/time consistency
- **Smart time adjustment** to prevent invalid time ranges
- **Double-click to edit** functionality for quick log modifications

---

## Code Design and Structure

The project follows a modular structure with clear separation of concerns:

- **`app/main.py`** – Application entry point that initializes and runs the GUI
- **`app/shell/main_window.py`** – Contains the main application window and core functionality
- **`app/core/db.py`** – Database management module handling all SQLite operations
- **`app/core/styles.qss`** – Qt Stylesheet for application theming
- **`app/core/database.db`** – SQLite database file (auto-generated)

---

## Screenshots

### Main Interface
[![Main Window](https://i.postimg.cc/W4gBKxYK/Main-Window.png)](https://postimg.cc/8FkXfXSB)

### Add Log Dialog
[![Adding Log](https://i.postimg.cc/TwQ4vxVK/Adding-Log.png)](https://postimg.cc/zbbjT9PN)

### Statistics Display
[![Statistics Display](https://i.postimg.cc/HsrPRfVS/Statistics-Display.png)](https://postimg.cc/F7QZJCbc)

---

## How to Run the Program

### Prerequisites
- Python 3.7 or higher
- PyQt6 library

### Installation Steps

1. **Install Python 3.x** from [python.org](https://python.org) if not already installed

2. **Install required dependencies**:
   ```bash
   pip install PyQt6
   ```

3. **Download the project files** and navigate to the project directory in your terminal/command prompt:
   ```bash
   cd path/to/travel-and-commute-time-logger-main
   ```

4. **Run the application**:
   ```bash
   python app/main.py
   ```

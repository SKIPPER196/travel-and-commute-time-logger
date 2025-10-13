import os
import sqlite3
from typing import List, Tuple, Optional

# Database file path setup
db_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(db_dir, "database.db")
conn = sqlite3.connect(db_path, check_same_thread=False)

def init_table():
    # Initialize database table for travel logs
    stmt = """CREATE TABLE IF NOT EXISTS log(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        origin TEXT NOT NULL, 
        destination TEXT NOT NULL, 
        mode TEXT NOT NULL, 
        start TEXT NOT NULL, 
        end TEXT NOT NULL, 
        description TEXT DEFAULT ''
    )"""
    conn.execute(stmt)
    conn.commit()

init_table()

def get_all_logs() -> List[Tuple]:
    # Retrieve all travel logs ordered by ID
    stmt = "SELECT * FROM log ORDER BY id"
    rows = conn.execute(stmt).fetchall()
    return rows

def get_log(log_id: int) -> Optional[Tuple]:
    # Retrieve specific log by ID, returns None if not found
    stmt = "SELECT * FROM log WHERE id=?"
    row = conn.execute(stmt, (log_id,)).fetchone()
    return row

def create_log(origin: str, destination: str, mode: str, start: str, end: str, description: str = "") -> int:
    # Create new travel log and return generated ID
    # Validate required fields
    if not origin:
        raise ValueError("Origin is required")
    if not destination:
        raise ValueError("Destination is required")
    if not mode:
        raise ValueError("Mode is required")
    if not start:
        raise ValueError("Start is required")
    if not end:
        raise ValueError("End is required")
    
    # Insert new record
    stmt = "INSERT INTO log(origin, destination, mode, start, end, description) VALUES (?, ?, ?, ?, ?, ?)"
    cursor = conn.execute(stmt, (origin, destination, mode, start, end, description))
    conn.commit()
    return cursor.lastrowid

def update_log(log_id: int, origin: str, destination: str, mode: str, start: str, end: str, description: str = ""):
    # Update existing travel log
    # Validate required fields
    if not origin:
        raise ValueError("Origin is required")
    if not destination:
        raise ValueError("Destination is required")
    if not mode:
        raise ValueError("Mode is required")
    if not start:
        raise ValueError("Start is required")
    if not end:
        raise ValueError("End is required")
    
    # Update record
    stmt = "UPDATE log SET origin=?, destination=?, mode=?, start=?, end=?, description=? WHERE id=?"
    conn.execute(stmt, (origin, destination, mode, start, end, description, log_id))
    conn.commit()

def delete_log(log_id: int):
    # Delete specific log by ID
    stmt = "DELETE FROM log WHERE id=?"
    conn.execute(stmt, (log_id,))
    conn.commit()

def clear_all_logs():
    # Delete all logs from database
    stmt = "DELETE FROM log"
    conn.execute(stmt)
    conn.commit()
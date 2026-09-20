# database.py
import sqlite3
from datetime import datetime

DB_PATH = "hostel.db"

def init_db():
    """Создать таблицы, если их нет"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            phone TEXT,
            check_in TEXT,
            check_out TEXT,
            room_type TEXT,
            guests INTEGER,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_available_beds(check_in: str, check_out: str) -> int:
    """Сколько свободных мест в дорме на указанные даты."""
    total_beds = 8
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(guests) FROM bookings
        WHERE room_type = 'dorm'
        AND NOT (check_out <= ? OR check_in >= ?)
    """, (check_in, check_out))
    booked = cursor.fetchone()[0] or 0
    conn.close()
    return total_beds - booked

def get_available_private(check_in: str, check_out: str) -> int:
    """Сколько свободных приватных комнат на указанные даты."""
    total_rooms = 2
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM bookings
        WHERE room_type = 'private'
        AND NOT (check_out <= ? OR check_in >= ?)
    """, (check_in, check_out))
    booked = cursor.fetchone()[0] or 0
    conn.close()
    return total_rooms - booked

def save_booking(user_id, name, phone, check_in, check_out, room_type, guests):
    """Сохранить бронь в базу"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bookings (user_id, name, phone, check_in, check_out, room_type, guests, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, phone, check_in, check_out, room_type, guests, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_bookings():
    """Получить все брони (для админа)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings ORDER BY check_in")
    rows = cursor.fetchall()
    conn.close()
    return rows
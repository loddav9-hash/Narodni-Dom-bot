# database.py
import sqlite3
from datetime import datetime

DB_NAME = "hostel.db"

def init_db():
    """Создание таблиц, если их нет"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица бронирований
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            full_name TEXT,
            phone TEXT,
            language TEXT,
            room_type TEXT,
            check_in DATE,
            check_out DATE,
            guests INTEGER,
            total_price REAL,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Таблица для хранения языка пользователя
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_language (
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'ru'
        )
    """)
    
    conn.commit()
    conn.close()

def save_booking(data: dict):
    """Сохранить бронирование"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bookings (user_id, username, full_name, phone, language, 
                             room_type, check_in, check_out, guests, total_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('user_id'),
        data.get('username'),
        data.get('full_name'),
        data.get('phone'),
        data.get('language'),
        data.get('room_type'),
        data.get('check_in'),
        data.get('check_out'),
        data.get('guests'),
        data.get('total_price')
    ))
    conn.commit()
    booking_id = cursor.lastrowid
    conn.close()
    return booking_id

def get_user_language(user_id: int) -> str:
    """Получить язык пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM user_language WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'ru'

def set_user_language(user_id: int, language: str):
    """Сохранить язык пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_language (user_id, language) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET language = ?
    """, (user_id, language, language))
    conn.commit()
    conn.close()

def get_all_bookings():
    """Получить все брони (для админа)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings ORDER BY created_at DESC")
    bookings = cursor.fetchall()
    conn.close()
    return bookings
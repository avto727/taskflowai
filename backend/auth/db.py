"""
База данных для хранения токенов пользователей
"""
import sqlite3
import os
from typing import Optional

DB_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'users.db'
)

def init_db():
    """Инициализация БД"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            todoist_token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_token(telegram_id: int, todoist_token: str):
    """Сохранить токен пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO users (telegram_id, todoist_token)
        VALUES (?, ?)
    ''', (telegram_id, todoist_token))
    
    conn.commit()
    conn.close()

def get_token(telegram_id: int) -> Optional[str]:
    """Получить токен пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT todoist_token FROM users WHERE telegram_id = ?',
        (telegram_id,)
    )
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def delete_token(telegram_id: int):
    """Удалить токен пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'DELETE FROM users WHERE telegram_id = ?',
        (telegram_id,)
    )
    
    conn.commit()
    conn.close()

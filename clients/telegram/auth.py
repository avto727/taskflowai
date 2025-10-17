"""
Simple auth system for MCP bot
"""

import os
import json

AUTH_FILE = "telegram_users.json"


def load_users():
    """Load users from file"""
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_users(users):
    """Save users to file"""
    with open(AUTH_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def save_token(telegram_id: int, token: str):
    """Save user token"""
    users = load_users()
    users[str(telegram_id)] = token
    save_users(users)


def get_token(telegram_id: int) -> str:
    """Get user token"""
    users = load_users()
    return users.get(str(telegram_id))


def delete_token(telegram_id: int):
    """Delete user token"""
    users = load_users()
    if str(telegram_id) in users:
        del users[str(telegram_id)]
        save_users(users)


def init_db():
    """Initialize auth system"""
    pass  # No initialization needed for JSON file
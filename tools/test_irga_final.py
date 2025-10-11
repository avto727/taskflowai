#!/usr/bin/env python3
"""Финальный автотест команд Ирги"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def to_telegram(message):
    """Отправить сообщение боту"""
    bot_token = os.getenv("bot_token_helper")
    chat_id = os.getenv("my_tg_id_1")
    params = {"chat_id": chat_id, "text": message}
    r = requests.get(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        params=params
    )
    return r.status_code == 200

def main():
    tests = [
        'Ирга, привет!',
        'Ирга, помоги',
        'Ирга, покажи задачи',
    ]
    
    print("🚀 Автотесты команд Ирги\n")
    
    for cmd in tests:
        print(f"📤 {cmd}")
        if to_telegram(cmd):
            print("   ✅ Отправлено\n")
        else:
            print("   ❌ Ошибка\n")
    
    print("✅ Проверьте ответы в Telegram!")

if __name__ == '__main__':
    main()

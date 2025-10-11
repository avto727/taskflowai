#!/usr/bin/env python3
"""Простые автотесты - отправка команд и инструкция по проверке"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TEST_BOT_TOKEN = os.getenv('TEST_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_TEST_CHAT_ID')

def send_test_message(text):
    """Отправить от тестового бота"""
    url = f'https://api.telegram.org/bot{TEST_BOT_TOKEN}/sendMessage'
    r = requests.post(url, json={'chat_id': CHAT_ID, 'text': text})
    return r.json().get('ok', False)

def main():
    """Запуск тестов"""
    tests = [
        'Ирга, привет!',
        'Ирга, помоги',
        'Ирга, покажи задачи',
        'Ирга, план на сегодня',
        'Ирга, что по здоровью?',
    ]
    
    print("🚀 Автотесты команд Ирги\n")
    print("📋 Будут отправлены команды от @woodnote_bot")
    print("✅ Проверьте ответы основного бота вручную\n")
    
    input("Нажмите Enter для начала тестов...")
    
    for i, cmd in enumerate(tests, 1):
        print(f"\n{i}. Отправка: {cmd}")
        if send_test_message(cmd):
            print("   ✅ Отправлено")
        else:
            print("   ❌ Ошибка")
    
    print("\n" + "="*50)
    print("✅ Все команды отправлены!")
    print("📱 Проверьте Telegram - должны быть ответы от бота")
    print("="*50)

if __name__ == '__main__':
    main()

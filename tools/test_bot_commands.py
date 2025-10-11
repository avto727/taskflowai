#!/usr/bin/env python3
"""Автотесты команд Ирги через Telegram API"""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_TEST_CHAT_ID')
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

def send_message(text):
    """Отправить сообщение боту"""
    response = requests.post(
        f'{BASE_URL}/sendMessage',
        json={'chat_id': CHAT_ID, 'text': text}
    )
    return response.json()

def get_updates(offset=None):
    """Получить обновления"""
    params = {'offset': offset} if offset else {}
    response = requests.get(f'{BASE_URL}/getUpdates', params=params)
    return response.json()

def test_irga_commands():
    """Тестировать команды Ирги"""
    commands = [
        'Ирга, привет!',
        'Ирга, помоги',
        'Ирга, покажи задачи',
    ]
    
    print("🚀 Запуск тестов команд Ирги\n")
    
    for cmd in commands:
        print(f"📤 Отправка: {cmd}")
        result = send_message(cmd)
        if result.get('ok'):
            print(f"✅ Отправлено (msg_id: {result['result']['message_id']})")
        else:
            print(f"❌ Ошибка: {result}")
        time.sleep(1)
    
    print("\n⏳ Ждём 3 секунды ответов бота...")
    time.sleep(3)
    
    print("\n📥 Проверка ответов:")
    updates = get_updates()
    if updates.get('ok'):
        messages = updates.get('result', [])
        print(f"Получено сообщений: {len(messages)}")
        for msg in messages[-5:]:
            text = msg.get('message', {}).get('text', '')
            print(f"  - {text[:50]}...")
    
    print("\n✅ Тесты завершены!")

if __name__ == '__main__':
    test_irga_commands()

#!/usr/bin/env python3
"""Автотесты команд Ирги через тестового бота"""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TEST_BOT_TOKEN = os.getenv('TEST_BOT_TOKEN')
MAIN_BOT_USERNAME = 'sdet_727_bot'  # Ваш основной бот
CHAT_ID = os.getenv('TELEGRAM_TEST_CHAT_ID')

def send_from_test_bot(text):
    """Отправить сообщение от тестового бота"""
    url = f'https://api.telegram.org/bot{TEST_BOT_TOKEN}/sendMessage'
    response = requests.post(url, json={'chat_id': CHAT_ID, 'text': text})
    return response.json()

def get_updates_test_bot(offset=None):
    """Получить обновления тестового бота"""
    url = f'https://api.telegram.org/bot{TEST_BOT_TOKEN}/getUpdates'
    params = {'offset': offset, 'timeout': 5} if offset else {'timeout': 5}
    response = requests.get(url, params=params)
    return response.json()

def test_irga():
    """Тестировать команды Ирги"""
    tests = [
        ('Ирга, привет!', 'Привет'),
        ('Ирга, помоги', 'команд'),
        ('Ирга, покажи задачи', 'задач'),
    ]
    
    print("🚀 Автотесты команд Ирги\n")
    
    for cmd, expected in tests:
        print(f"📤 Команда: {cmd}")
        result = send_from_test_bot(cmd)
        
        if not result.get('ok'):
            print(f"❌ Ошибка отправки: {result}")
            continue
        
        print(f"✅ Отправлено")
        time.sleep(2)
        
        # Проверяем ответ
        updates = get_updates_test_bot()
        if updates.get('ok') and updates.get('result'):
            last_msg = updates['result'][-1].get('message', {})
            text = last_msg.get('text', '')
            
            if expected.lower() in text.lower():
                print(f"✅ Тест пройден: '{expected}' найдено в ответе\n")
            else:
                print(f"⚠️  Ответ: {text[:100]}\n")
        else:
            print(f"⚠️  Нет ответа\n")
        
        time.sleep(1)
    
    print("✅ Все тесты завершены!")

if __name__ == '__main__':
    test_irga()

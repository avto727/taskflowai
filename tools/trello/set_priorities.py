#!/usr/bin/env python3
"""Установить приоритеты для эпиков в Бэклоге"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('TRELLO_API_KEY')
token = os.getenv('TRELLO_TOKEN')
board_id = os.getenv('TRELLO_BOARD_ID')

# Получить карточки
url = f'https://api.trello.com/1/boards/{board_id}/cards'
params = {'key': api_key, 'token': token}
cards = requests.get(url, params=params).json()

# Приоритеты (порядок выполнения)
priorities = {
    'Б10': '🎯 ПРИОРИТЕТ 1 (после Н1)',
    'Б13': '⭐ ПРИОРИТЕТ 2',
    'Б1': '🌐 ПРИОРИТЕТ 3',
    'Б12': '📊 ПРИОРИТЕТ 4 (с Web App)',
    'Б11': '📍 ПРИОРИТЕТ 5 (эксперимент)'
}

for card in cards:
    for key, priority in priorities.items():
        if key in card['name']:
            # Обновить описание
            current_desc = card.get('desc', '')
            new_desc = f"**{priority}**\n\n{current_desc}"
            
            url = f'https://api.trello.com/1/cards/{card["id"]}'
            data = {
                'desc': new_desc,
                'key': api_key,
                'token': token
            }
            response = requests.put(url, params=data)
            if response.status_code == 200:
                print(f'✅ {card["name"]} → {priority}')
            break

print('\n✅ Приоритеты установлены!')

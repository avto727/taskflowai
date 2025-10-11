#!/usr/bin/env python3
"""Добавить эпик Obsidian в Miro"""
import os
import sys
sys.path.append(os.path.dirname(__file__))
from miro_client import MiroClient

client = MiroClient()
board_id = os.getenv('MIRO_BOARD_ID')

# Получить элементы
items = client.get_items(board_id)
shapes = [i for i in items if i['type'] == 'shape']

# Найти последний эпик в Бэклоге
backlog_epics = [s for s in shapes if 'Б' in s.get('data', 
                 {}).get('content', '')]
if backlog_epics:
    last_epic = max(backlog_epics, 
                    key=lambda x: x['position']['x'])
    x = last_epic['position']['x'] + 300
    y = last_epic['position']['y']
else:
    x = 2000
    y = -1000

# Создать Б19
try:
    shape = client.create_rounded_shape(
        board_id=board_id,
        x=x,
        y=y,
        width=250,
        height=100,
        text='Б19. Obsidian (граф)',
        color='#E6E6FA'
    )
    print(f'✅ Б19. Obsidian добавлен в Miro')
except Exception as e:
    print(f'❌ Ошибка: {e}')

print(f'\nОткройте: https://miro.com/app/board/{board_id}/')

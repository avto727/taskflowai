#!/usr/bin/env python3
"""Добавить недостающие эпики в Бэклог на Miro"""
import os
import sys
sys.path.append(os.path.dirname(__file__))
from miro_client import MiroClient

client = MiroClient()
board_id = os.getenv('MIRO_BOARD_ID')

if not board_id:
    print('❌ MIRO_BOARD_ID не найден в .env')
    exit(1)

print(f'Доска: {board_id}\n')

# Получить существующие элементы
items = client.get_items(board_id)
shapes = [i for i in items if i['type'] == 'shape']

# Найти последний эпик в Бэклоге (по X координате)
backlog_epics = [s for s in shapes if 'Б' in s.get('data', 
                 {}).get('content', '')]
if backlog_epics:
    last_epic = max(backlog_epics, 
                    key=lambda x: x['position']['x'])
    start_x = last_epic['position']['x'] + 300
    start_y = last_epic['position']['y']
else:
    start_x = 2000
    start_y = -1000

print(f'Начальная позиция: x={start_x}, y={start_y}\n')

# Новые эпики
new_epics = [
    'Б10. Приоритеты (1-4)',
    'Б11. Гео-триггеры',
    'Б12. Квадрат Эйзенхауэра',
    'Б13. Три важные задачи',
    'Б14. Система поощрений',
    'Б15. Inbox + Project',
    'Б16. Ритуалы',
    'Б17. Шаблоны'
]

# Создать эпики
for i, epic in enumerate(new_epics):
    x = start_x + (i * 300)
    y = start_y
    
    try:
        shape = client.create_rounded_shape(
            board_id=board_id,
            x=x,
            y=y,
            width=250,
            height=100,
            text=epic,
            color='#E6E6FA'  # Светло-фиолетовый
        )
        print(f'✅ {epic}')
    except Exception as e:
        print(f'❌ {epic}: {e}')

print('\n✅ Все эпики добавлены в Miro!')
print(f'Откройте: https://miro.com/app/board/{board_id}/')

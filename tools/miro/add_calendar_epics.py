#!/usr/bin/env python3
"""Добавить эпики по календарю в Miro"""
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

# Найти последний эпик в Бэклоге
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
    'Б18. Умная работа с календарём'
]

# Н2 добавляем в линию "В процессе" (выше)
n2_y = start_y - 300

# Создать Н2
try:
    shape = client.create_rounded_shape(
        board_id=board_id,
        x=start_x,
        y=n2_y,
        width=250,
        height=100,
        text='Н2. Интеграция с Calendar',
        color='#FFE5B4'  # Персиковый (как Н1)
    )
    print(f'✅ Н2. Интеграция с Calendar (В процессе)')
except Exception as e:
    print(f'❌ Н2: {e}')

# Создать Б18
for i, epic in enumerate(new_epics):
    x = start_x + 300
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
        print(f'✅ {epic} (Бэклог)')
    except Exception as e:
        print(f'❌ {epic}: {e}')

print('\n✅ Эпики по календарю добавлены в Miro!')
print(f'Откройте: https://miro.com/app/board/{board_id}/')

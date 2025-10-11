#!/usr/bin/env python3
"""Перестроить доску Miro по новой структуре"""
import sys
from pathlib import Path
import csv
sys.path.append(str(Path(__file__).parent.parent))

from miro.miro_client import MiroClient
import os

client = MiroClient()
board_id = os.getenv("MIRO_BOARD_ID")

# Удаляем всё
items = client.get_items(board_id)
for item in items:
    client.delete_item(board_id, item['id'])
print("Очистил доску")

# Читаем roadmap
roadmap = Path(__file__).parent.parent.parent / "roadmap.csv"
epics = {}
with open(roadmap, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        epic = row['Этап']
        if epic not in epics:
            epics[epic] = []
        epics[epic].append({
            'name': row['Задача'],
            'done': row['Выполнено'] == '✓'
        })

# Размеры
EW, EH = 243, 150  # эпик
TW, TH = 243, 50   # задача
GAP = 10

# Линия 1: Бэклог (Б1-Б9)
y = 0
backlog = [f"Б{i}. {e.split('.', 1)[1].strip()}" 
           for i, e in enumerate(list(epics.keys())[6:9] + 
           list(epics.keys())[15:], 1)]
for i, name in enumerate(backlog):
    x = i * (EW + GAP)
    client.create_rounded_shape(board_id, x, y, EW, EH, 
                                 name, '#ffffff')
print(f"Бэклог: {len(backlog)} эпиков")

# Линия 2-4: Нужно сделать, В процессе, Тестирование (пусто)
# Пропускаем

# Линия 5: Готово (Г1-Г12) с задачами
y = 1000
done = list(epics.keys())[:6] + list(epics.keys())[9:15]
for i, epic_name in enumerate(done):
    x = i * (EW + GAP)
    name = f"Г{i+1}. {epic_name.split('.', 1)[1].strip()}"
    client.create_rounded_shape(board_id, x, y, EW, EH, 
                                 name, '#d5f692')
    
    # Задачи под эпиком
    tasks = epics[epic_name]
    for j, task in enumerate(tasks):
        ty = y + EH/2 + TH/2 + GAP + j * (TH + GAP)
        color = '#d5f692' if task['done'] else '#ffffff'
        client.create_rounded_shape(board_id, x, ty, TW, TH,
                                     task['name'], color)

print(f"Готово: {len(done)} эпиков с задачами")
print("✅ Доска перестроена")

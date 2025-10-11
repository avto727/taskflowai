#!/usr/bin/env python3
"""Проверить координаты эпика и задач"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from miro.miro_client import MiroClient
import os

client = MiroClient()
board_id = os.getenv("MIRO_BOARD_ID")

items = client.get_items(board_id)
shapes = [i for i in items if i.get('type') == 'shape']

epic1 = None
tasks = []

for s in shapes:
    content = s.get('data', {}).get('content', '')
    y = s.get('position', {}).get('y', 0)
    h = s.get('geometry', {}).get('height', 0)
    
    if '1. Подготовка' in content:
        epic1 = s
        print(f"Эпик: y={y}, h={h}, bottom={y+h/2}")
    elif epic1 and abs(s['position']['x'] - epic1['position']['x']) < 50:
        if y > epic1['position']['y']:
            tasks.append((y, h, content[:40]))

if tasks:
    tasks.sort()
    epic_bottom = epic1['position']['y'] + epic1['geometry']['height']/2
    first_task_top = tasks[0][0] - tasks[0][1]/2
    gap1 = first_task_top - epic_bottom
    
    print(f"\nОтступ эпик→задача: {gap1:.1f}px")
    
    for i in range(len(tasks)-1):
        t1_bottom = tasks[i][0] + tasks[i][1]/2
        t2_top = tasks[i+1][0] - tasks[i+1][1]/2
        gap = t2_top - t1_bottom
        print(f"Отступ задача{i+1}→задача{i+2}: {gap:.1f}px")

#!/usr/bin/env python3
"""
Реорганизация доски Miro:
1. Единый размер шрифта
2. Горизонтальная линия по факту выполнения
3. Стрелки между стикерами
"""
import sys
from pathlib import Path
import csv

sys.path.append(str(Path(__file__).parent.parent))

from miro.miro_client import MiroClient
import os


def get_epic_order():
    """Получить порядок эпиков по номерам"""
    roadmap = Path(__file__).parent.parent.parent / "roadmap.csv"
    
    epics = set()
    with open(roadmap, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            epics.add(row['Этап'])
    
    # Сортируем по номеру в начале названия
    def get_number(epic_name):
        if '. ' in epic_name:
            parts = epic_name.split('. ', 1)
            if parts[0].isdigit():
                return int(parts[0])
        return 999
    
    sorted_epics = sorted(epics, key=get_number)
    return sorted_epics


def reorganize_board():
    """Реорганизовать доску"""
    client = MiroClient()
    board_id = os.getenv("MIRO_BOARD_ID")
    
    # Получаем порядок
    order = get_epic_order()
    print(f"📋 Порядок эпиков ({len(order)}):")
    for i, epic in enumerate(order, 1):
        print(f"  {i}. {epic}")
    
    # Получаем стикеры
    items = client.get_items(board_id, item_type='sticky_note')
    
    # Создаём маппинг стикер → позиция
    sticker_map = {}
    for item in items:
        content = item.get('data', {}).get('content', '')
        for i, epic in enumerate(order):
            # Точное совпадение
            if epic in content or content in epic:
                sticker_map[item['id']] = {
                    'position': i,
                    'epic': epic,
                    'item': item
                }
                break
            # Частичное совпадение по номеру
            if '. ' in epic and '. ' in content:
                epic_num = epic.split('. ', 1)[0]
                content_num = content.split('. ', 1)[0]
                if epic_num == content_num:
                    sticker_map[item['id']] = {
                        'position': i,
                        'epic': epic,
                        'item': item
                    }
                    break
    
    print(f"\n🎯 Найдено стикеров: {len(sticker_map)}")
    
    # Расставляем по горизонтали
    start_x = -3000
    spacing = 400
    y = 0
    
    sorted_stickers = sorted(
        sticker_map.items(),
        key=lambda x: x[1]['position']
    )
    
    print("\n📍 Перемещаю стикеры...")
    for i, (item_id, data) in enumerate(sorted_stickers):
        x = start_x + (i * spacing)
        
        # Обновляем позицию
        client.update_sticky_position(
            board_id,
            item_id,
            x,
            y
        )
        print(f"  {i+1}. {data['epic'][:40]}... → x={x}")
    
    # Создаём стрелки
    print("\n➡️  Создаю стрелки...")
    for i in range(len(sorted_stickers) - 1):
        start_id = sorted_stickers[i][0]
        end_id = sorted_stickers[i + 1][0]
        
        try:
            client.create_connector(board_id, start_id, end_id)
            print(f"  {i+1} → {i+2}")
        except Exception as e:
            print(f"  ⚠️  {i+1} → {i+2}: {e}")
    
    print("\n✅ Готово!")


if __name__ == "__main__":
    reorganize_board()

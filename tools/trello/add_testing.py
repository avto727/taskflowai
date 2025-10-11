#!/usr/bin/env python3
"""Добавить колонку Тестирование между В процессе и Готово"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from trello.trello_client import TrelloClient
import os

client = TrelloClient()
board_id = os.getenv("TRELLO_BOARD_ID")

# Получаем списки
lists = client.get_lists(board_id)
done_list = next((l for l in lists if 'Готово' in l['name']), None)

# Создаём Тестирование перед Готово
testing = client.create_list(
    board_id, "Тестирование", pos=done_list['pos'] - 1
)
print(f"✅ Создана колонка: {testing['name']}")

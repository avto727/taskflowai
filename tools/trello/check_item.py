#!/usr/bin/env python3
"""Отметить пункт чеклиста в Trello"""
import os
from dotenv import load_dotenv
from trello_client import TrelloClient

load_dotenv()

client = TrelloClient(
    os.getenv("TRELLO_API_KEY"),
    os.getenv("TRELLO_TOKEN")
)

board_id = os.getenv("TRELLO_BOARD_ID")
cards = client.get_cards(board_id)

# Найти карточку Н1
card = next((c for c in cards if "Н1" in c["name"]), None)
if not card:
    print("Карточка Н1 не найдена")
    exit(1)

# Получить чеклисты
checklists = client.get_checklists(card["id"])
if not checklists:
    print("Чеклисты не найдены")
    exit(1)

# Найти первый пункт
checklist = checklists[0]
items = checklist["checkItems"]
item = next((i for i in items 
             if "Backend: поддержка parent_id" in i["name"]),
            None)

if item:
    client.check_item(card["id"], checklist["id"], item["id"])
    print(f"✅ Отмечен: {item['name']}")
else:
    print("Пункт не найден")

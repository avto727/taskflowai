#!/usr/bin/env python3
"""
Синхронизация имён эпиков из Trello в roadmap.csv и Miro
"""
import csv
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from trello.trello_client import TrelloClient
from miro.miro_client import MiroClient


def get_trello_epic_names():
    """Получить имена эпиков из Trello"""
    client = TrelloClient()
    board_id = os.getenv("TRELLO_BOARD_ID")

    cards = client.get_cards(board_id)

    # Сортируем по позиции
    cards.sort(key=lambda x: x.get("pos", 0))

    epic_names = {}
    for card in cards:
        name = card["name"]
        # Извлекаем номер эпика (например, "19. ")
        if ". " in name:
            parts = name.split(". ", 1)
            if parts[0].isdigit():
                num = int(parts[0])
                epic_names[num] = name

    return epic_names


def update_roadmap_csv(epic_names):
    """Обновить названия в roadmap.csv"""
    roadmap_path = Path(__file__).parent.parent / "roadmap.csv"

    # Маппинг старых названий на номера эпиков
    mapping = {
        "Подготовка": 1,
        "Этап 1.1: Структура": 2,
        "Этап 1.2: Todoist Integration": 3,
        "Этап 1.3: Irga Layer": 4,
        "Этап 1.4: Backend API": 5,
        "Этап 2: Telegram Bot": 6,
        "Этап 3: Web App": 7,
        "Этап 4: Mobile App": 8,
        "Этап 5: Browser Extension": 9,
        "Авторизация в TaskFlowAI: MVP": 10,
        "Умный чат: Понимание вопросов": 11,
        "Умный чат: Дружелюбность": 12,
        "Умный чат: Контекст": 13,
        "Удаление задач в todoist": 14,
        "Пагинация в чате": 15,
        "Аналитика: Статистика": 16,
        "Аналитика: Паттерны": 17,
        "Аналитика: Советы": 18,
        "Авторизация todoist: OAuth": 19,
        "Монетизация": 20,
        "Маркетинг": 21,
    }

    # Читаем CSV
    rows = []
    with open(roadmap_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            old_stage = row["Этап"]
            # Ищем номер эпика
            for old_name, epic_num in mapping.items():
                if old_stage == old_name:
                    if epic_num in epic_names:
                        row["Этап"] = epic_names[epic_num]
                    break
            rows.append(row)

    # Записываем обратно
    with open(roadmap_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Этап", "Задача", "План", "В процессе", "Выполнено"]
        )
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def update_miro_stickers(epic_names):
    """Обновить названия стикеров в Miro"""
    client = MiroClient()
    board_id = os.getenv("MIRO_BOARD_ID")

    # Получаем все стикеры
    items = client.get_items(board_id, item_type="sticky_note")

    updated = 0
    for item in items:
        content = item.get("data", {}).get("content", "")

        # Проверяем, есть ли номер эпика в начале
        if ". " in content:
            parts = content.split(". ", 1)
            if parts[0].isdigit():
                num = int(parts[0])
                if num in epic_names:
                    new_name = epic_names[num]
                    if content != new_name:
                        client.update_sticky_note(
                            board_id, item["id"], new_name
                        )
                        updated += 1
                        print(f"  {content} → {new_name}")

    return updated


if __name__ == "__main__":
    print("🔄 Синхронизация имён эпиков...")

    # 1. Получаем имена из Trello
    print("\n1️⃣ Читаю эпики из Trello...")
    epic_names = get_trello_epic_names()
    print(f"   Найдено эпиков: {len(epic_names)}")

    # 2. Обновляем roadmap.csv
    print("\n2️⃣ Обновляю roadmap.csv...")
    updated_rows = update_roadmap_csv(epic_names)
    print(f"   Обработано строк: {updated_rows}")

    # 3. Обновляем Miro
    print("\n3️⃣ Обновляю стикеры в Miro...")
    updated_stickers = update_miro_stickers(epic_names)
    print(f"   Обновлено стикеров: {updated_stickers}")

    print("\n✅ Синхронизация завершена!")

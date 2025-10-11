"""
Синхронизация roadmap.csv → Kaiten
"""
import csv
import os
import sys
from kaiten_client import KaitenClient

# Добавляем путь к корню проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

ROADMAP_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'roadmap.csv'
)


def sync_roadmap_to_kaiten():
    """Синхронизировать roadmap.csv в Kaiten"""
    
    client = KaitenClient()
    board_id = int(os.getenv("KAITEN_BOARD_ID"))
    
    # Получаем колонки
    columns = client.get_columns(board_id)
    column_map = {col['title']: col['id'] for col in columns}
    
    # Читаем roadmap
    with open(ROADMAP_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        tasks = list(reader)
    
    print(f"📋 Найдено задач в roadmap: {len(tasks)}")
    
    # Получаем существующие карточки
    existing_cards = client.get_cards(board_id)
    existing_titles = {card['title'] for card in existing_cards}
    
    created = 0
    skipped = 0
    
    for task in tasks:
        title = f"{task['Этап']}: {task['Задача']}"
        
        # Пропускаем если уже есть
        if title in existing_titles:
            skipped += 1
            continue
        
        # Определяем колонку
        if task['Выполнено']:
            column_name = 'Готово'
        elif task['В процессе']:
            column_name = 'В работе'
        else:
            column_name = 'Очередь'
        
        column_id = column_map.get(column_name)
        if not column_id:
            print(f"⚠️ Колонка '{column_name}' не найдена")
            continue
        
        # Создаём карточку
        try:
            client.create_card(
                board_id=board_id,
                column_id=column_id,
                title=title,
                description=f"Этап: {task['Этап']}"
            )
            created += 1
            print(f"✅ Создана: {title}")
        except Exception as e:
            print(f"❌ Ошибка создания '{title}': {e}")
    
    print(f"\n🎉 Синхронизация завершена!")
    print(f"   Создано: {created}")
    print(f"   Пропущено: {skipped}")


if __name__ == "__main__":
    sync_roadmap_to_kaiten()

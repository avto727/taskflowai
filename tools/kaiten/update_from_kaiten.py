"""
Обновление roadmap.csv из Kaiten
"""
import csv
import os
import sys
from kaiten_client import KaitenClient

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

ROADMAP_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'roadmap.csv'
)


def update_roadmap_from_kaiten():
    """Обновить roadmap.csv из Kaiten"""
    
    client = KaitenClient()
    board_id = int(os.getenv("KAITEN_BOARD_ID"))
    
    # Получаем колонки и карточки
    columns = client.get_columns(board_id)
    column_names = {col['id']: col['title'] for col in columns}
    
    cards = client.get_cards(board_id)
    
    print(f"📋 Найдено карточек в Kaiten: {len(cards)}")
    
    # Читаем текущий roadmap
    with open(ROADMAP_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        tasks = list(reader)
    
    updated = 0
    
    for card in cards:
        title = card['title']
        column = column_names.get(card['column_id'], '')
        
        # Ищем задачу в roadmap
        for task in tasks:
            task_title = f"{task['Этап']}: {task['Задача']}"
            
            if task_title == title:
                # Обновляем статус
                old_status = (
                    task['Выполнено'], 
                    task['В процессе']
                )
                
                if column == '✅ Done':
                    task['Выполнено'] = 'TRUE'
                    task['В процессе'] = ''
                elif column == '🔄 In Progress':
                    task['Выполнено'] = ''
                    task['В процессе'] = 'TRUE'
                else:
                    task['Выполнено'] = ''
                    task['В процессе'] = ''
                
                new_status = (
                    task['Выполнено'], 
                    task['В процессе']
                )
                
                if old_status != new_status:
                    updated += 1
                    print(f"✅ Обновлено: {title}")
                
                break
    
    # Сохраняем roadmap
    if updated > 0:
        with open(ROADMAP_PATH, 'w', encoding='utf-8', 
                  newline='') as f:
            fieldnames = tasks[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(tasks)
        
        print(f"\n🎉 Обновлено задач: {updated}")
    else:
        print(f"\n✅ Изменений нет")


if __name__ == "__main__":
    update_roadmap_from_kaiten()

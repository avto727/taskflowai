"""
Синхронизация roadmap.csv → Trello
"""
import csv
import os
import sys
from collections import defaultdict

sys.path.append(os.path.dirname(__file__))
from trello_client import TrelloClient

# Читаем roadmap
roadmap_path = os.path.join(
    os.path.dirname(__file__), '..', '..', 'roadmap.csv'
)
with open(roadmap_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    tasks = list(reader)

# Группируем по этапам
stages = defaultdict(list)
for task in tasks:
    stages[task['Этап']].append(task)

print(f"Этапов: {len(stages)}")
print(f"Задач: {len(tasks)}\n")

client = TrelloClient()
board_id = os.getenv("TRELLO_BOARD_ID")

# Получаем списки (Trello создаёт 3 по умолчанию)
lists = client.get_lists(board_id)
print(f"Списков на доске: {len(lists)}")

# Переименовываем списки
if len(lists) >= 3:
    # To Do → Очередь
    # Doing → В работе  
    # Done → Готово
    pass  # Используем как есть

# Создаём карточки для каждого этапа
created = 0
for stage_name in sorted(stages.keys()):
    stage_tasks = stages[stage_name]
    
    # Определяем список
    all_done = all(t['Выполнено'].strip() == '✓' 
                   for t in stage_tasks)
    in_progress = any(t['В процессе'].strip() == '✓' 
                      for t in stage_tasks)
    
    if all_done:
        list_id = lists[2]['id']  # Done
    elif in_progress:
        list_id = lists[1]['id']  # Doing
    else:
        list_id = lists[0]['id']  # To Do
    
    # Создаём карточку-эпик
    desc = f"**Задач:** {len(stage_tasks)}\n\n"
    desc += "**Чеклист:**\n"
    for task in stage_tasks:
        status = "✅" if task['Выполнено'].strip() == '✓' else "⬜"
        desc += f"{status} {task['Задача']}\n"
    
    card = client.create_card(
        list_id=list_id,
        name=stage_name,
        desc=desc
    )
    created += 1
    print(f"✅ {stage_name}")

print(f"\n✅ Создано карточек: {created}")
print(f"\nОткройте: https://trello.com/b/uCUxLXBA/taskflowai")

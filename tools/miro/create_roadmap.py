"""
Создание roadmap на Miro доске
"""
import csv
import os
import sys
from collections import defaultdict

sys.path.append(os.path.dirname(__file__))
from miro_client import MiroClient

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

# Получаем актуальные названия из Trello
import requests
trello_token = os.getenv("TRELLO_TOKEN")
trello_key = os.getenv("TRELLO_API_KEY")
trello_board = os.getenv("TRELLO_BOARD_ID")

response = requests.get(
    f"https://api.trello.com/1/boards/{trello_board}/cards",
    params={'key': trello_key, 'token': trello_token}
)
trello_cards = {c['name'].split('. ', 1)[1] if '. ' in c['name'] 
                else c['name']: c['name'] 
                for c in response.json()}

client = MiroClient()
board_id = os.getenv("MIRO_BOARD_ID")

print(f"Создаю roadmap на доске {board_id}\n")

# Создаём карточки для каждого этапа
x = 0
y = 0
created = 0

for i, (stage_name, stage_tasks) in enumerate(stages.items(), 1):
    # Используем название из Trello если есть
    display_name = trello_cards.get(stage_name, f"{i}. {stage_name}")
    # Считаем прогресс
    done = sum(1 for t in stage_tasks 
               if t['Выполнено'].strip() == '✓')
    total = len(stage_tasks)
    progress = int(done / total * 100)
    
    # Цвет в зависимости от статуса
    if progress == 100:
        color = "green"  # Зелёный
    elif progress > 0:
        color = "yellow"  # Жёлтый
    else:
        color = "light_yellow"  # Белый (светло-жёлтый)
    
    # Текст карточки
    text = f"{display_name}\n\n"
    text += f"Прогресс: {done}/{total} ({progress}%)"
    
    try:
        sticky = client.create_sticky(
            board_id=board_id,
            x=x,
            y=y,
            text=text,
            color=color
        )
        created += 1
        print(f"✅ {display_name} ({progress}%)")
        
        # Следующая позиция
        x += 350
        if (i % 4) == 0:  # 4 карточки в ряд
            x = 0
            y += 200
            
    except Exception as e:
        print(f"❌ {stage_name}: {e}")

print(f"\n✅ Создано карточек: {created}")
print(f"\nОткройте: https://miro.com/app/board/{board_id}/")

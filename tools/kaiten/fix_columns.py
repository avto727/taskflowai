"""
Перенос выполненных задач в Готово
"""
import requests
import csv
import os
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv("KAITEN_API_TOKEN")
board_id = int(os.getenv("KAITEN_BOARD_ID"))
base_url = "https://avto727a.kaiten.ru/api/latest"
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# Читаем roadmap
roadmap_path = os.path.join(
    os.path.dirname(__file__), '..', '..', 'roadmap.csv'
)
with open(roadmap_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    tasks = list(reader)

# Создаём словарь: название задачи → статус
task_status = {}
for task in tasks:
    task_status[task['Задача']] = task['Выполнено'].strip() == '✓'

print(f"Выполненных задач в roadmap: {sum(task_status.values())}")

# Получаем доску
response = requests.get(
    f"{base_url}/boards/{board_id}", headers=headers
)
board = response.json()
columns = {col['type']: col['id'] for col in board['columns']}
done_column_id = columns[3]  # Готово

# Получаем все карточки
response = requests.get(
    f"{base_url}/cards?board_id={board_id}", headers=headers
)
cards = response.json()

moved = 0
skipped = 0
for card in cards:
    title = card['title']
    
    # Пропускаем эпики (родительские карточки)
    if card.get('children_count', 0) > 0:
        skipped += 1
        continue
    
    # Проверяем статус
    if title in task_status:
        if task_status[title]:
            # Задача выполнена, переносим в Готово
            update_data = {"column_id": done_column_id}
            response = requests.patch(
                f"{base_url}/cards/{card['id']}",
                headers=headers,
                json=update_data
            )
            if response.status_code == 200:
                moved += 1
                print(f"✅ {title[:60]}")
    else:
        print(f"⚠️ Не найдено в roadmap: {title[:60]}")

print(f"\n✅ Перенесено в Готово: {moved}")
print(f"Пропущено эпиков: {skipped}")

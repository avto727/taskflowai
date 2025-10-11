"""
Исправление нумерации карточек
"""
import sys, os, requests
sys.path.append(os.path.dirname(__file__))
from trello_client import TrelloClient

client = TrelloClient()
board_id = os.getenv('TRELLO_BOARD_ID')
cards = client.get_cards(board_id)

# Маппинг названий на номера
renames = {
    'Авторизация todoist: OAuth': '19. Авторизация todoist: OAuth',
    'Авторизация в TaskFlowAI: MVP': '10. Авторизация в TaskFlowAI: MVP',
    'Пагинация в чате': '15. Пагинация в чате',
    'Удаление задач в todoist': '14. Удаление задач в todoist'
}

renamed = 0
for old_name, new_name in renames.items():
    card = next((c for c in cards if c['name'] == old_name), None)
    if card:
        response = requests.put(
            f'https://api.trello.com/1/cards/{card["id"]}',
            params={
                'key': client.api_key,
                'token': client.token,
                'name': new_name
            }
        )
        if response.status_code == 200:
            renamed += 1
            print(f'✅ {old_name} → {new_name}')

print(f'\n✅ Переименовано: {renamed}')

# Сортируем карточки по номеру
cards = client.get_cards(board_id)
lists = client.get_lists(board_id)

for list_obj in lists:
    list_cards = [c for c in cards if c['idList'] == list_obj['id']]
    list_cards.sort(key=lambda x: int(x['name'].split('.')[0]) 
                    if x['name'][0].isdigit() else 999)
    
    for pos, card in enumerate(list_cards):
        requests.put(
            f'https://api.trello.com/1/cards/{card["id"]}',
            params={
                'key': client.api_key,
                'token': client.token,
                'pos': pos
            }
        )
    print(f'✅ Отсортировано: {list_obj["name"]} ({len(list_cards)})')

"""
Детальная проверка досок
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from kaiten_client import KaitenClient

def check_board_details():
    client = KaitenClient()
    
    board_ids = [1518417, 1518362]
    
    for board_id in board_ids:
        print(f"\n{'='*60}")
        print(f"Доска ID: {board_id}")
        print('='*60)
        
        # Получаем колонки
        columns = client.get_columns(board_id)
        print(f"\nКолонки ({len(columns)}):")
        for col in columns:
            print(f"  - {col['title']} (ID: {col['id']})")
        
        # Получаем карточки
        cards = client.get_cards(board_id)
        print(f"\nКарточки ({len(cards)}):")
        for card in cards[:5]:
            print(f"  - {card['title']}")
        if len(cards) > 5:
            print(f"  ... и ещё {len(cards) - 5}")

if __name__ == "__main__":
    check_board_details()

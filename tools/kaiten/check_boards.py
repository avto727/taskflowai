"""
Проверка доступных досок в Kaiten
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from kaiten_client import KaitenClient

def check_boards():
    """Показать все доступные доски"""
    client = KaitenClient()
    
    print("🔍 Получаю список досок...\n")
    
    boards = client.get_boards()
    
    if not boards:
        print("❌ Доски не найдены")
        return
    
    print(f"📋 Найдено досок: {len(boards)}\n")
    
    for board in boards:
        print(f"ID: {board['id']}")
        print(f"Название: {board['title']}")
        print(f"Пространство: {board.get('space', {}).get('title', 'N/A')}")
        print("-" * 50)

if __name__ == "__main__":
    check_boards()

"""
Клиент для Kaiten API
"""
import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class KaitenClient:
    """Клиент для работы с Kaiten API"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("KAITEN_API_TOKEN")
        self.base_url = "https://avto727a.kaiten.ru/api/latest"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def get_boards(self) -> List[Dict]:
        """Получить все доски"""
        response = requests.get(
            f"{self.base_url}/spaces", headers=self.headers
        )
        response.raise_for_status()
        spaces = response.json()
        boards = []
        for space in spaces:
            if 'boards' in space:
                boards.extend(space['boards'])
        return boards
    
    def get_columns(self, board_id: int) -> List[Dict]:
        """Получить колонки доски"""
        response = requests.get(
            f"{self.base_url}/boards/{board_id}",
            headers=self.headers
        )
        response.raise_for_status()
        board = response.json()
        return board.get('columns', [])
    
    def get_cards(self, board_id: int) -> List[Dict]:
        """Получить карточки доски"""
        response = requests.get(
            f"{self.base_url}/cards?board_id={board_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_card(self, board_id: int, column_id: int,
                   title: str, description: str = "") -> Dict:
        """Создать карточку"""
        data = {
            "board_id": board_id,
            "column_id": column_id,
            "title": title,
            "description": description
        }
        response = requests.post(
            f"{self.base_url}/cards",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_card(self, card_id: int, column_id: Optional[int] = None,
                   title: Optional[str] = None) -> Dict:
        """Обновить карточку"""
        data = {}
        if column_id:
            data["column_id"] = column_id
        if title:
            data["title"] = title
        
        response = requests.patch(
            f"{self.base_url}/cards/{card_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    client = KaitenClient()
    try:
        boards = client.get_boards()
        print(f"✅ Подключение к Kaiten успешно!")
        print(f"Найдено досок: {len(boards)}")
        for board in boards:
            print(f"  - {board['title']} (ID: {board['id']})")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

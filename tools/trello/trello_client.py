"""
Клиент для Trello API
"""
import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class TrelloClient:
    """Клиент для работы с Trello API"""
    
    def __init__(self, api_key: Optional[str] = None,
                 token: Optional[str] = None):
        self.api_key = api_key or os.getenv("TRELLO_API_KEY")
        self.token = token or os.getenv("TRELLO_TOKEN")
        self.base_url = "https://api.trello.com/1"
        self.auth = {
            "key": self.api_key,
            "token": self.token
        }
    
    def get_boards(self) -> List[Dict]:
        """Получить все доски"""
        response = requests.get(
            f"{self.base_url}/members/me/boards",
            params=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def create_board(self, name: str) -> Dict:
        """Создать доску"""
        params = {**self.auth, "name": name}
        response = requests.post(
            f"{self.base_url}/boards",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_lists(self, board_id: str) -> List[Dict]:
        """Получить списки (колонки) доски"""
        response = requests.get(
            f"{self.base_url}/boards/{board_id}/lists",
            params=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def get_cards(self, board_id: str) -> List[Dict]:
        """Получить карточки доски"""
        response = requests.get(
            f"{self.base_url}/boards/{board_id}/cards",
            params=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def create_card(self, list_id: str, name: str,
                   desc: str = "") -> Dict:
        """Создать карточку"""
        params = {
            **self.auth,
            "idList": list_id,
            "name": name,
            "desc": desc
        }
        response = requests.post(
            f"{self.base_url}/cards",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def create_list(self, board_id: str, name: str,
                    pos: float = None) -> Dict:
        """Создать список (колонку)"""
        params = {**self.auth, "name": name, "idBoard": board_id}
        if pos is not None:
            params["pos"] = pos
        response = requests.post(
            f"{self.base_url}/lists",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def move_card(self, card_id: str, list_id: str) -> Dict:
        """Переместить карточку в другой список"""
        params = {**self.auth, "idList": list_id}
        response = requests.put(
            f"{self.base_url}/cards/{card_id}",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def set_card_cover(self, card_id: str, color: str) -> Dict:
        """Установить цвет обложки карточки"""
        params = {**self.auth, "cover": {"color": color}}
        response = requests.put(
            f"{self.base_url}/cards/{card_id}",
            json={"cover": {"color": color}},
            params=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def get_checklists(self, card_id: str) -> List[Dict]:
        """Получить чеклисты карточки"""
        response = requests.get(
            f"{self.base_url}/cards/{card_id}/checklists",
            params=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def check_item(self, card_id: str, checklist_id: str,
                   item_id: str) -> Dict:
        """Отметить пункт чеклиста"""
        params = {**self.auth, "state": "complete"}
        response = requests.put(
            f"{self.base_url}/cards/{card_id}/checkItem/"
            f"{item_id}",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def _request(self, method: str, url: str, **kwargs) -> Dict:
        """Базовый запрос"""
        params = kwargs.pop('params', {})
        params.update(self.auth)
        response = requests.request(
            method, url, params=params, **kwargs
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    client = TrelloClient()
    try:
        boards = client.get_boards()
        print(f"✅ Подключение к Trello успешно!")
        print(f"Найдено досок: {len(boards)}")
        for board in boards[:5]:
            print(f"  - {board['name']} (ID: {board['id']})")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

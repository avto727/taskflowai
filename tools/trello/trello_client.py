"""
Trello Client for TaskFlowAI
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()


class TaskFlowTrello:
    def __init__(self):
        self.api_key = os.getenv("TRELLO_API_KEY")
        self.token = os.getenv("TRELLO_TOKEN")
        self.base_url = "https://api.trello.com/1"
        
        if not self.api_key or not self.token:
            raise ValueError("TRELLO_API_KEY and TRELLO_TOKEN required in .env")
    
    def _make_request(self, endpoint, method="GET", data=None):
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        params = {"key": self.api_key, "token": self.token}
        
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, params=params, json=data)
        elif method == "PUT":
            response = requests.put(url, params=params, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    def get_boards(self):
        """Get all boards"""
        return self._make_request("/members/me/boards")
    
    def get_board_by_name(self, name):
        """Find board by name"""
        boards = self.get_boards()
        for board in boards:
            if board["name"] == name:
                return board
        return None
    
    def get_board_lists(self, board_id):
        """Get lists from board"""
        return self._make_request(f"/boards/{board_id}/lists")
    
    def get_list_cards(self, list_id):
        """Get cards from list"""
        return self._make_request(f"/lists/{list_id}/cards")
    
    def create_card(self, list_id, name, desc=""):
        """Create card in list"""
        data = {"name": name, "desc": desc, "idList": list_id}
        return self._make_request("/cards", "POST", data)
    
    def get_cards_from_list(self, list_name, board_name="TaskFlowAI"):
        """Get cards from list by name"""
        board = self.get_board_by_name(board_name)
        if not board:
            return None
        
        lists = self.get_board_lists(board["id"])
        for lst in lists:
            if lst["name"] == list_name:
                return self.get_list_cards(lst["id"])
        return None
    
    def test_connection(self):
        """Test Trello connection"""
        try:
            boards = self.get_boards()
            print(f"Connected! Found {len(boards)} boards")
            
            # Find TaskFlowAI board
            taskflow_board = self.get_board_by_name("TaskFlowAI")
            if taskflow_board:
                print(f"Found TaskFlowAI board: {taskflow_board['name']}")
                
                # Get lists
                lists = self.get_board_lists(taskflow_board["id"])
                print("\nLists:")
                for lst in lists:
                    cards = self.get_list_cards(lst["id"])
                    print(f"- {lst['name']}: {len(cards)} cards")
            else:
                print("TaskFlowAI board not found")
                
        except Exception as e:
            print(f"Connection failed: {e}")


if __name__ == "__main__":
    client = TaskFlowTrello()
    client.test_connection()
    
    # Получаем карточки из колонки "Готово"
    done_cards = client.get_cards_from_list("Готово")
    if done_cards:
        print("\n📋 Карточки в колонке 'Готово':")
        for i, card in enumerate(done_cards, 1):
            print(f"{i}. {card['name']}")
    else:
        print("\n❌ Карточки в колонке 'Готово' не найдены")
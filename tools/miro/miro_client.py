"""
Клиент для Miro API
"""
import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class MiroClient:
    """Клиент для работы с Miro API"""
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or os.getenv("MIRO_ACCESS_TOKEN")
        self.base_url = "https://api.miro.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_boards(self) -> List[Dict]:
        """Получить все доски"""
        response = requests.get(
            f"{self.base_url}/boards",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get('data', [])
    
    def create_sticky(self, board_id: str, x: float, y: float,
                     text: str, color: str = "light_yellow") -> Dict:
        """Создать стикер"""
        data = {
            "data": {
                "content": text,
                "shape": "square"
            },
            "style": {
                "fillColor": color
            },
            "position": {
                "x": x,
                "y": y
            }
        }
        response = requests.post(
            f"{self.base_url}/boards/{board_id}/sticky_notes",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def create_connector(self, board_id: str,
                        start_item: str,
                        end_item: str) -> Dict:
        """Создать соединитель между фигурами"""
        data = {
            "startItem": {"id": start_item},
            "endItem": {"id": end_item},
            "style": {
                "strokeColor": "#1a1a1a"
            }
        }
        response = requests.post(
            f"{self.base_url}/boards/{board_id}/connectors",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_items(self, board_id: str,
                 item_type: str = None) -> List[Dict]:
        """Получить все элементы доски (с пагинацией)"""
        params = {'limit': 50}
        if item_type:
            params['type'] = item_type
        
        all_items = []
        cursor = None
        
        while True:
            if cursor:
                params['cursor'] = cursor
            
            response = requests.get(
                f"{self.base_url}/boards/{board_id}/items",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            all_items.extend(data.get('data', []))
            
            cursor = data.get('cursor')
            if not cursor:
                break
        
        return all_items
    
    def update_sticky_note(self, board_id: str,
                          item_id: str,
                          content: str) -> Dict:
        """Обновить содержимое стикера"""
        data = {
            "data": {
                "content": content
            }
        }
        response = requests.patch(
            f"{self.base_url}/boards/{board_id}/sticky_notes/{item_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_sticky_position(self, board_id: str,
                              item_id: str, x: float,
                              y: float) -> Dict:
        """Обновить позицию стикера"""
        data = {"position": {"x": x, "y": y}}
        response = requests.patch(
            f"{self.base_url}/boards/{board_id}/sticky_notes/{item_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_item(self, board_id: str, item_id: str):
        """Удалить элемент"""
        response = requests.delete(
            f"{self.base_url}/boards/{board_id}/items/{item_id}",
            headers=self.headers
        )
        response.raise_for_status()
    
    def create_shape(self, board_id: str, x: float, y: float,
                    width: int, height: int,
                    text: str) -> Dict:
        """Создать прямоугольник"""
        data = {
            "data": {"content": text, "shape": "rectangle"},
            "style": {"fillColor": "#fff9b1"},
            "position": {"x": x, "y": y},
            "geometry": {"width": width, "height": height}
        }
        response = requests.post(
            f"{self.base_url}/boards/{board_id}/shapes",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_shape_color(self, board_id: str,
                          shape_id: str, color: str):
        """Изменить цвет shape"""
        data = {"style": {"fillColor": color}}
        response = requests.patch(
            f"{self.base_url}/boards/{board_id}/shapes/{shape_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
    
    def center_shape_text(self, board_id: str, shape_id: str):
        """Центрировать текст в shape"""
        data = {
            "style": {
                "textAlign": "center",
                "textAlignVertical": "middle"
            }
        }
        response = requests.patch(
            f"{self.base_url}/boards/{board_id}/shapes/{shape_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
    
    def create_rounded_shape(self, board_id: str, x: float,
                            y: float, width: int, height: int,
                            text: str, color: str) -> Dict:
        """Создать прямоугольник со скруглением"""
        data = {
            "data": {"content": text, "shape": "round_rectangle"},
            "style": {
                "fillColor": color,
                "textAlign": "center",
                "textAlignVertical": "middle"
            },
            "position": {"x": x, "y": y},
            "geometry": {"width": width, "height": height}
        }
        response = requests.post(
            f"{self.base_url}/boards/{board_id}/shapes",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_connectors(self, board_id: str) -> List[Dict]:
        """Получить все connectors"""
        response = requests.get(
            f"{self.base_url}/boards/{board_id}/connectors",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get('data', [])
    
    def delete_connector(self, board_id: str,
                        connector_id: str):
        """Удалить connector"""
        response = requests.delete(
            f"{self.base_url}/boards/{board_id}/connectors/{connector_id}",
            headers=self.headers
        )
        response.raise_for_status()


if __name__ == "__main__":
    client = MiroClient()
    try:
        boards = client.get_boards()
        print(f"✅ Подключение к Miro успешно!")
        print(f"Найдено досок: {len(boards)}")
        for board in boards[:5]:
            print(f"  - {board['name']} (ID: {board['id']})")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

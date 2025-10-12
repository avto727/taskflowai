"""
API клиент для подключения к TaskFlowAI Backend
"""

import requests
from typing import Dict, Any


class TaskFlowAPIClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        todoist_token: str = None,
    ):
        self.base_url = base_url
        self.todoist_token = todoist_token

    def health_check(self) -> bool:
        """Проверка доступности API"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def get_tasks(
        self, category: str = None, time_filter: str = None
    ) -> Dict[str, Any]:
        """
        Получить список задач

        Args:
            category: Категория ('Здоровье', 'Деньги')
            time_filter: Время ('today', 'tomorrow', 'week')
        """
        try:
            params = {}
            if category:
                params["category"] = category
            if time_filter:
                params["time_filter"] = time_filter

            headers = {}
            if self.todoist_token:
                headers["X-Todoist-Token"] = self.todoist_token

            response = requests.get(
                f"{self.base_url}/tasks", params=params, headers=headers
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_categories(self) -> Dict[str, Any]:
        """Получить категории"""
        try:
            response = requests.get(f"{self.base_url}/categories")
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def analyze_message(self, text: str) -> Dict[str, Any]:
        """Анализ сообщения через ИИ"""
        try:
            response = requests.post(
                f"{self.base_url}/ai/analyze", json={"text": text}
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def reschedule_overdue(self) -> Dict[str, Any]:
        """Перенести просроченные задачи на сегодня"""
        try:
            headers = {}
            if self.todoist_token:
                headers["X-Todoist-Token"] = self.todoist_token

            response = requests.post(
                f"{self.base_url}/tasks/reschedule-overdue", headers=headers
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

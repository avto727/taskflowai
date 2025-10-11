"""
Todoist API Client для TaskFlowAI
"""
import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class TodoistClient:
    """Клиент для работы с Todoist API"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("TODOIST_API_TOKEN")
        self.base_url = "https://api.todoist.com/rest/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def get_projects(self) -> List[Dict]:
        """Получить все проекты"""
        response = requests.get(f"{self.base_url}/projects", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_tasks(self, project_id: Optional[str] = None) -> List[Dict]:
        """Получить задачи (все или по проекту)"""
        params = {}
        if project_id:
            params["project_id"] = project_id
            
        response = requests.get(
            f"{self.base_url}/tasks",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_subtasks(self, parent_id: str) -> List[Dict]:
        """Получить подзадачи"""
        all_tasks = self.get_tasks()
        return [t for t in all_tasks if t.get("parent_id") == parent_id]
    
    def create_task(self, content: str, project_id: Optional[str] = None, 
                   due_string: Optional[str] = None, priority: int = 1,
                   parent_id: Optional[str] = None) -> Dict:
        """Создать задачу"""
        data = {
            "content": content,
            "priority": priority
        }
        
        if project_id:
            data["project_id"] = project_id
        if due_string:
            data["due_string"] = due_string
        if parent_id:
            data["parent_id"] = parent_id
            
        response = requests.post(f"{self.base_url}/tasks",
                                headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def update_task(self, task_id: str, content: Optional[str] = None,
                   due_string: Optional[str] = None, priority: Optional[int] = None) -> bool:
        """Обновить задачу"""
        data = {}
        if content:
            data["content"] = content
        if due_string:
            data["due_string"] = due_string
        if priority:
            data["priority"] = priority
            
        response = requests.post(f"{self.base_url}/tasks/{task_id}", headers=self.headers, json=data)
        response.raise_for_status()
        return True
    
    def close_task(self, task_id: str) -> bool:
        """Закрыть задачу (отметить как выполненную)"""
        response = requests.post(f"{self.base_url}/tasks/{task_id}/close", headers=self.headers)
        response.raise_for_status()
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """Удалить задачу"""
        response = requests.delete(f"{self.base_url}/tasks/{task_id}", headers=self.headers)
        response.raise_for_status()
        return True


# Тестирование подключения
if __name__ == "__main__":
    client = TodoistClient()
    try:
        projects = client.get_projects()
        print(f"✅ Подключение к Todoist успешно! Найдено проектов: {len(projects)}")
        for project in projects:
            print(f"  - {project['name']} (ID: {project['id']})")
    except Exception as e:
        print(f"❌ Ошибка подключения к Todoist: {e}")
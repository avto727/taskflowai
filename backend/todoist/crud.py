"""
CRUD операции для TaskFlowAI с Todoist
"""
from typing import List, Dict, Optional
from client import TodoistClient
from mapper import CategoryMapper


class TaskFlowTodoist:
    """Высокоуровневый интерфейс для работы с Todoist через TaskFlowAI"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.client = TodoistClient(api_token)
        
        # Инициализируем маппер с проектами
        projects = self.client.get_projects()
        self.mapper = CategoryMapper(projects)
    
    def create_task_with_category(self, content: str, irga_category: str, 
                                 due_string: Optional[str] = None,
                                 priority: int = 1,
                                 parent_id: Optional[str] = None) -> Dict:
        """
        Создать задачу с категорией Irga
        
        Args:
            content: Текст задачи
            irga_category: Категория из Irga (например, "Покупки")
            due_string: Дата выполнения (например, "завтра", "2025-01-10")
            priority: Приоритет (1-4, где 4 = самый высокий)
            parent_id: ID родительской задачи (для подзадач)
            
        Returns:
            Созданная задача
        """
        project_id = self.mapper.get_project_id(irga_category)
        return self.client.create_task(
            content=content,
            project_id=project_id,
            due_string=due_string,
            priority=priority,
            parent_id=parent_id
        )
    
    def get_tasks_by_category(self, irga_category: str) -> List[Dict]:
        """
        Получить задачи по категории Irga
        
        Args:
            irga_category: Категория из Irga
            
        Returns:
            Список задач
        """
        project_id = self.mapper.get_project_id(irga_category)
        if project_id:
            return self.client.get_tasks(project_id=project_id)
        return []
    
    def get_all_tasks(self) -> List[Dict]:
        """Получить все задачи"""
        return self.client.get_tasks()
    
    def get_tasks_by_time(self, time_filter: str) -> List[Dict]:
        """
        Получить задачи по времени
        
        Args:
            time_filter: 'today', 'tomorrow', 'week'
            
        Returns:
            Список задач
        """
        from datetime import datetime, timedelta
        
        all_tasks = self.get_all_tasks()
        filtered = []
        
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        week_end = today + timedelta(days=7)
        
        for task in all_tasks:
            due = task.get('due')
            if not due:
                continue
            
            due_date_str = due.get('date')
            if not due_date_str:
                continue
            
            try:
                due_date = datetime.fromisoformat(
                    due_date_str.split('T')[0]
                ).date()
                
                if time_filter == 'today' and due_date == today:
                    filtered.append(task)
                elif time_filter == 'tomorrow' and due_date == tomorrow:
                    filtered.append(task)
                elif time_filter == 'week' and today <= due_date <= week_end:
                    filtered.append(task)
            except:
                continue
        
        return filtered
    
    def update_task(self, task_id: str, content: Optional[str] = None,
                   due_string: Optional[str] = None, priority: Optional[int] = None) -> bool:
        """Обновить задачу"""
        return self.client.update_task(task_id, content, due_string, priority)
    
    def complete_task(self, task_id: str) -> bool:
        """Отметить задачу как выполненную"""
        return self.client.close_task(task_id)
    
    def delete_task(self, task_id: str) -> bool:
        """Удалить задачу"""
        return self.client.delete_task(task_id)
    
    def get_projects_info(self) -> List[Dict]:
        """Получить информацию о проектах"""
        return self.client.get_projects()
    
    def find_similar_tasks(self, content: str, limit: int = 5) -> List[Dict]:
        """
        Найти похожие задачи (простая реализация)
        
        Args:
            content: Текст для поиска
            limit: Максимум результатов
            
        Returns:
            Список похожих задач
        """
        all_tasks = self.get_all_tasks()
        similar = []
        
        content_lower = content.lower()
        words = content_lower.split()
        
        for task in all_tasks:
            task_content = task.get('content', '').lower()
            
            # Простой поиск по словам
            matches = sum(1 for word in words if word in task_content)
            if matches > 0:
                task['similarity_score'] = matches / len(words)
                similar.append(task)
        
        # Сортируем по релевантности
        similar.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar[:limit]


# Тестирование CRUD операций
if __name__ == "__main__":
    taskflow = TaskFlowTodoist()
    
    print("🧪 Тестирование TaskFlowAI CRUD операций:")
    
    # 1. Создаём тестовую задачу
    print("\n1. Создание задачи:")
    task = taskflow.create_task_with_category(
        content="Купить молоко (тест TaskFlowAI)",
        irga_category="Покупки",
        due_string="завтра"
    )
    print(f"   ✅ Создана задача: {task['content']} (ID: {task['id']})")
    
    # 2. Получаем задачи по категории
    print("\n2. Задачи в категории 'Покупки':")
    tasks = taskflow.get_tasks_by_category("Покупки")
    for task in tasks[:3]:  # Показываем первые 3
        print(f"   - {task['content']}")
    
    # 3. Поиск похожих задач
    print("\n3. Поиск похожих задач для 'молоко':")
    similar = taskflow.find_similar_tasks("молоко")
    for task in similar[:2]:  # Показываем первые 2
        score = task.get('similarity_score', 0)
        print(f"   - {task['content']} (релевантность: {score:.2f})")
    
    # 4. Отмечаем задачу как выполненную
    print(f"\n4. Отмечаем задачу как выполненную:")
    if taskflow.complete_task(task['id']):
        print("   ✅ Задача отмечена как выполненная")
    
    print("\n🎉 Тестирование завершено!")
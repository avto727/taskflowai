"""
Интеграция Irga AI + Todoist для TaskFlowAI
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'todoist'))

import os
from crud import TaskFlowTodoist
from mapper import CategoryMapper

# Проверяем доступность Ollama
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"

if OLLAMA_ENABLED:
    from ai_processor import AIProcessor

# Категории Irga (55 штук)
IRGA_CATEGORIES = [
    # Деньги (1-10)
    (1, "Зарплата"), (2, "Инвестиции"), (3, "Оплата счетов"), (4, "Покупки"), 
    (5, "Налоги"), (6, "Кредиты"), (7, "Сбережения"), (8, "Бюджет"), 
    (9, "Расходы"), (10, "Доходы"),
    
    # Семья (11-20)
    (11, "Дети"), (12, "Родители"), (13, "Супруг(а)"), (14, "Родственники"), 
    (15, "Встречи"), (16, "Праздники"), (17, "Поездки"), (18, "Быт"), 
    (19, "Образование"), (20, "Досуг"),
    
    # Здоровье (21-30)
    (21, "Врачи"), (22, "Анализы"), (23, "Лекарства"), (24, "Спорт"), 
    (25, "Питание"), (26, "Сон"), (27, "Профилактика"), (28, "Стоматология"), 
    (29, "Медосмотр"), (30, "Процедуры"),
    
    # Взаимоотношения (31-40)
    (31, "Друзья"), (32, "Коллеги"), (33, "Партнёры"), (34, "Знакомства"), 
    (35, "Общение"), (36, "Конфликты"), (37, "Поддержка"), (38, "Сотрудничество"), 
    (39, "Нетворкинг"), (40, "Мероприятия"),
    
    # Духовность и развитие личности (41-50)
    (41, "Обучение"), (42, "Книги"), (43, "Курсы"), (44, "Медитация"), 
    (45, "Хобби"), (46, "Творчество"), (47, "Саморазвитие"), (48, "Цели"), 
    (49, "Рефлексия"), (50, "Практики")
]

class TaskFlowAI:
    """Главный класс TaskFlowAI - интеграция Irga AI + Todoist"""
    
    def __init__(self):
        self.ai = AIProcessor() if OLLAMA_ENABLED else None
        self.todoist = TaskFlowTodoist()
        
        # Создаём маппинг ID → название категории
        self.category_map = {cat_id: cat_name for cat_id, cat_name in IRGA_CATEGORIES}
    
    def process_message(self, text: str) -> dict:
        """
        Обработка сообщения пользователя
        
        Args:
            text: Текст сообщения
            
        Returns:
            Результат обработки
        """
        # Если Ollama отключён - просто создаём задачу
        if not OLLAMA_ENABLED or not self.ai:
            return self._create_task(
                text, 
                "Покупки",  # Дефолтная категория
                {'type': 'task', 'planned_time': None}
            )
        
        # 1. ИИ-анализ
        analysis = self.ai.analyze_message(text, IRGA_CATEGORIES)
        
        # 2. Получаем название категории
        category_name = self.category_map.get(analysis.get('category_id'), 'Неизвестно')
        
        # 3. Обрабатываем в зависимости от типа
        if analysis['type'] == 'task':
            return self._create_task(text, category_name, analysis)
        elif analysis['type'] == 'completed':
            return self._mark_completed(text, category_name, analysis)
        elif analysis['type'] == 'query':
            return self._get_tasks(category_name, analysis)
        else:
            return {'status': 'error', 'message': 'Неизвестный тип сообщения'}
    
    def _create_task(self, text: str, category_name: str, analysis: dict) -> dict:
        """Создание задачи в Todoist"""
        try:
            # Создаём задачу
            task = self.todoist.create_task_with_category(
                content=text,
                irga_category=category_name,
                due_string=analysis.get('planned_time'),
                priority=1
            )
            
            return {
                'status': 'success',
                'action': 'task_created',
                'task': task,
                'category': category_name,
                'analysis': analysis
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Ошибка создания задачи: {e}'
            }
    
    def _mark_completed(self, text: str, category_name: str, analysis: dict) -> dict:
        """Поиск и отметка задачи как выполненной"""
        try:
            # Ищем похожие задачи
            similar_tasks = self.todoist.find_similar_tasks(text, limit=3)
            
            if similar_tasks:
                # Берём самую похожую
                task = similar_tasks[0]
                self.todoist.complete_task(task['id'])
                
                return {
                    'status': 'success',
                    'action': 'task_completed',
                    'task': task,
                    'category': category_name,
                    'analysis': analysis
                }
            else:
                return {
                    'status': 'info',
                    'message': 'Похожие задачи не найдены',
                    'category': category_name
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Ошибка поиска задач: {e}'
            }
    
    def _get_tasks(self, category_name: str, analysis: dict) -> dict:
        """Получение списка задач"""
        try:
            if category_name != 'Неизвестно':
                tasks = self.todoist.get_tasks_by_category(category_name)
            else:
                tasks = self.todoist.get_all_tasks()
            
            return {
                'status': 'success',
                'action': 'tasks_list',
                'tasks': tasks[:10],  # Первые 10
                'category': category_name,
                'total': len(tasks)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Ошибка получения задач: {e}'
            }


# Тестирование интеграции
if __name__ == "__main__":
    taskflow = TaskFlowAI()
    
    test_messages = [
        "Купить хлеб в магазине",
        "Сходил к стоматологу", 
        "Что у меня по здоровью?"
    ]
    
    print("🚀 Тестирование TaskFlowAI Integration:")
    print("=" * 50)
    
    for message in test_messages:
        print(f"\n📝 Сообщение: '{message}'")
        
        result = taskflow.process_message(message)
        
        print(f"   Статус: {result['status']}")
        print(f"   Действие: {result.get('action', 'нет')}")
        print(f"   Категория: {result.get('category', 'нет')}")
        
        if result['status'] == 'success':
            if result['action'] == 'task_created':
                print(f"   ✅ Задача создана: {result['task']['content']}")
            elif result['action'] == 'task_completed':
                print(f"   ✅ Задача выполнена: {result['task']['content']}")
            elif result['action'] == 'tasks_list':
                print(f"   📋 Найдено задач: {result['total']}")
        else:
            print(f"   ❌ {result.get('message', 'Неизвестная ошибка')}")
    
    print("\n🎉 Тестирование завершено!")
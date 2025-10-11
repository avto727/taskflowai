"""
Интеграция Irga AI + Todoist для TaskFlowAI
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "todoist"))

import os
from crud import TaskFlowTodoist
from constants import TASK_EXAMPLES

# Проверяем доступность Ollama
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"

if OLLAMA_ENABLED:
    from ai_processor import AIProcessor

# Категории Irga (для обратной совместимости)
IRGA_CATEGORIES = TASK_EXAMPLES


class TaskFlowAI:
    """Главный класс TaskFlowAI - интеграция Irga AI + Todoist"""

    def __init__(self):
        self.ai = AIProcessor() if OLLAMA_ENABLED else None
        self.todoist = TaskFlowTodoist()

        # Создаём маппинг ID → название категории
        self.category_map = {
            cat_id: cat_name for cat_id, cat_name in IRGA_CATEGORIES
        }

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
                {"type": "task", "planned_time": None},
            )

        # 1. ИИ-анализ
        analysis = self.ai.analyze_message(text, IRGA_CATEGORIES)

        # 2. Получаем название категории
        category_name = self.category_map.get(
            analysis.get("category_id"), "Неизвестно"
        )

        # 3. Обрабатываем в зависимости от типа
        if analysis["type"] == "task":
            return self._create_task(text, category_name, analysis)
        elif analysis["type"] == "completed":
            return self._mark_completed(text, category_name, analysis)
        elif analysis["type"] == "query":
            return self._get_tasks(category_name, analysis)
        else:
            return {"status": "error", "message": "Неизвестный тип сообщения"}

    def _create_task(
        self, text: str, category_name: str, analysis: dict
    ) -> dict:
        """Создание задачи в Todoist"""
        try:
            from datetime import datetime, timedelta
            import sys
            import os
            sys.path.insert(
                0, os.path.join(os.path.dirname(__file__), "..", "todoist")
            )
            from crud import find_free_slot

            planned_time = analysis.get("planned_time")

            # Обработка "утром", "днём", "вечером"
            time_ranges = {
                "утром": (6, 12),
                "утра": (6, 12),
                "morning": (6, 12),
                "днём": (12, 18),
                "днем": (12, 18),
                "обед": (12, 18),
                "afternoon": (12, 18),
                "вечером": (18, 23),
                "evening": (18, 23),
                "ночью": (22, 24),
                "night": (22, 24),
            }

            time_word_found = None
            for word, (start, end) in time_ranges.items():
                if planned_time and word in planned_time.lower():
                    time_word_found = (start, end)
                    break

            if time_word_found:
                # Получаем все задачи
                all_tasks = self.todoist.get_all_tasks()

                # Определяем целевую дату
                target_date = datetime.now()
                if planned_time and (
                    "завтра" in planned_time.lower()
                    or "tomorrow" in planned_time.lower()
                ):
                    target_date += timedelta(days=1)

                # Ищем свободный слот в диапазоне
                start_hour, end_hour = time_word_found
                free_time = find_free_slot(
                    all_tasks, target_date, start_hour, end_hour
                )
                planned_time = (
                    f"{target_date.strftime('%Y-%m-%d')} {free_time}"
                )

            # Создаём задачу
            task = self.todoist.create_task_with_category(
                content=text,
                irga_category=category_name,
                due_string=planned_time,
                priority=1,
            )

            return {
                "status": "success",
                "action": "task_created",
                "task": task,
                "category": category_name,
                "analysis": analysis,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка создания задачи: {e}",
            }

    def _mark_completed(
        self, text: str, category_name: str, analysis: dict
    ) -> dict:
        """Поиск и отметка задачи как выполненной"""
        try:
            # Ищем похожие задачи
            similar_tasks = self.todoist.find_similar_tasks(text, limit=3)

            if similar_tasks:
                # Берём самую похожую
                task = similar_tasks[0]
                self.todoist.complete_task(task["id"])

                return {
                    "status": "success",
                    "action": "task_completed",
                    "task": task,
                    "category": category_name,
                    "analysis": analysis,
                }
            else:
                return {
                    "status": "info",
                    "message": "Похожие задачи не найдены",
                    "category": category_name,
                }
        except Exception as e:
            return {"status": "error", "message": f"Ошибка поиска задач: {e}"}

    def _get_tasks(self, category_name: str, analysis: dict) -> dict:
        """Получение списка задач"""
        try:
            if category_name != "Неизвестно":
                tasks = self.todoist.get_tasks_by_category(category_name)
            else:
                tasks = self.todoist.get_all_tasks()

            return {
                "status": "success",
                "action": "tasks_list",
                "tasks": tasks[:10],  # Первые 10
                "category": category_name,
                "total": len(tasks),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка получения задач: {e}",
            }


# Тестирование интеграции
if __name__ == "__main__":
    taskflow = TaskFlowAI()

    test_messages = [
        "Купить хлеб в магазине",
        "Сходил к стоматологу",
        "Что у меня по здоровью?",
    ]

    print("🚀 Тестирование TaskFlowAI Integration:")
    print("=" * 50)

    for message in test_messages:
        print(f"\n📝 Сообщение: '{message}'")

        result = taskflow.process_message(message)

        print(f"   Статус: {result['status']}")
        print(f"   Действие: {result.get('action', 'нет')}")
        print(f"   Категория: {result.get('category', 'нет')}")

        if result["status"] == "success":
            if result["action"] == "task_created":
                print(f"   ✅ Задача создана: {result['task']['content']}")
            elif result["action"] == "task_completed":
                print(f"   ✅ Задача выполнена: {result['task']['content']}")
            elif result["action"] == "tasks_list":
                print(f"   📋 Найдено задач: {result['total']}")
        else:
            print(f"   ❌ {result.get('message', 'Неизвестная ошибка')}")

    print("\n🎉 Тестирование завершено!")

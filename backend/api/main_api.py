"""
TaskFlowAI Backend API
FastAPI сервер для подключения клиентов
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sys
import os

# Добавляем пути для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "irga"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "todoist"))

from taskflow_integration import TaskFlowAI
from .models import MessageRequest, TaskRequest
from crud import filter_tasks_by_time

# Создаём FastAPI приложение
app = FastAPI(
    title="TaskFlowAI API",
    description="Умный таск-менеджер на базе Todoist с ИИ-автоматизацией",
    version="1.0.0",
)

# CORS для веб-клиентов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем TaskFlowAI
taskflow = TaskFlowAI()


# Эндпоинты
@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "TaskFlowAI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy"}


@app.post("/ai/analyze")
async def analyze_message(request: MessageRequest):
    """ИИ-анализ сообщения пользователя"""
    try:
        result = taskflow.process_message(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks")
async def get_tasks(
    category: Optional[str] = None,
    time_filter: Optional[str] = None,
    x_todoist_token: Optional[str] = Header(None),  # noqa: B008
):
    """
    Получить список задач

    Args:
        category: Проект Todoist (например, 'Здоровье', 'Покупки')
                 Поддерживает старую терминологию "категория"
        time_filter: Фильтр по времени ('today', 'tomorrow', 'week')
    """
    try:
        # Используем токен пользователя если есть
        if x_todoist_token:
            from crud import TaskFlowTodoist

            user_todoist = TaskFlowTodoist(x_todoist_token)
        else:
            user_todoist = taskflow.todoist

        if category and time_filter:
            # Фильтр по проекту и времени
            cat_tasks = user_todoist.get_tasks_by_category(category)
            tasks = filter_tasks_by_time(cat_tasks, time_filter)
        elif category:
            tasks = user_todoist.get_tasks_by_category(category)
        elif time_filter:
            # Фильтр только по времени
            all_tasks = user_todoist.get_all_tasks()
            tasks = filter_tasks_by_time(all_tasks, time_filter)
        else:
            tasks = user_todoist.get_all_tasks()

        return {"status": "success", "tasks": tasks, "total": len(tasks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tasks")
async def create_task(request: TaskRequest):
    """Создать новую задачу"""
    try:
        if request.parent_id:
            # Для подзадач используем проект родителя
            # (определяется автоматически в crud.py)
            task = taskflow.todoist.create_task_with_category(
                content=request.content,
                irga_category="Здоровье",  # будет переопределено
                due_string=request.due_string,
                priority=request.priority,
                parent_id=request.parent_id,
            )
        elif request.category:
            task = taskflow.todoist.create_task_with_category(
                content=request.content,
                irga_category=request.category,
                due_string=request.due_string,
                priority=request.priority,
                parent_id=request.parent_id,
            )
        else:
            result = taskflow.process_message(request.content)
            if (
                result["status"] == "success"
                and result["action"] == "task_created"
            ):
                task = result["task"]
            else:
                raise HTTPException(
                    status_code=400,
                    detail=result.get("message", "Ошибка создания задачи"),
                )

        return {"status": "success", "task": task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/{task_id}/subtasks")
async def get_subtasks(
    task_id: str, x_todoist_token: Optional[str] = Header(None)  # noqa: B008
):
    """Получить подзадачи"""
    try:
        if x_todoist_token:
            from client import TodoistClient

            client = TodoistClient(x_todoist_token)
        else:
            client = taskflow.todoist.client

        subtasks = client.get_subtasks(task_id)
        return {"status": "success", "subtasks": subtasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str, x_todoist_token: Optional[str] = Header(None)  # noqa: B008
):
    """Удалить задачу"""
    try:
        if x_todoist_token:
            from crud import TaskFlowTodoist

            user_todoist = TaskFlowTodoist(x_todoist_token)
        else:
            user_todoist = taskflow.todoist

        user_todoist.delete_task(task_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tasks/reschedule-overdue")
async def reschedule_overdue_tasks(
    x_todoist_token: Optional[str] = Header(None),  # noqa: B008
):
    """Перенести просроченные задачи на сегодня"""
    try:
        if x_todoist_token:
            from crud import TaskFlowTodoist

            user_todoist = TaskFlowTodoist(x_todoist_token)
        else:
            user_todoist = taskflow.todoist

        # Получаем просроченные задачи
        overdue = user_todoist.get_overdue_tasks()

        if not overdue:
            return {
                "status": "success",
                "message": "Нет просроченных задач",
                "count": 0,
            }

        # Переносим на сегодня
        count = user_todoist.reschedule_overdue_to_tomorrow()

        return {
            "status": "success",
            "message": f"Перенесено {count} задач(и) на сегодня",
            "count": count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/categories")
async def get_categories():
    """Получить список категорий Irga"""
    categories = [
        {"id": 1, "name": "Деньги", "emoji": "💰"},
        {"id": 2, "name": "Семья", "emoji": "👫"},
        {"id": 3, "name": "Здоровье", "emoji": "💪"},
        {"id": 4, "name": "Взаимоотношения", "emoji": "💕"},
        {"id": 5, "name": "Духовность и развитие личности", "emoji": "📚"},
    ]
    return {"status": "success", "categories": categories}


# Запуск сервера
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

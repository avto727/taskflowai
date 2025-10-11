"""
TaskFlowAI Backend API
FastAPI сервер для подключения клиентов
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Добавляем пути для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'irga'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'todoist'))

from taskflow_integration import TaskFlowAI

# Создаём FastAPI приложение
app = FastAPI(
    title="TaskFlowAI API",
    description="Умный таск-менеджер на базе Todoist с ИИ-автоматизацией",
    version="1.0.0"
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

# Импортируем модели
from models import MessageRequest, TaskRequest, TaskUpdate

# Эндпоинты
@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "TaskFlowAI Backend API",
        "version": "1.0.0",
        "docs": "/docs"
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

from fastapi import Header

@app.get("/tasks")
async def get_tasks(
    category: Optional[str] = None,
    time_filter: Optional[str] = None,
    x_todoist_token: Optional[str] = Header(None)
):
    """
    Получить список задач
    
    Args:
        category: Категория Irga (например, 'Здоровье')
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
            # Фильтр по категории и времени
            cat_tasks = user_todoist.get_tasks_by_category(category)
            from datetime import datetime, timedelta
            
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            week_end = today + timedelta(days=7)
            
            tasks = []
            for task in cat_tasks:
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
                        tasks.append(task)
                    elif time_filter == 'tomorrow' and due_date == tomorrow:
                        tasks.append(task)
                    elif time_filter == 'week' and today <= due_date <= week_end:
                        tasks.append(task)
                except:
                    continue
        elif category:
            tasks = user_todoist.get_tasks_by_category(category)
        elif time_filter:
            # Фильтр только по времени
            all_tasks = user_todoist.get_all_tasks()
            from datetime import datetime, timedelta
            
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            week_end = today + timedelta(days=7)
            
            tasks = []
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
                        tasks.append(task)
                    elif time_filter == 'tomorrow' and due_date == tomorrow:
                        tasks.append(task)
                    elif time_filter == 'week' and today <= due_date <= week_end:
                        tasks.append(task)
                except:
                    continue
        else:
            tasks = user_todoist.get_all_tasks()
        
        return {
            "status": "success",
            "tasks": tasks,
            "total": len(tasks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks")
async def create_task(request: TaskRequest):
    """Создать новую задачу"""
    try:
        if request.parent_id:
            result = taskflow.irga.analyze_task(request.content)
            category = result.get('category', 'Здоровье')
            task = taskflow.todoist.create_task_with_category(
                content=request.content,
                irga_category=category,
                due_string=request.due_string,
                priority=request.priority,
                parent_id=request.parent_id
            )
        elif request.category:
            task = taskflow.todoist.create_task_with_category(
                content=request.content,
                irga_category=request.category,
                due_string=request.due_string,
                priority=request.priority,
                parent_id=request.parent_id
            )
        else:
            result = taskflow.process_message(request.content)
            if result['status'] == 'success' and \
               result['action'] == 'task_created':
                task = result['task']
            else:
                raise HTTPException(
                    status_code=400,
                    detail=result.get('message',
                                     'Ошибка создания задачи')
                )
        
        return {"status": "success", "task": task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}/subtasks")
async def get_subtasks(
    task_id: str,
    x_todoist_token: Optional[str] = Header(None)
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
    task_id: str,
    x_todoist_token: Optional[str] = Header(None)
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

@app.get("/categories")
async def get_categories():
    """Получить список категорий Irga"""
    categories = [
        {"id": 1, "name": "Деньги", "emoji": "💰"},
        {"id": 2, "name": "Семья", "emoji": "👨👩👧👦"},
        {"id": 3, "name": "Здоровье", "emoji": "💪"},
        {"id": 4, "name": "Взаимоотношения", "emoji": "💕"},
        {"id": 5, "name": "Духовность и развитие личности", "emoji": "📚"}
    ]
    return {"status": "success", "categories": categories}

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
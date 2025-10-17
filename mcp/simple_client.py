"""
Simple Ollama client without complications
"""

import ollama
from .todoist_tools import TodoistMCP


class SimpleOllamaClient:
    def __init__(self, api_token: str, model: str = "qwen2.5:7b"):
        self.model = model
        self.todoist = TodoistMCP(api_token)

    def chat(self, message: str) -> str:
        """Chat with manual tool detection"""
        try:
            message_lower = message.lower()
            
            # Delete task
            if any(word in message_lower for word in ["удали", "стери"]):
                return self._handle_delete_task(message)
            
            # Complete task
            if any(word in message_lower for word in ["заверши", "выполни", "готово"]):
                return self._handle_complete_task(message)
            
            # Create subtask (more specific, check first)
            if "подзадач" in message_lower:
                return self._handle_create_subtask(message)
            
            # Show tasks by project (more specific, check first)
            if "проект" in message_lower and "задач" in message_lower:
                return self._handle_show_tasks_by_project(message)
            
            # Show life areas (projects)
            if any(word in message_lower for word in ["проект", "категори", "область", "жизн"]):
                return self._handle_show_life_areas(message)
            
            # Show tasks
            if any(word in message_lower for word in ["покажи", "список", "задач"]):
                return self._handle_show_tasks(message)
            
            # Reschedule overdue
            if any(word in message_lower for word in ["перенос", "просроч"]):
                return self._handle_reschedule_overdue(message)
            
            # Create task - check for action verbs or task-like content
            if (any(word in message_lower for word in ["создай", "добавь", "запиши"]) or
                self._is_task_content(message)):
                return self._handle_create_task(message)
            
            # Regular chat with Russian system prompt
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Всегда отвечай на русском языке. Ты умный помощник по управлению задачами."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )
            return response["message"]["content"]
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def _handle_show_tasks(self, message: str) -> str:
        """Handle task listing requests"""
        # Определяем фильтр по времени
        filter_expr = None
        message_lower = message.lower()
        
        if "сегодня" in message_lower:
            filter_expr = "today"
        elif "завтра" in message_lower:
            filter_expr = "tomorrow"
        
        result = self.todoist.get_tasks(filter_expr=filter_expr)
        if result["success"]:
            tasks = result["tasks"]
            if not tasks:
                return "📋 У вас нет задач"
            
            # Разделяем на родительские задачи и подзадачи
            parent_tasks = [t for t in tasks if not t.get("parent_id")]
            subtasks = [t for t in tasks if t.get("parent_id")]
            
            # Группируем по датам
            grouped_by_date = self._group_tasks_by_date(parent_tasks, subtasks)
            
            response = f"📋 Ваши задачи ({len(tasks)}):\n\n"
            
            counter = 1
            for date_key in sorted(grouped_by_date.keys()):
                date_label, tasks_for_date = grouped_by_date[date_key]
                
                # Заголовок даты
                response += f"<b>📅 {date_label}</b>\n"
                
                # Задачи этой даты
                for parent, parent_subtasks in tasks_for_date:
                    time_str = self._format_task_time(parent)
                    response += f"☐ {counter}. {parent['content']}{time_str}\n"
                    counter += 1
                    
                    # Подзадачи
                    for subtask in parent_subtasks:
                        subtask_time_str = self._format_task_time(subtask)
                        response += f"  ☐ ↳ {subtask['content']}{subtask_time_str}\n"
                
                response += "\n"
            
            return response
        else:
            return f"❌ Ошибка: {result['error']}"
    
    def _handle_create_task(self, message: str) -> str:
        """Handle task creation requests"""
        content = message
        for word in ["создай задачу:", "добавь задачу:", "запиши:"]:
            if word in message.lower():
                content = message.split(":", 1)[1].strip()
                break
        
        # Parse date and time from content
        due_string = self._parse_due_date(content)
        
        result = self.todoist.create_task(content=content, due_string=due_string)
        if result["success"]:
            time_info = f" на {due_string}" if due_string else ""
            return f"✅ Задача создана{time_info}: {content}"
        else:
            return f"❌ Ошибка: {result['error']}"
    
    def _handle_complete_task(self, message: str) -> str:
        """Handle task completion requests"""
        # Try to extract task ID from message
        import re
        task_id_match = re.search(r'\b\d{10}\b', message)
        
        if task_id_match:
            task_id = task_id_match.group()
            result = self.todoist.complete_task(task_id)
            if result["success"]:
                return f"✅ Задача {task_id} завершена!"
            else:
                return f"❌ Ошибка: {result['error']}"
        else:
            return "❌ Не найден ID задачи. Пример: 'Заверши задачу 9644708245'"
    
    def _handle_delete_task(self, message: str) -> str:
        """Handle task deletion requests"""
        import re
        task_id_match = re.search(r'\b\d{10}\b', message)
        
        if task_id_match:
            task_id = task_id_match.group()
            result = self.todoist.delete_task(task_id)
            if result["success"]:
                return f"✅ Задача {task_id} удалена!"
            else:
                return f"❌ Ошибка: {result['error']}"
        else:
            return "❌ Не найден ID задачи. Пример: 'Удали задачу 9644708245'"
    
    def _handle_show_life_areas(self, message: str) -> str:
        """Handle life areas listing requests"""
        result = self.todoist.get_projects()
        if result["success"]:
            life_areas = result["projects"]
            response = f"🌟 Области жизни ({result['count']}):\n\n"
            for area in life_areas:
                response += f"- {area['name']} (ID: {area['id']})\n"
            return response
        else:
            return f"❌ Ошибка: {result['error']}"
    
    def _handle_show_tasks_by_project(self, message: str) -> str:
        """Handle tasks by project requests"""
        message_lower = message.lower()
        
        # Find project by name
        project_names = {
            "здоровь": "💪 Здоровье",
            "деньг": "💰 Деньги",
            "семь": "👨👩👧👦 Семья",
            "отношен": "💕 Отношения",
            "развит": "📚 Развитие"
        }
        
        project_name = None
        for key, name in project_names.items():
            if key in message_lower:
                project_name = name
                break
        
        if not project_name:
            return "❌ Не найден проект. Пример: 'Покажи задачи проекта здоровье'"
        
        # Get project ID
        projects_result = self.todoist.get_projects()
        if not projects_result["success"]:
            return f"❌ Ошибка получения проектов: {projects_result['error']}"
        
        project_id = None
        for project in projects_result["projects"]:
            if project_name.lower() in project["name"].lower():
                project_id = project["id"]
                break
        
        if not project_id:
            return f"❌ Проект '{project_name}' не найден"
        
        # Get tasks for project
        result = self.todoist.get_tasks(project_id=project_id)
        if result["success"]:
            tasks = result["tasks"]
            if not tasks:
                return f"🎉 В проекте '{project_name}' нет задач!"
            
            response = f"📂 Задачи проекта '{project_name}' ({len(tasks)}):\n\n"
            for i, task in enumerate(tasks, 1):
                response += f"{i}. {task['content']}\n"
            return response
        else:
            return f"❌ Ошибка: {result['error']}"
    
    def _handle_create_subtask(self, message: str) -> str:
        """Handle subtask creation requests"""
        import re
        
        # Extract parent task number and subtask content
        pattern = r"к задаче (\d+):?\s*(.+)"
        match = re.search(pattern, message, re.IGNORECASE)
        
        if not match:
            return "❌ Неверный формат. Пример: 'Добавь подзадачу к задаче 3: отжимания'"
        
        try:
            parent_number = int(match.group(1))
        except ValueError:
            return "❌ Номер задачи должен быть числом"
        
        subtask_content = match.group(2).strip()
        
        if not subtask_content:
            return "❌ Не указано содержание подзадачи"
        
        # Get all tasks to find parent by number
        tasks_result = self.todoist.get_tasks()
        if not tasks_result["success"]:
            return f"❌ Ошибка получения задач: {tasks_result['error']}"
        
        tasks = tasks_result["tasks"]
        
        if parent_number < 1 or parent_number > len(tasks):
            return f"❌ Номер задачи должен быть от 1 до {len(tasks)}"
        
        parent_task = tasks[parent_number - 1]
        parent_id = parent_task["id"]
        
        # Create subtask
        result = self.todoist.create_task(
            content=subtask_content,
            parent_id=parent_id
        )
        
        if result["success"]:
            return f"✅ Подзадача создана!\n\n📝 {subtask_content}\n↳ Родитель: {parent_task['content']}"
        else:
            return f"❌ Ошибка создания подзадачи: {result['error']}"
    
    def _parse_due_date(self, content: str) -> str:
        """Parse due date and time from task content"""
        from datetime import datetime, timedelta
        import re
        
        content_lower = content.lower()
        
        # Date parsing
        date_part = ""
        if "завтра" in content_lower:
            tomorrow = datetime.now() + timedelta(days=1)
            date_part = tomorrow.strftime("%Y-%m-%d")
        elif "послезавтра" in content_lower:
            day_after = datetime.now() + timedelta(days=2)
            date_part = day_after.strftime("%Y-%m-%d")
        elif "сегодня" in content_lower:
            today = datetime.now()
            date_part = today.strftime("%Y-%m-%d")
        else:
            # Check for specific date patterns (dd.mm, dd/mm, etc)
            date_match = re.search(r'(\d{1,2})[./](\d{1,2})', content)
            if date_match:
                day, month = date_match.groups()
                year = datetime.now().year
                try:
                    date_obj = datetime(year, int(month), int(day))
                    date_part = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    pass
        
        # Time parsing
        time_part = ""
        if "утром" in content_lower or "утро" in content_lower:
            time_part = self._get_free_morning_slot()
        elif "днем" in content_lower or "обед" in content_lower:
            time_part = self._get_free_afternoon_slot()
        elif "вечером" in content_lower or "вечер" in content_lower:
            time_part = self._get_free_evening_slot()
        elif "ночью" in content_lower or "ночь" in content_lower:
            time_part = self._get_free_night_slot()
        else:
            # Check for specific time (HH:MM, HH-MM)
            time_match = re.search(r'(\d{1,2})[:.-](\d{2})', content)
            if time_match:
                hour, minute = time_match.groups()
                time_part = f"{hour.zfill(2)}:{minute}"
        
        # Combine date and time
        if date_part and time_part:
            return f"{date_part} {time_part}"
        elif date_part:
            return date_part
        elif time_part:
            return f"today {time_part}"
        else:
            return ""
    
    def _get_free_morning_slot(self) -> str:
        """Get free morning slot (6-12)"""
        import random
        hour = random.choice([6, 7, 8, 9, 10, 11])
        return f"{hour:02d}:00"
    
    def _get_free_afternoon_slot(self) -> str:
        """Get free afternoon slot (12-16)"""
        import random
        hour = random.choice([12, 13, 14, 15])
        return f"{hour:02d}:00"
    
    def _get_free_evening_slot(self) -> str:
        """Get free evening slot (16-22)"""
        import random
        hour = random.choice([16, 17, 18, 19, 20, 21])
        return f"{hour:02d}:00"
    
    def _get_free_night_slot(self) -> str:
        """Get free night slot (22-6)"""
        import random
        hour = random.choice([22, 23, 0, 1, 2, 3, 4, 5])
        return f"{hour:02d}:00"
    
    def _is_task_content(self, message: str) -> bool:
        """Check if message looks like task content"""
        message_lower = message.lower()
        
        # Task action verbs
        task_verbs = [
            "купить", "заплатить", "позвонить", "встретить", "сходить",
            "записать", "отправить", "проверить", "сделать", "выполнить",
            "забрать", "доставить", "оплатить", "подготовить", "организовать",
            "зайти", "пойти", "поехать", "посетить", "навестить"
        ]
        
        # Check if starts with task verb
        for verb in task_verbs:
            if message_lower.startswith(verb):
                return True
        
        # Check if contains time indicators (likely a task)
        time_indicators = [
            "завтра", "сегодня", "вечером", "утром", "днем", "ночью",
            "в ", "до ", "после ", "через ", ":", "-"
        ]
        
        # Check for places (likely tasks)
        places = [
            "аптек", "магази", "банк", "офис", "врач", "работ",
            "дом", "школ", "университет", "поликлиник", "больниц"
        ]
        
        has_verb = any(verb in message_lower for verb in task_verbs)
        has_time = any(indicator in message_lower for indicator in time_indicators)
        has_place = any(place in message_lower for place in places)
        
        # Task if: (verb + time) OR (verb + place) OR starts with verb
        return (has_verb and has_time) or (has_verb and has_place) or any(message_lower.startswith(verb) for verb in task_verbs)
    
    def _group_tasks_by_date(self, parent_tasks, subtasks):
        """Group tasks by date"""
        from datetime import datetime, date, timedelta
        
        grouped = {}
        
        for parent in parent_tasks:
            # Определяем дату задачи
            due = parent.get("due")
            if due and due.get("date"):
                task_date = due.get("date").split("T")[0]
                try:
                    dt = datetime.fromisoformat(task_date)
                    today = date.today()
                    
                    if dt.date() == today:
                        date_key = "1_today"
                        date_label = "Сегодня"
                    elif dt.date() == (today + timedelta(days=1)):
                        date_key = "2_tomorrow"
                        date_label = "Завтра"
                    else:
                        date_key = f"3_{task_date}"
                        date_label = dt.strftime("%d.%m.%Y")
                except:
                    date_key = "9_no_date"
                    date_label = "Без даты"
            else:
                date_key = "9_no_date"
                date_label = "Без даты"
            
            # Находим подзадачи для этой родительской задачи
            parent_subtasks = [s for s in subtasks if s.get("parent_id") == parent["id"]]
            
            if date_key not in grouped:
                grouped[date_key] = (date_label, [])
            
            grouped[date_key][1].append((parent, parent_subtasks))
        
        return grouped
    
    def _handle_reschedule_overdue(self, message: str) -> str:
        """Handle rescheduling overdue tasks"""
        from datetime import datetime, date
        
        # Получаем все задачи
        result = self.todoist.get_tasks()
        if not result["success"]:
            return f"❌ Ошибка: {result['error']}"
        
        tasks = result["tasks"]
        today = date.today()
        overdue_tasks = []
        
        # Находим просроченные задачи
        for task in tasks:
            due = task.get("due")
            if due and due.get("date"):
                try:
                    task_date = datetime.fromisoformat(due.get("date").split("T")[0]).date()
                    if task_date < today:
                        overdue_tasks.append(task)
                except:
                    continue
        
        if not overdue_tasks:
            return "✅ У вас нет просроченных задач!"
        
        # Переносим каждую задачу на сегодня
        updated_count = 0
        for task in overdue_tasks:
            due = task.get("due")
            
            # Сохраняем время, меняем только дату
            if due.get("datetime"):
                # Если есть время - сохраняем его
                time_part = due.get("datetime").split("T")[1]
                new_due = f"today {time_part.split('+')[0][:5]}"
            elif due.get("string") and any(t in due.get("string", "") for t in [":", "утро", "вечер", "днем"]):
                # Если есть текстовое время
                time_part = due.get("string", "")
                for word in ["завтра", "вчера", "понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]:
                    time_part = time_part.replace(word, "сегодня")
                new_due = time_part.strip()
            else:
                # Просто на сегодня
                new_due = "today"
            
            # Обновляем задачу
            update_result = self.todoist.update_task(task["id"], due_string=new_due)
            if update_result["success"]:
                updated_count += 1
        
        return f"✅ Перенесено {updated_count} задач(и) на сегодня!"
    
    def _format_task_time(self, task: dict) -> str:
        """Format task time for display"""
        due = task.get("due")
        if not due:
            return ""
        
        # Если есть datetime, извлекаем только время
        datetime_str = due.get("datetime")
        if datetime_str:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
                time_part = dt.strftime("%H:%M")
                return f" 🕒 {time_part}"
            except:
                pass
        
        # Проверяем due_string на наличие только времени (без даты)
        due_string = due.get("string", "")
        if due_string:
            # Исключаем строки с датами (2025-10-16)
            if not any(char.isdigit() and "-" in due_string for char in due_string):
                # Оставляем только если это не дата
                return f" 🕒 {due_string}"
        
        return ""
    
    def get_life_areas(self):
        """Get all life areas (alias for get_projects)"""
        result = self.todoist.get_projects()
        if result["success"]:
            return result["projects"]
        return []
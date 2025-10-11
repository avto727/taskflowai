"""
Простой Telegram бот для TaskFlowAI
Подключается к Backend API вместо SQLite
"""
import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv

from api_client import TaskFlowAPIClient

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# БД для токенов
import sqlite3
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 
                       'users.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            todoist_token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_token(telegram_id: int, todoist_token: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (telegram_id, todoist_token)
        VALUES (?, ?)
    ''', (telegram_id, todoist_token))
    conn.commit()
    conn.close()

def get_token(telegram_id: int) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT todoist_token FROM users WHERE telegram_id = ?',
        (telegram_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def delete_token(telegram_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM users WHERE telegram_id = ?',
        (telegram_id,)
    )
    conn.commit()
    conn.close()

init_db()

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

class AuthStates(StatesGroup):
    waiting_for_token = State()

class DeleteStates(StatesGroup):
    waiting_for_number = State()

class SubtaskStates(StatesGroup):
    waiting_for_parent_id = State()
    waiting_for_content = State()

def get_api_client(telegram_id: int):
    token = get_token(telegram_id)
    if token:
        return TaskFlowAPIClient(todoist_token=token)
    return None

@dp.message(Command("auth"))
async def auth_handler(message: Message, state: FSMContext):
    await state.set_state(AuthStates.waiting_for_token)
    await message.answer(
        "🔐 <b>Авторизация в Todoist</b>\n\n"
        "Отправьте ваш Todoist API token.\n\n"
        "Как получить токен:\n"
        "1. https://todoist.com/app/settings/integrations "
        "→ \"Для разработчиков\"\n"
        "2. Скопируйте API token\n"
        "3. Отправьте его мне\n\n"
        "Отмена: /cancel",
        parse_mode="HTML"
    )

@dp.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Операция отменена")

@dp.message(AuthStates.waiting_for_token)
async def token_handler(message: Message, state: FSMContext):
    text = message.text.strip()
    
    # Игнорируем эмодзи кнопки меню
    menu_emojis = ['❓', '📋', '📂', '🏠', '⚙️']
    if any(emoji in text for emoji in menu_emojis):
        return
    
    # Проверка длины токена (минимум 40 символов)
    if len(text) < 40:
        await message.answer(
            "❌ Токен слишком короткий\n"
            "Todoist API token должен быть длиннее.\n\n"
            "Попробуйте ещё раз или /cancel"
        )
        return
    
    token = text
    
    api = TaskFlowAPIClient(todoist_token=token)
    if not api.health_check():
        await message.answer(
            "❌ Неверный токен или API недоступен\n"
            "Попробуйте ещё раз или /cancel"
        )
        return
    
    save_token(message.from_user.id, token)
    await state.clear()
    
    await message.answer(
        "✅ <b>Авторизация успешна!</b>\n\n"
        "⚠️ Удалите сообщение с токеном для безопасности!\n\n"
        "Теперь вы можете пользоваться ботом.\n\n"
        "Выход: /logout",
        parse_mode="HTML"
    )

@dp.message(Command("logout"))
async def logout_handler(message: Message):
    delete_token(message.from_user.id)
    await message.answer("👋 Вы вышли из аккаунта")

@dp.message(Command("start"))
async def start_handler(message: Message):
    api = get_api_client(message.from_user.id)
    
    if not api:
        await message.answer(
            "👋 <b>Добро пожаловать в TaskFlowAI!</b>\n\n"
            "Для начала работы авторизуйтесь:\n"
            "/auth - подключить Todoist",
            parse_mode="HTML"
        )
        return
    
    if not api.health_check():
        await message.answer(
            "❌ Backend API недоступен\n"
            "Запустите: python backend/api/main.py"
        )
        return
    
    await message.answer(
        "🚀 <b>TaskFlowAI Bot</b>\n\n"
        "Умный таск-менеджер с ИИ!\n\n"
        "📝 Просто напишите задачу:\n"
        "• Купить молоко\n"
        "• Позвонить врачу завтра\n"
        "• Оплатить интернет\n\n"
        "🤖 ИИ автоматически определит категорию и время\n\n"
        "Команды:\n"
        "/tasks - показать задачи\n"
        "/categories - категории\n"
        "/help - помощь",
        parse_mode="HTML"
    )

@dp.message(Command("tasks"))
async def tasks_handler(message: Message, state: FSMContext):
    api = get_api_client(message.from_user.id)
    if not api:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return
    
    result = api.get_tasks()
    
    if result.get("status") != "success":
        await message.answer(
            f"❌ Ошибка: {result.get('message', 'Неизвестная ошибка')}"
        )
        return
    
    tasks = result["tasks"]
    
    if not tasks:
        await message.answer("📝 Задач пока нет. Добавьте первую!")
        return
    
    # Сохраняем для пагинации
    await state.update_data(all_tasks=tasks, tasks_page=0)
    
    text = f"📋 <b>Ваши задачи ({len(tasks)}):</b>\n\n"
    
    # Группировка по дням
    from datetime import datetime
    grouped = {}
    for task in tasks[:10]:
        due = task.get('due')
        if due:
            date_str = due.get('date', '').split('T')[0]
            full_str = due.get('string', '')
            if ' ' in full_str:
                parts = full_str.split(' ')
                if ':' in parts[-1]:
                    time_str = parts[-1]
                else:
                    time_str = ''
            else:
                time_str = ''
            
            if time_str:
                sort_key = date_str + 'T' + time_str
            else:
                sort_key = date_str + 'T99:99'
        else:
            date_str = 'Без даты'
            time_str = ''
            sort_key = '9999-99-99T99:99'
        
        if date_str not in grouped:
            grouped[date_str] = []
        grouped[date_str].append((task, time_str, sort_key))
    
    for date_str in sorted(grouped.keys()):
        if date_str != 'Без даты':
            text += f"<b>📅 {date_str}</b>\n"
        sorted_tasks = sorted(grouped[date_str], key=lambda x: x[2])
        for task, time_str, _ in sorted_tasks:
            time_part = f" 🕒 {time_str}" if time_str else ""
            indent = "    ↳ " if task.get('parent_id') else "  • "
            task_id = f" [#{task['id'][-4:]}]" if not task.get('parent_id') else ""
            text += f"{indent}{task['content']}{time_part}{task_id}\n"
        text += "\n"
    
    # Кнопка пагинации
    keyboard = None
    if len(tasks) > 10:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"Ещё ({len(tasks) - 10})",
                callback_data="tasks_more_1"
            )]
        ])
    
    await message.answer(text, parse_mode="HTML", 
                        reply_markup=keyboard)

@dp.message(Command("categories"))
async def categories_handler(message: Message):
    api = get_api_client(message.from_user.id)
    if not api:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return
    
    result = api.get_categories()
    
    if result.get("status") != "success":
        await message.answer(
            f"❌ Ошибка: {result.get('message', 'Неизвестная ошибка')}"
        )
        return
    
    categories = result["categories"]
    text = "📂 <b>Категории TaskFlowAI:</b>\n\n"
    
    for cat in categories:
        text += f"{cat['emoji']} {cat['name']}\n"
    
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("subtask"))
async def subtask_handler(message: Message, state: FSMContext):
    api = get_api_client(message.from_user.id)
    if not api:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return
    
    await state.set_state(SubtaskStates.waiting_for_parent_id)
    await message.answer(
        "📝 <b>Создание подзадачи</b>\n\n"
        "Отправьте ID родительской задачи\n"
        "(используйте /tasks чтобы увидеть ID)\n\n"
        "Отмена: /cancel",
        parse_mode="HTML"
    )

@dp.message(SubtaskStates.waiting_for_parent_id)
async def subtask_parent_handler(message: Message, state: FSMContext):
    parent_id = message.text.strip()
    await state.update_data(parent_id=parent_id)
    await state.set_state(SubtaskStates.waiting_for_content)
    await message.answer(
        "✍️ Отправьте текст подзадачи:\n\n"
        "Например: Отжимания 20 раз"
    )

@dp.message(SubtaskStates.waiting_for_content)
async def subtask_content_handler(message: Message, state: FSMContext):
    content = message.text.strip()
    data = await state.get_data()
    parent_id = data.get('parent_id')
    
    api = get_api_client(message.from_user.id)
    
    # Создаём подзадачу через API
    import requests
    try:
        response = requests.post(
            "http://localhost:8000/tasks",
            headers={'X-Todoist-Token': get_token(message.from_user.id)},
            json={
                "content": content,
                "parent_id": parent_id
            }
        )
        if response.status_code == 200:
            await message.answer(
                f"✅ <b>Подзадача создана!</b>\n\n"
                f"📝 {content}\n"
                f"↳ Родитель: {parent_id}",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                f"❌ Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}"
            )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    
    await state.clear()

@dp.message(Command("delete"))
async def delete_handler(message: Message, state: FSMContext):
    api = get_api_client(message.from_user.id)
    if not api:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return
    
    result = api.get_tasks()
    if result.get("status") != "success":
        await message.answer(
            f"❌ Ошибка: {result.get('message', 'Неизвестная ошибка')}"
        )
        return
    
    tasks = result["tasks"]
    if not tasks:
        await message.answer("📋 Задач нет")
        return
    
    # Сохраняем задачи в состояние
    await state.update_data(tasks=tasks, page=0)
    await state.set_state(DeleteStates.waiting_for_number)
    
    page = 0
    start = page * 10
    end = start + 10
    
    text = "🗑️ <b>Удаление задач:</b>\n\n"
    text += "Отправьте номер задачи:\n\n"
    
    for i in range(start, min(end, len(tasks))):
        text += f"{i + 1}. {tasks[i]['content'][:40]}\n"
    
    text += "\n\nОтмена: /cancel"
    
    # Кнопка "Ещё" если есть ещё задачи
    keyboard = None
    if len(tasks) > end:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"Ещё ({len(tasks) - end})",
                callback_data=f"delete_more_{page + 1}"
            )]
        ])
    
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

@dp.message(DeleteStates.waiting_for_number)
async def delete_number_handler(message: Message, state: FSMContext):
    try:
        num = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ Неверный номер. Отправьте число или /cancel"
        )
        return
    
    data = await state.get_data()
    tasks = data.get('tasks', [])
    
    if num < 1 or num > len(tasks):
        await message.answer(
            f"❌ Номер должен быть от 1 до {len(tasks)}"
        )
        return
    
    task = tasks[num - 1]
    api = get_api_client(message.from_user.id)
    
    # Удаляем через API
    import requests
    try:
        response = requests.delete(
            f"http://localhost:8000/tasks/{task['id']}",
            headers={'X-Todoist-Token': get_token(message.from_user.id)}
        )
        if response.status_code == 200:
            await message.answer(
                f"✅ Удалено: {task['content']}"
            )
        else:
            await message.answer("❌ Ошибка удаления")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    
    await state.clear()

@dp.callback_query(lambda c: c.data.startswith('delete_more_'))
async def delete_more_callback(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split('_')[-1])
    data = await state.get_data()
    tasks = data.get('tasks', [])
    
    start = page * 10
    end = start + 10
    
    text = "🗑️ <b>Удаление задач:</b>\n\n"
    text += "Отправьте номер задачи:\n\n"
    
    for i in range(start, min(end, len(tasks))):
        text += f"{i + 1}. {tasks[i]['content'][:40]}\n"
    
    text += "\n\nОтмена: /cancel"
    
    keyboard = None
    if len(tasks) > end:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"Ещё ({len(tasks) - end})",
                callback_data=f"delete_more_{page + 1}"
            )]
        ])
    
    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith('tasks_more_'))
async def tasks_more_callback(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split('_')[-1])
    data = await state.get_data()
    tasks = data.get('all_tasks', [])
    
    start = page * 10
    end = start + 10
    
    text = f"📋 <b>Ваши задачи ({len(tasks)}):</b>\n\n"
    
    from datetime import datetime
    grouped = {}
    for task in tasks[start:end]:
        due = task.get('due')
        if due:
            date_str = due.get('date', '').split('T')[0]
            full_str = due.get('string', '')
            if ' ' in full_str:
                parts = full_str.split(' ')
                if ':' in parts[-1]:
                    time_str = parts[-1]
                else:
                    time_str = ''
            else:
                time_str = ''
            
            if time_str:
                sort_key = date_str + 'T' + time_str
            else:
                sort_key = date_str + 'T99:99'
        else:
            date_str = 'Без даты'
            time_str = ''
            sort_key = '9999-99-99T99:99'
        
        if date_str not in grouped:
            grouped[date_str] = []
        grouped[date_str].append((task, time_str, sort_key))
    
    for date_str in sorted(grouped.keys()):
        if date_str != 'Без даты':
            text += f"<b>📅 {date_str}</b>\n"
        sorted_tasks = sorted(grouped[date_str], key=lambda x: x[2])
        for task, time_str, _ in sorted_tasks:
            time_part = f" 🕒 {time_str}" if time_str else ""
            indent = "    ↳ " if task.get('parent_id') else "  • "
            task_id = f" [#{task['id'][-4:]}]" if not task.get('parent_id') else ""
            text += f"{indent}{task['content']}{time_part}{task_id}\n"
        text += "\n"
    
    keyboard = None
    if len(tasks) > end:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"Ещё ({len(tasks) - end})",
                callback_data=f"tasks_more_{page + 1}"
            )]
        ])
    
    await callback.message.edit_text(text, parse_mode="HTML",
                                     reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith('category_more_'))
async def category_more_callback(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split('_')[-1])
    data = await state.get_data()
    tasks = data.get('category_tasks', [])
    cat_emoji = data.get('category_name', '')
    
    start = page * 10
    end = start + 10
    
    response = f"{cat_emoji} ({len(tasks)}):\n\n"
    
    from datetime import datetime
    grouped = {}
    for task in tasks[start:end]:
        due = task.get('due')
        if due:
            date_str = due.get('date', '').split('T')[0]
            full_str = due.get('string', '')
            if ' ' in full_str:
                parts = full_str.split(' ')
                if ':' in parts[-1]:
                    time_str = parts[-1]
                else:
                    time_str = ''
            else:
                time_str = ''
            
            if time_str:
                sort_key = date_str + 'T' + time_str
            else:
                sort_key = date_str + 'T99:99'
        else:
            date_str = 'Без даты'
            time_str = ''
            sort_key = '9999-99-99T99:99'
        
        if date_str not in grouped:
            grouped[date_str] = []
        grouped[date_str].append((task, time_str, sort_key))
    
    for date_str in sorted(grouped.keys()):
        if date_str != 'Без даты':
            response += f"<b>📅 {date_str}</b>\n"
        sorted_tasks = sorted(grouped[date_str], key=lambda x: x[2])
        for task, time_str, _ in sorted_tasks:
            time_part = f" 🕒 {time_str}" if time_str else ""
            indent = "    ↳ " if task.get('parent_id') else "  • "
            task_id = f" [#{task['id'][-4:]}]" if not task.get('parent_id') else ""
            response += f"{indent}{task['content']}{time_part}{task_id}\n"
        response += "\n"
    
    keyboard = None
    if len(tasks) > end:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"Ещё ({len(tasks) - end})",
                callback_data=f"category_more_{page + 1}"
            )]
        ])
    
    await callback.message.edit_text(
        response, parse_mode="HTML", reply_markup=keyboard
    )
    await callback.answer()

@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "🤖 <b>TaskFlowAI Bot - Помощь</b>\n\n"
        "📝 <b>Добавление задач:</b>\n"
        "Просто напишите что нужно сделать:\n"
        "• Купить продукты\n"
        "• Позвонить маме завтра\n"
        "• Оплатить счета до пятницы\n\n"
        "🧠 <b>ИИ автоматически:</b>\n"
        "• Определит категорию (💰 Деньги, 👨👩👧👦 Семья)\n"
        "• Извлечёт дату и время\n"
        "• Создаст задачу в Todoist\n\n"
        "📱 <b>Команды:</b>\n"
        "/tasks - список задач\n"
        "/categories - категории\n"
        "/start - главное меню",
        parse_mode="HTML"
    )

@dp.message()
async def message_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        return
    
    api = get_api_client(message.from_user.id)
    if not api:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return
    
    text = message.text
    
    # 🤖 Обработка обращения "Ирга"
    if text.lower().startswith(('ирга', 'irga')):
        # Убираем обращение и запятую
        command = text[4:].strip()
        if command.startswith(','):
            command = command[1:].strip()
        
        command_lower = command.lower()
        
        # Команда: показать задачи
        if any(word in command_lower for word in ['покаж', 'список', 'задач', 'план']):
            await tasks_handler(message, state)
            return
        
        # Команда: создать подзадачу
        if 'подзадач' in command_lower:
            # Ищем ID родителя
            import re
            match = re.search(r'к задаче (\d+)', command_lower)
            if match:
                parent_id = match.group(1)
                # Ищем текст подзадачи после ":"
                if ':' in command:
                    content = command.split(':', 1)[1].strip()
                else:
                    content = command.split(parent_id, 1)[1].strip()
                
                # Создаём подзадачу
                import requests
                try:
                    response = requests.post(
                        "http://localhost:8000/tasks",
                        headers={'X-Todoist-Token': get_token(message.from_user.id)},
                        json={"content": content, "parent_id": parent_id}
                    )
                    if response.status_code == 200:
                        await message.answer(
                            f"✅ <b>Ирга:</b> Подзадача создана!\n\n"
                            f"📝 {content}\n"
                            f"↳ Родитель: {parent_id}",
                            parse_mode="HTML"
                        )
                    else:
                        await message.answer(
                            f"❌ <b>Ирга:</b> Ошибка создания"
                        )
                except Exception as e:
                    await message.answer(f"❌ <b>Ирга:</b> {e}")
                return
            else:
                await message.answer(
                    "🤔 <b>Ирга:</b> Укажите ID задачи\n\n"
                    "Пример: Ирга, создай подзадачу к задаче 12345: отжимания",
                    parse_mode="HTML"
                )
                return
        
        # Команда: удалить задачу
        if 'удал' in command_lower:
            await delete_handler(message, state)
            return
        
        # Команда: категории
        if 'категор' in command_lower:
            await categories_handler(message)
            return
        
        # Приветствие
        if any(word in command_lower for word in ['привет', 'здравств', 'добр']):
            import datetime
            hour = datetime.datetime.now().hour
            if hour < 12:
                greeting = "🌅 Доброе утро"
            elif hour < 18:
                greeting = "☀️ Добрый день"
            else:
                greeting = "🌆 Добрый вечер"
            
            await message.answer(
                f"{greeting}, Андрей Алексеевич!\n\n"
                f"🤖 <b>Ирга к вашим услугам!</b>\n\n"
                f"Чем могу помочь?",
                parse_mode="HTML"
            )
            return
        
        # Помощь
        if 'помощ' in command_lower or 'помог' in command_lower:
            await message.answer(
                "🤖 <b>Ирга - ваш умный помощник</b>\n\n"
                "🗣️ <b>Примеры команд:</b>\n\n"
                "• Ирга, покажи задачи\n"
                "• Ирга, запиши задачу: купить молоко\n"
                "• Ирга, создай подзадачу к задаче 123: отжимания\n"
                "• Ирга, удали задачу\n"
                "• Ирга, план на сегодня\n"
                "• Ирга, что по здоровью?\n\n"
                "💬 Говорите со мной как с человеком!",
                parse_mode="HTML"
            )
            return
        
        # Остальное - создание задачи
        text = command  # Продолжаем обработку как обычную задачу
    
    text = message.text
    
    # Обработка кнопок меню
    if '❓' in text and 'Помощь' in text:
        await help_handler(message)
        return
    
    if '🗑' in text or 'Удалить' in text:
        await delete_handler(message, state)
        return
    
    # Игнорируем остальные эмодзи кнопки меню
    menu_emojis = ['📋', '📂', '🏠', '⚙️']
    if any(emoji in text for emoji in menu_emojis):
        return
    
    # Умная обработка вопросов и команд
    text_lower = text.lower()
    
    # Паттерны: показать задачи
    if any(word in text_lower for word in ['что', 'покажи', 'список', 'план']):
        # Определяем фильтр по времени
        time_filter = None
        if 'сегодня' in text_lower:
            time_filter = 'today'
        elif 'завтра' in text_lower:
            time_filter = 'tomorrow'
        elif 'недел' in text_lower:
            time_filter = 'week'
        
        # "Что на сегодня?", "Покажи план", "План на сегодня"
        if any(word in text_lower for word in ['сегодня', 'завтра', 'недел', 'план', 'дела', 'задач']):
            result = api.get_tasks(time_filter=time_filter)
            if result.get("status") == "success":
                tasks = result["tasks"]
                if not tasks:
                    await message.answer(
                        "🎉 <b>Отлично!</b>\n\n"
                        "Задач на сегодня нет!\n"
                        "Можете отдохнуть или запланировать что-то новое 😊"
                    )
                    return
                
                # Дружелюбное приветствие
                import datetime
                hour = datetime.datetime.now().hour
                if hour < 12:
                    greeting = "🌅 Доброе утро!"
                elif hour < 18:
                    greeting = "☀️ Добрый день!"
                else:
                    greeting = "🌆 Добрый вечер!"
                
                # Заголовок в зависимости от фильтра
                if time_filter == 'today':
                    title = "План на сегодня"
                elif time_filter == 'tomorrow':
                    title = "План на завтра"
                elif time_filter == 'week':
                    title = "План на неделю"
                else:
                    title = "Все задачи"
                
                response = f"{greeting}\n\n"
                response += f"📋 <b>{title} ({len(tasks)}):</b>\n\n"
                
                # Группируем по дням
                from datetime import datetime
                grouped = {}
                for task in tasks[:10]:
                    due = task.get('due')
                    if due:
                        date_str = due.get('date', '').split('T')[0]
                        # Извлекаем время из string
                        full_str = due.get('string', '')
                        # Пример: "2025-10-05 13:55" или "завтра 09:00"
                        if ' ' in full_str:
                            parts = full_str.split(' ')
                            if ':' in parts[-1]:
                                time_str = parts[-1]
                            else:
                                time_str = ''
                        else:
                            time_str = ''
                        
                        if time_str:
                            sort_key = date_str + 'T' + time_str
                        else:
                            sort_key = date_str + 'T99:99'
                    else:
                        date_str = 'Без даты'
                        time_str = ''
                        sort_key = '9999-99-99T99:99'
                    
                    if date_str not in grouped:
                        grouped[date_str] = []
                    grouped[date_str].append((task, time_str, sort_key))
                
                # Выводим по дням
                for date_str in sorted(grouped.keys()):
                    if date_str != 'Без даты':
                        response += f"<b>📅 {date_str}</b>\n"
                    # Сортируем по времени
                    sorted_tasks = sorted(
                        grouped[date_str], key=lambda x: x[2]
                    )
                    for task, time_str, _ in sorted_tasks:
                        time_part = f" 🕒 {time_str}" if time_str else ""
                        indent = "    ↳ " if task.get('parent_id') else "  • "
                        task_id = f" [#{task['id'][-4:]}]" if not task.get('parent_id') else ""
                        response += f"{indent}{task['content']}{time_part}{task_id}\n"
                    response += "\n"
                
                if len(tasks) > 10:
                    response = response.rstrip() + f"\n\n... и ещё {len(tasks) - 10}"
                
                # Мотивация
                if len(tasks) <= 3:
                    response += "\n\nЛегкий день! 😊"
                elif len(tasks) <= 7:
                    response += "\n\nВы справитесь! 💪"
                else:
                    response += "\n\nМного дел, но вы сильны! 🔥"
                
                await message.answer(response, parse_mode="HTML")
                return
            else:
                await message.answer(
                    f"❌ Ошибка: {result.get('message', 'Неизвестная ошибка')}"
                )
                return
        
        # "Что по здоровью?", "Покажи задачи по деньгам"
        categories_map = {
            'здоровь': '💪 Здоровье',
            'деньг': '💰 Деньги',
            'семь': '👨👩👧👦 Семья',
            'отношен': '💕 Взаимоотношения',
            'развит': '📚 Духовность и развитие'
        }
        
        for key, cat_emoji in categories_map.items():
            if key in text_lower:
                cat_name = cat_emoji.split(' ', 1)[1]
                result = api.get_tasks(category=cat_name)
                if result.get("status") == "success":
                    tasks = result["tasks"]
                    if not tasks:
                        await message.answer(
                            f"{cat_emoji}\n\n"
                            f"Задач нет! Всё в порядке ✅",
                            parse_mode="HTML"
                        )
                        return
                    
                    # Сохраняем для пагинации
                    await state.update_data(
                        category_tasks=tasks,
                        category_name=cat_emoji,
                        category_page=0
                    )
                    
                    response = f"{cat_emoji} ({len(tasks)}):\n\n"
                    
                    # Группируем по дням
                    from datetime import datetime
                    grouped = {}
                    for task in tasks[:10]:
                        due = task.get('due')
                        if due:
                            date_str = due.get('date', '').split('T')[0]
                            full_str = due.get('string', '')
                            if ' ' in full_str:
                                parts = full_str.split(' ')
                                if ':' in parts[-1]:
                                    time_str = parts[-1]
                                else:
                                    time_str = ''
                            else:
                                time_str = ''
                            
                            if time_str:
                                sort_key = date_str + 'T' + time_str
                            else:
                                sort_key = date_str + 'T99:99'
                        else:
                            date_str = 'Без даты'
                            time_str = ''
                            sort_key = '9999-99-99T99:99'
                        
                        if date_str not in grouped:
                            grouped[date_str] = []
                        grouped[date_str].append((task, time_str, sort_key))
                    
                    for date_str in sorted(grouped.keys()):
                        if date_str != 'Без даты':
                            response += f"<b>📅 {date_str}</b>\n"
                        sorted_tasks = sorted(
                            grouped[date_str], key=lambda x: x[2]
                        )
                        for task, time_str, _ in sorted_tasks:
                            time_part = f" 🕒 {time_str}" if time_str else ""
                            indent = "    ↳ " if task.get('parent_id') else "  • "
                            task_id = f" [#{task['id'][-4:]}]" if not task.get('parent_id') else ""
                            response += f"{indent}{task['content']}{time_part}{task_id}\n"
                        response += "\n"
                    
                    # Кнопка Ещё
                    keyboard = None
                    if len(tasks) > 10:
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(
                                text=f"Ещё ({len(tasks) - 10})",
                                callback_data="category_more_1"
                            )]
                        ])
                    
                    await message.answer(
                        response, parse_mode="HTML",
                        disable_web_page_preview=True,
                        reply_markup=keyboard
                    )
                    return
                else:
                    await message.answer(
                        f"❌ Ошибка: {result.get('message', 'Неизвестная ошибка')}"
                    )
                    return
    
    # Общий вопрос - подсказка
    if text.strip().endswith('?'):
        await message.answer(
            "🤔 Могу помочь!\n\n"
            "Попробуйте:\n"
            "• Что на сегодня?\n"
            "• Что по здоровью?\n"
            "• Покажи план\n\n"
            "Или используйте /tasks"
        )
        return
    
    await message.answer("🧠 Анализирую сообщение...")
    
    result = api.analyze_message(text)
    
    if result.get("status") == "error":
        await message.answer(f"❌ Ошибка: {result.get('message')}")
        return
    
    if result.get("action") == "task_created":
        task = result["task"]
        category = result.get("category", "Неизвестно")
        
        # Дружелюбные варианты ответов
        import random
        greetings = [
            "✅ <b>Отлично!</b>",
            "✅ <b>Записал!</b>",
            "✅ <b>Готово!</b>",
            "✅ <b>Добавил!</b>"
        ]
        
        response = f"{random.choice(greetings)}\n\n"
        response += f"📝 {task['content']}\n"
        response += f"📂 {category}\n"
        
        if task.get("due"):
            response += f"📅 {task['due']['string']}\n"
        
        response += f"\n🔗 <a href='{task['url']}'>Открыть в Todoist</a>"
        
    elif result.get("action") == "task_completed":
        task = result["task"]
        import random
        congrats = [
            "🎉 <b>Отличная работа!</b>",
            "🎉 <b>Молодец!</b>",
            "🎉 <b>Здорово!</b>",
            "🎉 <b>Круто!</b>"
        ]
        response = f"{random.choice(congrats)}\n\n"
        response += f"✅ {task['content']}\n\n"
        response += "Продолжайте в том же духе! 💪"
        
    elif result.get("action") == "tasks_list":
        tasks = result["tasks"]
        total = result["total"]
        response = f"📋 <b>Найдено задач: {total}</b>\n\n"
        
        for i, task in enumerate(tasks[:5], 1):
            response += f"{i}. {task['content']}\n"
            
    else:
        response = "🤔 Не понял. Ответ API: " + str(result)
    
    await message.answer(
        response, parse_mode="HTML", disable_web_page_preview=True
    )

async def main():
    from aiogram.types import BotCommand
    
    # Устанавливаем команды меню
    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="auth", description="Авторизация"),
        BotCommand(command="tasks", description="Список задач"),
        BotCommand(command="subtask", description="Создать подзадачу"),
        BotCommand(command="categories", description="Категории"),
        BotCommand(command="delete", description="Удалить задачу"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="logout", description="Выход")
    ]
    await bot.set_my_commands(commands)
    
    logger.info("🚀 Запуск TaskFlowAI Telegram Bot")
    logger.info("✅ Бот запущен с поддержкой авторизации")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

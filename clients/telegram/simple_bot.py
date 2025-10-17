"""
Простой Telegram бот для TaskFlowAI
Подключается к Backend API вместо SQLite
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from dotenv import load_dotenv
import sys

# Добавляем пути для импорта модулей backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.simple_client import SimpleOllamaClient
from auth import init_db, save_token, get_token, delete_token

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

init_db()

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()


class AuthStates(StatesGroup):
    waiting_for_token = State()


class DeleteStates(StatesGroup):
    waiting_for_number = State()


@dp.message(DeleteStates.waiting_for_number)
async def delete_number_handler(message: Message, state: FSMContext):
    text = message.text.strip()
    
    # Check for cancel command
    if text.startswith('/cancel'):
        return  # Let cancel handler process it
    
    # Extract numbers from text
    import re
    numbers = re.findall(r'\d+', text)
    
    if not numbers:
        await message.answer("❌ Не найден номер. Попробуйте ещё раз:")
        return
    
    # Sort numbers in descending order to avoid index shifting
    sorted_numbers = sorted([int(n) for n in numbers], reverse=True)
    
    # Process each number
    for task_number in sorted_numbers:

        client = get_mcp_client(message.from_user.id)
        
        # Получаем все задачи
        result = client.todoist.get_tasks()
        if not result["success"]:
            await message.answer("❌ Ошибка получения задач")
            await state.clear()
            return
        
        # Используем только родительские задачи (как в /tasks)
        all_tasks = result["tasks"]
        parent_tasks = [t for t in all_tasks if not t.get("parent_id")]
        
        if task_number < 1 or task_number > len(parent_tasks):
            await message.answer(f"❌ Номер {task_number} должен быть от 1 до {len(parent_tasks)}")
            continue
        
        task_to_delete = parent_tasks[task_number - 1]
        
        # Удаляем задачу
        delete_result = client.todoist.delete_task(task_to_delete["id"])
        
        if delete_result["success"]:
            await message.answer(
                f"✅ <b>Задача {task_number} удалена!</b>\n\n"
                f"🗑️ {task_to_delete['content']}",
                parse_mode="HTML"
            )
        else:
            await message.answer(f"❌ Ошибка удаления {task_number}: {delete_result['error']}")
    
    await state.clear()


class SubtaskStates(StatesGroup):
    waiting_for_parent_id = State()
    waiting_for_content = State()


@dp.message(SubtaskStates.waiting_for_parent_id)
async def subtask_parent_handler(message: Message, state: FSMContext):
    text = message.text.strip()
    
    # Check for cancel command
    if text.startswith('/cancel'):
        return  # Let cancel handler process it
    
    try:
        parent_number = int(text)
    except ValueError:
        await message.answer("❌ Номер должен быть числом. Попробуйте ещё раз:")
        return

    client = get_mcp_client(message.from_user.id)
    
    # Получаем все задачи
    result = client.todoist.get_tasks()
    if not result["success"]:
        await message.answer("❌ Ошибка получения задач")
        await state.clear()
        return
    
    # Оставляем только родительские задачи
    parent_tasks = [t for t in result["tasks"] if not t.get("parent_id")]
    
    if parent_number < 1 or parent_number > len(parent_tasks):
        await message.answer(f"❌ Номер должен быть от 1 до {len(parent_tasks)}")
        return
    
    parent_task = parent_tasks[parent_number - 1]
    
    await state.update_data(parent_task=parent_task)
    await state.set_state(SubtaskStates.waiting_for_content)
    
    await message.answer(
        f"✅ Выбрана задача: <b>{parent_task['content']}</b>\n\n"
        "Введите текст подзадачи:",
        parse_mode="HTML"
    )


@dp.message(SubtaskStates.waiting_for_content)
async def subtask_content_handler(message: Message, state: FSMContext):
    content = message.text.strip()
    data = await state.get_data()
    parent_task = data.get("parent_task")
    
    client = get_mcp_client(message.from_user.id)
    
    # Создаём подзадачу
    result = client.todoist.create_task(
        content=content,
        parent_id=parent_task["id"]
    )
    
    if result["success"]:
        await message.answer(
            f"✅ <b>Подзадача создана!</b>\n\n"
            f"📝 {content}\n"
            f"↳ Родитель: {parent_task['content']}",
            parse_mode="HTML"
        )
    else:
        await message.answer(f"❌ Ошибка: {result['error']}")
    
    await state.clear()


def get_mcp_client(telegram_id: int):
    token = get_token(telegram_id)
    if token:
        return SimpleOllamaClient(token)
    return None


@dp.message(Command("auth"))
async def auth_handler(message: Message, state: FSMContext):
    await state.set_state(AuthStates.waiting_for_token)
    await message.answer(
        "🔐 <b>Авторизация в Todoist</b>\n\n"
        "Отправьте ваш Todoist API token.\n\n"
        "Как получить токен:\n"
        "1. https://todoist.com/app/settings/integrations "
        '→ "Для разработчиков"\n'
        "2. Скопируйте API token\n"
        "3. Отправьте его мне\n\n"
        "Отмена: /cancel",
        parse_mode="HTML",
    )


@dp.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Операция отменена")


@dp.message(AuthStates.waiting_for_token)
async def token_handler(message: Message, state: FSMContext):
    text = message.text.strip()

    # Игнорируем эмодзи кнопки меню
    menu_emojis = ["❓", "📋", "📂", "🏠", "⚙️"]
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

    # Simple token validation - just check length
    # MCP client will validate when used

    save_token(message.from_user.id, token)
    await state.clear()

    await message.answer(
        "✅ <b>Авторизация успешна!</b>\n\n"
        "⚠️ Удалите сообщение с токеном для безопасности!\n\n"
        "Теперь вы можете пользоваться ботом.\n\n"
        "Выход: /logout",
        parse_mode="HTML",
    )


@dp.message(Command("logout"))
async def logout_handler(message: Message):
    delete_token(message.from_user.id)
    await message.answer("👋 Вы вышли из аккаунта")


def get_main_keyboard():
    """Главная клавиатура бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 План на сегодня"),
                KeyboardButton(text="📅 План на завтра"),
            ],
            [
                KeyboardButton(text="🔄 Перенос просрочки"),
                KeyboardButton(text="✏️ Редактировать"),
            ],
        ],
        resize_keyboard=True,
    )
    return keyboard


@dp.message(Command("start"))
async def start_handler(message: Message):
    client = get_mcp_client(message.from_user.id)

    if not client:
        await message.answer(
            "👋 <b>Добро пожаловать в TaskFlowAI MCP!</b>\n\n"
            "Для начала работы авторизуйтесь:\n"
            "/auth - подключить Todoist",
            parse_mode="HTML",
        )
        return

    await message.answer(
        "🚀 <b>TaskFlowAI MCP Bot</b>\n\n"
        "Умный таск-менеджер с MCP + Ollama!\n\n"
        "📝 Просто общайтесь с ботом:\n"
        "• Покажи мои задачи\n"
        "• Создай задачу: купить молоко\n"
        "• Покажи задачи проекта здоровье\n\n"
        "🤖 MCP + Ollama понимают естественный язык!",
        parse_mode="HTML"
    )


@dp.message(Command("tasks"))
async def tasks_handler(message: Message, state: FSMContext):
    client = get_mcp_client(message.from_user.id)
    if not client:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return

    # Получаем задачи через MCP
    result = client.todoist.get_tasks()
    if not result["success"]:
        await message.answer(f"❌ Ошибка: {result['error']}")
        return
    
    tasks = result["tasks"]
    if not tasks:
        await message.answer("📋 У вас нет задач")
        return
    
    # Создаем inline клавиатуру
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    # Разделяем на родительские задачи и подзадачи
    parent_tasks = [t for t in tasks if not t.get("parent_id")]
    subtasks = [t for t in tasks if t.get("parent_id")]
    
    # Группируем по датам
    grouped_by_date = client._group_tasks_by_date(parent_tasks, subtasks)
    
    response = f"📋 Ваши задачи ({len(tasks)}):\n\n"
    keyboard_rows = []
    
    counter = 1
    for date_key in sorted(grouped_by_date.keys()):
        date_label, tasks_for_date = grouped_by_date[date_key]
        
        # Заголовок даты
        response += f"<b>📅 {date_label}</b>\n"
        
        # Задачи этой даты
        for parent, parent_subtasks in tasks_for_date:
            time_str = client._format_task_time(parent)
            
            # Строка с задачей и кнопкой
            response += f"☐ {counter}. {parent['content']}{time_str}"
            
            # Inline кнопка рядом с задачей
            keyboard_rows.append([
                InlineKeyboardButton(
                    text="✓",
                    callback_data=f"complete_{parent['id']}"
                )
            ])
            
            response += "\n"
            counter += 1
            
            # Подзадачи
            for subtask in parent_subtasks:
                subtask_time_str = client._format_task_time(subtask)
                
                response += f"  ☐ ↳ {subtask['content']}{subtask_time_str}"
                
                # Inline кнопка для подзадачи
                keyboard_rows.append([
                    InlineKeyboardButton(
                        text="✓",
                        callback_data=f"complete_{subtask['id']}"
                    )
                ])
                
                response += "\n"
        
        response += "\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    await message.answer(
        response, 
        parse_mode="HTML",
        reply_markup=keyboard
    )





@dp.message(Command("areas"))
@dp.message(Command("projects"))  # старая команда для совместимости
@dp.message(Command("categories"))  # старая команда для совместимости
async def life_areas_handler(message: Message):
    client = get_mcp_client(message.from_user.id)
    if not client:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return

    # Получаем области жизни через MCP
    result = client.todoist.get_projects()
    if result["success"]:
        life_areas = result["projects"]
        
        # Создаём клавиатуру с кнопками областей жизни
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for area in life_areas:
            if area["name"] != "Inbox":  # Пропускаем Inbox
                button = InlineKeyboardButton(
                    text=area["name"],
                    callback_data=f"life_area_{area['id']}"
                )
                keyboard.inline_keyboard.append([button])
        
        await message.answer(
            f"🌟 <b>Области жизни ({len(life_areas)-1}):</b>\n\n"
            "Выберите область для просмотра задач:",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        await message.answer(f"❌ Ошибка: {result['error']}")


@dp.message(Command("subtask"))
async def subtask_handler(message: Message, state: FSMContext):
    client = get_mcp_client(message.from_user.id)
    if not client:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return

    await state.set_state(SubtaskStates.waiting_for_parent_id)
    await message.answer(
        "📝 <b>Создание подзадачи</b>\n\n"
        "Введите номер задачи к которой хотите добавить подзадачу:\n\n"
        "Отмена: /cancel",
        parse_mode="HTML",
    )





@dp.message(Command("delete"))
async def delete_handler(message: Message, state: FSMContext):
    client = get_mcp_client(message.from_user.id)
    if not client:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return

    await state.set_state(DeleteStates.waiting_for_number)
    await message.answer(
        "🗑️ <b>Удаление задачи</b>\n\n"
        "Введите номер задачи для удаления:\n\n"
        "Используйте /tasks чтобы увидеть номера\n\n"
        "Отмена: /cancel",
        parse_mode="HTML"
    )





@dp.callback_query(lambda c: c.data.startswith("complete_"))
async def complete_task_callback(callback: CallbackQuery):
    task_id = callback.data.split("_", 1)[1]
    
    client = get_mcp_client(callback.from_user.id)
    if not client:
        await callback.answer("❌ Сначала авторизуйтесь: /auth")
        return
    
    # Завершаем задачу
    result = client.todoist.complete_task(task_id)
    
    if result["success"]:
        await callback.answer("✅ Задача выполнена!")
        # Обновляем список задач
        response = client.chat("Покажи мои задачи")
        await callback.message.edit_text(response, parse_mode="HTML")
    else:
        await callback.answer(f"❌ Ошибка: {result['error']}")


@dp.callback_query(lambda c: c.data.startswith("life_area_"))
async def life_area_callback(callback: CallbackQuery):
    area_id = callback.data.split("_", 2)[2]
    
    client = get_mcp_client(callback.from_user.id)
    if not client:
        await callback.answer("❌ Сначала авторизуйтесь: /auth")
        return
    
    # Получаем задачи области жизни
    result = client.todoist.get_tasks(project_id=area_id)
    
    if result["success"]:
        tasks = result["tasks"]
        
        # Находим название области жизни
        areas_result = client.todoist.get_projects()
        area_name = "Область жизни"
        if areas_result["success"]:
            for area in areas_result["projects"]:
                if area["id"] == area_id:
                    area_name = area["name"]
                    break
        
        if not tasks:
            text = f"🎉 В области '{area_name}' нет задач!"
        else:
            text = f"🌟 <b>{area_name}</b> ({len(tasks)} задач):\n\n"
            for i, task in enumerate(tasks, 1):
                text += f"{i}. {task['content']}\n"
        
        await callback.message.edit_text(text, parse_mode="HTML")
    else:
        await callback.message.edit_text(f"❌ Ошибка: {result['error']}")
    
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("delete_more_"))
async def delete_more_callback(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[-1])
    data = await state.get_data()
    tasks = data.get("tasks", [])

    start = page * 10
    end = start + 10

    text = "🗑️ <b>Удаление задач:</b>\n\n"
    text += "Отправьте номер задачи:\n\n"

    for i in range(start, min(end, len(tasks))):
        text += f"{i + 1}. {tasks[i]['content'][:40]}\n"

    text += "\n\nОтмена: /cancel"

    keyboard = None
    if len(tasks) > end:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"Ещё ({len(tasks) - end})",
                        callback_data=f"delete_more_{page + 1}",
                    )
                ]
            ]
        )

    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=keyboard
    )
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("tasks_more_"))
async def tasks_more_callback(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[-1])
    data = await state.get_data()
    tasks = data.get("all_tasks", [])

    start = page * 10
    end = start + 10

    text = f"📋 <b>Ваши задачи ({len(tasks)}):</b>\n\n"

    grouped = {}
    for task in tasks[start:end]:
        due = task.get("due")
        if due:
            date_str = due.get("date", "").split("T")[0]
            full_str = due.get("string", "")
            if " " in full_str:
                parts = full_str.split(" ")
                if ":" in parts[-1]:
                    time_str = parts[-1]
                else:
                    time_str = ""
            else:
                time_str = ""

            if time_str:
                sort_key = date_str + "T" + time_str
            else:
                sort_key = date_str + "T99:99"
        else:
            date_str = "Без даты"
            time_str = ""
            sort_key = "9999-99-99T99:99"

        if date_str not in grouped:
            grouped[date_str] = []
        grouped[date_str].append((task, time_str, sort_key))

    for date_str in sorted(grouped.keys()):
        if date_str != "Без даты":
            text += f"<b>📅 {date_str}</b>\n"
        sorted_tasks = sorted(grouped[date_str], key=lambda x: x[2])
        for task, time_str, _ in sorted_tasks:
            time_part = f" 🕒 {time_str}" if time_str else ""
            indent = "    ↳ " if task.get("parent_id") else "  • "
            task_id = (
                f" [#{task['id'][-4:]}]" if not task.get("parent_id") else ""
            )
            text += f"{indent}{task['content']}{time_part}{task_id}\n"
        text += "\n"

    keyboard = None
    if len(tasks) > end:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"Ещё ({len(tasks) - end})",
                        callback_data=f"tasks_more_{page + 1}",
                    )
                ]
            ]
        )

    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=keyboard
    )
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("category_more_"))
async def category_more_callback(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[-1])
    data = await state.get_data()
    tasks = data.get("category_tasks", [])
    cat_emoji = data.get("category_name", "")

    start = page * 10
    end = start + 10

    response = f"{cat_emoji} ({len(tasks)}):\n\n"

    grouped = {}
    for task in tasks[start:end]:
        due = task.get("due")
        if due:
            date_str = due.get("date", "").split("T")[0]
            full_str = due.get("string", "")
            if " " in full_str:
                parts = full_str.split(" ")
                if ":" in parts[-1]:
                    time_str = parts[-1]
                else:
                    time_str = ""
            else:
                time_str = ""

            if time_str:
                sort_key = date_str + "T" + time_str
            else:
                sort_key = date_str + "T99:99"
        else:
            date_str = "Без даты"
            time_str = ""
            sort_key = "9999-99-99T99:99"

        if date_str not in grouped:
            grouped[date_str] = []
        grouped[date_str].append((task, time_str, sort_key))

    for date_str in sorted(grouped.keys()):
        if date_str != "Без даты":
            response += f"<b>📅 {date_str}</b>\n"
        sorted_tasks = sorted(grouped[date_str], key=lambda x: x[2])
        for task, time_str, _ in sorted_tasks:
            time_part = f" 🕒 {time_str}" if time_str else ""
            indent = "    ↳ " if task.get("parent_id") else "  • "
            task_id = (
                f" [#{task['id'][-4:]}]" if not task.get("parent_id") else ""
            )
            response += f"{indent}{task['content']}{time_part}{task_id}\n"
        response += "\n"

    keyboard = None
    if len(tasks) > end:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"Ещё ({len(tasks) - end})",
                        callback_data=f"category_more_{page + 1}",
                    )
                ]
            ]
        )

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
        "/projects - проекты\n"
        "/start - главное меню",
        parse_mode="HTML",
    )


async def handle_irga_show_tasks(message: Message, command_lower: str, client):
    """Обработка команды 'покажи задачи' от Ирги"""
    time_filter = None
    if "сегодня" in command_lower:
        time_filter = "today"
    elif "завтра" in command_lower:
        time_filter = "tomorrow"
    elif "недел" in command_lower:
        time_filter = "week"

    if time_filter:
        result = api.get_tasks(time_filter=time_filter)
        if result.get("status") == "success":
            tasks = result["tasks"]
            title = "План на сегодня" if time_filter == "today" else "План"
            response = format_tasks_response(tasks, title)
            await message.answer(response, parse_mode="HTML")
        else:
            await message.answer("❌ Ошибка получения задач")
        return True
    return False


async def handle_irga_subtask(
    message: Message, command: str, command_lower: str
):
    """Обработка команды создания подзадачи от Ирги"""
    import re
    import requests

    match = re.search(r"к задаче (\d+)", command_lower)
    if match:
        parent_id = match.group(1)
        content = (
            command.split(":", 1)[1].strip()
            if ":" in command
            else command.split(parent_id, 1)[1].strip()
        )

        try:
            response = requests.post(
                "http://localhost:8000/tasks",
                headers={"X-Todoist-Token": get_token(message.from_user.id)},
                json={"content": content, "parent_id": parent_id},
            )
            if response.status_code == 200:
                await message.answer(
                    f"✅ <b>Ирга:</b> Подзадача создана!\n\n"
                    f"📝 {content}\n"
                    f"↳ Родитель: {parent_id}",
                    parse_mode="HTML",
                )
            else:
                await message.answer("❌ <b>Ирга:</b> Ошибка создания")
        except Exception as e:
            await message.answer(f"❌ <b>Ирга:</b> {e}")
    else:
        await message.answer(
            "🤔 <b>Ирга:</b> Укажите ID задачи\n\n"
            "Пример: Ирга, создай подзадачу к задаче 12345: отжимания",
            parse_mode="HTML",
        )


async def handle_irga_greeting(message: Message, command_lower: str):
    """Обработка приветствия от Ирги"""
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
        parse_mode="HTML",
    )


async def handle_irga_help(message: Message):
    """Обработка запроса помощи от Ирги"""
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
        parse_mode="HTML",
    )


# Command Registry для обработки "Ирга, ..."
IRGA_COMMAND_HANDLERS = [
    (["покаж", "список", "задач", "план"], "show_tasks"),
    (["подзадач"], "subtask"),
    (["удал"], "delete"),
    (["категор", "проект"], "categories"),
    (["привет", "здравств", "добр"], "greeting"),
    (["помощ", "помог"], "help"),
]


async def handle_menu_button(message: Message, text: str, api):
    """Обработка кнопок меню"""
    if "📋 План на сегодня" in text or "План на сегодня" in text:
        result = api.get_tasks(time_filter="today")
        if result.get("status") == "success":
            tasks = result["tasks"]
            response = format_tasks_response(tasks, "План на сегодня")
            await message.answer(response, parse_mode="HTML")
        else:
            await message.answer(
                f"❌ Ошибка: {result.get('message', 'Неизвестная ошибка')}"
            )
        return True

    if "📅 План на завтра" in text or "План на завтра" in text:
        result = api.get_tasks(time_filter="tomorrow")
        if result.get("status") == "success":
            tasks = result["tasks"]
            response = format_tasks_response(tasks, "План на завтра")
            await message.answer(response, parse_mode="HTML")
        else:
            await message.answer(
                f"❌ Ошибка: {result.get('message', 'Неизвестная ошибка')}"
            )
        return True

    if "🔄 Перенос просрочки" in text or "Перенос просрочки" in text:
        result = api.reschedule_overdue()
        if result.get("status") == "success":
            count = result.get("count", 0)
            if count == 0:
                await message.answer(
                    "✅ У вас нет просроченных задач!", parse_mode="HTML"
                )
            else:
                await message.answer(
                    f"✅ <b>Перенесено {count} задач(и) на сегодня</b>\n\n"
                    f"Время выполнения сохранено!",
                    parse_mode="HTML",
                )
        else:
            await message.answer(
                f"❌ Ошибка: {result.get('message', 'Неизвестная ошибка')}"
            )
        return True

    if "✏️" in text or "Редактировать" in text:
        await message.answer("⚠️ Редактирование задач будет в v2.0")
        return True

    return False


async def process_irga_command(
    message: Message, command: str, command_lower: str, state: FSMContext, api
):
    """Обработка команд, начинающихся с 'Ирга'"""
    # Проверяем команды в порядке приоритета
    for keywords, handler_type in IRGA_COMMAND_HANDLERS:
        if any(word in command_lower for word in keywords):
            if handler_type == "show_tasks":
                await handle_irga_show_tasks_dispatch(
                    message, command_lower, state, api
                )
            elif handler_type == "subtask":
                await handle_irga_subtask(message, command, command_lower)
            elif handler_type == "delete":
                await delete_handler(message, state)
            elif handler_type == "categories":
                await categories_handler(message)
            elif handler_type == "greeting":
                await handle_irga_greeting(message, command_lower)
            elif handler_type == "help":
                await handle_irga_help(message)
            return True

    # Если не нашли команду - это создание задачи
    return False


async def handle_irga_show_tasks_dispatch(
    message: Message, command_lower: str, state: FSMContext, api
):
    """Диспетчер для show_tasks с проверкой на успешность"""
    handled = await handle_irga_show_tasks(message, command_lower, api)
    if not handled:
        await tasks_handler(message, state)


async def handle_natural_language_query(
    message: Message, text_lower: str, api
):
    """Обработка естественных запросов вне команд 'Ирга'"""
    # Паттерны: показать задачи
    if not any(
        word in text_lower for word in ["что", "покажи", "список", "план"]
    ):
        return False

    # Определяем фильтр по времени
    time_filter = None
    if "сегодня" in text_lower:
        time_filter = "today"
    elif "завтра" in text_lower:
        time_filter = "tomorrow"
    elif "недел" in text_lower:
        time_filter = "week"

    # "Что на сегодня?", "Покажи план", "План на сегодня"
    if any(
        word in text_lower
        for word in ["сегодня", "завтра", "недел", "план", "дела", "задач"]
    ):
        result = api.get_tasks(time_filter=time_filter)
        if result.get("status") == "success":
            tasks = result["tasks"]
            title = "План на сегодня" if time_filter == "today" else "План"
            response = format_tasks_response(tasks, title)
            await message.answer(response, parse_mode="HTML")
        else:
            await message.answer("❌ Ошибка получения задач")
        return True

    # "Что по здоровью?", "Покажи задачи по деньгам"
    categories_map = {
        "здоровь": "💪 Здоровье",
        "деньг": "💰 Деньги",
        "семь": "👨👩👧👦 Семья",
        "отношен": "💕 Взаимоотношения",
        "развит": "📚 Духовность и развитие",
    }

    for key, cat_emoji in categories_map.items():
        if key in text_lower:
            cat_name = cat_emoji.split(" ", 1)[1]
            result = api.get_tasks(category=cat_name)
            if result.get("status") == "success":
                tasks = result["tasks"]
                if not tasks:
                    await message.answer(
                        f"🎉 Задач по категории <b>{cat_name}</b> нет!",
                        parse_mode="HTML",
                    )
                else:
                    response = f"📂 <b>{cat_name}</b>\n\n"
                    for i, task in enumerate(tasks[:5], 1):
                        response += f"{i}. {task['content']}\n"
                    if len(tasks) > 5:
                        response += f"\n... и ещё {len(tasks) - 5}"
                    await message.answer(response, parse_mode="HTML")
            else:
                await message.answer("❌ Ошибка получения задач")
            return True

    # Если не распознали конкретный запрос
    await message.answer(
        "🤔 Не понял ваш запрос.\n\n"
        "Попробуйте:\n"
        "• Что на сегодня?\n"
        "• Что по здоровью?\n"
        "• Покажи план\n\n"
        "Или используйте /tasks"
    )
    return True


async def dispatch_message(
    message: Message, state: FSMContext, api, text: str
):
    """Центральный диспетчер сообщений"""
    # Обработка кнопок меню
    if await handle_menu_button(message, text, api):
        return True

    # Обработка специальных кнопок
    if "❓" in text and "Помощь" in text:
        await help_handler(message)
        return True

    if "🗑" in text or "Удалить" in text:
        await delete_handler(message, state)
        return True

    # Игнорируем остальные эмодзи кнопок меню
    menu_emojis = ["📂", "🏠", "⚙️", "📊"]
    if any(emoji in text for emoji in menu_emojis):
        return True

    # Умная обработка естественных запросов
    text_lower = text.lower()
    if await handle_natural_language_query(message, text_lower, api):
        return True

    return False


@dp.message()
async def message_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        return

    client = get_mcp_client(message.from_user.id)
    if not client:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return

    text = message.text
    
    # Обработка кнопок меню
    if "📋 План на сегодня" in text:
        response = client.chat("Покажи задачи на сегодня")
        await message.answer(response, parse_mode="HTML")
        return
    
    if "📅 План на завтра" in text:
        response = client.chat("Покажи задачи на завтра")
        await message.answer(response, parse_mode="HTML")
        return
    
    if "🔄 Перенос просрочки" in text:
        response = client.chat("Перенос просрочки")
        await message.answer(response, parse_mode="HTML")
        return
    
    if "✏️ Редактировать" in text:
        await message.answer("⚠️ Редактирование задач будет в v2.0")
        return
    
    # Обычное сообщение в MCP клиент
    response = client.chat(text)
    await message.answer(response, parse_mode="HTML")


async def main():
    from aiogram.types import BotCommand

    # Устанавливаем команды меню
    # Сначала удаляем старые команды
    await bot.delete_my_commands()

    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="auth", description="Авторизация"),
        BotCommand(command="tasks", description="Список задач"),
        BotCommand(command="subtask", description="Создать подзадачу"),
        BotCommand(command="areas", description="Области жизни"),
        BotCommand(command="delete", description="Удалить задачу"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="logout", description="Выход"),
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Команды меню обновлены")

    logger.info("🚀 Запуск TaskFlowAI Telegram Bot")
    logger.info("✅ Бот запущен с поддержкой авторизации")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

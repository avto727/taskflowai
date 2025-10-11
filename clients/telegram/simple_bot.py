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

from api_client import TaskFlowAPIClient
from backend.auth.db import init_db, save_token, get_token, delete_token

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
    api = get_api_client(message.from_user.id)

    if not api:
        await message.answer(
            "👋 <b>Добро пожаловать в TaskFlowAI!</b>\n\n"
            "Для начала работы авторизуйтесь:\n"
            "/auth - подключить Todoist",
            parse_mode="HTML",
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
        "/projects - проекты\n"
        "/help - помощь",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
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

    # v1.0: используем format_tasks_response для всех задач
    text = format_tasks_response(tasks, "Ваши задачи")

    # Добавляем статистику
    total = len(tasks)
    with_date = len([t for t in tasks if t.get("due")])
    without_date = total - with_date
    text += f"\n📊 <b>Статистика:</b> дел всего: {total}\n"
    text += f"📅 С датами: {with_date} | ❓ Без даты: {without_date}\n"

    await message.answer(text, parse_mode="HTML")


def parse_due_datetime(due: dict) -> tuple[str, str]:
    """
    Парсит дату и время из due объекта Todoist

    Returns:
        (date_str, time_str): например ('2025-10-12', '14:30')
        или ('2025-10-12', '')
    """
    if not due or not due.get("date"):
        return "", ""

    from datetime import datetime

    due_str = due.get("datetime") or due.get("date")
    dt = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
    date_str = dt.strftime("%Y-%m-%d")
    time_str = dt.strftime("%H:%M") if due.get("datetime") else ""
    return date_str, time_str


def extract_time_from_text(text: str) -> str:
    """Извлечь время из текста используя dateutil.parser"""
    from dateutil import parser

    try:
        # fuzzy=True игнорирует всё лишнее и ищет только дату/время
        dt = parser.parse(text, fuzzy=True)
        # Возвращаем только время в формате HH:MM
        return dt.strftime("%H:%M")
    except (ValueError, parser.ParserError):
        return ""


def format_tasks_response(tasks: list, title: str = "Задачи") -> str:
    """Форматирование списка задач"""
    if not tasks:
        return f"<b>{title}</b>\n\nЗадач нет"

    # v1.0: показываем все задачи без пагинации
    tasks_to_show = tasks
    text = f"📋 <b>{title} ({len(tasks)}):</b>\n\n"

    # Создаём индекс родителей для поиска
    parent_index = {
        t["id"]: t for t in tasks_to_show if not t.get("parent_id")
    }

    # Группировка по дням
    grouped = {}
    for task in tasks_to_show:
        # Для подзадач без даты берём дату родителя
        if task.get("parent_id") and not task.get("due"):
            parent = parent_index.get(task["parent_id"])
            if parent and parent.get("due"):
                due = parent["due"]
            else:
                due = None
        else:
            due = task.get("due")

        date_str, time_str = parse_due_datetime(due)
        if date_str:
            sort_key = f"{date_str}T{time_str if time_str else '99:99'}"

            # Для подзадач без своего времени пытаемся извлечь из текста
            if task.get("parent_id") and not task.get("due"):
                extracted_time = extract_time_from_text(task["content"])
                if extracted_time:
                    time_str = extracted_time
                    sort_key = date_str + "T" + time_str
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

        # Сортируем задачи по времени
        sorted_tasks = sorted(grouped[date_str], key=lambda x: x[2])

        # Разделяем на родителей и подзадачи
        parents = [
            (t, ts, sk) for t, ts, sk in sorted_tasks if not t.get("parent_id")
        ]
        children = [
            (t, ts, sk) for t, ts, sk in sorted_tasks if t.get("parent_id")
        ]

        # Выводим родителей с их подзадачами
        shown_children = set()
        for parent, time_str, _ in parents:
            # Показываем родителя
            time_part = f" 🕒 {time_str}" if time_str else ""
            task_id = f" [#{parent['id'][-4:]}]"
            text += f"  • {parent['content']}{time_part}{task_id}\n"

            # Показываем его подзадачи
            for child, child_time, _ in children:
                if child.get("parent_id") == parent["id"]:
                    child_time_part = f" 🕒 {child_time}" if child_time else ""
                    text += f"    ↳ {child['content']}" f"{child_time_part}\n"
                    shown_children.add(child["id"])

        # Показываем "осиротевшие" подзадачи
        for child, child_time, _ in children:
            if child["id"] not in shown_children:
                child_time_part = f" 🕒 {child_time}" if child_time else ""
                text += f"    ↳ {child['content']}" f"{child_time_part}\n"

        text += "\n"

    return text


@dp.message(Command("projects"))
@dp.message(Command("categories"))  # старая команда для совместимости
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
        parse_mode="HTML",
    )


@dp.message(SubtaskStates.waiting_for_parent_id)
async def subtask_parent_handler(message: Message, state: FSMContext):
    short_id = message.text.strip()

    # Получаем все задачи и ищем по короткому ID
    api = get_api_client(message.from_user.id)
    result = api.get_tasks()

    if result.get("status") == "success":
        tasks = result["tasks"]
        # Ищем задачу по последним 4 цифрам ID
        full_id = None
        for task in tasks:
            if task["id"].endswith(short_id):
                full_id = task["id"]
                break

        if not full_id:
            await message.answer(
                f"❌ Задача с ID #{short_id} не найдена\n\n"
                "Используйте /tasks чтобы увидеть ID задач"
            )
            await state.clear()
            return

        await state.update_data(parent_id=full_id)
        await state.set_state(SubtaskStates.waiting_for_content)
        await message.answer(
            "✍️ Отправьте текст подзадачи:\n\n" "Например: Отжимания 20 раз"
        )
    else:
        await message.answer("❌ Ошибка получения задач")
        await state.clear()


@dp.message(SubtaskStates.waiting_for_content)
async def subtask_content_handler(message: Message, state: FSMContext):
    content = message.text.strip()
    data = await state.get_data()
    parent_id = data.get("parent_id")

    # Создаём подзадачу через API
    import requests

    try:
        response = requests.post(
            "http://localhost:8000/tasks",
            headers={"X-Todoist-Token": get_token(message.from_user.id)},
            json={"content": content, "parent_id": parent_id},
        )
        if response.status_code == 200:
            await message.answer(
                f"✅ <b>Подзадача создана!</b>\n\n"
                f"📝 {content}\n"
                f"↳ Родитель: {parent_id}",
                parse_mode="HTML",
            )
        else:
            await message.answer(
                f"❌ Ошибка: "
                f"{response.json().get('detail', 'Неизвестная ошибка')}"
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

    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


@dp.message(DeleteStates.waiting_for_number)
async def delete_number_handler(message: Message, state: FSMContext):
    try:
        num = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Неверный номер. Отправьте число или /cancel")
        return

    data = await state.get_data()
    tasks = data.get("tasks", [])

    if num < 1 or num > len(tasks):
        await message.answer(f"❌ Номер должен быть от 1 до {len(tasks)}")
        return

    task = tasks[num - 1]

    # Удаляем через API
    import requests

    try:
        response = requests.delete(
            f"http://localhost:8000/tasks/{task['id']}",
            headers={"X-Todoist-Token": get_token(message.from_user.id)},
        )
        if response.status_code == 200:
            await message.answer(f"✅ Удалено: {task['content']}")
        else:
            await message.answer("❌ Ошибка удаления")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

    await state.clear()


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


async def handle_irga_show_tasks(message: Message, command_lower: str, api):
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

    api = get_api_client(message.from_user.id)
    if not api:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return

    text = message.text

    # 🤖 Обработка обращения "Ирга"
    if text.lower().startswith(("ирга", "irga")):
        command = text[4:].strip()
        if command.startswith(","):
            command = command[1:].strip()

        command_lower = command.lower()

        # Используем Command Registry
        if await process_irga_command(
            message, command, command_lower, state, api
        ):
            return

        # Если команда не распознана - создаём задачу
        text = command

    # Центральный диспетчер обработки сообщений
    if await dispatch_message(message, state, api, message.text):
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
            "✅ <b>Добавил!</b>",
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
            "🎉 <b>Круто!</b>",
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
    # Сначала удаляем старые команды
    await bot.delete_my_commands()

    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="auth", description="Авторизация"),
        BotCommand(command="tasks", description="Список задач"),
        BotCommand(command="subtask", description="Создать подзадачу"),
        BotCommand(command="projects", description="Проекты"),
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

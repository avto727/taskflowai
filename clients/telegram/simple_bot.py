"""
Простой Telegram бот для TaskFlowAI
Подключается к Backend API вместо SQLite
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
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
from typing import Optional

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

init_db()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logger.critical("❌ TELEGRAM_BOT_TOKEN не найден в .env файле!")
    sys.exit(1)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


class AuthStates(StatesGroup):
    waiting_for_token = State()


class DeleteStates(StatesGroup):
    waiting_for_number = State()


@dp.message(DeleteStates.waiting_for_number)
async def delete_number_handler(message: Message, state: FSMContext):
    if not message.text or not message.from_user:
        return
        
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
        if not client:
            await message.answer("❌ Сначала авторизуйтесь: /auth")
            return
        
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
    if not message.text or not message.from_user:
        return

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
    if not client:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return
    
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
    if not message.text or not message.from_user:
        return
        
    content = message.text.strip()
    data = await state.get_data()
    parent_task = data.get("parent_task")
    
    client = get_mcp_client(message.from_user.id)
    if not client:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return
    
    # Создаём подзадачу
    if not parent_task:
        await message.answer("❌ Не удалось найти родительскую задачу. Попробуйте снова.")
        await state.clear()
        return

    result = client.todoist.create_task(
        content=content,
        parent_id=parent_task["id"]
    )
    
    if result["success"]:
        await message.answer(
            f"✅ <b>Подзадача создана!</b>\n\n"
            f"📝 {content}\n"
            f"↳ Родитель: {parent_task['content'] if parent_task else 'Неизвестно'}",
            parse_mode="HTML"
        )
    else:
        await message.answer(f"❌ Ошибка: {result['error']}")
    
    await state.clear()


def get_mcp_client(telegram_id: int) -> Optional[SimpleOllamaClient]:
    token = get_token(telegram_id)
    if token:
        return SimpleOllamaClient(token)
    return None


@dp.message(Command("auth"))
async def auth_handler(message: Message, state: FSMContext):
    if not message.from_user:
        return
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
    if not message.from_user:
        return
    await state.clear()
    await message.answer("❌ Операция отменена")


@dp.message(AuthStates.waiting_for_token)
async def token_handler(message: Message, state: FSMContext):
    if not message.text or not message.from_user:
        return

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
    if not message.from_user:
        return
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
    if not message.from_user:
        return
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
    if not message.from_user:
        return
    client = get_mcp_client(message.from_user.id)
    if not client:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return

    # Всю сложную логику форматирования делегируем MCP
    response = client.chat("Покажи мои задачи")
    
    # MCP может вернуть клавиатуру, если захочет, но в данном случае мы ожидаем простой текст
    await message.answer(response, parse_mode="HTML")





@dp.message(Command("areas"))
@dp.message(Command("projects"))  # старая команда для совместимости
@dp.message(Command("categories"))  # старая команда для совместимости
async def life_areas_handler(message: Message):
    if not message.from_user:
        return
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
    if not message.from_user:
        return
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
    if not message.from_user:
        return
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





@dp.callback_query(F.data.startswith("complete_"))
async def complete_task_callback(callback: CallbackQuery):
    if not callback.data:
        await callback.answer("❌ Ошибка: нет данных в колбэке")
        return
        
    task_id = callback.data.split("_", 1)[1]
    
    client = get_mcp_client(callback.from_user.id)
    if not client:
        await callback.answer("❌ Сначала авторизуйтесь: /auth")
        return
    
    result = client.todoist.complete_task(task_id)
    
    if result["success"]:
        await callback.answer("✅ Задача выполнена!")
        # Обновляем список задач
        response = client.chat("Покажи мои задачи")
        if callback.message and isinstance(callback.message, Message):
            await callback.message.edit_text(response, parse_mode="HTML")
    else:
        await callback.answer(f"❌ Ошибка: {result['error']}")


@dp.callback_query(F.data.startswith("life_area_"))
async def life_area_callback(callback: CallbackQuery):
    if not callback.data or not callback.message:
        await callback.answer("❌ Ошибка: нет данных в колбэке")
        return

    area_id = callback.data.split("_", 2)[2]
    
    client = get_mcp_client(callback.from_user.id)
    if not client:
        await callback.answer("❌ Сначала авторизуйтесь: /auth")
        return

    # Делегируем получение задач по области жизни в MCP
    # Сначала получаем имя области
    areas_result = client.todoist.get_projects()
    area_name = None
    if areas_result["success"]:
        for area in areas_result["projects"]:
            if area["id"] == area_id:
                area_name = area["name"]
                break
    
    if area_name:
        response = client.chat(f"Покажи задачи по {area_name}")
        if isinstance(callback.message, Message):
            await callback.message.edit_text(response, parse_mode="HTML")
    else:
        if isinstance(callback.message, Message):
            await callback.message.edit_text("❌ Не удалось найти такую область жизни.")
    
    await callback.answer()


@dp.callback_query(F.data.startswith("delete_more_"))
async def delete_more_callback(callback: CallbackQuery, state: FSMContext):
    """Этот колбэк больше не нужен, так как пагинация делегирована в MCP"""
    await callback.answer("⚠️ Эта функция устарела.", show_alert=True)


@dp.callback_query(F.data.startswith("tasks_more_"))
async def tasks_more_callback(callback: CallbackQuery, state: FSMContext):
    """Этот колбэк больше не нужен, так как пагинация делегирована в MCP"""
    await callback.answer("⚠️ Эта функция устарела.", show_alert=True)


@dp.callback_query(F.data.startswith("category_more_"))
async def category_more_callback(callback: CallbackQuery, state: FSMContext):
    """Этот колбэк больше не нужен, так как пагинация делегирована в MCP"""
    await callback.answer("⚠️ Эта функция устарела.", show_alert=True)


@dp.message(Command("help"))
async def help_handler(message: Message):
    if not message.from_user:
        return
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


async def handle_irga_subtask(
    message: Message, command: str, command_lower: str, client: SimpleOllamaClient
):
    """Обработка команды создания подзадачи от Ирги"""
    import re

    match = re.search(r"к задаче (\d+)", command_lower)
    if not match:
        await message.answer(
            "🤔 <b>Ирга:</b> Укажите номер задачи\n\n"
            "Пример: Ирга, создай подзадачу к задаче 1: отжимания",
            parse_mode="HTML",
        )
        return

    parent_id_str = match.group(1)
    
    result = client.todoist.get_tasks()
    if not result["success"]:
        await message.answer("❌ Ошибка получения задач для поиска родительской.")
        return

    parent_tasks = [t for t in result["tasks"] if not t.get("parent_id")]
    
    try:
        parent_number = int(parent_id_str)
        if not (1 <= parent_number <= len(parent_tasks)):
            raise ValueError
        parent_task = parent_tasks[parent_number - 1]
        parent_id = parent_task["id"]
    except (ValueError, IndexError):
        await message.answer(f"❌ Неверный номер родительской задачи: {parent_id_str}")
        return

    content = (
        command.split(":", 1)[1].strip()
        if ":" in command
        else command.split(parent_id_str, 1)[1].strip()
    )

    create_result = client.todoist.create_task(content=content, parent_id=parent_id)

    if create_result["success"]:
        await message.answer(
            f"✅ <b>Ирга:</b> Подзадача создана!\n\n"
            f"📝 {content}\n"
            f"↳ Родитель: {parent_task['content']}",
            parse_mode="HTML",
        )
    else:
        await message.answer(f"❌ <b>Ирга:</b> Ошибка создания: {create_result.get('error')}")


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


@dp.message()
async def message_handler(message: Message, state: FSMContext):
    # Убедимся, что мы не в каком-либо состоянии (например, ожидание токена)
    current_state = await state.get_state()
    if current_state:
        return

    if not message.from_user:
        return

    # 1. Получаем клиент MCP
    client = get_mcp_client(message.from_user.id)

    # 2. Проверяем авторизацию
    if not client:
        await message.answer("❌ Сначала авторизуйтесь: /auth")
        return

    if not message.text:
        return
    text = message.text.strip()
    command_lower = text.lower()

    # 3. Обработка команд "Ирга, ..."
    if command_lower.startswith("ирга"):
        command_part = command_lower.split("ирга", 1)[-1].strip()
        
        # Приветствие
        if any(word in command_part for word in ["привет", "здравств", "добр"]):
            await handle_irga_greeting(message, command_part)
            return

        # Помощь
        if any(word in command_part for word in ["помощ", "помог"]):
            await handle_irga_help(message)
            return
        
        # Создание подзадачи
        if "подзадач" in command_part:
            await handle_irga_subtask(message, text, command_part, client)
            return
            
        # Удаление
        if "удал" in command_part:
            await delete_handler(message, state)
            return
            
        # Категории
        if any(word in command_part for word in ["категор", "проект"]):
            await life_areas_handler(message)
            return

    # 4. В остальных случаях (включая кнопки) передаем текст напрямую в MCP
    # MCP сам разберется, это "покажи задачи" или "создай задачу"
    response_text = client.chat(text)

    # 5. Отправляем готовый ответ от MCP пользователю
    await message.answer(response_text, parse_mode="HTML")


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

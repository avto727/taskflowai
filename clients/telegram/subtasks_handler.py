"""Обработчик подзадач для Telegram бота"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import requests

router = Router()

class SubtaskStates(StatesGroup):
    waiting_for_parent = State()
    waiting_for_content = State()

@router.message(Command("subtask"))
async def subtask_handler(message: Message, state: FSMContext):
    """Создать подзадачу"""
    await state.set_state(SubtaskStates.waiting_for_parent)
    await message.answer(
        "📝 <b>Создание подзадачи</b>\n\n"
        "Отправьте ID родительской задачи\n"
        "Отмена: /cancel",
        parse_mode="HTML"
    )

@router.message(SubtaskStates.waiting_for_parent)
async def parent_handler(message: Message, state: FSMContext):
    """Получить ID родителя"""
    parent_id = message.text.strip()
    await state.update_data(parent_id=parent_id)
    await state.set_state(SubtaskStates.waiting_for_content)
    await message.answer("Теперь отправьте текст подзадачи:")

@router.message(SubtaskStates.waiting_for_content)
async def content_handler(message: Message, state: FSMContext):
    """Создать подзадачу"""
    data = await state.get_data()
    parent_id = data.get('parent_id')
    content = message.text.strip()
    
    # Получаем токен
    from simple_bot import get_token
    token = get_token(message.from_user.id)
    
    try:
        response = requests.post(
            "http://localhost:8000/tasks",
            json={
                "content": content,
                "parent_id": parent_id
            },
            headers={'X-Todoist-Token': token}
        )
        if response.status_code == 200:
            await message.answer(f"✅ Подзадача создана: {content}")
        else:
            await message.answer("❌ Ошибка создания")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    
    await state.clear()

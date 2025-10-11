from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
import logging
from db import Database
from ai_processor import AIProcessor
from config import TOKEN, DB_PATH
from time_scheduler import TimeScheduler

logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = Database(DB_PATH)
ai = AIProcessor()

class TaskConfirmation(StatesGroup):
    waiting_for_confirmation = State()

class TaskDeletion(StatesGroup):
    waiting_for_task_selection = State()

class TaskEdit(StatesGroup):
    waiting_for_task_selection = State()
    waiting_for_field_selection = State()
    waiting_for_new_value = State()

class RecurringTask(StatesGroup):
    waiting_for_description = State()
    waiting_for_recurrence = State()
    waiting_for_time = State()

# Главное меню - единая страница
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 План на сегодня"), KeyboardButton(text="📅 План на завтра")],
        [KeyboardButton(text="📆 План на неделю"), KeyboardButton(text="📊 Статус")],
        [KeyboardButton(text="✏️ Редактировать"), KeyboardButton(text="🗑️ Удалить")],
        [KeyboardButton(text="🔁 Периодические задачи")],
        [KeyboardButton(text="🚀 Перенести просроченные на завтра")],
        [KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True
)

logger.info("Бот инициализирован")

@dp.message(Command('start'))
async def start_handler(message: types.Message):
    user = message.from_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    logger.info(f"Пользователь {user.id} (@{user.username}) запустил бота")
    await message.reply(
        "👋 Привет! Я Irga — ваш умный помощник по делам.\n\n"
        "📝 Пишите дела естественным языком\n"
        "❓ Хотите увидеть список? Ставьте ? в конце\n\n"
        "📊 Бот автоматически определит категорию, статус и время\n\n"
        "Используйте кнопки меню для быстрого доступа.\n\n"
        "🚀 Киллер-фича: перенос просроченных задач на завтра с сохранением времени!",
        reply_markup=main_menu
    )

@dp.message(Command('help'))
async def help_handler(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запросил помощь")
    await message.reply(
        "📋 Как пользоваться:\n\n"
        "📝 Пишите дела естественным языком\n"
        "❓ Хотите увидеть список? Ставьте ? в конце\n"
        "📊 Бот автоматически определит категорию, статус и время\n\n"
        "Используйте кнопки меню для быстрого доступа:\n"
        "📋 План на сегодня - задачи на сегодня\n"
        "📅 План на завтра - задачи на завтра\n"
        "📆 План на неделю - задачи на 7 дней\n"
        "📊 Статус - статистика за сегодня\n"
        "✏️ Редактировать - изменение задачи\n"
        "🗑️ Удалить - удаление дел\n"
        "❓ Помощь - эта справка\n\n"
        "🚀 Перенести просроченные на завтра - киллер-фича!",
        reply_markup=main_menu
    )

@dp.message(Command('show_plan'))
async def show_plan(message: types.Message):
    tasks = db.get_tasks(user_id=message.from_user.id, status='план')
    if not tasks:
        await message.reply("План пуст.", reply_markup=main_menu)
        return
    text = "Ваш план:\n"
    for task in tasks:
        text += f"- {task[2]} (статус: {task[4]})\n"
    await message.reply(text, reply_markup=main_menu)

@dp.message(Command('morning'))
async def test_morning(message: types.Message):
    """Тестовая команда для проверки утреннего сообщения"""
    from scheduler import TaskScheduler
    scheduler = TaskScheduler(bot, db)
    await scheduler.send_morning_message(message.from_user.id)

@dp.message(Command('edit'))
async def edit_task_command(message: types.Message, state: FSMContext):
    """Редактирование задачи"""
    tasks = db.get_tasks(user_id=message.from_user.id)
    
    if not tasks:
        await message.reply("У вас нет задач для редактирования.", reply_markup=main_menu)
        return
    
    # Показываем список задач с inline-кнопками
    keyboard_buttons = []
    for task in tasks[:10]:
        task_id, _, description, _, status, planned_time = task[0], task[1], task[2], task[3], task[4], task[5]
        button_text = f"{description[:30]}..." if len(description) > 30 else description
        keyboard_buttons.append([types.InlineKeyboardButton(
            text=f"{status[:1].upper()} | {button_text}",
            callback_data=f"edit_{task_id}"
        )])
    
    keyboard_buttons.append([types.InlineKeyboardButton(text="❌ Отмена", callback_data="edit_cancel")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.reply(
        "✏️ Выберите задачу для редактирования:\n\n"
        "П - план, В - в процессе, Вы - выполнено",
        reply_markup=keyboard
    )
    await state.set_state(TaskEdit.waiting_for_task_selection)

@dp.message(Command('delete'))
async def delete_task_command(message: types.Message, state: FSMContext):
    """Удаление задачи"""
    tasks = db.get_tasks(user_id=message.from_user.id)
    
    if not tasks:
        await message.reply("У вас нет задач для удаления.", reply_markup=main_menu)
        return
    
    # Показываем список задач с inline-кнопками
    keyboard_buttons = []
    for task in tasks[:10]:  # Показываем максимум 10 задач
        task_id, _, description, _, status, planned_time = task[0], task[1], task[2], task[3], task[4], task[5]
        button_text = f"{description[:30]}..." if len(description) > 30 else description
        keyboard_buttons.append([types.InlineKeyboardButton(
            text=f"{status[:1].upper()} | {button_text}",
            callback_data=f"delete_{task_id}"
        )])
    
    keyboard_buttons.append([types.InlineKeyboardButton(text="❌ Отмена", callback_data="delete_cancel")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.reply(
        "🗑️ Выберите задачу для удаления:\n\n"
        "П - план, В - в процессе, Вы - выполнено",
        reply_markup=keyboard
    )
    await state.set_state(TaskDeletion.waiting_for_task_selection)

@dp.message(Command('status'))
async def status_today(message: types.Message):
    """Статус дел на сегодня"""
    from datetime import datetime
    today = datetime.now().date()
    
    # Задачи на сегодня
    tasks_today = db.get_tasks_filtered(message.from_user.id, date_filter='today')
    completed_today = [t for t in tasks_today if t[4] == 'выполнено']
    planned_today = [t for t in tasks_today if t[4] == 'план']
    
    # Просроченные
    overdue = db.get_overdue_tasks(message.from_user.id)
    
    text = f"📊 Статус на сегодня ({today.strftime('%d.%m.%Y')}):\n\n"
    text += f"✅ Выполнено: {len(completed_today)}\n"
    text += f"📌 В плане: {len(planned_today)}\n"
    text += f"❌ Просрочено: {len(overdue)}\n"
    
    if planned_today:
        text += f"\n📝 Осталось сделать:\n"
        for task in planned_today[:3]:
            text += f"  • {task[2]}\n"
        if len(planned_today) > 3:
            text += f"  ... и ещё {len(planned_today) - 3}\n"
    
    await message.reply(text, reply_markup=main_menu)

@dp.callback_query(F.data.startswith('edit_'))
async def handle_edit(callback: types.CallbackQuery, state: FSMContext):
    """Обработка редактирования задачи"""
    action = callback.data.split('_', 1)[1]
    
    if action == 'cancel':
        await callback.message.edit_text("❌ Редактирование отменено.")
        await state.clear()
        await callback.answer()
        return
    
    task_id = int(action)
    task = db.get_task_by_id(task_id, callback.from_user.id)
    
    if not task:
        await callback.message.edit_text("❌ Задача не найдена.")
        await state.clear()
        await callback.answer()
        return
    
    # Сохраняем задачу и предлагаем выбрать поле
    await state.update_data(task_id=task_id, task=task)
    await state.set_state(TaskEdit.waiting_for_field_selection)
    
    time_str = task[5] if task[5] else "не указано"
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📝 Описание", callback_data="editfield_description")],
        [types.InlineKeyboardButton(text="📊 Статус", callback_data="editfield_status")],
        [types.InlineKeyboardButton(text="⏰ Время", callback_data="editfield_time")],
        [types.InlineKeyboardButton(text="❌ Отмена", callback_data="editfield_cancel")]
    ])
    
    await callback.message.edit_text(
        f"✏️ Задача: \"{task[2]}\"\n\n"
        f"📊 Статус: {task[4]}\n"
        f"⏰ Время: {time_str}\n\n"
        f"Что хотите изменить?",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data.startswith('editfield_'))
async def handle_field_selection(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора поля для редактирования"""
    field = callback.data.split('_', 1)[1]
    
    if field == 'cancel':
        await callback.message.edit_text("❌ Редактирование отменено.")
        await state.clear()
        await callback.answer()
        return
    
    data = await state.get_data()
    task = data.get('task')
    
    if field == 'status':
        # Показываем кнопки с вариантами статуса
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="📌 План", callback_data="setstatus_план")],
            [types.InlineKeyboardButton(text="⏳ В процессе", callback_data="setstatus_в процессе")],
            [types.InlineKeyboardButton(text="✅ Выполнено", callback_data="setstatus_выполнено")],
            [types.InlineKeyboardButton(text="❌ Отмена", callback_data="setstatus_cancel")]
        ])
        await callback.message.edit_text(
            f"📊 Текущий статус: {task[4]}\n\n"
            f"Выберите новый статус:",
            reply_markup=keyboard
        )
    elif field == 'description':
        await state.update_data(edit_field='description')
        await state.set_state(TaskEdit.waiting_for_new_value)
        await callback.message.edit_text(
            f"📝 Текущее описание:\n\n\"{task[2]}\"\n\n"
            f"Напишите новое описание:"
        )
    elif field == 'time':
        await state.update_data(edit_field='time')
        await state.set_state(TaskEdit.waiting_for_new_value)
        time_str = task[5] if task[5] else "не указано"
        await callback.message.edit_text(
            f"⏰ Текущее время: {time_str}\n\n"
            f"Напишите новое время (например: '2024-01-15 10:00' или 'завтра утром'):"
        )
    
    await callback.answer()

@dp.callback_query(F.data == 'reschedule_all')
async def handle_reschedule_all(callback: types.CallbackQuery):
    """Обработка переноса всех просроченных задач на завтра"""
    count = db.reschedule_overdue_to_tomorrow(callback.from_user.id)
    
    if count > 0:
        await callback.message.edit_text(
            f"✅ Отлично! Перенесено {count} задач(и) на завтра.\n\n"
            f"Время выполнения сохранено! 🚀"
        )
    else:
        await callback.message.edit_text("❌ Нет просроченных задач для переноса.")
    
    await callback.answer()

@dp.callback_query(F.data.startswith('setstatus_'))
async def handle_status_change(callback: types.CallbackQuery, state: FSMContext):
    """Обработка изменения статуса"""
    new_status = callback.data.split('_', 1)[1]
    
    if new_status == 'cancel':
        await callback.message.edit_text("❌ Редактирование отменено.")
        await state.clear()
        await callback.answer()
        return
    
    data = await state.get_data()
    task_id = data.get('task_id')
    
    if db.update_task(task_id, callback.from_user.id, status=new_status):
        await callback.message.edit_text(f"✅ Статус изменён на: {new_status}")
    else:
        await callback.message.edit_text("❌ Ошибка при обновлении статуса.")
    
    await state.clear()
    await callback.answer()

@dp.message(TaskEdit.waiting_for_new_value)
async def process_edit_value(message: types.Message, state: FSMContext):
    """Обработка нового значения поля"""
    data = await state.get_data()
    task_id = data.get('task_id')
    edit_field = data.get('edit_field')
    
    if not task_id or not edit_field:
        await message.reply("❌ Ошибка: данные не найдены.", reply_markup=main_menu)
        await state.clear()
        return
    
    if edit_field == 'description':
        if db.update_task(task_id, message.from_user.id, description=message.text):
            await message.reply(f"✅ Описание обновлено:\n\n\"{message.text}\"", reply_markup=main_menu)
        else:
            await message.reply("❌ Ошибка при обновлении.", reply_markup=main_menu)
    
    elif edit_field == 'time':
        # Используем ИИ для парсинга времени
        categories = db.get_categories(parent_id=None)
        analysis = ai.analyze_message(message.text, categories)
        planned_time = analysis.get('planned_time')
        
        if db.update_task(task_id, message.from_user.id, planned_time=planned_time):
            time_str = planned_time if planned_time else "удалено"
            await message.reply(f"✅ Время обновлено: {time_str}", reply_markup=main_menu)
        else:
            await message.reply("❌ Ошибка при обновлении.", reply_markup=main_menu)
    
    await state.clear()

@dp.callback_query(F.data.startswith('delete_'))
async def handle_delete(callback: types.CallbackQuery, state: FSMContext):
    """Обработка удаления задачи"""
    action = callback.data.split('_', 1)[1]
    
    if action == 'cancel':
        await callback.message.edit_text("❌ Удаление отменено.")
        await state.clear()
        await callback.answer()
        return
    
    task_id = int(action)
    task = db.get_task_by_id(task_id, callback.from_user.id)
    
    if not task:
        await callback.message.edit_text("❌ Задача не найдена.")
        await state.clear()
        await callback.answer()
        return
    
    # Удаляем задачу
    if db.delete_task(task_id, callback.from_user.id):
        await callback.message.edit_text(f"✅ Задача удалена:\n\n\"{task[2]}\"")
    else:
        await callback.message.edit_text("❌ Ошибка при удалении задачи.")
    
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data.startswith('confirm_'))
async def handle_confirmation(callback: types.CallbackQuery, state: FSMContext):
    """Обработка подтверждения"""
    action = callback.data.split('_')[1]
    data = await state.get_data()
    task_id = data.get('task_id')
    
    if action == 'yes' and task_id:
        # Обновляем статус
        db.update_task_status(task_id, 'выполнено')
        await callback.message.edit_text("✅ Отлично! Задача отмечена как выполненная.")
    else:
        # Создаём новую задачу
        original_text = data.get('original_text')
        category_id = data.get('category_id')
        db.add_task(
            user_id=callback.from_user.id,
            description=original_text,
            category_id=category_id,
            status='выполнено'
        )
        await callback.message.edit_text("✅ Создана новая задача со статусом 'выполнено'.")
    
    await state.clear()
    await callback.answer()

@dp.message(F.text.in_(["📋 План на сегодня", "📋 План на сегодня_"]))
async def menu_plan_today(message: types.Message):
    """План на сегодня"""
    tasks = db.get_tasks_filtered(message.from_user.id, status='план', date_filter='today')
    
    if not tasks:
        await message.reply("📋 План на сегодня пуст.", reply_markup=main_menu)
        return
    
    text = "📋 План на сегодня:\n\n"
    for task in tasks:
        emoji = "📌"
        time_str = f" ⏰ {task[5]}" if task[5] else ""
        text += f"{emoji} {task[2]}{time_str}\n"
    text += f"\n✅ Всего: {len(tasks)}"
    await message.reply(text, reply_markup=main_menu)

@dp.message(F.text.in_(["📅 План на завтра"]))
async def menu_plan_tomorrow(message: types.Message):
    """План на завтра"""
    tasks = db.get_tasks_filtered(message.from_user.id, status='план', date_filter='tomorrow')
    
    if not tasks:
        await message.reply("📅 План на завтра пуст.", reply_markup=main_menu)
        return
    
    text = "📅 План на завтра:\n\n"
    for task in tasks:
        emoji = "📌"
        time_str = f" ⏰ {task[5]}" if task[5] else ""
        text += f"{emoji} {task[2]}{time_str}\n"
    text += f"\n✅ Всего: {len(tasks)}"
    await message.reply(text, reply_markup=main_menu)

@dp.message(F.text.in_(["📆 План на неделю"]))
async def menu_plan_week(message: types.Message):
    """План на неделю"""
    tasks = db.get_tasks_filtered(message.from_user.id, status='план', date_filter='week')
    
    if not tasks:
        await message.reply("📆 План на неделю пуст.", reply_markup=main_menu)
        return
    
    text = "📆 План на неделю:\n\n"
    for task in tasks:
        emoji = "📌"
        time_str = f" ⏰ {task[5]}" if task[5] else ""
        text += f"{emoji} {task[2]}{time_str}\n"
    text += f"\n✅ Всего: {len(tasks)}"
    await message.reply(text, reply_markup=main_menu)

@dp.message(F.text.in_(["📊 Статус"]))
async def menu_status(message: types.Message):
    await status_today(message)

@dp.message(F.text.in_(["✏️ Редактировать"]))
async def menu_edit(message: types.Message, state: FSMContext):
    await edit_task_command(message, state)

@dp.message(F.text.in_(["🗑️ Удалить"]))
async def menu_delete(message: types.Message, state: FSMContext):
    await delete_task_command(message, state)

@dp.message(F.text.in_(["❓ Помощь"]))
async def menu_help(message: types.Message):
    await help_handler(message)

@dp.message(F.text.in_(["🔄 Обновить меню"]))
async def menu_refresh(message: types.Message):
    await start_handler(message)

@dp.message(F.text.in_(["🔁 Периодические задачи"]))
async def menu_recurring(message: types.Message):
    """Меню периодических задач"""
    recurring = db.get_recurring_tasks(message.from_user.id)
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="➕ Добавить периодическую задачу", callback_data="recurring_add")]
    ])
    
    if not recurring:
        await message.reply(
            "🔁 Периодические задачи\n\n"
            "У вас пока нет периодических задач.\n\n"
            "Периодические задачи автоматически создаются каждый день/неделю/месяц.",
            reply_markup=keyboard
        )
    else:
        text = "🔁 Ваши периодические задачи:\n\n"
        for task in recurring:
            rec_type = {"daily": "Каждый день", "weekly": "Каждую неделю", "monthly": "Каждый месяц"}
            time_str = f" в {task[4]}" if task[4] else ""
            text += f"🔁 {task[2]} ({rec_type[task[3]]}{time_str})\n"
            keyboard.inline_keyboard.append([
                types.InlineKeyboardButton(text=f"🗑️ {task[2][:20]}...", callback_data=f"recurring_del_{task[0]}")
            ])
        await message.reply(text, reply_markup=keyboard)

@dp.callback_query(F.data == "recurring_add")
async def recurring_add_start(callback: types.CallbackQuery, state: FSMContext):
    """Начало добавления периодической задачи"""
    await state.set_state(RecurringTask.waiting_for_description)
    await callback.message.edit_text(
        "➕ Добавление периодической задачи\n\n"
        "Напишите описание задачи:"
    )
    await callback.answer()

@dp.message(RecurringTask.waiting_for_description)
async def recurring_get_description(message: types.Message, state: FSMContext):
    """Получение описания"""
    await state.update_data(description=message.text)
    await state.set_state(RecurringTask.waiting_for_recurrence)
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📅 Каждый день", callback_data="rec_daily")],
        [types.InlineKeyboardButton(text="📆 Каждую неделю", callback_data="rec_weekly")],
        [types.InlineKeyboardButton(text="🗓️ Каждый месяц", callback_data="rec_monthly")],
        [types.InlineKeyboardButton(text="❌ Отмена", callback_data="rec_cancel")]
    ])
    
    await message.reply(
        f"Задача: \"{message.text}\"\n\n"
        f"Выберите периодичность:",
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith("rec_"))
async def recurring_get_recurrence(callback: types.CallbackQuery, state: FSMContext):
    """Получение периодичности"""
    action = callback.data.split('_', 1)[1]
    
    if action == 'cancel':
        await callback.message.edit_text("❌ Добавление отменено.")
        await state.clear()
        await callback.answer()
        return
    
    await state.update_data(recurrence=action)
    await state.set_state(RecurringTask.waiting_for_time)
    
    await callback.message.edit_text(
        "⏰ Введите время выполнения (например: 09:00)\n"
        "Или напишите 'пропустить' для времени по умолчанию (09:00)"
    )
    await callback.answer()

@dp.message(RecurringTask.waiting_for_time)
async def recurring_get_time(message: types.Message, state: FSMContext):
    """Получение времени и создание задачи"""
    data = await state.get_data()
    description = data.get('description')
    recurrence = data.get('recurrence')
    
    time_str = None if message.text.lower() == 'пропустить' else message.text
    
    # Создаём периодическую задачу
    db.add_recurring_task(message.from_user.id, description, recurrence, time_str)
    
    rec_text = {"daily": "каждый день", "weekly": "каждую неделю", "monthly": "каждый месяц"}
    time_display = time_str if time_str else "09:00"
    
    await message.reply(
        f"✅ Периодическая задача добавлена!\n\n"
        f"🔁 {description}\n"
        f"📅 {rec_text[recurrence]} в {time_display}\n\n"
        f"Задача будет автоматически создаваться каждый день в 00:01.",
        reply_markup=main_menu
    )
    await state.clear()

@dp.callback_query(F.data.startswith("recurring_del_"))
async def recurring_delete(callback: types.CallbackQuery):
    """Удаление периодической задачи"""
    task_id = int(callback.data.split('_', 2)[2])
    
    if db.delete_recurring_task(task_id, callback.from_user.id):
        await callback.message.edit_text("✅ Периодическая задача удалена.")
    else:
        await callback.message.edit_text("❌ Ошибка при удалении.")
    
    await callback.answer()

@dp.message(F.text.in_(["🚀 Перенести просроченные на завтра"]))
async def menu_reschedule(message: types.Message):
    """Перенос просроченных задач на завтра"""
    overdue = db.get_overdue_tasks(message.from_user.id)
    
    if not overdue:
        await message.reply("✅ У вас нет просроченных задач!", reply_markup=main_menu)
        return
    
    count = db.reschedule_overdue_to_tomorrow(message.from_user.id)
    await message.reply(
        f"✅ Отлично! Перенесено {count} задач(и) на завтра.\n\n"
        f"Время выполнения сохранено! 🚀",
        reply_markup=main_menu
    )

@dp.message()
async def smart_handler(message: types.Message, state: FSMContext):
    """Умный обработчик с ИИ-анализом"""
    logger.info(f"Сообщение от {message.from_user.id}: {message.text[:50]}...")
    
    # Простое правило: если есть "?" - это query
    if message.text.endswith('?'):
        msg_type = 'query'
        categories = db.get_categories(parent_id=None)
        analysis = ai.analyze_message(message.text, categories)
        logger.debug(f"Результат анализа: {analysis}")
    else:
        categories = db.get_categories(parent_id=None)
        analysis = ai.analyze_message(message.text, categories)
        logger.debug(f"Результат анализа: {analysis}")
        msg_type = analysis.get('type', 'task')
    
    if msg_type == 'query':
        # Проверяем фильтры
        category_id = None
        filter_category = analysis.get('filter_category')
        date_filter = analysis.get('filter_date')
        
        # Если ИИ вернул категорию из списка - ищем её
        if filter_category and filter_category.lower() not in ['null', 'none', '']:
            cat = db.get_category_by_name(filter_category)
            if cat:
                category_id = cat[0]
        
        # Если date_filter = null или пустой - убираем
        if date_filter and date_filter.lower() in ['null', 'none', '']:
            date_filter = None
        
        tasks = db.get_tasks_filtered(
            user_id=message.from_user.id,
            status='план',
            category_id=category_id,
            date_filter=date_filter
        )
        
        if not tasks:
            filter_text = ""
            if category_id:
                filter_text += f" по категории '{filter_category}'"
            if date_filter:
                filter_text += f" на {date_filter}"
            await message.reply(f"📋 План{filter_text} пуст.", reply_markup=main_menu)
            return
        
        # Красивое форматирование
        text = "📋 Ваш план:\n\n"
        for task in tasks:
            emoji = "📌"
            time_str = f" ⏰ {task[5]}" if task[5] else ""
            text += f"{emoji} {task[2]}{time_str}\n"
        
        text += f"\n✅ Всего: {len(tasks)}"
        await message.reply(text, reply_markup=main_menu)
    
    elif msg_type in ['task', 'completed']:
        # Умное связывание: ищем похожие задачи
        if msg_type == 'completed':
            keywords = [word for word in message.text.lower().split() if len(word) > 3]
            similar_tasks = db.find_similar_tasks(message.from_user.id, keywords, status='план')
            
            if similar_tasks:
                # Нашли похожую задачу - спрашиваем
                task = similar_tasks[0]
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    [
                        types.InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
                        types.InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no")
                    ]
                ])
                
                await state.set_state(TaskConfirmation.waiting_for_confirmation)
                await state.update_data(
                    task_id=task[0],
                    original_text=message.text,
                    category_id=analysis.get('category_id')
                )
                
                await message.reply(
                    f"🔍 Нашёл задачу в плане:\n\n"
                    f"\"{task[2]}\"\n\n"
                    f"Отметить её как выполненную?",
                    reply_markup=keyboard
                )
                return
        
        # Умное планирование времени
        planned_time = analysis.get('planned_time')
        
        # Если время не указано точно, но есть указание на время суток
        if not planned_time:
            time_of_day = TimeScheduler.detect_time_of_day(message.text)
            if time_of_day:
                from datetime import datetime
                # Определяем дату (сегодня или завтра)
                target_date = datetime.now().date()
                if 'завтра' in message.text.lower():
                    from datetime import timedelta
                    target_date = target_date + timedelta(days=1)
                
                # Ищем свободное время
                planned_time = TimeScheduler.find_free_time(
                    db, message.from_user.id, target_date, time_of_day, duration=60
                )
        
        # Не нашли похожих или это новая задача
        db.add_task(
            user_id=message.from_user.id,
            description=message.text,
            category_id=analysis.get('category_id'),
            status=analysis.get('status', 'план'),
            planned_time=planned_time,
            duration=60,
            delegated_to=None
        )
        
        if msg_type == 'completed':
            await message.reply("✅ Отлично! Задача отмечена как выполненная.", reply_markup=main_menu)
        else:
            time_msg = f" на {planned_time}" if planned_time else ""
            await message.reply(f"✅ Задача добавлена в {analysis.get('status', 'план')}{time_msg}.", reply_markup=main_menu)
    
    else:
        db.add_task(user_id=message.from_user.id, description=message.text)
        await message.reply("Задача добавлена в план.", reply_markup=main_menu)

async def run_bot():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)

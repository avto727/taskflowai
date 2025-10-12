#!/usr/bin/env python3
"""
Тест фильтров по дате
Проверяем: today, tomorrow, week
"""

import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "backend", "todoist")
)

load_dotenv()

from crud import TaskFlowTodoist  # noqa: E402


def test_date_filters():
    """Тестирование фильтров по дате"""

    print("🧪 Тестирование фильтров по дате\n")
    print(f"📅 Текущая дата: {datetime.now().strftime('%Y-%m-%d')}")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"📅 Завтра: {tomorrow}")
    week_end = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    print(f"📅 Конец недели: {week_end}")
    print("=" * 60)

    taskflow = TaskFlowTodoist()

    # Получаем все задачи для сравнения
    all_tasks = taskflow.get_all_tasks()
    print(f"\n📊 Всего задач в Todoist: {len(all_tasks)}")

    # Показываем распределение по датам
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    week_end = today + timedelta(days=6)  # 7 дней: сегодня + 6

    tasks_by_date = {
        "today": [],
        "tomorrow": [],
        "week": [],
        "no_date": [],
        "past": [],
    }

    for task in all_tasks:
        due = task.get("due")
        if not due or not due.get("date"):
            tasks_by_date["no_date"].append(task)
            continue

        try:
            due_date_str = due["date"].split("T")[0]
            due_date = datetime.fromisoformat(due_date_str).date()

            if due_date < today:
                tasks_by_date["past"].append(task)
            elif due_date == today:
                tasks_by_date["today"].append(task)
                tasks_by_date["week"].append(task)  # Сегодня тоже в неделе
            elif due_date == tomorrow:
                tasks_by_date["tomorrow"].append(task)
                tasks_by_date["week"].append(task)  # Завтра тоже в неделе
            elif today < due_date <= week_end:
                tasks_by_date["week"].append(task)
        except (ValueError, KeyError, TypeError):
            tasks_by_date["no_date"].append(task)

    print("\n📈 Распределение задач:")
    print(f"  🕐 Просрочено: {len(tasks_by_date['past'])}")
    print(f"  📅 Сегодня: {len(tasks_by_date['today'])}")
    print(f"  ⏭️  Завтра: {len(tasks_by_date['tomorrow'])}")
    print(f"  📆 На неделю: {len(tasks_by_date['week'])}")
    print(f"  ❓ Без даты: {len(tasks_by_date['no_date'])}")

    # Тест 1: Фильтр "сегодня"
    print("\n" + "=" * 60)
    print("🔍 ТЕСТ 1: Фильтр 'today'")
    today_tasks = taskflow.get_tasks_by_time("today")
    print(f"   Результат: {len(today_tasks)} задач")
    print(f"   Ожидалось: {len(tasks_by_date['today'])} задач")

    if len(today_tasks) == len(tasks_by_date["today"]):
        print("   ✅ PASS")
    else:
        print("   ❌ FAIL")
        print("\n   Задачи 'today' по фильтру:")
        for task in today_tasks[:5]:
            print(
                f"     - {task['content']} | {task.get('due', {}).get('date')}"
            )
        print("\n   Ожидаемые задачи 'today':")
        for task in tasks_by_date["today"][:5]:
            print(
                f"     - {task['content']} | {task.get('due', {}).get('date')}"
            )

    # Тест 2: Фильтр "завтра"
    print("\n" + "=" * 60)
    print("🔍 ТЕСТ 2: Фильтр 'tomorrow'")
    tomorrow_tasks = taskflow.get_tasks_by_time("tomorrow")
    print(f"   Результат: {len(tomorrow_tasks)} задач")
    print(f"   Ожидалось: {len(tasks_by_date['tomorrow'])} задач")

    if len(tomorrow_tasks) == len(tasks_by_date["tomorrow"]):
        print("   ✅ PASS")
    else:
        print("   ❌ FAIL")
        print("\n   Задачи 'tomorrow' по фильтру:")
        for task in tomorrow_tasks[:5]:
            print(
                f"     - {task['content']} | {task.get('due', {}).get('date')}"
            )

    # Тест 3: Фильтр "неделя"
    print("\n" + "=" * 60)
    print("🔍 ТЕСТ 3: Фильтр 'week'")
    week_tasks = taskflow.get_tasks_by_time("week")
    print(f"   Результат: {len(week_tasks)} задач")
    print(f"   Ожидалось: {len(tasks_by_date['week'])} задач")

    if len(week_tasks) == len(tasks_by_date["week"]):
        print("   ✅ PASS")
    else:
        print("   ❌ FAIL")
        print("\n   Задачи 'week' по фильтру:")
        for task in week_tasks[:5]:
            print(
                f"     - {task['content']} | {task.get('due', {}).get('date')}"
            )

    # Итоги
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ:")

    tests_passed = 0
    tests_total = 3

    if len(today_tasks) == len(tasks_by_date["today"]):
        tests_passed += 1
    if len(tomorrow_tasks) == len(tasks_by_date["tomorrow"]):
        tests_passed += 1
    if len(week_tasks) == len(tasks_by_date["week"]):
        tests_passed += 1

    print(f"✅ Пройдено: {tests_passed}/{tests_total}")
    print(f"❌ Провалено: {tests_total - tests_passed}/{tests_total}")

    if tests_passed == tests_total:
        print("\n🎉 Все фильтры работают корректно!")
        return True
    else:
        print("\n⚠️  Обнаружены проблемы с фильтрами!")
        return False


if __name__ == "__main__":
    success = test_date_filters()
    sys.exit(0 if success else 1)

"""
Тест ИИ-анализа для TaskFlowAI
"""

from ai_processor import AIProcessor
from constants import TASK_EXAMPLES

# Категории Irga
CATEGORIES = TASK_EXAMPLES


def test_ai_analysis():
    """Тестирование ИИ-анализа"""
    ai = AIProcessor()

    test_messages = [
        "сходить в спортзал завтра утром",
    ]

    print("🧠 Тестирование ИИ-анализа TaskFlowAI:")
    print("=" * 50)

    for message in test_messages:
        print(f"\n📝 Сообщение: '{message}'")

        try:
            result = ai.analyze_message(message, CATEGORIES)

            # Находим название категории
            category_name = "Неизвестно"
            if result.get("category_id"):
                for cat_id, cat_name in CATEGORIES:
                    if cat_id == result["category_id"]:
                        category_name = cat_name
                        break

            print(f"   Тип: {result.get('type', 'неизвестно')}")
            print(
                f"   Категория: {category_name} "
                f"(ID: {result.get('category_id')})"
            )
            print(f"   Статус: {result.get('status', 'неизвестно')}")
            print(f"   Время: {result.get('planned_time', 'не указано')}")
            print(
                f"   Тип выполнения: "
                f"{result.get('execution_type', 'не указано')}"
            )

        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

    print("\n🎉 Тестирование завершено!")


if __name__ == "__main__":
    test_ai_analysis()

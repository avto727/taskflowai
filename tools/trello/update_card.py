#!/usr/bin/env python3
"""
Update Trello card description
"""

from trello_client import TaskFlowTrello

def update_card_description():
    client = TaskFlowTrello()
    
    # ID карточки из URL
    card_id = "rDu366gp"
    
    description = """
## Что нужно изменить:
1. **Telegram бот** - команда /projects → кнопки и текст
2. **MCP клиент** - методы get_projects() → get_life_areas()
3. **README** - обновить описание терминологии
4. **Комментарии в коде** - заменить "проекты" на "области жизни"

## Файлы для изменения:
- `clients/telegram/simple_bot.py` - обработчики команд
- `mcp/simple_client.py` - методы и логика
- `README.md` - пользовательская документация

## Подход:
- Сохранить совместимость с Todoist API (там остаются "projects")
- Изменить только пользовательский интерфейс и терминологию
- Обновить все сообщения бота

## Результат:
- Вместо "📂 Ваши проекты" → "🌟 Области жизни"
- Вместо "Покажи задачи проекта здоровье" → "Покажи задачи по здоровью"
- В коде: get_projects() → get_life_areas()
"""
    
    try:
        # Обновляем описание карточки
        response = client._make_request(f"/cards/{card_id}", "PUT", {
            "desc": description.strip()
        })
        print(f"✅ Описание карточки обновлено: {response.get('name', 'Unknown')}")
        print(f"🔗 URL: {response.get('url', 'No URL')}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_card_description()
# MCP сервер для Trello

## Описание

MCP сервер для работы с Trello через REST API. Используется Python и библиотека FastMCP.

## Конфигурация

Через переменные окружения (`.env`):

- `TRELLO_API_KEY` — API ключ Trello
- `TRELLO_TOKEN` — API токен
- `TRELLO_BOARD_ID` — ID доски по умолчанию (опционально)

## Инструменты

### Основные операции

**get_board_lists(board_id=None)**
- Получить списки (колонки) доски
- board_id опционален, используется из .env

**get_board_cards(board_id=None)**
- Получить все карточки доски

**create_card(list_name, name, desc="", board_id=None)**
- Создать карточку в списке
- list_name: название списка (например, "Бэклог")
- name: название карточки
- desc: описание (опционально)

**update_card(card_id, name=None, desc=None)**
- Обновить название или описание карточки

**move_card(card_id, list_name, board_id=None)**
- Переместить карточку в другой список
- list_name: название целевого списка

**search_cards(query, board_id=None)**
- Поиск карточек по тексту в названии или описании

### Работа с чеклистами

**get_card_checklists(card_id)**
- Получить все чеклисты карточки

**add_checklist_item(card_id, checklist_name, item_name)**
- Добавить пункт в чеклист
- checklist_name: название чеклиста
- item_name: текст пункта

**check_checklist_item(card_id, item_id)**
- Отметить пункт чеклиста как выполненный

## Установка

1. Установить зависимости:
```bash
pip install fastmcp requests python-dotenv
```

2. Создать `.env` с переменными:
```
TRELLO_API_KEY=your_key
TRELLO_TOKEN=your_token
TRELLO_BOARD_ID=your_board_id
```

3. Запустить сервер:
```bash
python tools/mcp/trello_mcp_server.py
```

## Интеграция с Amazon Q

Создать файл `~/.aws/amazonq/mcp.json`:

```json
{
  "mcpServers": {
    "trello": {
      "command": "python3",
      "args": [
        "/Users/a.dubodelov/PycharmProjects/irga_new/tools/mcp/trello_mcp_server.py"
      ],
      "env": {
        "TRELLO_API_KEY": "your_key",
        "TRELLO_TOKEN": "your_token",
        "TRELLO_BOARD_ID": "your_board_id"
      }
    }
  }
}
```

Перезапустить IDE.

## Примеры использования

**Создать эпик:**
```python
create_card(
    list_name="Бэклог",
    name="Б20. Новый эпик",
    desc="Описание эпика"
)
```

**Переместить в работу:**
```python
move_card(
    card_id="card_id",
    list_name="В процессе"
)
```

**Найти карточки:**
```python
search_cards(query="Obsidian")
```

**Отметить пункт чеклиста:**
```python
check_checklist_item(
    card_id="card_id",
    item_id="item_id"
)
```

## Преимущества

- ✅ Простая настройка
- ✅ Работа через Amazon Q напрямую
- ✅ Нет необходимости в Python скриптах
- ✅ Единый стек (Python)
- ✅ Расширяемость

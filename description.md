# TaskFlowAI - Техническое описание

> **Для разработчиков**

## Архитектура

TaskFlowAI использует MCP (Model Context Protocol) архитектуру:

```
Telegram Bot → MCP Client → Ollama + MCP Tools → Todoist API
```

### Компоненты:

- **MCP Client** (`mcp/simple_client.py`) - обработка естественного языка
- **MCP Tools** (`mcp/todoist_tools.py`) - инструменты для работы с Todoist
- **Telegram Bot** (`clients/telegram/simple_bot.py`) - интерфейс пользователя
- **Auth System** (`auth.py`) - простая авторизация через JSON файл

## Технологии

- **Python 3.11+**
- **MCP (Model Context Protocol)** - протокол взаимодействия с ИИ
- **Ollama + Qwen 2.5:7b** - локальная ИИ-модель
- **Todoist REST API v2** - хранение и синхронизация задач
- **aiogram 3.x** - Telegram Bot framework
- **Docker** - контейнеризация

## Структура проекта

```
irga/
├── mcp/                    # MCP сервер и клиент
│   ├── simple_client.py    # Ollama + MCP клиент
│   ├── todoist_tools.py    # Инструменты Todoist
│   └── tests/              # Тесты MCP функций
├── clients/telegram/       # Telegram бот
│   ├── simple_bot.py       # Основной бот
│   └── telegram_users.json # Токены пользователей
├── auth.py                 # Система авторизации
├── requirements.txt        # Python зависимости
├── Dockerfile             # Docker образ
├── docker-compose.yml     # Docker сервисы
├── docker-run.sh          # Скрипт запуска
└── .env                   # Конфигурация
```

## Разработка

### Локальная разработка:

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск Ollama
ollama serve
ollama pull qwen2.5:7b

# Запуск бота
python clients/telegram/simple_bot.py
```

### Тестирование MCP:

```bash
cd mcp/tests
python test_mcp.py          # Базовые функции
python test_mcp_tools.py    # Интеграция с Ollama
```

### Docker разработка:

```bash
# Сборка и запуск
docker-compose up --build

# Логи
docker logs -f taskflowai_bot

# Остановка
docker-compose down
```

## API Reference

### MCP Tools

- `get_tasks(project_id=None, filter_expr=None)` - получить задачи
- `create_task(content, due_string=None, parent_id=None)` - создать задачу
- `complete_task(task_id)` - завершить задачу
- `delete_task(task_id)` - удалить задачу
- `update_task(task_id, **kwargs)` - обновить задачу
- `get_projects()` - получить проекты

### Умные функции

- `_parse_due_date(content)` - парсинг даты и времени из текста
- `_is_task_content(message)` - определение задач по глаголам действия
- `_handle_reschedule_overdue()` - перенос просроченных задач
- `_group_tasks_by_date()` - группировка задач по датам

## Конфигурация

### .env файл:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TODOIST_API_TOKEN=your_todoist_api_token
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### Ollama модель:

- **Модель:** qwen2.5:7b (~4GB)
- **Язык:** Русский (системный промпт)
- **Функции:** Function calling для MCP tools

## Деплой

### Локальный Docker:

```bash
./docker-run.sh
```

### Продакшн:

1. Настроить .env с продакшн токенами
2. Запустить Ollama на сервере
3. Деплой через docker-compose

## История версий

- **v1.0** - MCP архитектура, базовые функции
- **v0.x** - Legacy REST API архитектура (удалена)

## Roadmap v2.0

- Web интерфейс (React/Vue)
- OAuth авторизация
- Мультиязычность
- Интеграция с другими сервисами
- Облачная Ollama

## Лицензия

MIT License
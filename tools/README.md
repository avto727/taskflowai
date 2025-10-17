# TaskFlowAI Tools

Служебные инструменты для разработки TaskFlowAI.

## 📋 Trello Integration

### Установка:
```bash
pip install -r tools/trello/requirements-dev.txt
```

### Настройка:
Добавьте в `.env`:
```env
TRELLO_API_KEY=your_api_key
TRELLO_TOKEN=your_token
```

### Получение ключей:
1. API Key: https://trello.com/app-key
2. Token: https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&name=TaskFlowAI&key=YOUR_API_KEY

### Использование:
```bash
# Синхронизация roadmap с Trello
python tools/trello/sync_roadmap.py

# Тест подключения
python -c "from tools.trello.trello_client import TaskFlowTrello; t=TaskFlowTrello(); print('OK')"
```

## 📁 Структура:
```
tools/
└── trello/
    ├── trello_client.py      # Базовый клиент
    ├── sync_roadmap.py       # Синхронизация roadmap
    └── requirements-dev.txt  # Dev зависимости
```
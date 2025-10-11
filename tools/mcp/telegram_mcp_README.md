# MCP сервер для Telegram Bot

## Описание

MCP сервер для автоматического тестирования Telegram бота через Bot API.

## Конфигурация

Добавьте в `.env`:

```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
TELEGRAM_TEST_CHAT_ID=ваш_chat_id
```

**Как узнать chat_id:**
1. Напишите боту `/start`
2. Откройте: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Найдите `"chat":{"id":123456789}`

## Инструменты

### send_message(text, chat_id=None)
Отправить сообщение боту

**Пример:**
```python
send_message("Ирга, привет!")
```

### get_updates(offset=None, limit=10)
Получить обновления от бота

### get_last_message(chat_id=None)
Получить последнее сообщение

### send_and_wait(text, chat_id=None, wait_seconds=3)
Отправить сообщение и получить ответ

**Пример:**
```python
result = send_and_wait("Ирга, покажи задачи")
print(result["response"])
```

### test_irga_commands(chat_id=None)
Автоматически протестировать все команды Ирги

**Возвращает:**
```json
[
  {
    "command": "Ирга, привет!",
    "response": "🌆 Добрый вечер...",
    "success": true
  },
  ...
]
```

## Использование

### Через Python:

```python
import requests
import time

BOT_TOKEN = "your_token"
CHAT_ID = "your_chat_id"

# Отправить
requests.get(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    params={"chat_id": CHAT_ID, "text": "Ирга, привет!"}
)

# Подождать
time.sleep(3)

# Получить ответ
r = requests.get(
    f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
)
print(r.json())
```

### Через MCP (когда Amazon Q подключит):

```
Просто спросите меня:
"Протестируй команды Ирги"
"Отправь боту: Ирга, покажи задачи"
```

## Автотесты

Создайте файл `tests/test_irga_bot.py`:

```python
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_TEST_CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": text})

def test_irga_commands():
    commands = [
        "Ирга, привет!",
        "Ирга, помоги",
        "Ирга, покажи задачи",
    ]
    
    for cmd in commands:
        print(f"Тест: {cmd}")
        send_message(cmd)
        time.sleep(5)
        print("✅ Отправлено")

if __name__ == "__main__":
    test_irga_commands()
```

## Преимущества

- ✅ Автоматическое тестирование
- ✅ Не нужно вручную писать в бота
- ✅ Проверка ответов
- ✅ Интеграция с CI/CD

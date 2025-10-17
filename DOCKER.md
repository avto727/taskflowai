# 🐳 TaskFlowAI Docker

Запуск TaskFlowAI в Docker контейнерах.

## 🚀 Быстрый старт

```bash
# 1. Создайте .env файл с токенами
cp .env.example .env
# Отредактируйте .env

# 2. Запустите
./docker-run.sh
```

## 📋 Требования

- Docker
- Docker Compose
- 4GB RAM (для Ollama)
- Токены Telegram и Todoist

## 🔧 Конфигурация

### .env файл

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TODOIST_API_TOKEN=your_todoist_api_token
OLLAMA_BASE_URL=http://ollama:11434
```

### Сервисы

- **taskflowai** - Telegram бот
- **ollama** - локальная установка (порт 11434)

## 📊 Управление

```bash
# Статус
docker-compose ps

# Логи
docker-compose logs -f taskflowai
docker-compose logs -f ollama

# Перезапуск
docker-compose restart taskflowai

# Остановка
docker-compose down

# Полная очистка
docker-compose down -v
docker system prune -a
```

## 🔍 Отладка

### Проверка Ollama

```bash
# Проверить локальную Ollama
curl http://localhost:11434/api/tags

# Тест модели
ollama run qwen2.5:7b "Привет"
```

### Проверка бота

```bash
# Логи бота
docker-compose logs taskflowai

# Войти в контейнер
docker-compose exec taskflowai bash
```

## 📁 Структура

```
irga/
├── Dockerfile              # Образ приложения
├── docker-compose.yml      # Оркестрация сервисов
├── docker-run.sh          # Скрипт запуска
├── .dockerignore          # Исключения для Docker
├── data/                  # Данные (volume)
└── clients/telegram/telegram_users.json  # Токены пользователей
```

## ⚠️ Важно

- Файл `telegram_users.json` монтируется как volume для сохранения авторизации
- Ollama должна быть установлена локально с моделью qwen2.5:7b
- Запустите `ollama serve` перед запуском Docker

## 🚀 Продакшн

Для продакшн деплоя используйте:

```bash
# Запуск в фоне
docker-compose up -d

# Автозапуск при перезагрузке
docker-compose up -d --restart unless-stopped
```
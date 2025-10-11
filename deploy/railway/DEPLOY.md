# Деплой TaskFlowAI на Railway

## Подготовка (выполнено ✅)

- ✅ `Procfile` - команда запуска API
- ✅ `railway.json` - конфиг для API
- ✅ `railway.bot.json` - конфиг для бота
- ✅ `runtime.txt` - версия Python
- ✅ `.dockerignore` - исключения при деплое

## Деплой на Railway

### 1. Регистрация

1. Перейти на https://railway.app
2. Sign up with GitHub
3. Подтвердить email

### 2. Создание проекта

1. New Project → Deploy from GitHub repo
2. Выбрать репозиторий `irga_new`
3. Railway автоматически создаст сервис

### 3. Настройка API сервиса

**Variables (переменные окружения):**
```
TODOIST_API_TOKEN=your_default_token_here
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
```

**Settings:**
- Start Command: `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`
- Root Directory: `/`

### 4. Создание Bot сервиса

1. В том же проекте: New → GitHub Repo (тот же репо)
2. Settings → Start Command: `python clients/telegram/simple_bot.py`

**Variables:**
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TODOIST_API_TOKEN=your_default_token_here
```

### 5. Проверка

**API:**
- Railway даст URL типа: `https://irga-new-production.up.railway.app`
- Проверить: `https://your-url.railway.app/health`

**Bot:**
- Написать боту в Telegram
- Проверить логи в Railway

## Важно

⚠️ **Ollama отключён** - ИИ-анализ не работает на Railway
- Категории нужно задавать вручную
- Или использовать OpenAI API (платно)

## Мониторинг

- Логи: Railway Dashboard → Deployments → Logs
- Метрики: Railway Dashboard → Metrics
- Бюджет: Settings → Usage

## Troubleshooting

**Проблема:** Bot не запускается
**Решение:** Проверить TELEGRAM_BOT_TOKEN в Variables

**Проблема:** API не отвечает
**Решение:** Проверить логи, возможно нужно добавить CORS

**Проблема:** Превышен бюджет $5
**Решение:** 
- Уменьшить ресурсы (Settings → Resources)
- Или добавить карту для оплаты

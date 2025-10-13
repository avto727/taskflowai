# 🚀 Деплой v1.0 на Railway (Гибридный вариант)

> **Статус:** 🔷 Н3. В работе (Октябрь 2025)  
> **Версия:** v1.0 (19 эпиков завершено)

## 📋 Архитектура
- **Ollama**: Локально на рабочем компе (через ngrok/Cloudflare)
- **API + Bot**: Railway.app

**Почему гибридный?**
- Ollama требует мощное железо (GPU для быстрых ответов)
- Railway не предоставляет GPU в бесплатном тарифе
- Локальный Ollama + ngrok = бесплатное решение для тестирования

---

## 🔧 Шаг 1: Настройка локального Ollama

### 1.1. Запустить Ollama
```bash
# В отдельном терминале
ollama serve
```

### 1.2. Запустить ngrok
```bash
# В еще одном терминале
ngrok http 11434
```

**Результат:** Получите URL вида `https://abc123.ngrok.io`

### 1.3. Проверить доступ
```bash
curl https://abc123.ngrok.io/api/tags
```

---

## 🚂 Шаг 2: Деплой API на Railway

### 2.1. Создать проект на Railway
1. Зайти на [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. Выбрать репозиторий `irga`
4. Выбрать ветку `release-1`

### 2.2. Настроить переменные окружения
```env
# Обязательные
TODOIST_API_TOKEN=ваш_токен
OLLAMA_BASE_URL=https://abc123.ngrok.io
API_BASE_URL=https://ваш-api.railway.app

# Опциональные (если нужна авторизация)
AUTH_ENABLED=false
```

### 2.3. Указать конфигурацию
- **Root Directory**: оставить пустым (корень проекта)
- **Start Command**: `uvicorn backend.api.main_api:app --host 0.0.0.0 --port $PORT`

### 2.4. Деплой
Railway автоматически запустит деплой после коммита.

---

## 🤖 Шаг 3: Деплой Bot на Railway

### 3.1. Создать второй сервис
1. В том же проекте Railway → **New Service**
2. Выбрать тот же репозиторий и ветку

### 3.2. Настроить переменные окружения
```env
# Обязательные
TELEGRAM_BOT_TOKEN=ваш_токен
TODOIST_API_TOKEN=ваш_токен
OLLAMA_BASE_URL=https://abc123.ngrok.io
API_BASE_URL=https://ваш-api.railway.app

# Опциональные
AUTH_ENABLED=false
```

### 3.3. Указать конфигурацию
- **Root Directory**: оставить пустым
- **Start Command**: `python clients/telegram/simple_bot.py`

### 3.4. Деплой
Railway автоматически запустит бота.

---

## ✅ Шаг 4: Проверка

### 4.1. API Health Check
```bash
curl https://ваш-api.railway.app/health
```

Ожидаемый ответ:
```json
{
  "status": "ok",
  "ollama": "connected",
  "todoist": "connected"
}
```

### 4.2. Telegram Bot
1. Открыть бот в Telegram
2. Отправить `/start`
3. Проверить команды меню

### 4.3. Тестовая задача
```
сходить в спортзал завтра утром
```

Ожидаемый результат:
- ✅ Категория: Здоровье (Спорт)
- ✅ Дата: tomorrow
- ✅ Время: 09:00

---

## 🔒 Безопасность

### Важно!
- **ngrok URL меняется** при каждом перезапуске (бесплатная версия)
- Для продакшена рекомендуется:
  - Платный ngrok (статичный домен)
  - Cloudflare Tunnel
  - VPS с белым IP

### Обновление OLLAMA_BASE_URL
Если ngrok URL изменился:
1. Railway Dashboard → Service → Variables
2. Обновить `OLLAMA_BASE_URL`
3. Сервисы перезапустятся автоматически

---

## 📊 Мониторинг

### Railway Logs
```bash
# Смотреть логи API
railway logs --service api

# Смотреть логи Bot
railway logs --service bot
```

### Локальные логи Ollama
```bash
# В терминале где запущен ollama serve
# Видны все запросы от Railway
```

---

## 🐛 Troubleshooting

### API не стартует
1. Проверить логи: `railway logs`
2. Проверить переменные окружения
3. Проверить `OLLAMA_BASE_URL` доступен извне

### Bot не отвечает
1. Проверить `TELEGRAM_BOT_TOKEN`
2. Проверить `API_BASE_URL`
3. Проверить логи бота

### Ollama timeout
1. Проверить ngrok активен
2. Проверить `curl https://abc123.ngrok.io/api/tags`
3. Увеличить timeout в `ai_processor.py`

---

## 📝 Полезные команды

```bash
# Локально запустить как на Railway
PORT=8000 uvicorn backend.api.main_api:app --host 0.0.0.0

# Проверить Ollama
curl http://localhost:11434/api/tags

# Проверить ngrok
curl https://abc123.ngrok.io/api/tags
```

---

## 📦 Что готово для деплоя (2025-10-13)

### ✅ Код полностью готов
- ✅ Все 73 ошибки линтеров исправлены (8 линтеров: RUFF, BLACK, 
  VULTURE, PYLINT, FLAKE8-BUGBEAR)
- ✅ Рефакторинг завершён (нет дублирования, нет мёртвого кода)
- ✅ API работает локально (FastAPI на порту 8000)
- ✅ Bot работает локально (aiogram 3.x)
- ✅ Ollama интегрирован (модель qwen2.5:7b)
- ✅ Все зависимости в `requirements.txt`

### ✅ Конфигурация Railway готова
- ✅ `Procfile` - команды запуска
- ✅ `railway.json` - конфиг API сервиса
- ✅ `railway.bot.json` - конфиг Bot сервиса
- ✅ `runtime.txt` - Python 3.13
- ✅ `.gitignore` - исключения для деплоя

### ✅ Документация готова
- ✅ `DEPLOY_V1.md` - пошаговая инструкция деплоя
- ✅ `README.md` - общая документация проекта
- ✅ `description.md` - техническая архитектура
- ✅ Все переменные окружения описаны

### 🔧 Что нужно сделать при деплое

**1. Подготовка (5 минут):**
   - Запустить локально `ollama serve`
   - Запустить `ngrok http 11434` (или Cloudflare Tunnel)
   - Скопировать ngrok URL (например: `https://abc123.ngrok.io`)

**2. Railway настройка (10 минут):**
   - Создать проект на railway.app
   - Создать 2 сервиса: API и Bot
   - Добавить переменные окружения (см. секцию 2.2 и 3.2)
   - Railway автоматически задеплоит из ветки `release-1`

**3. Проверка (5 минут):**
   - Проверить `/health` эндпоинт API
   - Отправить `/start` в Telegram боте
   - Создать тестовую задачу

### 📝 Переменные окружения (критично!)

**API сервис на Railway:**
```env
TODOIST_API_TOKEN=ваш_токен_todoist
OLLAMA_BASE_URL=https://ваш-ngrok-url.ngrok.io
API_BASE_URL=https://ваш-api.railway.app
AUTH_ENABLED=false
```

**Bot сервис на Railway:**
```env
TELEGRAM_BOT_TOKEN=ваш_токен_telegram
TODOIST_API_TOKEN=ваш_токен_todoist
OLLAMA_BASE_URL=https://ваш-ngrok-url.ngrok.io
API_BASE_URL=https://ваш-api.railway.app
AUTH_ENABLED=false
```

### ⚠️ Важно знать через год

**ngrok URL меняется при перезапуске:**
- Бесплатный ngrok даёт новый URL каждый раз
- Решение 1: Платный ngrok ($8/мес) - статичный домен
- Решение 2: Cloudflare Tunnel (бесплатно, стабильно)
- Решение 3: VPS с белым IP (для продакшена)

**Обновление OLLAMA_BASE_URL:**
1. Railway Dashboard → Your Project → Variables
2. Обновить `OLLAMA_BASE_URL` в обоих сервисах
3. Сервисы перезапустятся автоматически

**Структура проекта не менялась:**
- `backend/api/main_api.py` - FastAPI сервер
- `clients/telegram/simple_bot.py` - Telegram бот
- `backend/irga/ai_processor.py` - AI анализ
- `backend/todoist/crud.py` - Todoist интеграция

**Если что-то сломалось:**
1. Проверить логи: `railway logs --service api` или `--service bot`
2. Проверить ngrok активен: `curl https://your-url.ngrok.io/api/tags`
3. Проверить переменные окружения в Railway Dashboard
4. Проверить ветку деплоя: должна быть `release-1`

---

## 🎯 Следующие шаги (v2.0 - 43 задачи в бэклоге)

- [ ] Перенести Ollama на VPS (GPU сервер)
- [ ] Настроить Cloudflare Tunnel (вместо ngrok)
- [ ] Продуктовая интеграция Trello ↔ Todoist
- [ ] Чат-бот поддержки
- [ ] MCP интеграции (Trello/Todoist)
- [ ] Добавить мониторинг (Sentry, Grafana)
- [ ] Настроить автоматические бэкапы БД
- [ ] CI/CD пайплайны (тесты перед деплоем)








# 🚀 Деплой v1.0 на Railway (Гибридный вариант)

## 📋 Архитектура
- **Ollama**: Локально на рабочем компе (через ngrok)
- **API + Bot**: Railway.app

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

## 🎯 Следующие шаги (Release 2)

- [ ] Перенести Ollama на VPS
- [ ] Настроить Cloudflare Tunnel (вместо ngrok)
- [ ] Добавить мониторинг (Sentry, Grafana)
- [ ] Настроить автоматические бэкапы БД
- [ ] CI/CD пайплайны (тесты перед деплоем)


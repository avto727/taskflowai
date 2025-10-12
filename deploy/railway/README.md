# Railway Deployment

Файлы для деплоя TaskFlowAI на Railway.app

## 📁 Файлы

- `Procfile` - команда запуска API
- `railway.json` - конфиг для API сервиса
- `railway.bot.json` - конфиг для Bot сервиса
- `runtime.txt` - версия Python (3.13)
- `DEPLOY_V1.md` - инструкция деплоя v1.0 (гибридный)
- `DEPLOY.md` - полная инструкция (все варианты)

## 🚀 Версия 1.0 (Текущая)

**Архитектура:** Гибридный деплой
- **Ollama:** Локально (через ngrok)
- **API + Bot:** Railway.app

**Инструкция:** См. `DEPLOY_V1.md`

## 📋 Быстрый старт

### 1. Локальная подготовка
```bash
# Запустить Ollama
ollama serve

# Пробросить через ngrok
ngrok http 11434
```

### 2. Railway настройка
1. Создать проект на [railway.app](https://railway.app)
2. Два сервиса: API и Bot
3. Переменные окружения (см. DEPLOY_V1.md)

### 3. Деплой
```bash
# Коммит в ветку release-1
git push origin release-1
```

Railway автоматически задеплоит изменения.

## 🔗 Полезные ссылки

- [Railway Dashboard](https://railway.app/dashboard)
- [ngrok Dashboard](https://dashboard.ngrok.com)
- [Todoist API](https://developer.todoist.com)

## 📊 Следующие релизы

**v2.0:** Полный деплой Ollama на VPS
**v3.0:** Kubernetes + масштабирование

# Railway Deployment

Файлы для деплоя TaskFlowAI на Railway.app

## Файлы

- `Procfile` - команда запуска API
- `railway.json` - конфиг для API сервиса
- `railway.bot.json` - конфиг для Bot сервиса
- `runtime.txt` - версия Python
- `.env.railway` - пример переменных окружения
- `.dockerignore` - исключения для деплоя
- `DEPLOY.md` - полная инструкция по деплою

## Быстрый старт

1. Зарегистрироваться на https://railway.app
2. Создать 2 сервиса из GitHub репозитория
3. Настроить переменные из `.env.railway`
4. Деплой автоматический

Подробнее в `DEPLOY.md`

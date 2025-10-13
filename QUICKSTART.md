# 🚀 QUICKSTART — Возврат к проекту через год

> **Дата создания:** 2025-10-13  
> **Версия:** v1.0 (19 эпиков завершено, готов к деплою)  
> **Статус:** Код полностью готов, деплой в процессе (Н3)

---

## 📋 Что это за проект?

**TaskFlowAI** — умный таск-менеджер на базе Todoist с AI-автоматизацией.

- **Backend:** Todoist API (хранение) + Irga AI (анализ)
- **AI:** Ollama + Qwen 2.5:7b (локально)
- **Клиент:** Telegram бот (aiogram 3.x)
- **API:** FastAPI на порту 8000

**Аналогия:** Todoist — двигатель, Irga — автопилот, TaskFlowAI — Tesla.

---

## ⚡ Быстрый старт (5 минут)

```bash
# 1. Активировать окружение
cd /Users/a.dubodelov/Documents/irga
source .venv/bin/activate

# 2. Установить зависимости (если нужно)
pip install -r requirements.txt

# 3. Запустить Ollama (в отдельном терминале)
ollama serve

# 4. Запустить API (в отдельном терминале)
python backend/api/main_api.py

# 5. Запустить бота (в отдельном терминале)
python clients/telegram/simple_bot.py
```

**Проверка работы:**
- API: http://localhost:8000/docs
- Bot: отправить `/start` в Telegram

---

## 📦 Что готово к деплою (Railway)

### ✅ Код
- Все 73 ошибки линтеров исправлены (8 линтеров)
- Рефакторинг завершён (нет дублирования, нет мёртвого кода)
- `simple_bot.py` — 1166 строк (было 950, рефакторинг снизил
  сложность)

### ✅ Конфигурация Railway
- `deploy/railway/Procfile` — команды запуска
- `deploy/railway/railway.json` — API сервис
- `deploy/railway/railway.bot.json` — Bot сервис
- `deploy/railway/runtime.txt` — Python 3.13

### ✅ Документация
- `deploy/railway/DEPLOY_V1.md` — пошаговая инструкция деплоя
- `README.md` — общая документация
- `description.md` — техническая архитектура

---

## 🚂 Деплой на Railway (20 минут)

**Архитектура:** Гибридный деплой
- **Ollama:** Локально (через ngrok/Cloudflare Tunnel)
- **API + Bot:** Railway.app

**Инструкция:** См. `deploy/railway/DEPLOY_V1.md`

**Кратко:**
1. Запустить локально `ollama serve`
2. Запустить `ngrok http 11434` → скопировать URL
3. Railway: создать проект, 2 сервиса (API + Bot)
4. Добавить переменные окружения (см. DEPLOY_V1.md секция 2.2 и 3.2)
5. Railway автоматически задеплоит из ветки `release-1`

---

## 📂 Структура проекта

```
irga/
├─ backend/
│  ├─ api/main_api.py          # FastAPI сервер (порт 8000)
│  ├─ irga/ai_processor.py     # AI анализ (Ollama)
│  ├─ irga/taskflow_integration.py  # Irga + Todoist
│  ├─ todoist/crud.py          # Todoist CRUD
│  └─ auth/db.py               # SQLite для токенов
├─ clients/telegram/
│  └─ simple_bot.py            # Telegram бот (1166 строк)
├─ deploy/railway/
│  ├─ DEPLOY_V1.md             # 📖 Инструкция деплоя
│  ├─ Procfile                 # Команды запуска
│  └─ railway*.json            # Конфиги Railway
├─ tests/                      # Тесты
├─ tools/                      # Служебные скрипты
│  ├─ trello/                  # Управление Trello (roadmap)
│  ├─ kaiten/                  # Kaiten интеграция
│  └─ miro/                    # Miro roadmap
├─ README.md                   # 📖 Главная документация
├─ description.md              # 📖 Техническая архитектура
├─ requirements.txt            # Зависимости Python
└─ lint.sh                     # 8 линтеров (все проходят)
```

---

## 🔑 Ключевые файлы для понимания

**Если забыл как всё работает:**

1. **`README.md`** — общая документация, команды бота, установка
2. **`description.md`** — архитектура, философия, процессы
3. **`deploy/railway/DEPLOY_V1.md`** — деплой на Railway
4. **`backend/api/main_api.py`** — API эндпоинты
5. **`clients/telegram/simple_bot.py`** — логика бота
6. **`backend/irga/taskflow_integration.py`** — AI + Todoist

---

## 🧰 Полезные команды

```bash
# Линтеры (все должны проходить ✅)
./lint.sh

# Автоисправление форматирования
./lint-fix.sh

# Запуск тестов
pytest tests/

# Проверка API
curl http://localhost:8000/health

# Проверка Ollama
curl http://localhost:11434/api/tags
```

---

## 📊 Текущий статус проекта

**✅ v1.0 - ЗАВЕРШЁН** (19/21 эпиков, 2025-10-13)
- Backend MVP (Todoist + Irga + FastAPI)
- Telegram Bot с умным чатом
- Мультипользовательская авторизация
- AI-анализ (Ollama + Qwen 2.5:7b)
- Подзадачи с иерархией
- Все 73 ошибки линтеров исправлены

**🔷 В работе:**
- Н3: Деплой v1.0 на Railway

**📋 Бэклог v2.0:** (43 задачи в Trello)
- Продуктовая интеграция: Trello ↔ Todoist
- Чат-бот поддержки
- MCP интеграции (Trello/Todoist)
- Улучшения AI промпта
- Ollama на VPS

---

## 🔗 Управление проектом

**Trello:** https://trello.com/b/uCUxLXBA/taskflowai
- 19 эпиков в "Готово"
- 1 эпик в "Нужно сделать" (Н3: Деплой)
- 1 эпик в "Нужно сделать" (Г14: v2.0)
- 43 задачи в "Бэклоге" (помечены [v2.0])

**Ветки Git:**
- `main` — стабильная версия
- `DEV-1-irga-deploy` — текущая ветка разработки
- `release-1` — для деплоя на Railway (создать при деплое)

---

## ⚠️ Важные замечания через год

1. **ngrok URL меняется** при каждом перезапуске (бесплатная версия)
   - Решение: Cloudflare Tunnel (бесплатно, стабильно)
   - Или платный ngrok ($8/мес)

2. **Python 3.13** требуется для Railway
   - Указано в `runtime.txt`

3. **Ollama модель:** `qwen2.5:7b`
   - Проверить: `ollama list`
   - Скачать: `ollama pull qwen2.5:7b`

4. **Токены:**
   - Todoist: https://todoist.com/app/settings/integrations
   - Telegram Bot: https://t.me/BotFather

5. **Линтеры настроены строго (79 символов)**
   - Все проходят без ошибок
   - Запуск: `./lint.sh`

---

## 📞 Контакты и ресурсы

- **Railway:** https://railway.app
- **Todoist API:** https://developer.todoist.com
- **Ollama:** https://ollama.ai
- **ngrok:** https://ngrok.com
- **Cloudflare Tunnel:** https://developers.cloudflare.com/cloudflare-one/

---

## 🎯 Что делать дальше?

**Если просто запустить локально:**
→ См. раздел "⚡ Быстрый старт"

**Если деплоить на Railway:**
→ См. `deploy/railway/DEPLOY_V1.md`

**Если продолжить разработку v2.0:**
→ См. Trello бэклог (43 задачи) и `description.md`

---

*Удачи! Всё готово к работе. Код чистый, документация полная,
деплой подготовлен.* 🚀


# Кайтен для управления TaskFlowAI

> **"Строительные леса"** - временный инструмент для управления проектом

## Что это?

Интеграция с Кайтен (kaiten.ru) для визуализации roadmap.csv

## Настройка (пошагово)

### 1. Регистрация
- Зайти на https://kaiten.ru
- Зарегистрироваться (email или через соцсети)

### 2. Создать доску
- "Создать доску" → "TaskFlowAI Development"
- Добавить колонки:
  - 📋 Backlog
  - 📝 To Do
  - 🔄 In Progress
  - 🧪 Testing
  - ✅ Done

### 3. Получить токены
- Настройки → API → "Создать токен"
- Скопировать токен
- Скопировать ID доски (из URL: `kaiten.ru/space/XXX/board/YYY` - YYY это ID)

### 4. Добавить в `.env`
```bash
KAITEN_API_TOKEN=ваш_токен
KAITEN_BOARD_ID=123456
```

### 5. Проверить подключение
```bash
python tools/kaiten/kaiten_client.py
```

## Использование

### Синхронизация roadmap → Кайтен:
```bash
python tools/kaiten/sync_roadmap.py
```

### Обновление roadmap из Кайтен:
```bash
python tools/kaiten/update_from_kaiten.py
```

## Структура доски

**Колонки:**
- 📋 Backlog
- 📝 To Do
- 🔄 In Progress
- 🧪 Testing
- ✅ Done

**Метки:**
- 🐛 Bug
- ✨ Feature
- 🔧 Enhancement
- 📚 Documentation

## Удаление

Когда Кайтен больше не нужен - просто удалите папку `tools/kaiten/`

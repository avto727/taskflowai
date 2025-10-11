#!/bin/bash
# Автотест с перезапуском бота

cd "$(dirname "$0")/.."

echo "🚀 Автотест команд Ирги с перезапуском"
echo ""

# 1. Отправляем команды
echo "📤 Отправка команд..."
source .venv/bin/activate
python3 tools/test_irga_working.py

echo ""
echo "⏸️  Остановите бота (Ctrl+C) и перезапустите"
echo "🔄 Бот увидит сообщения и ответит"
echo ""
echo "Команда для перезапуска:"
echo "python3 clients/telegram/simple_bot.py"

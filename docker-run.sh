#!/bin/bash

echo "🚀 Запуск TaskFlowAI в Docker..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "Создайте .env с токенами:"
    echo "TELEGRAM_BOT_TOKEN=your_telegram_token"
    echo "TODOIST_API_TOKEN=your_todoist_token"
    exit 1
fi

# Create data directory
mkdir -p data

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    exit 1
fi

# Build and run
echo "📦 Сборка образа..."
docker-compose build

# Check local Ollama
echo "🔍 Проверка локальной Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Локальная Ollama не запущена!"
    echo "Запустите: ollama serve"
    exit 1
fi

echo "🤖 Запуск TaskFlowAI бота..."
docker-compose up -d taskflowai

echo "✅ TaskFlowAI запущен!"
echo "📊 Проверить статус: docker ps | grep taskflowai"
echo "📋 Посмотреть логи: docker logs -f taskflowai_bot"
echo "🛑 Остановить: docker-compose down"
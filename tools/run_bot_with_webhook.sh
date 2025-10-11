#!/bin/bash
# Запуск бота с webhook через ngrok для автотестов

cd "$(dirname "$0")/.."

echo "🚀 Запуск бота с webhook"

# Проверка ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok не установлен"
    echo "Установите: brew install ngrok"
    exit 1
fi

# Запуск ngrok в фоне
echo "📡 Запуск ngrok..."
ngrok http 8000 > /dev/null &
NGROK_PID=$!
sleep 3

# Получение URL от ngrok
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])")

if [ -z "$NGROK_URL" ]; then
    echo "❌ Не удалось получить ngrok URL"
    kill $NGROK_PID
    exit 1
fi

echo "✅ Ngrok URL: $NGROK_URL"

# Запуск бота
source .venv/bin/activate
python3 clients/telegram/bot_webhook.py "$NGROK_URL"

# Очистка при выходе
kill $NGROK_PID

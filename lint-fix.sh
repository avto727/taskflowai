#!/bin/bash
# Скрипт для автоисправления проблем линтеров

set -e  # Останавливаться при ошибках

echo "🛠️ Запуск линтеров с автоисправлением..."

echo ""
echo "=== 1. RUFF (автоисправление) ==="
ruff check backend/ clients/ tools/ --exclude .venv --fix

echo ""
echo "=== 2. BLACK (автоформатирование) ==="
black backend/ clients/ tools/ --line-length 79

echo ""
echo "=== 3. VULTURE (проверка мертвого кода) ==="
vulture backend/ clients/ tools/ --min-confidence 70

echo ""
echo "✅ Линтеры выполнены с автоисправлениями!"
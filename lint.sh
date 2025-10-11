#!/bin/bash
# Скрипт для запуска всех линтеров проекта

set -e  # Останавливаться при ошибках

echo "🚀 Запуск всех линтеров..."

echo ""
echo "=== 1. RUFF (статический анализ) ==="
ruff check backend/ clients/ tools/ --exclude .venv

echo ""
echo "=== 2. BLACK (форматирование) ==="
black --check backend/ clients/ tools/ --line-length 79

echo ""
echo "=== 3. VULTURE (мертвый код) ==="
vulture backend/ clients/ tools/ --min-confidence 70

echo ""
echo "=== 4. PYLINT (дублирование кода) ==="
pylint --disable=all --enable=duplicate-code backend/ clients/ tools/ --ignore=conftest.py,__pycache__

echo ""
echo "✅ Все линтеры прошли успешно!"
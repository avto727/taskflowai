#!/bin/bash
# Скрипт для запуска всех линтеров проекта

echo "🚀 Запуск всех линтеров..."

# Счётчик ошибок
ERRORS=0

# Функция для запуска линтера
add_linter() {
    local name="$1"
    local command="$2"
    
    echo ""
    echo "=== $name ==="
    if eval "$command"; then
        echo "✅ $name: OK"
    else
        echo "⚠️  $name: FAILED"
        ERRORS=$((ERRORS + 1))
    fi
}

# Основные линтеры
add_linter "RUFF основной" "ruff check . --exclude .venv"
add_linter "RUFF E501" "ruff check --select=E501 . --exclude .venv --line-length 79"  
add_linter "RUFF W292" "ruff check --select=W292 . --exclude .venv"
add_linter "BLACK" "black --check --line-length 79 ."
add_linter "VULTURE" \
    "vulture backend/ clients/ tools/ --min-confidence 70"
add_linter "PYLINT дублирование" \
    "pylint --min-similarity-lines=3 --disable=all --enable=duplicate-code \
    backend/ clients/ tools/ --ignore=conftest.py,__pycache__"
add_linter "PYLINT структура" \
    "pylint --disable=all \
    --enable=too-many-nested-blocks,too-many-return-statements,broad-except,broad-exception-caught \
    backend/ clients/ tools/ --ignore=conftest.py,__pycache__"
add_linter "FLAKE8-BUGBEAR" \
    "flake8 --select=B backend/ clients/ tools/ --exclude=__pycache__"

echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ Все линтеры прошли успешно!"
    exit 0
else
    echo "⚠️  Найдено проблем: $ERRORS линтеров с ошибками"
    exit 1
fi

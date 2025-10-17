# MCP Tests

Тесты для MCP инструментов Todoist.

## Запуск тестов

```bash
# Базовые MCP функции
python mcp/tests/test_mcp.py

# Полный тест всех инструментов
python mcp/tests/test_mcp_tools.py
```

## Тесты

- `test_mcp.py` - базовые MCP функции (get_tasks, create_task, complete_task)
- `test_mcp_tools.py` - полный набор инструментов через Ollama клиент
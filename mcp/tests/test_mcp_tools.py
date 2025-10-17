#!/usr/bin/env python3
"""
Complete test suite for MCP tools
"""

import os
import sys
import signal
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from mcp.simple_client import SimpleOllamaClient

load_dotenv()


def timeout_handler(signum, frame):
    raise TimeoutError("Test timeout")


def run_test(client, test_name, query):
    """Run single test with timeout"""
    print(f"\n🧪 {test_name}")
    print("=" * 50)
    print(f"🤖 Запрос: {query}")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)
    
    try:
        response = client.chat(query)
        print(f"📝 Ответ: {response}")
        return True
    except TimeoutError:
        print("⏰ Таймаут 5 секунд")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        signal.alarm(0)


def main():
    """Test all MCP tools"""
    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        print("❌ TODOIST_API_TOKEN not found")
        return
    
    client = SimpleOllamaClient(api_token)
    
    print("🚀 Testing MCP Tools")
    print("=" * 50)
    
    tests = [
        ("Basic Chat", "Привет!"),
        ("Get Projects", "Покажи проекты"),
        ("Get All Tasks", "Покажи мои задачи"),
        ("Get Tasks by Project", "Покажи задачи проекта здоровье"),
        ("Create Task", "Создай задачу: MCP тест"),
        ("Complete Task", "Заверши задачу 9644708245"),
        ("Delete Task", "Удали задачу 9644708245")
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, query in tests:
        if run_test(client, test_name, query):
            passed += 1
    
    print(f"\n📊 Результаты: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("✅ Все MCP инструменты работают!")
    else:
        print("⚠️ Некоторые тесты не прошли")


if __name__ == "__main__":
    main()
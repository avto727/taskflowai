#!/usr/bin/env python3
"""Автотесты для команд Ирги в Telegram боте"""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_TEST_CHAT_ID")

if not CHAT_ID:
    print("⚠️  TELEGRAM_TEST_CHAT_ID не установлен в .env")
    print("Узнайте ваш chat_id:")
    print("1. Напишите боту /start")
    print(f"2. Откройте: https://api.telegram.org/bot{BOT_TOKEN}/getUpdates")
    print("3. Найдите 'chat':{'id':123456789}")
    print("4. Добавьте в .env: TELEGRAM_TEST_CHAT_ID=123456789")
    exit(1)


def send_message(text: str):
    """Отправить сообщение боту"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": text}
    r = requests.get(url, params=params)
    return r.json()


def get_last_bot_message():
    """Получить последнее сообщение от бота"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    r = requests.get(url, params={"limit": 100})
    updates = r.json().get("result", [])

    # Ищем последнее сообщение от бота в нашем чате
    for update in reversed(updates):
        msg = update.get("message", {})
        if str(msg.get("chat", {}).get("id")) == str(CHAT_ID) and msg.get(
            "from", {}
        ).get("is_bot"):
            return msg.get("text", "")

    return ""


def test_command(command: str, wait_seconds: int = 5):
    """Протестировать команду"""
    print(f"\n🧪 Тест: {command}")

    # Отправляем
    result = send_message(command)
    if not result.get("ok"):
        print(f"❌ Ошибка отправки: {result}")
        return False

    print("✅ Отправлено")

    # Ждём ответ
    print(f"⏳ Ожидание {wait_seconds} сек...")
    time.sleep(wait_seconds)

    # Проверяем ответ
    response = get_last_bot_message()
    if response:
        print(f"📨 Ответ: {response[:100]}...")
        return True
    else:
        print("❌ Нет ответа")
        return False


def main():
    print("🤖 Автотесты команд Ирги\n")
    print(f"Bot Token: {BOT_TOKEN[:10]}...")
    print(f"Chat ID: {CHAT_ID}\n")

    commands = [
        "Ирга, привет!",
        "Ирга, помоги",
        "Ирга, покажи задачи",
        "Ирга, план на сегодня",
        "Ирга, что по здоровью?",
    ]

    results = []
    for cmd in commands:
        success = test_command(cmd, wait_seconds=5)
        results.append((cmd, success))
        time.sleep(2)  # Пауза между тестами

    # Итоги
    print("\n" + "=" * 50)
    print("📊 Результаты тестирования:\n")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for cmd, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {cmd}")

    print(f"\n🎯 Пройдено: {passed}/{total}")

    if passed == total:
        print("🎉 Все тесты пройдены!")
    else:
        print("⚠️  Есть проблемы")


if __name__ == "__main__":
    main()

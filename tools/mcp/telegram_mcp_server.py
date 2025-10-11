#!/usr/bin/env python3
"""MCP сервер для Telegram Bot API"""
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import requests
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Telegram MCP")


def get_env_config() -> tuple[str, str]:
    """Получить конфигурацию из окружения"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_TEST_CHAT_ID")

    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN не установлен")

    return bot_token, chat_id


@mcp.tool
def send_message(text: str, chat_id: str = None) -> dict:
    """Отправить сообщение боту"""
    bot_token, default_chat = get_env_config()
    target_chat = chat_id or default_chat

    if not target_chat:
        raise ValueError("chat_id не указан")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {"chat_id": target_chat, "text": text}

    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()


@mcp.tool
def get_updates(offset: int = None, limit: int = 10) -> list[dict]:
    """Получить обновления (сообщения) от бота"""
    bot_token, _ = get_env_config()

    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    params = {"limit": limit}

    if offset:
        params["offset"] = offset

    r = requests.get(url, params=params)
    r.raise_for_status()

    result = r.json()
    return result.get("result", [])


@mcp.tool
def get_last_message(chat_id: str = None) -> dict:
    """Получить последнее сообщение от бота"""
    bot_token, default_chat = get_env_config()
    target_chat = chat_id or default_chat

    updates = get_updates(limit=100)

    # Фильтруем по chat_id и берём последнее
    messages = []
    for update in updates:
        msg = update.get("message", {})
        if str(msg.get("chat", {}).get("id")) == str(target_chat):
            messages.append(msg)

    if messages:
        return messages[-1]

    return {}


@mcp.tool
def send_and_wait(
    text: str, chat_id: str = None, wait_seconds: int = 3
) -> dict:
    """Отправить сообщение и подождать ответ"""
    bot_token, default_chat = get_env_config()
    target_chat = chat_id or default_chat

    # Получаем текущий offset
    updates = get_updates(limit=1)
    last_update_id = updates[-1]["update_id"] if updates else 0

    # Отправляем сообщение
    send_message(text, target_chat)

    # Ждём ответ
    time.sleep(wait_seconds)

    # Получаем новые сообщения
    new_updates = get_updates(offset=last_update_id + 1, limit=100)

    # Ищем ответ бота
    bot_messages = []
    for update in new_updates:
        msg = update.get("message", {})
        if str(msg.get("chat", {}).get("id")) == str(target_chat) and msg.get(
            "from", {}
        ).get("is_bot"):
            bot_messages.append(msg)

    if bot_messages:
        return {
            "sent": text,
            "response": bot_messages[-1].get("text", ""),
            "full_response": bot_messages[-1],
        }

    return {"sent": text, "response": "Нет ответа", "full_response": {}}


@mcp.tool
def test_irga_commands(chat_id: str = None) -> list[dict]:
    """Протестировать все команды Ирги"""
    commands = [
        "Ирга, привет!",
        "Ирга, помоги",
        "Ирга, покажи задачи",
        "Ирга, план на сегодня",
        "Ирга, что по здоровью?",
    ]

    results = []
    for cmd in commands:
        result = send_and_wait(cmd, chat_id, wait_seconds=5)
        results.append(
            {
                "command": cmd,
                "response": result.get("response", ""),
                "success": bool(result.get("response")),
            }
        )
        time.sleep(2)  # Пауза между командами

    return results


if __name__ == "__main__":
    mcp.run(transport="stdio")

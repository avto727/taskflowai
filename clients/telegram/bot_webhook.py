#!/usr/bin/env python3
"""Telegram бот с webhook для автотестов"""
import os
import sys
from pathlib import Path
from aiohttp import web
from aiogram.types import Update
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
load_dotenv()

# Импорт после load_dotenv() необходим для загрузки токенов
from clients.telegram.simple_bot import dp, bot  # noqa: E402

WEBHOOK_PATH = f"/bot/{os.getenv('TELEGRAM_BOT_TOKEN')}"
WEBHOOK_URL = ""  # Устанавливается при запуске
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = 8000


async def on_startup(app):
    """Установить webhook при старте"""
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook установлен: {WEBHOOK_URL}")


async def on_shutdown(app):
    """Удалить webhook при остановке"""
    await bot.delete_webhook()
    print("✅ Webhook удалён")


async def webhook_handler(request):
    """Обработчик webhook запросов"""
    update = Update(**(await request.json()))
    await dp.feed_update(bot, update)
    return web.Response()


def main():
    """Запуск бота в webhook режиме"""
    if len(sys.argv) < 2:
        print("Usage: python bot_webhook.py <ngrok_url>")
        print("Example: python bot_webhook.py https://abc123.ngrok.io")
        sys.exit(1)

    global WEBHOOK_URL
    WEBHOOK_URL = sys.argv[1] + WEBHOOK_PATH

    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    print("🚀 Запуск бота в webhook режиме")
    print(f"📡 Webhook: {WEBHOOK_URL}")
    print(f"🌐 Server: http://{WEBAPP_HOST}:{WEBAPP_PORT}")

    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)


if __name__ == "__main__":
    main()

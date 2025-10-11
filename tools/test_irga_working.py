#!/usr/bin/env python3
"""Рабочий автотест через aiogram.Bot"""
import os
import asyncio
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

async def test_irga():
    """Тест команд Ирги"""
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    chat_id = os.getenv('TELEGRAM_TEST_CHAT_ID')
    
    tests = [
        'Ирга, привет!',
        'Ирга, помоги',
        'Ирга, покажи задачи',
    ]
    
    print("🚀 Автотесты команд Ирги\n")
    print("⏳ Отправка команд...\n")
    
    for cmd in tests:
        print(f"📤 {cmd}")
        await bot.send_message(chat_id, cmd)
        await asyncio.sleep(2)
        print("   ✅ Отправлено\n")
    
    await bot.session.close()
    
    print("="*50)
    print("✅ Команды отправлены!")
    print("📱 Проверьте Telegram - должны быть ответы")
    print("="*50)

if __name__ == '__main__':
    asyncio.run(test_irga())

#!/usr/bin/env python3
"""
Run TaskFlowAI MCP Bot
"""

import subprocess
import sys
import os

def main():
    print("🚀 Запуск TaskFlowAI MCP Bot...")
    
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("Создайте .env с токенами Todoist и Telegram")
        return
    
    # Check virtual environment
    if not os.path.exists('.venv'):
        print("📦 Создание виртуального окружения...")
        subprocess.run([sys.executable, '-m', 'venv', '.venv'])
        
        print("📦 Установка зависимостей...")
        subprocess.run(['.venv/bin/python', '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # Run bot
    print("🤖 Запуск Telegram бота...")
    subprocess.run(['.venv/bin/python', 'clients/telegram/simple_bot.py'])

if __name__ == "__main__":
    main()
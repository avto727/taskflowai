"""
Конфигурация TaskFlowAI
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Ollama настройки
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Todoist
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

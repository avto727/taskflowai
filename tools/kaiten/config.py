"""
Конфигурация для Kaiten интеграции
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Kaiten API
KAITEN_API_TOKEN = os.getenv("KAITEN_API_TOKEN")
KAITEN_BOARD_ID = os.getenv("KAITEN_BOARD_ID")

# Маппинг колонок
COLUMN_MAPPING = {
    "backlog": "📋 Backlog",
    "todo": "📝 To Do",
    "in_progress": "🔄 In Progress",
    "testing": "🧪 Testing",
    "done": "✅ Done"
}

# Маппинг меток
LABEL_MAPPING = {
    "bug": "🐛 Bug",
    "feature": "✨ Feature",
    "enhancement": "🔧 Enhancement",
    "documentation": "📚 Documentation"
}

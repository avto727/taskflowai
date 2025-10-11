import requests
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self, model=None, base_url=None):
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.api_url = f"{self.base_url}/api/generate"
        logger.info(f"Инициализация AIProcessor: model={self.model}, url={self.base_url}")
    
    def _call_ollama(self, prompt: str) -> str:
        """Вызов Ollama API"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Ошибка вызова Ollama: {e}")
            return ""
    
    def analyze_message(self, text: str, categories: list) -> Dict:
        """
        Анализ сообщения пользователя
        Возвращает: {
            'type': 'task' | 'query' | 'completed',
            'category_id': int,
            'status': 'план' | 'в процессе' | 'выполнено',
            'planned_time': str,
            'execution_type': 'компьютер' | 'поездка' | 'делегирование'
        }
        """
        
        # Текущая дата и время
        now = datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M")
        current_date_readable = now.strftime("%d.%m.%Y (%A)")
        
        # Определяем время суток
        hour = now.hour
        if 6 <= hour < 12:
            time_of_day = "утро (6:00-12:00)"
        elif 12 <= hour < 16:
            time_of_day = "обед (12:00-16:00)"
        elif 16 <= hour < 22:
            time_of_day = "вечер (16:00-22:00)"
        else:
            time_of_day = "ночь (22:00-6:00)"
        
        # Формируем список категорий для промпта
        categories_str = "\n".join([f"{cat[0]}. {cat[1]}" for cat in categories])
        
        prompt = f"""Текущая дата и время: {current_datetime} ({current_date_readable})
Время суток: {time_of_day}

Проанализируй сообщение пользователя и верни JSON.

Сообщение: "{text}"

Доступные категории:
{categories_str}

Верни JSON в формате:
{{
    "type": "task или query или completed",
    "category_id": номер категории из списка или null,
    "status": "план или в процессе или выполнено",
    "planned_time": "дата в формате YYYY-MM-DD HH:MM или null",
    "execution_type": "компьютер или поездка или делегирование или null",
    "filter_category": "название категории для фильтрации или null",
    "filter_date": "today или tomorrow или week или month или null"
}}

Правила категоризации:
- type: "query" если сообщение заканчивается знаком "?" (это вопрос, не задача!)
- type: "completed" если сообщает о выполнении (сделал, сходил, оплатил)
- type: "task" во всех остальных случаях (добавление задачи)
- category_id: выбери наиболее подходящую категорию по примерам (для query может быть null):
- filter_category: ТОЛЬКО если пользователь ЯВНО спрашивает про конкретную категорию ("что по здоровью", "дела по деньгам") - укажи название. Если просто "покажи план" - ставь null
- filter_date: ТОЛЬКО если ЯВНО указан период ("на завтра", "на неделю", "на сегодня") - укажи период. Если просто "покажи план" - ставь null
  * Деньги: оплата, зарплата, покупки, счета, налоги, инвестиции
  * Семья: дети, родители, супруг(а), быт, домашние дела, покупка продуктов
  * Здоровье: врачи, анализы, лекарства, спорт, ЕДА И НАПИТКИ (кофе, чай, завтрак, обед, ужин), сон
  * Взаимоотношения: друзья, коллеги, звонки, встречи, общение
  * Духовность и развитие личности: обучение, книги, курсы, медитация, хобби, творчество
- status: "план" если будущее, "в процессе" если делает сейчас, "выполнено" если сделал
- planned_time: извлеки дату из текста ("завтра утром" = завтра 09:00, "сегодня вечером" = сегодня 18:00)
- execution_type: определи тип выполнения задачи

Примеры:
- "Попить кофе" → category_id: Здоровье (это питание)
- "Купить продукты" → category_id: Семья (быт)
- "Позвонить другу" → category_id: Взаимоотношения
- "Оплатить интернет" → category_id: Деньги
- "Прочитать книгу" → category_id: Духовность и развитие личности

Верни ТОЛЬКО JSON, без дополнительного текста."""

        response = self._call_ollama(prompt)
        
        try:
            # Извлекаем JSON из ответа
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                # Fallback: базовая обработка
                return self._fallback_analysis(text, categories)
        except Exception as e:
            logger.warning(f"Ошибка парсинга JSON: {e}, использую fallback")
            return self._fallback_analysis(text, categories)
    
    def _fallback_analysis(self, text: str, categories: list) -> Dict:
        """Базовая обработка без ИИ"""
        text_lower = text.lower()
        
        # Определяем тип
        if any(word in text_lower for word in ['покажи', 'что', 'список', 'план']):
            msg_type = 'query'
        elif any(word in text_lower for word in ['сделал', 'выполнил', 'завершил', 'сходил']):
            msg_type = 'completed'
            status = 'выполнено'
        else:
            msg_type = 'task'
            status = 'план'
        
        # Определяем статус для задач
        if msg_type == 'task':
            if any(word in text_lower for word in ['делаю', 'занимаюсь', 'работаю']):
                status = 'в процессе'
            else:
                status = 'план'
        elif msg_type == 'query':
            status = 'план'
        
        return {
            'type': msg_type,
            'category_id': categories[0][0] if categories else None,
            'status': status,
            'planned_time': None,
            'execution_type': None
        }

from datetime import datetime, timedelta

class TimeScheduler:
    """Умное планирование времени по режиму дня"""
    
    # Режимы дня (часы)
    TIME_RANGES = {
        'утро': (6, 12),
        'день': (12, 18),
        'вечер': (18, 23),
        'ночь': (23, 6)  # особый случай - переход через полночь
    }
    
    @staticmethod
    def find_free_time(db, user_id, date, time_of_day, duration=60):
        """
        Найти свободное время в указанном диапазоне
        
        Args:
            db: объект базы данных
            user_id: ID пользователя
            date: дата (datetime.date)
            time_of_day: 'утро', 'день', 'вечер', 'ночь'
            duration: длительность задачи в минутах
            
        Returns:
            str: время в формате "YYYY-MM-DD HH:MM" или None
        """
        if time_of_day not in TimeScheduler.TIME_RANGES:
            return None
        
        start_hour, end_hour = TimeScheduler.TIME_RANGES[time_of_day]
        
        # Получаем занятое время на эту дату
        busy_times = db.get_busy_times(user_id, date)
        
        # Преобразуем в список занятых интервалов
        busy_intervals = []
        for time_str, task_duration in busy_times:
            if not time_str:
                continue
            try:
                start = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                end = start + timedelta(minutes=task_duration or 60)
                busy_intervals.append((start, end))
            except:
                continue
        
        # Проверяем каждый час в диапазоне
        if time_of_day == 'ночь':
            # Ночь: с 23:00 до 6:00 следующего дня
            hours = list(range(23, 24)) + list(range(0, 6))
        else:
            hours = range(start_hour, end_hour)
        
        for hour in hours:
            # Формируем время начала
            if time_of_day == 'ночь' and hour < 6:
                # Для ночи после полуночи берём следующий день
                check_date = date + timedelta(days=1)
            else:
                check_date = date
            
            candidate_start = datetime.combine(check_date, datetime.min.time().replace(hour=hour))
            candidate_end = candidate_start + timedelta(minutes=duration)
            
            # Проверяем, не пересекается ли с занятыми интервалами
            is_free = True
            for busy_start, busy_end in busy_intervals:
                # Проверка пересечения интервалов
                if not (candidate_end <= busy_start or candidate_start >= busy_end):
                    is_free = False
                    break
            
            if is_free:
                return candidate_start.strftime("%Y-%m-%d %H:%M")
        
        # Если не нашли свободное время, возвращаем первый час диапазона
        if time_of_day == 'ночь':
            fallback_date = date
            fallback_hour = 23
        else:
            fallback_date = date
            fallback_hour = start_hour
        
        return datetime.combine(fallback_date, datetime.min.time().replace(hour=fallback_hour)).strftime("%Y-%m-%d %H:%M")
    
    @staticmethod
    def detect_time_of_day(text):
        """
        Определить время суток из текста
        
        Args:
            text: текст задачи
            
        Returns:
            str: 'утро', 'день', 'вечер', 'ночь' или None
        """
        text_lower = text.lower()
        
        morning_keywords = ['утро', 'утром', 'утра', 'рано', 'завтрак']
        day_keywords = ['день', 'днём', 'днем', 'обед', 'полдень']
        evening_keywords = ['вечер', 'вечером', 'вечера', 'ужин']
        night_keywords = ['ночь', 'ночью', 'ночи', 'поздно']
        
        for keyword in morning_keywords:
            if keyword in text_lower:
                return 'утро'
        
        for keyword in day_keywords:
            if keyword in text_lower:
                return 'день'
        
        for keyword in evening_keywords:
            if keyword in text_lower:
                return 'вечер'
        
        for keyword in night_keywords:
            if keyword in text_lower:
                return 'ночь'
        
        return None

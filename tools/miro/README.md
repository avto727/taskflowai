# Miro Integration

Интеграция с Miro для визуализации roadmap.

## Получение Access Token

1. **Создайте приложение:**
   - https://miro.com/app/settings/user-profile/apps
   - "Create new app"
   - Name: "TaskFlowAI"
   - Redirect URI: `http://localhost:8000/callback`

2. **Получите токен:**
   - В настройках приложения → "OAuth & Permissions"
   - Скопируйте "Access token"
   - Добавьте в `.env`:
     ```
     MIRO_ACCESS_TOKEN=ваш_токен
     ```

3. **Создайте доску:**
   - Откройте Miro → "Create new board"
   - Скопируйте ID из URL: `https://miro.com/app/board/BOARD_ID/`
   - Добавьте в `.env`:
     ```
     MIRO_BOARD_ID=ваш_board_id
     ```

## Использование

```bash
# Создать roadmap на доске
python tools/miro/create_roadmap.py

# Обновить roadmap
python tools/miro/update_roadmap.py
```

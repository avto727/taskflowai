#!/usr/bin/env python3
"""MCP сервер для Trello"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(__file__))))

import requests
from fastmcp import FastMCP

mcp = FastMCP("Trello MCP")


def get_env_config() -> tuple[str, str, str]:
    """Получить конфигурацию из окружения"""
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    board_id = os.getenv("TRELLO_BOARD_ID")

    if not (api_key and token):
        raise ValueError(
            "Установите TRELLO_API_KEY и TRELLO_TOKEN в окружении"
        )

    return api_key, token, board_id


def request_get(url: str, params: dict) -> dict:
    """GET запрос"""
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()


def request_post(url: str, params: dict) -> dict:
    """POST запрос"""
    r = requests.post(url, params=params)
    r.raise_for_status()
    return r.json()


def request_put(url: str, params: dict) -> dict:
    """PUT запрос"""
    r = requests.put(url, params=params)
    r.raise_for_status()
    return r.json()


# --- Основные инструменты ---


@mcp.tool
def get_board_lists(board_id: str = None) -> list[dict]:
    """Получить списки (колонки) доски"""
    api_key, token, default_board = get_env_config()
    board = board_id or default_board
    
    if not board:
        raise ValueError("board_id не указан")
    
    url = f"https://api.trello.com/1/boards/{board}/lists"
    params = {"key": api_key, "token": token}
    return request_get(url, params)


@mcp.tool
def get_board_cards(board_id: str = None) -> list[dict]:
    """Получить все карточки доски"""
    api_key, token, default_board = get_env_config()
    board = board_id or default_board
    
    if not board:
        raise ValueError("board_id не указан")
    
    url = f"https://api.trello.com/1/boards/{board}/cards"
    params = {"key": api_key, "token": token}
    return request_get(url, params)


@mcp.tool
def create_card(
    list_name: str, name: str, desc: str = "", board_id: str = None
) -> dict:
    """Создать карточку в списке"""
    api_key, token, default_board = get_env_config()
    board = board_id or default_board
    
    # Найти список по имени
    lists = get_board_lists(board)
    target_list = next(
        (l for l in lists if list_name.lower() in l["name"].lower()),
        None
    )
    
    if not target_list:
        available = [l["name"] for l in lists]
        raise ValueError(
            f"Список '{list_name}' не найден. "
            f"Доступные: {available}"
        )
    
    url = "https://api.trello.com/1/cards"
    params = {
        "key": api_key,
        "token": token,
        "idList": target_list["id"],
        "name": name,
        "desc": desc
    }
    return request_post(url, params)


@mcp.tool
def update_card(card_id: str, name: str = None, 
                desc: str = None) -> dict:
    """Обновить карточку"""
    api_key, token, _ = get_env_config()
    
    url = f"https://api.trello.com/1/cards/{card_id}"
    params = {"key": api_key, "token": token}
    
    if name:
        params["name"] = name
    if desc:
        params["desc"] = desc
    
    return request_put(url, params)


@mcp.tool
def move_card(card_id: str, list_name: str, 
              board_id: str = None) -> dict:
    """Переместить карточку в другой список"""
    api_key, token, default_board = get_env_config()
    board = board_id or default_board
    
    # Найти список
    lists = get_board_lists(board)
    target_list = next(
        (l for l in lists if list_name.lower() in l["name"].lower()),
        None
    )
    
    if not target_list:
        available = [l["name"] for l in lists]
        raise ValueError(
            f"Список '{list_name}' не найден. "
            f"Доступные: {available}"
        )
    
    url = f"https://api.trello.com/1/cards/{card_id}"
    params = {
        "key": api_key,
        "token": token,
        "idList": target_list["id"]
    }
    return request_put(url, params)


@mcp.tool
def search_cards(query: str, board_id: str = None) -> list[dict]:
    """Поиск карточек по тексту"""
    api_key, token, default_board = get_env_config()
    board = board_id or default_board
    
    cards = get_board_cards(board)
    
    # Фильтр по query
    results = []
    for card in cards:
        if (query.lower() in card["name"].lower() or 
            query.lower() in card.get("desc", "").lower()):
            results.append(card)
    
    return results


@mcp.tool
def get_card_checklists(card_id: str) -> list[dict]:
    """Получить чеклисты карточки"""
    api_key, token, _ = get_env_config()
    
    url = f"https://api.trello.com/1/cards/{card_id}/checklists"
    params = {"key": api_key, "token": token}
    return request_get(url, params)


@mcp.tool
def add_checklist_item(card_id: str, checklist_name: str,
                       item_name: str) -> dict:
    """Добавить пункт в чеклист"""
    api_key, token, _ = get_env_config()
    
    # Найти чеклист
    checklists = get_card_checklists(card_id)
    target = next(
        (c for c in checklists 
         if checklist_name.lower() in c["name"].lower()),
        None
    )
    
    if not target:
        raise ValueError(f"Чеклист '{checklist_name}' не найден")
    
    url = f"https://api.trello.com/1/checklists/{target['id']}/checkItems"
    params = {
        "key": api_key,
        "token": token,
        "name": item_name
    }
    return request_post(url, params)


@mcp.tool
def check_checklist_item(card_id: str, item_id: str) -> dict:
    """Отметить пункт чеклиста как выполненный"""
    api_key, token, _ = get_env_config()
    
    url = f"https://api.trello.com/1/cards/{card_id}/checkItem/{item_id}"
    params = {
        "key": api_key,
        "token": token,
        "state": "complete"
    }
    return request_put(url, params)


if __name__ == "__main__":
    mcp.run(transport="stdio")

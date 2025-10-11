#!/usr/bin/env python3
"""Найти connectors напрямую через API"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("MIRO_ACCESS_TOKEN")
board_id = os.getenv("MIRO_BOARD_ID")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Пробуем разные эндпоинты
endpoints = [
    f"https://api.miro.com/v2/boards/{board_id}/connectors",
    f"https://api.miro.com/v2/boards/{board_id}/items?type=connector",
    f"https://api.miro.com/v2/boards/{board_id}/items?limit=100",
]

for url in endpoints:
    print(f"\n🔍 {url}")
    r = requests.get(url, headers=headers)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        items = data.get('data', [])
        print(f"Items: {len(items)}")
        
        connectors = [i for i in items if i.get('type') == 'connector']
        print(f"Connectors: {len(connectors)}")
        
        if connectors:
            print("\nПервый connector:")
            print(connectors[0])
            break

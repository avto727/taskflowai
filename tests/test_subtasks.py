"""Автотесты для подзадач и привычек"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://localhost:8000"
TOKEN = os.getenv("TODOIST_API_TOKEN")
HEADERS = {"X-Todoist-Token": TOKEN}


class TestBackendAPI:
    """1. Backend API тесты"""

    def test_1_1_create_subtask(self):
        """1.1. Backend: создание подзадачи"""
        # Создаём родительскую задачу
        parent = requests.post(
            f"{API_URL}/tasks",
            json={"content": "Утренняя зарядка", "category": "Здоровье"},
            headers=HEADERS,
        ).json()

        assert parent["status"] == "success"
        parent_id = parent["task"]["id"]

        # Создаём подзадачу
        response = requests.post(
            f"{API_URL}/tasks",
            json={
                "content": "Отжимания 20 раз",
                "parent_id": parent_id,
                "category": "Здоровье",
            },
            headers=HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["task"]["parent_id"] == parent_id
        print("✅ 1.1. Создание подзадачи")

    def test_1_2_get_subtasks(self):
        """1.2. Backend: получение подзадач"""
        # Создаём родителя и подзадачу
        parent = requests.post(
            f"{API_URL}/tasks",
            json={"content": "Тест родитель", "category": "Здоровье"},
            headers=HEADERS,
        ).json()["task"]

        requests.post(
            f"{API_URL}/tasks",
            json={
                "content": "Тест подзадача",
                "parent_id": parent["id"],
                "category": "Здоровье",
            },
            headers=HEADERS,
        )

        # Получаем подзадачи
        response = requests.get(
            f"{API_URL}/tasks/{parent['id']}/subtasks", headers=HEADERS
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["subtasks"]) >= 1
        print("✅ 1.2. Получение подзадач")

    def test_1_3_recurring_task(self):
        """1.3. Backend: recurring задача"""
        response = requests.post(
            f"{API_URL}/tasks",
            json={
                "content": "Тест recurring",
                "due_string": "every day",
                "category": "Здоровье",
                "is_recurring": True,
            },
            headers=HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        task = data["task"]
        assert task.get("due") is not None
        print("✅ 1.3. Recurring задача")


class TestIntegration:
    """3. Интеграционные тесты"""

    def test_3_1_parent_with_subtasks(self):
        """3.1. Интеграция: родитель → подзадачи"""
        # Создаём родителя
        parent = requests.post(
            f"{API_URL}/tasks",
            json={"content": "Утренняя рутина", "category": "Здоровье"},
            headers=HEADERS,
        ).json()["task"]

        # Создаём 3 подзадачи
        subtasks = ["Отжимания", "Приседания", "Растяжка"]
        for content in subtasks:
            requests.post(
                f"{API_URL}/tasks",
                json={
                    "content": content,
                    "parent_id": parent["id"],
                    "category": "Здоровье",
                },
                headers=HEADERS,
            )

        # Проверяем
        response = requests.get(
            f"{API_URL}/tasks/{parent['id']}/subtasks", headers=HEADERS
        )
        data = response.json()
        assert len(data["subtasks"]) == 3
        print("✅ 3.1. Родитель → подзадачи")

    def test_3_2_recurring_with_subtasks(self):
        """3.2. Интеграция: recurring с подзадачами"""
        # Создаём recurring родителя
        parent = requests.post(
            f"{API_URL}/tasks",
            json={
                "content": "Ежедневная зарядка",
                "due_string": "every day at 7:00",
                "category": "Здоровье",
            },
            headers=HEADERS,
        ).json()["task"]

        # Добавляем подзадачу
        requests.post(
            f"{API_URL}/tasks",
            json={
                "content": "Разминка",
                "parent_id": parent["id"],
                "category": "Здоровье",
            },
            headers=HEADERS,
        )

        # Проверяем
        response = requests.get(
            f"{API_URL}/tasks/{parent['id']}/subtasks", headers=HEADERS
        )
        assert response.status_code == 200
        print("✅ 3.2. Recurring с подзадачами")


def run_tests():
    """Запуск всех тестов"""
    print("\n🧪 Запуск автотестов для подзадач\n")

    # Backend тесты
    backend = TestBackendAPI()
    try:
        backend.test_1_1_create_subtask()
    except Exception as e:
        print(f"❌ 1.1. Ошибка: {e}")

    try:
        backend.test_1_2_get_subtasks()
    except Exception as e:
        print(f"❌ 1.2. Ошибка: {e}")

    try:
        backend.test_1_3_recurring_task()
    except Exception as e:
        print(f"❌ 1.3. Ошибка: {e}")

    # Интеграционные тесты
    integration = TestIntegration()
    try:
        integration.test_3_1_parent_with_subtasks()
    except Exception as e:
        print(f"❌ 3.1. Ошибка: {e}")

    try:
        integration.test_3_2_recurring_with_subtasks()
    except Exception as e:
        print(f"❌ 3.2. Ошибка: {e}")

    print("\n✅ Автотесты завершены!\n")


if __name__ == "__main__":
    run_tests()

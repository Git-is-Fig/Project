import pytest
import requests
import time
import os
import subprocess
import signal
from multiprocessing import Process
import uvicorn


# URL для тестів
BASE_URL = "http://localhost:8000"
server_process = None


def run_server():
    """Запуск сервера для тестування"""
    import uvicorn
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="error")


def setup_module():
    """Запуск сервера перед початком тестів"""
    global server_process
    server_process = Process(target=run_server)
    server_process.start()
    # Даємо час серверу запуститися
    time.sleep(1)


def teardown_module():
    """Зупинка сервера після завершення тестів"""
    global server_process
    if server_process:
        server_process.terminate()
        server_process.join()


def test_server_is_up():
    """Перевірка, що сервер запущено"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_full_todo_workflow():
    """Тестування повного циклу роботи з завданнями"""
    # 1. Отримуємо початковий список завдань
    response = requests.get(f"{BASE_URL}/todos")
    assert response.status_code == 200
    initial_todos = response.json()
    
    # 2. Створюємо нове завдання
    new_todo = {"id": 100, "title": "Інтеграційне тестування", "completed": False}
    response = requests.post(f"{BASE_URL}/todos", json=new_todo)
    assert response.status_code == 200
    created_todo = response.json()
    assert created_todo["id"] == new_todo["id"]
    assert created_todo["title"] == new_todo["title"]
    
    # 3. Отримуємо завдання за ID
    response = requests.get(f"{BASE_URL}/todos/{new_todo['id']}")
    assert response.status_code == 200
    todo = response.json()
    assert todo["id"] == new_todo["id"]
    assert todo["title"] == new_todo["title"]
    
    # 4. Перевіряємо, що завдання додано до списку
    response = requests.get(f"{BASE_URL}/todos")
    assert response.status_code == 200
    updated_todos = response.json()
    assert len(updated_todos) == len(initial_todos) + 1
    
    # 5. Видаляємо завдання
    response = requests.delete(f"{BASE_URL}/todos/{new_todo['id']}")
    assert response.status_code == 200
    assert response.json() == {"message": "Завдання видалено"}
    
    # 6. Перевіряємо, що завдання видалено
    response = requests.get(f"{BASE_URL}/todos")
    assert response.status_code == 200
    final_todos = response.json()
    assert len(final_todos) == len(initial_todos)
    
    # 7. Перевіряємо, що завдання більше не існує
    response = requests.get(f"{BASE_URL}/todos/{new_todo['id']}")
    assert response.status_code == 404


def test_error_handling():
    """Тестування обробки помилок"""
    # Спроба отримати неіснуюче завдання
    response = requests.get(f"{BASE_URL}/todos/999999")
    assert response.status_code == 404
    assert "не знайдено" in response.json()["detail"]
    
    # Спроба створити дублікат завдання
    new_todo = {"id": 200, "title": "Тест обробки помилок", "completed": False}
    requests.post(f"{BASE_URL}/todos", json=new_todo)
    
    # Спроба створити завдання з тим самим ID
    response = requests.post(f"{BASE_URL}/todos", json=new_todo)
    assert response.status_code == 400
    assert "вже існує" in response.json()["detail"]
    
    # Видаляємо тестове завдання
    requests.delete(f"{BASE_URL}/todos/200")

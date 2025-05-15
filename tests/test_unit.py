import pytest
from fastapi.testclient import TestClient
from app.main import app, todos, TodoItem


client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Ласкаво просимо до TODO API"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_todos_empty():
    # Очищаємо список завдань перед тестом
    todos.clear()
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_create_todo():
    todos.clear()
    todo_data = {"id": 1, "title": "Тестове завдання", "completed": False}
    response = client.post("/todos", json=todo_data)
    assert response.status_code == 200
    assert response.json() == todo_data


def test_create_todo_duplicate_id():
    todos.clear()
    todo_data = {"id": 1, "title": "Перше завдання", "completed": False}
    response = client.post("/todos", json=todo_data)
    assert response.status_code == 200
    
    # Спроба створити завдання з таким самим ID
    todo_data_duplicate = {"id": 1, "title": "Дублікат завдання", "completed": True}
    response = client.post("/todos", json=todo_data_duplicate)
    assert response.status_code == 400
    assert "вже існує" in response.json()["detail"]


def test_get_todo_by_id():
    todos.clear()
    todo = TodoItem(id=1, title="Тестове завдання")
    todos.append(todo)
    
    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Тестове завдання", "completed": False}


def test_get_todo_not_found():
    todos.clear()
    response = client.get("/todos/999")
    assert response.status_code == 404
    assert "не знайдено" in response.json()["detail"]


def test_delete_todo():
    todos.clear()
    todo = TodoItem(id=1, title="Завдання для видалення")
    todos.append(todo)
    
    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Завдання видалено"}
    assert len(todos) == 0


def test_delete_todo_not_found():
    todos.clear()
    response = client.delete("/todos/999")
    assert response.status_code == 404
    assert "не знайдено" in response.json()["detail"]

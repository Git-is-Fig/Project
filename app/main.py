from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List


app = FastAPI()


# Модель даних для завдання
class TodoItem(BaseModel):
    id: int
    title: str
    completed: bool = False


# Імітація бази даних
todos: List[TodoItem] = []


@app.get("/", summary="Головна сторінка")
def read_root():
    return {"message": "Ласкаво просимо до TODO API"}


@app.get("/todos", response_model=List[TodoItem], summary="Отримати всі завдання")
def get_todos():
    return todos


@app.post("/todos", response_model=TodoItem, summary="Створити нове завдання")
def create_todo(todo: TodoItem):
    # Перевірка наявності ID
    for existing in todos:
        if existing.id == todo.id:
            raise HTTPException(status_code=400, detail="Завдання з таким ID вже існує")
    todos.append(todo)
    return todo


@app.get("/todos/{todo_id}", response_model=TodoItem, summary="Отримати завдання за ID")
def get_todo(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Завдання не знайдено")


@app.delete("/todos/{todo_id}", summary="Видалити завдання")
def delete_todo(todo_id: int):
    for i, todo in enumerate(todos):
        if todo.id == todo_id:
            todos.pop(i)
            return {"message": "Завдання видалено"}
    raise HTTPException(status_code=404, detail="Завдання не знайдено")


@app.get("/health", summary="Перевірка здоров'я сервера")
def health():
    return {"status": "ok"}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, constr, validator
from datetime import date
from typing import List

app = FastAPI()

# In-memory storage
users_db = {}
tasks_db = {}
user_counter = 1
task_counter = 1

# User Models
class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=20)
    email: EmailStr

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr

# Task Models
class Task(BaseModel):
    id: int
    title: str
    description: str
    due_date: date
    status: str = "pending"
    user_id: int

    @validator('due_date')
    def due_date_must_be_future(cls, v):
        if v < date.today():
            raise ValueError('Due date must be today or in the future')
        return v

class TaskCreate(BaseModel):
    title: str
    description: str
    due_date: date
    user_id: int

    @validator('due_date')
    def due_date_must_be_future(cls, v):
        if v < date.today():
            raise ValueError('Due date must be today or in the future')
        return v

class TaskStatusUpdate(BaseModel):
    status: str

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'in_progress', 'completed']
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return v

# Users Endpoints
@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate):
    global user_counter
    new_user = {"id": user_counter, **user.dict()}
    users_db[user_counter] = new_user
    user_counter += 1
    return new_user

@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Tasks Endpoints
@app.post("/tasks/", response_model=Task)
def create_task(task: TaskCreate):
    global task_counter
    if task.user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    new_task = Task(id=task_counter, **task.dict())
    tasks_db[task_counter] = new_task
    task_counter += 1
    return new_task

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task_status(task_id: int, update: TaskStatusUpdate):
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = update.status
    return task

@app.get("/users/{user_id}/tasks", response_model=List[Task])
def get_user_tasks(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return [task for task in tasks_db.values() if task.user_id == user_id]

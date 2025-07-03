from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


client = MongoClient("mongodb+srv://teamuser:password123team@cluster0.5wrc8bf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["task_dashboard"]
tasks_collection = db["tasks"]
operators_collection = db["operators"]


class StatusUpdate(BaseModel):
    status: str



@app.get("/")
def root():
    return {"message": "Task Dashboard API Running on Atlas"}

@app.post("/login")
def login(username: str, password: str):

    operator = operators_collection.find_one({"username": username, "password": password})
    if operator:
        return {
            "role": "operator",
            "operator_id": operator["operator_id"],
            "name": operator["name"]
        }

  
    try:
        managers_df = pd.read_csv("managers.csv")
        manager_row = managers_df[
            (managers_df["username"] == username) & (managers_df["password"] == password)
        ]
        if not manager_row.empty:
            manager_data = manager_row.iloc[0]
            return {
                "role": "manager",
                "manager_id": manager_data["manager_id"],
                "name": manager_data["name"]
            }
    except Exception as e:
        print(f"Error reading managers.csv: {e}")

    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/tasks/{operator_id}")
def get_tasks(operator_id: str):
    tasks = list(tasks_collection.find({"operator_id": operator_id}, {"_id": 0}))
    return tasks

@app.get("/all_tasks")
def get_all_tasks():
    tasks = list(tasks_collection.find({}, {"_id": 0}))
    return tasks

@app.patch("/update_task_status/{task_id}")
def update_task_status(task_id: int, payload: StatusUpdate):
    print(f"Updating task_id={task_id} to status={payload.status}")
    result = tasks_collection.update_one({"task_id": task_id}, {"$set": {"status": payload.status}})
    print(f"Matched count: {result.matched_count}")
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task status updated"}
from pydantic import BaseModel

class Task(BaseModel):
    operator_id: str
    task_type: str
    deadline: str
    status: str

@app.post("/add_task")
def add_task(task: Task):
    
    last_task = tasks_collection.find_one(sort=[("task_id", -1)])
    next_id = (last_task["task_id"] + 1) if last_task else 1

    task_doc = {
        "task_id": next_id,
        "operator_id": task.operator_id,
        "task_type": task.task_type,
        "deadline": task.deadline,
        "est_time": 0,  
        "status": task.status
    }

    tasks_collection.insert_one(task_doc)
    return {"message": "Task added successfully"}

from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb+srv://teamuser:password123team@cluster0.5wrc8bf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["task_dashboard"]


db.tasks.drop()


tasks_df = pd.read_csv("tasks.csv")
db.tasks.insert_many(tasks_df.to_dict(orient="records"))

print("Successfully seeded MongoDB Atlas with tasks from tasks.csv")

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

# 1. Connect to MongoDB Atlas via Environment Variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017") 
client = AsyncIOMotorClient(MONGO_URI)
db = client["todo_database"]
collection = db["tasks"]

class TodoItem(BaseModel):
    task: str

# 2. Updated HTML Frontend (Handles MongoDB unique text IDs instead of list indexes)
@app.get("/", response_class=HTMLResponse)
def get_frontend():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI MongoDB Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
            input { padding: 10px; width: 250px; }
            button { padding: 10px 15px; background-color: #28a745; color: white; border: none; cursor: pointer; }
            button.delete { background-color: #dc3545; margin-left: 10px; padding: 5px 10px; }
            ul { list-style-type: none; padding: 0; }
            li { background: white; margin: 5px 0; padding: 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; max-width: 400px; }
        </style>
    </head>
    <body>
        <h2>My Live Render + MongoDB To-Do List</h2>
        <input type="text" id="taskInput" placeholder="Enter a new cloud task...">
        <button onclick="addTask()">Add Task</button>
        
        <h3>Tasks from MongoDB Atlas:</h3>
        <ul id="taskList"></ul>

        <script>
            async function loadTasks() {
                const response = await fetch('/tasks');
                const tasks = await response.json();
                const list = document.getElementById('taskList');
                list.innerHTML = '';
                tasks.forEach(item => {
                    list.innerHTML += `<li>${item.task} <button class="delete" onclick="deleteTask('${item.id}')">X</button></li>`;
                });
            }

            async function addTask() {
                const input = document.getElementById('taskInput');
                if (!input.value) return;
                
                await fetch('/tasks', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task: input.value })
                });
                input.value = '';
                loadTasks();
            }

            async function deleteTask(id) {
                await fetch(`/tasks/${id}`, { method: 'DELETE' });
                loadTasks();
            }

            loadTasks();
        </script>
    </body>
    </html>
    """

# 3. GET Route (Fetch items from Atlas)
@app.get("/tasks")
async def get_tasks():
    tasks = []
    async for document in collection.find({}):
        tasks.append({"id": str(document["_id"]), "task": document["task"]})
    return tasks

# 4. POST Route (Insert item into Atlas)
@app.post("/tasks")
async def add_task(item: TodoItem):
    result = await collection.insert_one({"task": item.task})
    return {"message": "Task saved to Atlas!", "id": str(result.inserted_id)}

# 5. DELETE Route (Remove item from Atlas using its ObjectId string)
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    result = await collection.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 1:
        return {"message": "Deleted successfully"}
    return {"error": "Task not found"}

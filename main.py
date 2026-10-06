from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

# 1. Simulated Database (A simple Python list)
todo_db = ["Learn Render", "Deploy FastAPI app"]

# Data model for the POST request
class TodoItem(BaseModel):
    task: str

# 2. Built-in HTML Frontend
@app.get("/", response_class=HTMLResponse)
def get_frontend():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
            input { padding: 10px; width: 250px; }
            button { padding: 10px 15px; background-color: #007bff; color: white; border: none; cursor: pointer; }
            button.delete { background-color: #dc3545; margin-left: 10px; padding: 5px 10px; }
            ul { list-style-type: none; padding: 0; }
            li { background: white; margin: 5px 0; padding: 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; max-width: 400px; }
        </style>
    </head>
    <body>
        <h2>My Render To-Do List</h2>
        <input type="text" id="taskInput" placeholder="Enter a new task...">
        <button onclick="addTask()">Add Task</button>
        
        <h3>Tasks:</h3>
        <ul id="taskList"></ul>

        <script>
            // Fetch and display tasks when page loads
            async function loadTasks() {
                const response = await fetch('/tasks');
                const tasks = await response.json();
                const list = document.getElementById('taskList');
                list.innerHTML = '';
                tasks.forEach((task, index) => {
                    list.innerHTML += `<li>${task} <button class="delete" onclick="deleteTask(${index})">X</button></li>`;
                });
            }

            // POST request to add a task
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

            // DELETE request to remove a task
            async function deleteTask(index) {
                await fetch(`/tasks/${index}`, { method: 'DELETE' });
                loadTasks();
            }

            loadTasks();
        </script>
    </body>
    </html>
    """
    return html_content

# 3. GET Route (Read all items)
@app.get("/tasks")
def get_tasks():
    return todo_db

# 4. POST Route (Create a new item)
@app.post("/tasks")
def add_task(item: TodoItem):
    todo_db.append(item.task)
    return {"message": "Task added successfully!", "current_db": todo_db}

# 5. DELETE Route (Delete an item by its index)
@app.delete("/tasks/{index}")
def delete_task(index: int):
    if 0 <= index < len(todo_db):
        removed = todo_db.pop(index)
        return {"message": f"Removed: {removed}"}
    return {"error": "Task not found"}

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from your Render backend!"}

@app.get("/greet/{name}")
def greet_user(name: str):
    return {"message": f"Hello, {name}! Welcome to the app."}

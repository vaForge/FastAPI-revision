from fastapi import FastAPI

app = FastAPI() # app instance

@app.get("/")
def home():
    return {"message":"Welcome to todo api"}


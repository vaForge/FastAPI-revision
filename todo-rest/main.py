from fastapi import FastAPI
from routes import router

app = FastAPI() # app instance

app.include_router(router)

@app.get("/",tags=["Health"])
def home():
    return {"message":"Todo API is running"}
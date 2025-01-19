from fastapi import FastAPI
from datetime import datetime

app = FastAPI()


@app.get("/")
async def root():
    return {"message": f"Hello World at {datetime.now()}"}

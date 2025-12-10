from fastapi import FastAPI
from config import DB_FILE, LOG_LEVELS
from log_manager import LogEntry, fetch_logs
from typing import Optional, List

app = FastAPI()

@app.get("/")
def hello_world():
    return {"message": "Hello World"}


@app.get("/logs", response_model=List[LogEntry])
def api_get_logs(level: Optional[str] = None, component: Optional[str] = None):
    return fetch_logs(level, component)
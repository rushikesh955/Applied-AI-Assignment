from typing import List, Optional
from pydantic import BaseModel
import json
import os
from fastapi import HTTPException
from config import DB_FILE,LOG_LEVELS

DB_FILE = DB_FILE

############# DB Models ################################

class LogEntry(BaseModel):
    id: int
    timestamp: str
    level: str
    component: str
    message: str

##################    API Functions ########################

def fetch_logs(level: Optional[str] = None, component: Optional[str] = None) -> List[LogEntry]:
    if not os.path.exists(DB_FILE):
        raise HTTPException(status_code=404, detail=f"Database file '{DB_FILE}' not found")

    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
    except Exception as e:
        raise Exception(f"Error reading {DB_FILE}: {e}")
    
    logs = []
    for item in data:
        log_entry = LogEntry(**item)
        logs.append(log_entry)

    # handle the invalid filter
    if level.upper() not in LOG_LEVELS:
        raise HTTPException(status_code=400, detail=f'''The Given filter parameter '{level}' is not supported. Please Use any of the supported value : {LOG_LEVELS}''')
    
    if level:
        logs = [log for log in logs if (log.level).upper() == level.upper()]
    if component:
        logs = [log for log in logs if log.component == component]

    return logs

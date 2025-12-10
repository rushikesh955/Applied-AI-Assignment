from typing import List, Optional
from pydantic import BaseModel
import json
import os, uuid
from fastapi import HTTPException, UploadFile
from config import LOG_STORE, ALLOWED_EXTENSIONS, DB_FILE_PATH, LOG_STORE_PATH, LOG_LEVELS
import pandas as pd
from datetime import datetime


############# DB Models ################################

class LogEntry(BaseModel):
    id: str
    timestamp: str
    level: str
    component: str
    message: str


################# Helper func #####################

def is_valid_log_file(file: UploadFile):

    os.makedirs(LOG_STORE_PATH, exist_ok=True)
    file_location = os.path.join(LOG_STORE_PATH, file.filename)

    # Check file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Only {ALLOWED_EXTENSIONS} files are allowed."
        )

    # Check if file already exists
    file_location = f"{LOG_STORE}/{file.filename}"
    if os.path.exists(file_location):
        raise HTTPException(
            status_code=400,
            detail=f"File '{file.filename}' already exists. Upload failed."
        )

    return True


##################    API Functions ########################

def fetch_logs(level: Optional[str] = None, component: Optional[str] = None, start_time: Optional[str]=None, end_time: Optional[str]=None):

    if not os.path.exists(DB_FILE_PATH):
     raise HTTPException(status_code=404, detail=f"Database file '{DB_FILE_PATH}' not found")

    try:
        with open(DB_FILE_PATH, "r") as f:
            data = json.load(f)
    except Exception as e:
        raise Exception(f"Error reading {DB_FILE_PATH}: {e}")
    
    logs = []
    for item in data:
        log_entry = LogEntry(**item)
        logs.append(log_entry)
    
    if level:
         # handle the invalid filter
        if level.upper() not in LOG_LEVELS:
            raise HTTPException(status_code=400, detail=f'''The Given filter parameter '{level}' is not supported. Please Use any of the supported value : {LOG_LEVELS}''')
        logs = [log for log in logs if (log.level).upper() == level.upper()]
    if component:
        logs = [log for log in logs if log.component == component]

    if start_time:
        try:
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            logs = [log for log in logs if datetime.strptime(log.timestamp, "%Y-%m-%d %H:%M:%S") >= start_dt]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_time format. Use 'YYYY-MM-DD HH:MM:SS'")

    # Filter by end_time
    if end_time:
        try:
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            logs = [log for log in logs if datetime.strptime(log.timestamp, "%Y-%m-%d %H:%M:%S") <= end_dt]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_time format. Use 'YYYY-MM-DD HH:MM:SS'")
    return logs



def process_uploaded_file(file_path: str):
    print(file_path)
    new_logs=[]
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found.")

    # Read existing database
    if os.path.exists(DB_FILE_PATH):
        with open(DB_FILE_PATH, "r") as f:
            try:
                db_data = json.load(f)
            except json.JSONDecodeError:
                db_data = []
    else:
        db_data = []

    # Read the log file using pandas
    try:
        df = pd.read_csv(
            file_path,
            sep="\t",
            names=["Timestamp", "Level", "Component", "Message"],
            header=0, 
            on_bad_lines='skip', 
            dtype=str 
        )
    except Exception as e:
        raise Exception(f"Error reading log file: {e}")

    new_logs = []

    for _, row in df.iterrows():
        # Validate log level
        if row["Level"] not in LOG_LEVELS:
            continue

        log_entry = LogEntry(
            id=str(uuid.uuid4()),
            timestamp=row["Timestamp"],
            level=row["Level"],
            component=row["Component"],
            message=row["Message"]
        )
        new_logs.append(log_entry)
        db_data.append(log_entry.dict())

    # Save updated logs to dummy database
    with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(db_data, f, indent=4)

    return new_logs

# print("hello")
# import os

# file_path = os.path.join(os.path.dirname(__file__), "logs", "demo_log1.txt")
# logs = process_uploaded_file(file_path)
# print(f"{len(logs)} logs processed and saved to db.json")



from fastapi import FastAPI, UploadFile, File, HTTPException
from log_manager import LogEntry, fetch_logs, is_valid_log_file,process_uploaded_file
from typing import Optional, List
from pathlib import Path
import os
from config import LOG_STORE_PATH

app = FastAPI()


@app.get("/")
def hello_world():
    return {"message": "Hello World"}


@app.get("/logs")
def api_get_logs(level: Optional[str] = None, component: Optional[str] = None, start_time: Optional[str]=None, end_time: Optional[str]=None):
    return fetch_logs(level, component,start_time, end_time)


@app.get("/logs/stats")
def get_logs_stats():
    logs = fetch_logs()

    total_logs = 0
    level_counts = {}
    component_counts = {}

    for log in logs:
        total_logs += 1

        # Count per level
        if log.level in level_counts:
            level_counts[log.level] += 1
        else:
            level_counts[log.level] = 1

        # Count per component
        if log.component in component_counts:
            component_counts[log.component] += 1
        else:
            component_counts[log.component] = 1

    return {
        "total_logs": total_logs,
        "logs_per_level": level_counts,
        "logs_per_component": component_counts
    }



@app.get("/logs/{log_id}", response_model=LogEntry)
def get_log_by_id(log_id: str):
    logs = fetch_logs()
    for log in logs:
        if log.id == log_id:
            return log
    raise HTTPException(status_code=404, detail=f"Log with ID '{log_id}' not found")




@app.post("/upload-log")
async def upload_log(file: UploadFile):
    # Validate file
    is_valid_log_file(file)
    # make sure log folder exists
    os.makedirs(LOG_STORE_PATH, exist_ok=True)
    # Save the uploaded file
    file_location = os.path.join(LOG_STORE_PATH, file.filename)
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    process_uploaded_file(file_location)
    return {"Log File Uploaded Successfully": file.filename}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000,log_level="debug",reload=True)

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


@app.get("/logs", response_model=List[LogEntry])
def api_get_logs(level: Optional[str] = None, component: Optional[str] = None, start_time: Optional[str]=None, end_time: Optional[str]=None):
    return fetch_logs(level, component,start_time, end_time)


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

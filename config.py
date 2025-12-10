import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dummy DB File
DB_FILE = "db.json"
DB_FILE_PATH = os.path.join(BASE_DIR, DB_FILE)
# supported log levels
LOG_LEVELS = ["INFO", "DEBUG" , "WARNING", "ERROR"]

# log file store  folder
LOG_STORE = "logs"
LOG_STORE_PATH = os.path.join(BASE_DIR, LOG_STORE)

# allowed log file extentions 
ALLOWED_EXTENSIONS = [".txt",".log"]













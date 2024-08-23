import uuid
from datetime import datetime
from storage.sqlite import SQLiteStorage

class Logger:
    def __init__(self, storage: SQLiteStorage):
        if storage is None:
            self.storage = SQLiteStorage("lightagent.db")
        else:
            self.storage = storage
        self.storage.create_table("logs", "id TEXT PRIMARY KEY, log TEXT, datetime TEXT")
    
    def log(self, log: str, id: str = None):
        if id is None:
            id = str(uuid.uuid4())

        self.storage.upsert("logs", 
                            {"id": id, 
                             "log": log, 
                             "datetime": str(datetime.now())
                             })

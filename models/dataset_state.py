from datetime import datetime

class DatasetState:
    def __init__(self, filename, version, action):
        self.filename = filename
        self.version = version
        self.action = action
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "filename": self.filename,
            "version": self.version,
            "action": self.action,
            "timestamp": self.timestamp
        }

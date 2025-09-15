from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class LogEntry:
    timestamp: datetime
    source: str
    level: str
    message: str
    raw: Optional[str] = None

class BaseParser:
    def __init__(self, filepath):
        self.filepath = filepath

    def parse(self):
        raise NotImplementedError("Subclasses must implement this")

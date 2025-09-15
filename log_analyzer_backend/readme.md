Here's a **clean, scalable backend structure** for a **modular log parser engine**, ideal for your log analyzer project.

It’s designed to:

* Support **multiple log types** (auth.log, nginx, JSON logs, custom formats)
* Be **easily extensible** via plug-and-play parsers
* Keep parsing logic **decoupled** from the GUI frontend

---

# 🧱 1. 🔁 High-Level Architecture

```
/log_analyzer_backend/
├── __init__.py
├── log_loader.py         ← Handles file loading and format detection
├── log_parser.py         ← Dispatcher for parser selection
├── parsers/
│   ├── __init__.py
│   ├── base_parser.py    ← Abstract base class
│   ├── auth_parser.py    ← For /var/log/auth.log
│   ├── nginx_parser.py   ← For access/error logs
│   └── json_parser.py    ← For structured logs
└── models/
    ├── __init__.py
    └── log_entry.py      ← Dataclass for unified log representation
```

---

# 🔧 2. `log_entry.py` — Unified Log Model

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    source: str  # file or service name
    message: str
    user: str = None
    ip_address: str = None
    raw: str = ""
```

---

# 🧱 3. `base_parser.py` — Abstract Base Class

```python
from abc import ABC, abstractmethod

class BaseParser(ABC):
    def __init__(self, filepath):
        self.filepath = filepath

    @abstractmethod
    def parse(self):
        """Yields LogEntry objects"""
        pass

    @abstractmethod
    def match_format(cls, filepath: str) -> bool:
        """Checks if this parser can handle the file"""
        pass
```

---

# 🗝️ 4. Example: `auth_parser.py`

```python
import re
from datetime import datetime
from ..models.log_entry import LogEntry
from .base_parser import BaseParser

class AuthLogParser(BaseParser):
    def parse(self):
        with open(self.filepath) as f:
            for line in f:
                match = re.match(r'^(\w+ +\d+ \d+:\d+:\d+) (\S+) (.+)', line)
                if match:
                    timestamp_str, hostname, msg = match.groups()
                    timestamp = datetime.strptime(timestamp_str, "%b %d %H:%M:%S")
                    yield LogEntry(
                        timestamp=timestamp,
                        level="INFO",  # Basic, can improve with severity detection
                        source="auth.log",
                        message=msg,
                        raw=line.strip()
                    )

    @classmethod
    def match_format(cls, filepath: str):
        return "auth.log" in filepath
```

---

# 🧭 5. `log_parser.py` — Central Dispatcher

```python
from .parsers.auth_parser import AuthLogParser
from .parsers.nginx_parser import NginxLogParser
from .parsers.json_parser import JSONLogParser

PARSERS = [AuthLogParser, NginxLogParser, JSONLogParser]

def get_parser(filepath: str):
    for parser_cls in PARSERS:
        if parser_cls.match_format(filepath):
            return parser_cls(filepath)
    raise ValueError("No suitable parser found.")
```

---

# 📂 6. `log_loader.py` — Load + Normalize

```python
from .log_parser import get_parser

def load_log_entries(filepath: str):
    parser = get_parser(filepath)
    return list(parser.parse())
```

---

# 💡 Optional: Plugin Support

Allow users to drop their own parsers into a `parsers/` directory:

```python
# log_parser.py
import importlib.util
import os

def load_custom_parsers():
    for file in os.listdir("log_analyzer_backend/parsers"):
        if file.endswith("_parser.py"):
            # Dynamically import
            ...
```

---

# 🧪 How It Connects to the GUI

Your GTK frontend will call:

```python
from log_analyzer_backend.log_loader import load_log_entries

entries = load_log_entries("/var/log/auth.log")
```

It gets a list of `LogEntry` objects to display in the UI.

---

# 🚀 Advantages of This Design

✅ Easy to add new formats
✅ Testable parsers (unit test each one)
✅ Frontend stays clean — it doesn’t care what file is loaded
✅ Uniform data structure (`LogEntry`) makes sorting, searching, exporting trivial
✅ Allows future plugin support or sandboxed execution

---

Let me know if you want:

* Sample parsers for NGINX or JSON logs
* A backend starter repo scaffold
* GUI integration with this backend

This architecture is production-ready for most single-user or team-based log analysis tools.


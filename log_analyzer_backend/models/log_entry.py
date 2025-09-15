from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class LogEntry:
    timestamp: Optional[datetime]
    level: str
    source: str
    message: str
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[str] = None
    dst_port: Optional[str] = None
    domains: List[str] = field(default_factory=list)
    raw: Optional[str] = None

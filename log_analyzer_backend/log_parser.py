from typing import List
import os

from .models.log_entry import LogEntry
from .parsers.auth_parser import AuthParser
from .parsers.nginx_parser import NginxParser


def detect_log_type(filepath: str) -> str:
    filename = os.path.basename(filepath).lower()

    if "auth.log" in filename:
        return "auth"
    elif "access.log" in filename or "nginx" in filename:
        return "nginx"
    else:
        return "unknown"


def parse_log_file(filepath: str) -> List[LogEntry]:
    log_type = detect_log_type(filepath)

    if log_type == "auth":
        parser = AuthParser(filepath)
    elif log_type == "nginx":
        parser = NginxParser(filepath)
    else:
        raise ValueError(f"Unsupported log type for file: {filepath}")

    return parser.parse()


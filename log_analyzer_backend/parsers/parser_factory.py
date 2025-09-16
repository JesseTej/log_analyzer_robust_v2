import os
import re
from typing import Optional

from .parser_registry import PARSERS
from .base_parser import BaseParser

# Patterns used to sniff file content
_NGINX_HINT = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}\s+-\s+-\s+\[', re.MULTILINE)
_AUTH_HINT = re.compile(r'\b(sshd|sudo|authentication|failed password|accepted password|session opened|session closed)\b', re.IGNORECASE)
_GENERIC_LOG_HINTS = [
    re.compile(r'\d{4}-\d{2}-\d{2}'),        # ISO date
    re.compile(r'\d{2}:\d{2}:\d{2}'),        # time
    re.compile(r'\b(INFO|ERROR|WARN|DEBUG|CRITICAL)\b', re.IGNORECASE)
]

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>.+?)\] '
    r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
    r'(?P<status>\d{3}) (?P<size>\S+) '
    r'"(?P<referrer>[^"]*)" "(?P<useragent>[^"]*)"'
)

def parse_log_line(line: str) -> dict | None:
    m = LOG_PATTERN.match(line)
    if not m:
        return None  # malformed line
    gd = m.groupdict()
    # Parse timestamp to datetime
    try:
        gd["time"] = datetime.strptime(gd["time"], "%d/%b/%Y:%H:%M:%S %z")
    except Exception:
        pass
    # Convert numeric fields
    gd["status"] = int(gd["status"])
    gd["size"] = 0 if gd["size"] == "-" else int(gd["size"])
    return gd

def extract_log_details(line):
    
    details = {}
    
    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    ips = re.findall(ip_pattern, line)
    if ips:
        details["ports"] = ports
        
    domain_pattern = r"(?:(?<=:)|\bport\s)(\d{2,5})\b"
    ports = re.findall(port_pattern, line, re.IGNORECASE)
    if ports:
        details["ports"] = ports

    # Regex for domains/URLs
    domain_pattern = r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b"
    domains = re.findall(domain_pattern, line)
    if domains:
        details["domains"] = domains

    return details

def is_log_file(file_path: str, sample_size: int = 4096) -> bool:
    """
    Heuristically decide whether a file looks like a log by sampling its content.
    Returns True if common log patterns are found.
    """
    try:
        if not os.path.isfile(file_path):
            return False

        with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
            sample = fh.read(sample_size)

        # quick checks
        for p in _GENERIC_LOG_HINTS:
            if p.search(sample):
                return True

        return False
    except Exception:
        return False


def detect_log_type(file_path: str) -> Optional[str]:
    """
    Decide which parser should handle the file, based on filename hints and content sniffing.
    Returns a key present in PARSERS (e.g., 'auth', 'nginx') or None.
    """
    filename = os.path.basename(file_path).lower()

    # filename-based heuristics (fast)
    if "auth" in filename or "secure" in filename or "sshd" in filename:
        return "auth"
    if "access.log" in filename or "access" in filename or "nginx" in filename:
        return "nginx"

    # content-based heuristics (fall back)
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
            sample = fh.read(8192)
            if _NGINX_HINT.search(sample):
                return "nginx"
            if _AUTH_HINT.search(sample):
                return "auth"
            # If generic log-like patterns present, fallback to auth parser if available
            for p in _GENERIC_LOG_HINTS:
                if p.search(sample):
                    return "auth" if "auth" in PARSERS else next(iter(PARSERS.keys()), None)
    except Exception:
        return None

    return None


def get_parser(file_path: str) -> Optional[BaseParser]:
    """
    Return an instance of a parser appropriate for file_path, or None if unsupported.
    """
    log_type = detect_log_type(file_path)

    if not log_type:
        # last resort: if file looks like any log, use the first registered parser as a fallback
        if is_log_file(file_path) and PARSERS:
            parser_name = next(iter(PARSERS.keys()))
            parser_cls = PARSERS.get(parser_name)
            if parser_cls:
                return parser_cls(file_path)
        return None

    parser_cls = PARSERS.get(log_type)
    if parser_cls:
        return parser_cls(file_path)

    return None

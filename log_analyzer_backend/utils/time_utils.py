# --- helpers for extracting IPs, ports, and domains from a log line/text ---
import re
from typing import List
from datetime import datetime

def parse_timestamp(ts_str: str) -> datetime | None:
    """
    Parse a timestamp string from common log formats into a datetime object.

    Supports:
      - Apache/Nginx style: 10/Oct/2020:13:55:36 +0000
      - ISO 8601: 2020-10-10T13:55:36Z or with offsets
      - Fallback: tries datetime.fromisoformat
    Returns None if parsing fails.
    """
    if not ts_str:
        return None

    # Apache/Nginx style: [10/Oct/2020:13:55:36 +0000]
    match = re.match(r"\[?(\d{1,2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4})\]?", ts_str)
    if match:
        try:
            return datetime.strptime(match.group(1), "%d/%b/%Y:%H:%M:%S %z")
        except Exception:
            pass

    # ISO 8601 (basic handling)
    try:
        # Normalize Z to +00:00 for fromisoformat
        norm = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(norm)
    except Exception:
        pass

    # Last resort: try common fallback without timezone
    try:
        return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None
    
def extract_ips_from_text(text: str) -> List[str]:
    """
    Extract unique IPv4 addresses from text. Validates octets (0-255).
    Returns a list preserving order.
    """
    if not text:
        return []
    candidates = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
    ips = []
    for ip in candidates:
        parts = ip.split('.')
        try:
            if all(0 <= int(p) <= 255 for p in parts):
                ips.append(ip)
        except ValueError:
            continue
    return list(dict.fromkeys(ips))


def extract_ports_from_text(text: str) -> List[int]:
    """
    Extract likely port numbers from text. Prefers context-aware matches:
      - IP:PORT (e.g. 10.0.0.1:8080)
      - domain.tld:PORT (e.g. example.com:8443)
      - port=1234 or 'port 1234'
    Avoids matching timestamps like 13:55:36.
    Returns unique ports as ints preserving order.
    """
    if not text:
        return []
    ports = []
    # IP:PORT
    for m in re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}:(\d{1,5})\b', text):
        p = int(m)
        if 1 <= p <= 65535:
            ports.append(p)
    # domain:port
    for m in re.findall(r'\b(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}:(\d{1,5})\b', text):
        p = int(m)
        if 1 <= p <= 65535:
            ports.append(p)
    # 'port=1234' or 'port 1234'
    for m in re.findall(r'\bport(?:=|\s+)([0-9]{1,5})\b', text, flags=re.IGNORECASE):
        p = int(m)
        if 1 <= p <= 65535:
            ports.append(p)
    return list(dict.fromkeys(ports))


def extract_domains_from_text(text: str) -> List[str]:
    """
    Extract domain-like tokens (multi-label domains) from text.
    Returns lowercase domains, unique preserving order.
    """
    if not text:
        return []
    candidates = re.findall(r'\b((?:[a-zA-Z0-9-]{1,63}\.)+(?:[a-zA-Z]{2,63}))\b', text)
    domains = []
    for d in candidates:
        # ignore IPv4-like matches just in case
        if not re.match(r'^(?:\d{1,3}\.){3}\d{1,3}$', d):
            domains.append(d.lower())
    return list(dict.fromkeys(domains))


def format_timestamp(ts: datetime, fmt: str = "%d/%b/%Y:%H:%M:%S %z") -> str:
    """
    Format a datetime object into a string for display/log export.
    
    Args:
        ts (datetime): datetime object
        fmt (str): strftime format string (default is common Apache/Nginx log format)
    
    Returns:
        str: formatted timestamp, or '' if input is None
    """
    if ts is None:
        return ""
    try:
        return ts.strftime(fmt)
    except Exception:
        return str(ts)
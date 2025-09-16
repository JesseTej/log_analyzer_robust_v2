import re
from datetime import datetime
from log_analyzer_backend.models.log_entry import LogEntry
from log_analyzer_backend.parsers.base_parser import BaseParser  # Adjust if needed
from log_analyzer_backend.utils.time_utils import parse_timestamp
from log_analyzer_backend.utils.time_utils import extract_ips_from_text, extract_ports_from_text, extract_domains_from_text  # Add this import
from log_analyzer_backend.utils.time_utils import parse_log_line

class AuthParser(BaseParser):

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

    
    def parse(self) -> list[LogEntry]:
        entries = []

        with open(self.filepath, "r") as f:
            for line in f:
                entry = self._parse_line(line)
                if entry:
                    entries.append(entry)
        return entries

    def _parse_line(self, line: str):
        regex = r"^(\w{3})\s+(\d{1,2})\s([\d:]+)\s([\w\-.]+)\s([\w\/\[\]\-\.]+):\s(.+)$"
        match = re.match(regex, line)

        if match:
            month_str, day, time_str, hostname, source, message = match.groups()
            try:
                timestamp = datetime.strptime(
                    f"{month_str} {day} {time_str} {datetime.now().year}",
                    "%b %d %H:%M:%S %Y"
                )
            except ValueError:
                return None

            # Basic logic to assign log level
            log_level = "INFO"
            if "failed" in message.lower():
                log_level = "WARNING"
            elif "error" in message.lower() or "denied" in message.lower():
                log_level = "ERROR"

            src, dst = extract_ips_from_text(line)
            srcp, dstp = extract_ports_from_text(line)
            domains = extract_domains_from_text(line)
            ts = None
            if 'dt' in locals():
                ts = locals().get('dt')
            elif 'timestamp' in locals():
                ts = parse_timestamp(locals().get('timestamp'))
            else:
                ts = None
            return LogEntry(
                timestamp=ts,
                level=locals().get('log_level', locals().get('level','UNKNOWN')),
                source=locals().get('source',''),
                message=locals().get('message',''),
                src_ip=src,
                dst_ip=dst,
                src_port=srcp,
                dst_port=dstp,
                domains=domains,
                raw=line.strip()
            )
    
        entry = parse_log_line(line)
        if not entry:
            return None  # skip malformed line

        ip, dash1, dash2, timestamp, request, status = entry[:6]
                    


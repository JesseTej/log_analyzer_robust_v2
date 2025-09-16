import re
from datetime import datetime
from log_analyzer_backend.utils.time_utils import parse_timestamp, extract_ips_from_text, extract_ports_from_text, extract_domains_from_text
from typing import List
from .base_parser import BaseParser
from ..models.log_entry import LogEntry
from log_analyzer_backend.utils.line_utils import parse_log_line

class NginxParser(BaseParser):
    def parse(self) -> List[LogEntry]:
        entries = []

        with open(self.filepath, "r") as f:
            for line in f:
                entry = self._parse_line(line)
                if entry:
                    entries.append(entry)

        return entries

#You should remove this piece 
    def _parse_line(self, line: str) -> LogEntry | None:
        regex = r'^([\d.]+) - - \[(.*?)\] "(.*?)" (\d{3} \d+ ".*?" "(.*?)")$'
        match = re.match(regex, line)

        if not match:
            return None

        ip, timestamp_str, request, status, user_agent = match.groups()

        # Convert timestamp like: 16/Jul/2025:11:24:17 +0300
        try:
            dt = datetime.strptime(timestamp_str.split()[0], "%d/%b/%Y:%H:%M:%S")
        except ValueError:
            return None

        message = f"{request} {status} \"{user_agent}\""

        ips = extract_ips_from_text(line)
        src, dst = (ips + [None, None])[:2]

        ports = extract_ports_from_text(line)
        srcp, dstp = (ports + [None, None])[:2]

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
        



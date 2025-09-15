from datetime import datetime
from typing import List, Optional
from log_analyzer_backend.models.log_entry import LogEntry
from log_analyzer_backend.utils.time_utils import format_timestamp


class LogAnalyzerBackend:
    def __init__(self):
        self.log_entries: List[LogEntry] = []  # Already parsed entries
        
    def load_logs(self, entries: List[LogEntry]):
        self.log_entries = entries

    def filter_logs(self, keyword=None, start_time=None, end_time=None):
        filtered = []

        keyword_lower = keyword.lower() if keyword else None

        for entry in self.log_entries:  
            # Skip entries outside date range
            if start_time and entry.timestamp < start_time:
                continue
            if end_time and entry.timestamp > end_time:
                continue
            
            # Skip if keyword doesn't appear in any searchable field
            if keyword_lower:
                if not (
                    keyword_lower in entry.level.lower()
                    or keyword_lower in entry.source.lower()
                    or keyword_lower in entry.message.lower()
                    or keyword_lower in format_timestamp(entry.timestamp)
                ):
                    continue

            filtered.append(entry)

        return filtered

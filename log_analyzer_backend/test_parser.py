# test_parser.py (create this at root for now)

from log_analyzer.log_parser import parse_log_file

entries = parse_log_file("/var/log/auth.log")  # Or path to your nginx test log

for e in entries:
    print(f"[{e.timestamp}] {e.source} — {e.message}")


# Log Analyzer Robust v2

A modular and GUI-based log analyzer designed for cybersecurity and system administration use cases.
This tool supports parsing multiple log formats (Nginx, Apache, Auth, etc.), provides a table-based GUI for filtering and searching logs, and can highlight IPs, ports, and domains.

Features

Multi-format log parsing

Nginx / Apache access logs

Auth logs (Linux authentication attempts, SSH, etc.)

Extendable parser system (parser_registry.py)

Robust parsing

Skips malformed log lines gracefully instead of crashing

Uses safe parsing functions with fallbacks

GUI Frontend

Built with Python + Qt (or wx, depending on setup)

Interactive table for browsing parsed logs

Sorting, filtering, and search

Utilities

Extract IPs, ports, and domains from logs

Format and normalize timestamps

Installation

Clone the repo:

git clone <https://github.com/your-repo/log_analyzer_robust_v2.git>
cd log_analyzer_robust_v2

Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Usage

Run the GUI:

python run.py

Or analyze a single log file via command line (if CLI helper is included):

python cli.py /path/to/access.log

Handling Malformed Lines

The analyzer is designed to skip bad log entries without failing.
Every parser uses a pattern like:

entry = parse_log_line(line)
if not entry:
    continue  # skip malformed line

This ensures:

Corrupt or incomplete log lines don’t break the program

Errors are logged but don’t stop the analysis

Extending the Parser

To add support for a new log format:

Create a new parser class in log_analyzer_backend/parsers/

Implement parse_log_line(line) returning a dictionary or None

Register it in parser_registry.py

Example

Sample Nginx log line:

127.0.0.1 - - [10/Oct/2020:13:55:36 +0000] "GET / HTTP/1.1" 200 612

Parsed result:

{
  "ip": "127.0.0.1",
    "timestamp": "2020-10-10T13:55:36+00:00",
  "method": "GET",
  "path": "/",
  "status": 200,
  "size": 612
}

Known Issues

Some .split()-based parsing is brittle on unusual log lines. Regex and safe split checks have been introduced to reduce errors.

Ensure logs are UTF-8 encoded; malformed encodings may be skipped.

License

MIT License – feel free to use, modify, and extend.

log_analyzer_robust_v2/
├── run.py                         ← Entry point for launching the GUI
├── requirements.txt               ← Python dependencies (if present)
├── README.md                      ← Documentation (to be finalized)

├── gui/                           ← Graphical user interface
│   ├── __init__.py
│   ├── main_window.py             ← Main application window
│   └── widgets/
│       ├── __init__.py
│       └── log_table.py           ← Table widget for displaying parsed logs

├── log_analyzer_backend/          ← Core backend logic
│   ├── __init__.py
│   ├── log_loader.py              ← Handles log file loading
│   ├── log_parser.py              ← Dispatcher for selecting the right parser
│   │
│   ├── parsers/                   ← Specific parsers for different log types
│   │   ├── __init__.py
│   │   ├── base_parser.py         ← Abstract base parser class
│   │   ├── parser_factory.py      ← Factory to get appropriate parser
│   │   ├── parser_registry.py     ← Registry of available parsers
│   │   ├── auth_parser.py         ← Parser for /var/log/auth.log
│   │   ├── nginx_parser.py        ← Parser for Nginx access/error logs
│   │   └── json_parser.py         ← Parser for structured JSON logs
│   │
│   ├── models/                    ← Shared data models
│   │   ├── __init__.py
│   │   └── log_entry.py           ← Dataclass representing a parsed log entry
│   │
│   └── utils/                     ← Helper functions
│       ├── __init__.py
│       └── time_utils.py          ← Timestamp parsing, formatting, IP/port/domain extractors
│
└── tests/                         ← (Optional) Unit tests if added
    ├── __init__.py
    └── test_parsers.py            ← Tests for individual parsers

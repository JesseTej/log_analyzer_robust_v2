# Log Analyzer Robust v2

A desktop log analyzer for Linux, built with **Python and GTK 3**. It is aimed at security and sysadmin work: open a log file, browse it in a sortable table, search and filter by time range, and follow new lines live as they are written (`tail -f` style).

The parser layer is modular. Each log format is its own parser class, and the right one is picked automatically from the file name or its contents.

> **Status: early development.** The Nginx/Apache access-log path works end to end. The auth-log parser and a few helpers still have bugs (see [Known issues](#known-issues)). Contributions are welcome.

---

## Features

- **Format auto-detection**: picks a parser by file name (`auth`, `secure`, `sshd`, `access`, `nginx`) and falls back to sniffing the first 8 KB of content.
- **Supported formats**
  - Nginx / Apache access logs (combined format)
  - Linux auth logs (`/var/log/auth.log`, `secure`: SSH, sudo, PAM), *in progress*
  - JSON structured logs, *planned* (`json_parser.py` is a stub)
- **Graceful handling of bad input**: lines that don't match a parser's pattern are skipped rather than crashing the load.
- **GTK 3 interface**
  - Table view with Timestamp, Level, Source IP, Destination IP, Message and Source columns
  - Colour-coded severity levels (CRITICAL, ERROR, WARNING, INFO, DEBUG, TRACE)
  - Live text search across the visible columns
  - Time-range filter (`YYYY-MM-DD HH:MM:SS`) combined with keyword search
  - **Live tailing**: a background thread watches the loaded file and appends new entries
- **Indicator extraction**: every entry is enriched with IPv4 addresses (validated octets), ports (`ip:port`, `host:port`, `port 22`, `port=22`) and domain names.
- **Bonus utility**: `utmp.py`, a standalone parser for binary `utmp`/`wtmp`/`btmp` login records, exports them to TSV.

---

## Requirements

- Linux (developed and tested on Debian/Ubuntu-family distros)
- Python **3.10+** (the code uses `X | None` type syntax)
- GTK 3 and PyGObject

Install the system packages (Debian/Ubuntu/Kali):

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

Fedora:

```bash
sudo dnf install python3-gobject gtk3
```

There are no other third-party Python dependencies: the backend uses only the standard library.

---

## Installation

```bash
git clone https://github.com/JesseTej/log_analyzer_robust_v2.git
```

```bash
cd log_analyzer_robust_v2
```

If you want a virtual environment, create it with access to the system PyGObject (installing PyGObject from pip needs extra build dependencies):

```bash
python3 -m venv --system-site-packages venv
```

```bash
source venv/bin/activate
```

---

## Usage

### GUI

Run from the repository root so the `gui` and `log_analyzer_backend` packages resolve:

```bash
python3 run.py
```

1. Click **Load Log** and choose a file.
2. Type in the search box to filter the table instantly.
3. Enter a start and/or end time and click **Filter Logs** to restrict by time range.
4. Click **Start Tailing** to stream new lines appended to the file. Click again to stop.

> Reading `/var/log/auth.log` usually requires root or membership in the `adm` group. Copying the file somewhere readable is a simple alternative to running the GUI as root.

### Using the backend from Python

```python
from log_analyzer_backend.parsers.parser_factory import get_parser
from log_analyzer_backend.backend import LogAnalyzerBackend

parser = get_parser("/var/log/nginx/access.log")
entries = parser.parse()                    # list[LogEntry]

backend = LogAnalyzerBackend()
backend.load_logs(entries)
for e in backend.filter_logs(keyword="404"):
    print(e.timestamp, e.src_ip, e.message)
```

### Parsing utmp / wtmp records

```bash
python3 utmp.py wtmp -o logins.tsv
```

Omit `-o` to print to stdout. A sample `wtmp` file is included in the repo.

---

## Example

Input line (Nginx combined format):

```
127.0.0.1 - - [10/Oct/2020:13:55:36 +0000] "GET / HTTP/1.1" 200 612 "-" "curl/7.0"
```

Resulting `LogEntry`:

```python
LogEntry(
    timestamp=datetime(2020, 10, 10, 13, 55, 36),
    level="UNKNOWN",
    source="",
    message='GET / HTTP/1.1 200 612 "-" "curl/7.0" "curl/7.0"',
    src_ip="127.0.0.1",
    dst_ip=None,
    src_port=None,
    dst_port=None,
    domains=[],
    raw='127.0.0.1 - - [10/Oct/2020:13:55:36 +0000] "GET / HTTP/1.1" 200 612 "-" "curl/7.0"',
)
```

---

## Project structure

```
log_analyzer_robust_v2/
├── run.py                       # Entry point: launches the GTK GUI
├── utmp.py                      # Standalone utmp/wtmp → TSV parser
├── wtmp                         # Sample binary wtmp file
├── gui/
│   ├── main.py                  # Older/alternate launcher (expects sample.log)
│   ├── main_window.py           # Main window: toolbar, load, filter, tailing
│   └── widgets/
│       └── log_table.py         # TreeView table with search + level colours
└── log_analyzer_backend/
    ├── backend.py               # LogAnalyzerBackend: keyword + time-range filtering
    ├── log_loader.py            # load_log_file() helper
    ├── log_parser.py            # Older filename-only dispatcher
    ├── log_models.py            # Legacy LogEntry/BaseParser (superseded by models/)
    ├── plan.txt                 # Feature roadmap and ideas
    ├── models/
    │   └── log_entry.py         # LogEntry dataclass (current)
    ├── parsers/
    │   ├── base_parser.py       # Abstract BaseParser
    │   ├── parser_registry.py   # PARSERS = {"auth": ..., "nginx": ...}
    │   ├── parser_factory.py    # detect_log_type() + get_parser()
    │   ├── auth_parser.py       # Syslog-style auth.log parser
    │   ├── nginx_parser.py      # Nginx/Apache access-log parser
    │   └── json_parser.py       # Placeholder
    └── utils/
        ├── time_utils.py        # Timestamp parse/format, IP/port/domain extraction
        └── line_utils.py        # Line-splitting helper
```

### The `LogEntry` model

| Field       | Type                  | Description                              |
|-------------|-----------------------|------------------------------------------|
| `timestamp` | `datetime \| None`    | Parsed event time                        |
| `level`     | `str`                 | Severity (`INFO`, `WARNING`, `ERROR`, …) |
| `source`    | `str`                 | Program/service that wrote the line      |
| `message`   | `str`                 | Human-readable message                   |
| `src_ip`    | `str \| None`         | First IP found in the line               |
| `dst_ip`    | `str \| None`         | Second IP found in the line              |
| `src_port`  | `int \| None`         | First port found                         |
| `dst_port`  | `int \| None`         | Second port found                        |
| `domains`   | `list[str]`           | Domain names found                       |
| `raw`       | `str \| None`         | The original line                        |

---

## Adding a new parser

1. Create a class in `log_analyzer_backend/parsers/` that subclasses `BaseParser`:

   ```python
   from .base_parser import BaseParser
   from ..models.log_entry import LogEntry

   class SyslogParser(BaseParser):
       def parse(self) -> list[LogEntry]:
           entries = []
           with open(self.filepath, "r", errors="replace") as f:
               for line in f:
                   entry = self._parse_line(line)
                   if entry:
                       entries.append(entry)
           return entries

       def _parse_line(self, line: str) -> LogEntry | None:
           ...  # return None for lines you can't parse
   ```

   Implement `_parse_line()` as well as `parse()`: live tailing in the GUI calls `_parse_line()` one line at a time.

2. Register it in `parsers/parser_registry.py`:

   ```python
   PARSERS = {
       "auth": AuthParser,
       "nginx": NginxParser,
       "syslog": SyslogParser,
   }
   ```

3. Teach `detect_log_type()` in `parsers/parser_factory.py` how to recognise it (by file name and/or a content regex).

---

## Known issues

These were found while reviewing the current code:

- **Auth-log parsing fails.** `AuthParser._parse_line` unpacks `extract_ips_from_text()` as exactly two values, which raises `ValueError` unless a line has exactly two IPs. It also passes a `datetime` into `parse_timestamp()`, which expects a string. `NginxParser` shows the safe pattern: `(ips + [None, None])[:2]`.
- **Nginx entries** get `level="UNKNOWN"` and an empty `source`, and the user agent appears twice in `message`. Lines without a numeric size (e.g. `-`) don't match the regex and are skipped.
- **Auth timestamps assume the current year**, because syslog lines don't include one.
- `parse_log_line()` in `utils/time_utils.py` and `utils/line_utils.py` calls itself recursively and never returns a value.
- `extract_log_details()` in `parser_factory.py` references undefined names, and that module uses `datetime` without importing it.
- The **"Show details"** checkbox in `MainWindow` is never added to the layout, and the table has only six columns, so it has no effect.
- **Filter Logs** before any file is loaded raises an error, because `self.backend` is still `None`.
- `gui/main.py`, `log_parser.py`, `log_models.py` and `test_parser.py` are older code paths and are not used by `run.py`.
- `__pycache__`/`.pyc` files, a `venv/` and a `.zip` snapshot are committed. They should be removed and added to a `.gitignore`.

---

## Roadmap

The full list of ideas is in [`log_analyzer_backend/plan.txt`](log_analyzer_backend/plan.txt). Highlights:

- Quick time filters (last hour, today, last 7 days)
- Regex search and filtering by username, IP and event type
- JSON, syslog and journald support, plus `.gz` and rotated logs (`.log.1`, `.log.2.gz`)
- Export filtered results to CSV, JSON or HTML
- Event tagging and notes, and pinned events
- Charts (failed logins over time, top IPs) and an hourly heatmap
- Basic anomaly detection (e.g. brute-force attempts) and multi-log correlation
- GeoIP and threat-intel enrichment (AbuseIPDB, VirusTotal)
- Remote log fetching over SSH, and `.deb`/Flatpak packaging

---

## License

No license has been chosen for this project yet. `utmp.py` carries its own Apache License 2.0 header.

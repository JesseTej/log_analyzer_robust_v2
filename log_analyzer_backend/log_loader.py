# log_analyzer_backend/log_loader.py
from log_analyzer_backend.log_models import LogEntry
from .log_parser import get_parser
from .parsers.auth_parser import AuthParser

def load_log_file(filepath):
    parser = get_parser(filepath)
    return parser.parse(filepath)  # Returns list of LogEntry

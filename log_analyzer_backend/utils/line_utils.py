def parse_log_line(line: str):
    """
    Safely parse a log line into tokens.
    Returns a list of parts or None if malformed.
    """
    try:
        entry = parse_log_line(line)
        if not entry:
            return  # skip malformed line

        ip, dash1, dash2, timestamp, request, status = entry[:6]
    except Exception:
        return None

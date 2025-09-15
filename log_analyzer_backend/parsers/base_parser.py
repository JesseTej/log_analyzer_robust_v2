from abc import ABC, abstractmethod
from typing import List
from ..models.log_entry import LogEntry


class BaseParser(ABC):

    """All parsers to inherit from this class and implent the parse() method"""

    def __init__(self, filepath: str):
        self.filepath =filepath

    @abstractmethod
    def parse(self) -> List[LogEntry]:
        """Parses the log file and returns a list of LogEntry Objects"""

        pass

import sys
from typing import TextIO

class Logger:
    _instance: "Logger | None" = None

    @classmethod
    def get(cls) -> "Logger":
        """
        Returns the singleton instance of the logger
        """
        if cls._instance is None:
            cls._instance = Logger()
        return cls._instance

    def e(self, msg: str, output: TextIO = sys.stdout, end: str = "\n") -> None:
        """
        Log an error
        """
        print(f"\033[31m[ERROR]\033[0m {msg}", file=output, end=end)

    def w(self, msg: str, output: TextIO = sys.stdout, end: str = "\n") -> None:
        """
        Log a warning
        """
        print(f"\033[33m[WARNING]\033[0m {msg}", file=output, end=end)

    def i(self, msg: str, output: TextIO = sys.stdout, end: str = "\n") -> None:
        """
        Log an info
        """
        print(f"\033[34m[INFO]\033[0m {msg}", file=output, end=end)

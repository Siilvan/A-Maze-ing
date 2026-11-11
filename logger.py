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

    def e(self, msg: str) -> None:
        """
        Log an error
        """
        print(f"\033[31m[ERROR]\033[0m {msg}")

    def w(self, msg: str) -> None:
        """
        Log a warning
        """
        print(f"\033[33m[WARNING]\033[0m {msg}")

    def i(self, msg: str) -> None:
        """
        Log an info
        """
        print(f"\033[34m[INFO]\033[0m {msg}")

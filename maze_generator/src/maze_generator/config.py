from typing import Any
from .utils import *
from .helpers import MazeGenerationException, MazeSizeException, ManualExit, Logger
import sys


class MazeConfig:

    class ParseError(Exception):
        def __init__(self, msg: str, line_n: int, line: str) -> None:
            self.msg = msg
            self.line_n = line_n
            self.line = line

    def __init__(self,
                 exit_pos: tuple[int, int] | None = None,
                 entry_pos: tuple[int, int] = (0, 0),
                 output_path: str = "output.mz",
                 perfect: bool = False,
                 width: int = 50,
                 height: int = 50,
                 logo:str = "42"
                 ) -> None:
        self.width: int = width
        self.height: int = height
        self.entry_pos: tuple[int, int] = entry_pos
        if (exit_pos is None):
            self.exit_pos: tuple[int, int] = (self.width - 1,
                                              self.height - 1)
        else:
            self.exit_pos = exit_pos
        self.output_path: str = output_path
        self.perfect: bool = perfect
        self.logo: str = logo

    def validate_config(self) -> bool:
        """
        Validates the config and it's current parameters.
        ensures everything is how it should be.

        returns True or False if the config is correct or not
        """
        if self.width < 2 or self.height < 2:
            raise MazeSizeException(
                "Maze must be at least 2 wide and 2 high")
        if (not 0 <= self.entry_pos[0] < self.height
            or not 0 <= self.entry_pos[1] < self.width):
            raise MazeGenerationException(
                "Entry position outside of maze.")
        if (not 0 <= self.exit_pos[0] < self.height
            or not 0 <= self.exit_pos[1] < self.width):
            raise MazeGenerationException(
                "Exit position outside of maze")
        logo_len = 0
        for i in range(len(self.logo)):
            logo_len += 3
            if i < len(self.logo) - 1 and self.logo[i + 1] != " ":
                logo_len += 1
        if self.height < 7 or self.width < logo_len + 2:
            Logger.get().w(f"Maze too small for logo: must be at least {logo_len + 2}"
                           f" wide and 7 high.")
            Logger.get().w("Continue printing maze without logo? (y/n) ", end="")
            sys.stdout.flush()
            y_n = sys.stdin.readline().strip()
            if y_n.lower() == "y":
                self.logo = ""
            else: 
                raise ManualExit("User exited program - quitting")

        return (False)

    @classmethod
    def from_file(cls, path: str) -> "MazeConfig":
        """
        Attemps to parse a config object from a file of 
        KEY=VALUE pairs.

        returns None on failure
        """
        config: "MazeConfig" = cls()
        with open(path, "r") as f:
            line_n : int = 1
            line: str = f.readline().strip()
            while (line != ""):
                tokens = line.split("=")
                if (len(tokens) != 2):
                    raise MazeConfig.ParseError(
                            msg="Unparseable line",
                            line_n=line_n,
                            line=line)
                if (not config._assign_key(tokens[0], tokens[1])):
                    raise MazeConfig.ParseError(
                            msg=f"Failed to assign {tokens[1]} to {tokens[0]}, " +
                            "ensure the type and naming are correct.",
                            line_n=line_n,
                            line=line
                            )
                line = f.readline()
        config.validate_config()
        return config


    def _assign_key(self, key: str, val: Any) -> bool:
        """
        Assigns the key with id `key` with the value `val`.
        only attemps to do so if val is of the right type,
        and key exists.
        """
        key = key.lower()
        # Ensure that this object has an attribute with the keyname
        if (hasattr(self, key)):
            parsed: Any = try_parse(val, type(getattr(self, key)))
            if (parsed is None):
                return False
            setattr(self, key, parsed)
            return True
        if (key == "entry"):
            return self._assign_key("entry_pos", val)
        if (key == "exit"):
            return self._assign_key("exit_pos", val)
        return False

    def __str__(self) -> str:
        return "\n".join([f"{k}={v}" for k, v in self.__dict__])

    def __repr__(self) -> str:
        return str(self)


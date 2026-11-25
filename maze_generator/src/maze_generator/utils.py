from .helpers import Logger
from typing import Any, Callable


def parse_position_tuple(string: str) -> tuple[int, int] | None:
    """
    Parses a tuple[int, int] from a string and returns it.
    returns None on failure
    """
    split: list[str] = string.split(",")
    if len(split) != 2:
        return None
    try:
        return (int(split[0]), int(split[1]))
    except TypeError:
        return None


def parse_bool(string: str) -> bool | None:
    n_str: str = string.strip().lower()
    if n_str == "true":
        return True
    if n_str == "false":
        return False
    return None


def try_parse[T](val: Any, to_type: type[T]) -> Any:
    """
    Tries to parse variable `val` as type T.
    returns the parsed var of type T on success or None
    on failure
    """
    if to_type is str:
        return str(val)
    if to_type is tuple:
        return parse_position_tuple(val)
    if to_type is int:
        try:
            return int(val)
        except ValueError:
            return None
    if to_type is bool:
        return parse_bool(val)
    return None


def solution_to_directions(solution: list[tuple[int, int]]) -> str | None:
    """
    Returns a string of cardinal directions from
    the list[tuple[int, int]] returned by the solver.
    """
    string: str = ""
    previous: tuple[int, int] | None = None
    for c in solution:
        if previous is None:
            previous = c
            continue
        direction: tuple[int, int] = tuple_op(c, previous, lambda a, b: a - b)
        match direction:
            case (0, 1):
                string += "N"
            case (1, 0):
                string += "E"
            case (0, -1):
                string += "S"
            case (-1, 0):
                string += "W"
            case _:
                Logger.get().e(
                    "Got unknown direction while " +
                    f"parsing solution: {direction}"
                )
                return
        previous = c
    return string


def tuple_op(
    a: tuple[int, int], b: tuple[int, int], op: Callable[[int, int], int]
) -> tuple[int, int]:
    """
    subtracts two position tuples and returns a new tuple with the result
    """
    return (op(a[0], b[0]), op(a[1], b[1]))

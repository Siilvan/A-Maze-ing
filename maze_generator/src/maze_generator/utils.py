from typing import Any

def parse_position_tuple(
        string: str
        ) -> tuple[int, int] | None:
    """
    Parses a tuple[int, int] from a string and returns it.
    returns None on failure
    """
    split: list[str] = string.split(",")
    if (len(split) != 2):
        return None
    try:
        return (int(split[0]), int(split[1]))
    except TypeError:
        return None

def parse_bool(string: str) -> bool | None:
    n_str: str = string.strip().lower()
    if (n_str == "true"):
        return True
    if (n_str == "false"):
        return False
    return None

def try_parse[T](val: Any, to_type: type[T]) -> Any:
    """
    Tries to parse variable `val` as type T.
    returns the parsed var of type T on success or None
    on failure
    """
    if (to_type is str):
        return str(val)
    if (to_type is tuple):
        return parse_position_tuple(val)
    if (to_type is int):
        try:
            return int(val)
        except ValueError:
            return None
    if (to_type is bool):
        return parse_bool(val)
    return None

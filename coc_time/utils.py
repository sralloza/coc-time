from datetime import datetime, timedelta
import re
import sys

COMMAND_TEMPLATE = "/home/sralloza/notifications/notify.sh '{title}' '{content}'"
QUOTE_CHARS = {'"'}


def escape(msg: str) -> str:
    for char in QUOTE_CHARS:
        msg = msg.replace(char, f"\\{char}")

    return msg


def compute_time(hours: int = 0, minutes: int = 0, dec: bool = True) -> datetime:
    time = datetime.now() + timedelta(hours=hours, minutes=minutes)
    if dec:
        time -= timedelta(minutes=1)
    return time


def input_int(msg: str) -> int:
    value = input(msg)
    try:
        return int(value)
    except ValueError:
        print(f"{value!r} is not a valid integer", file=sys.stderr)
        sys.exit(-1)
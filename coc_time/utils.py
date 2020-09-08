from datetime import datetime, timedelta
import re
import sys

COMMAND_TEMPLATE = "/home/coc/notifications/notify.sh '{title}' '{content}'"
QUOTE_CHARS = {'"'}


def escape(msg: str) -> str:
    for char in QUOTE_CHARS:
        msg = msg.replace(char, f"\\{char}")

    return msg


def compute_time(dec: bool = True, **date_kwargs: int) -> datetime:
    days = date_kwargs.get("days", 0)
    hours = date_kwargs.get("hours", 0)
    mins = date_kwargs.get("mins", 0)

    time = datetime.now() + timedelta(days=days, hours=hours, minutes=mins)
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

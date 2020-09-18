import pendulum

COMMAND_TEMPLATE = "/home/coc/notifications/notify.sh '{title}' '{content}'"
QUOTE_CHARS = {'"'}


def escape(msg: str) -> str:
    for char in QUOTE_CHARS:
        msg = msg.replace(char, f"\\{char}")

    return msg


def compute_time(dec: bool = True, **date_kwargs: int) -> pendulum.DateTime:
    days = date_kwargs.get("days", 0)
    hours = date_kwargs.get("hours", 0)
    mins = date_kwargs.get("mins", 0)

    time = pendulum.now() + pendulum.Duration(days=days, hours=hours, minutes=mins)
    if dec:
        time -= pendulum.Duration(minutes=1)
    return time

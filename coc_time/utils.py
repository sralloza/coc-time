import pendulum

COMMAND_TEMPLATE = "/home/coc/notifications/notify.sh '{title}' '{content}'"
QUOTE_CHARS = {'"'}


def escape(msg: str) -> str:
    for char in QUOTE_CHARS:
        msg = msg.replace(char, f"\\{char}")

    return msg


def compute_time(**date_kwargs: int) -> pendulum.DateTime:
    base_date = date_kwargs.pop("base_date", 0)
    days = date_kwargs.pop("days", 0)
    hours = date_kwargs.pop("hours", 0)
    mins = date_kwargs.pop("mins", 0)

    if base_date:
        time = base_date
    else:
        time = pendulum.now()

    time += pendulum.Duration(days=days, hours=hours, minutes=mins -1)
    return time

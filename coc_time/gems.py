import math
from pendulum import Duration


def gems_to_time(gems: int):
    timerange = [60, 3600, 86400, 604800]
    gemsrange = [1, 20, 260, 1000]
    seconds = 0
    if gems is None:
        gems = 0
    if gems < 0:
        pass
    elif gems == 0:
        seconds = 0
    else:
        gems = gems + 1

    if gems <= gemsrange[1]:
        seconds = (
            math.ceil(
                (gems - gemsrange[0])
                * ((timerange[1] - timerange[0]) / (gemsrange[1] - gemsrange[0]))
                + timerange[0]
            )
            - 1
        )
    elif gems <= gemsrange[2]:
        seconds = (
            math.ceil(
                (gems - gemsrange[1])
                * ((timerange[2] - timerange[1]) / (gemsrange[2] - gemsrange[1]))
                + timerange[1]
            )
            - 1
        )
    else:
        seconds = (
            math.ceil(
                (gems - gemsrange[2])
                * ((timerange[3] - timerange[2]) / (gemsrange[3] - gemsrange[2]))
                + timerange[2]
            )
            - 1
        )

    return Duration(seconds=seconds)


def time_to_gems(duration: Duration):
    ranges = [60, 3600, 86400, 604800]
    gems = [1, 20, 260, 1000]

    result = 0
    seconds = duration.seconds
    if seconds < 0:
        result = 0
    elif seconds == 0:
        result = 0
    elif seconds <= ranges[0]:
        result = 1
    elif seconds <= ranges[1]:
        result = math.floor(
            (seconds - ranges[0]) / ((ranges[1] - ranges[0]) / (gems[1] - gems[0]))
            + gems[0]
        )
    elif seconds <= ranges[2]:
        result = math.floor(
            (seconds - ranges[1]) / ((ranges[2] - ranges[1]) / (gems[2] - gems[1]))
            + gems[1]
        )
    else:
        result = math.floor(
            (seconds - ranges[2]) / ((ranges[3] - ranges[2]) / (gems[3] - gems[2]))
            + gems[2]
        )

    return result

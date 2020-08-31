from collections import namedtuple
from datetime import datetime
from shlex import split

from .ssh import remote_execution
from .utils import COMMAND_TEMPLATE, compute_time, input_int

Day = namedtuple("Day", "mins hours day month")


class CrontabManager:
    cron_tmp_path = "/tmp/clash-of-clans-cron"

    def __init__(self, iterable):
        self.crons = list(iterable)
        self.remove_old_crons()
        self.sort()

    def __bool__(self):
        return bool(self.crons)

    def __contains__(self, cron_line: str):
        return cron_line in self.crons

    def __iter__(self):
        return iter(self.crons)

    def __str__(self) -> str:
        if not self:
            return "<emtpy cron>"
        return "\n".join([split(x)[-1] for x in self])

    def append(self, cron_line: str):
        if cron_line not in self:
            self.crons.append(cron_line)
            self.sort()

    def add_cron(self, minutes: int = None, hours: int = None, reason: str = None):
        if hours is None:
            hours = input_int("Insert hours: ")

        if minutes is None:
            minutes = input_int("Insert minutes: ")

        time = compute_time(hours, minutes, dec=True)

        if reason is None:
            reason = input("Insert reason: ")
            if not reason:
                print("\nCancelled cron add")
                return

        command = self.generate_cron_line(time, reason)
        self.append(command)

    @staticmethod
    def gen_cron_time(time: datetime) -> str:
        return f"{time.minute:2d} {time.hour:2d} {time.day:2d} {time.month:2d} *"

    def generate_cron_line(self, time: datetime, content: str = "") -> str:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        content = f"[{ts}] {content}"
        cron_time = self.gen_cron_time(time)
        fmt = {"title": "Clash of clans", "content": content}
        return cron_time + " " + COMMAND_TEMPLATE.format(**fmt)

    def sort(self):
        self.crons.sort(key=self.sorter)

    @staticmethod
    def splitline(line: str) -> Day:
        mins, hours, day, month, *_ = line.split()
        mins, hours, day, month, *_ = map(int, (mins, hours, day, month))
        return Day(mins, hours, day, month)

    @classmethod
    def sorter(cls, line: str):
        day = cls.splitline(line)
        return day.month, day.day, day.hours, day.mins

    def remove_old_crons(self):
        self.crons = list(filter(self.filter, self.crons))

    @classmethod
    def filter(cls, line):
        day = cls.splitline(line)
        current = datetime.now()
        ts = datetime(
            month=day.month,
            day=day.day,
            hour=day.hours,
            minute=day.mins,
            year=current.year,
        )
        if current > ts:
            return False
        return True

    @classmethod
    def get_current_crons(cls) -> "CrontabManager":
        current_crons = remote_execution("crontab -l").splitlines()
        current_crons = [x.strip("\n") for x in current_crons if x.strip()]

        self = cls(current_crons)
        return self

    def save_to_server(self):
        commands = []
        for i, cron_line in enumerate(self):
            char = ">>" if i else ">"
            commands.append(f'echo "{cron_line}" {char} {self.cron_tmp_path}')

        commands.append(f"crontab {self.cron_tmp_path}")
        commands.append(f"rm {self.cron_tmp_path}")

        real_command = " && ".join(commands)
        return remote_execution(real_command)

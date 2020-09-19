from collections import UserList, UserString, namedtuple
from hashlib import sha256
from shlex import split
from typing import Optional

import click
import pendulum

from .exceptions import InvalidMethodError
from .ssh import remote_execution
from .types import get_color, get_type
from .utils import COMMAND_TEMPLATE, compute_time

Day = namedtuple("Day", "mins hours day month")


class CronLine(UserString):
    _split_str_a = "] "
    _split_str_b = "["

    @property
    def type(self) -> str:
        return get_type(self.new_project)

    @property
    def color(self) -> Optional[str]:
        return get_color(self.new_project)

    @property
    def message(self) -> str:
        return self.split(self._split_str_a)[-1]

    @property
    def notification(self) -> str:
        return split(str(self))[-1]

    @property
    def old_project(self) -> str:
        return self.message.split("-")[0].strip()

    @property
    def new_project(self) -> str:
        return self.message.split("-")[-1].strip()

    @property
    def dt(self) -> pendulum.DateTime:
        dt_str = self.split(self._split_str_a)[0].split(self._split_str_b)[-1]
        return pendulum.parse(dt_str)

    def replace_message(self, new_message: str):
        new_message += "'"
        new_cron_line = self.replace(self.message, new_message)
        self.__init__(new_cron_line)


class CrontabManager(UserList):
    cron_tmp_path = "/tmp/clash-of-clans-cron"

    def __init__(self, iterable):
        crons = [CronLine(x) for x in iterable]
        super().__init__(crons)
        self.original_length = len(self)
        self.original_hash = self.calculate_hash()
        self.remove_comments()
        self.remove_old_crons()
        self.sort()

    def __str__(self) -> str:
        raise InvalidMethodError("To print the crontab manager, use .print()")

    @property
    def has_changed(self):
        return self.original_hash != self.calculate_hash()

    def print(self, color=True):
        if not self:
            click.secho("<emtpy cron>", fg="bright_red")
            return

        for line in self:
            fg_color = line.color if color else None
            click.secho(line.notification, fg=fg_color)
        click.echo()

    def calculate_hash(self) -> str:
        data = "".join([str(x) for x in self]).encode("utf8")
        sha = sha256()
        sha.update(data)
        return sha.hexdigest()

    def append(self, cron_line: str):
        if cron_line not in self:
            super().append(CronLine(cron_line))
            self.sort()

    def add_cron(self, reason: str = None, demo: bool = False, **date_kwargs):
        days = date_kwargs.pop("days", None)
        hours = date_kwargs.pop("hours", None)
        mins = date_kwargs.pop("mins", None)

        if days is None:
            days = click.prompt("Insert days", type=int, default=0)

        if hours is None:
            hours = click.prompt("Insert hours", type=int, default=0)

        if mins is None:
            mins = click.prompt("Insert minutes", type=int, default=0)

        time = compute_time(days=days, hours=hours, mins=mins, **date_kwargs)
        if demo:
            click.secho(
                f'[{time.strftime("%Y-%m-%d %H:%M")}]', fg="bright_green", bold=True
            )
            return

        if reason is None:
            reason = click.prompt("Insert reason", default="")
            if not reason:
                click.secho("\nCancelled cron add", fg="bright_yellow")
                return

        command = self.generate_cron_line(time, reason)
        self.append(command)

    def add_extending(self, cron_number: int):
        base_cron = self.get_cron(cron_number)
        click.secho(f"Extending {base_cron.notification}")
        self.add_cron(base_date=base_cron.dt)

    def edit_cron_message(self, cron_number: int):
        cron_selected = self.get_cron(cron_number)

        new_message = click.edit(cron_selected.message.strip("'"))

        if not new_message:
            raise click.Abort()

        new_message = new_message.strip().strip("'")
        if not click.confirm(f"Confirm new message? ({new_message!r})", abort=True):
            raise click.Abort()

        cron_selected.replace_message(new_message)

    def get_cron(self, cron_number: int) -> CronLine:
        try:
            return self[cron_number - 1]
        except IndexError:
            raise click.UsageError(f"No cron found with id={cron_number}")

    def remove_cron(self, cron_number: int):
        cron_selected = self.get_cron(cron_number)

        confirm = click.confirm(
            f"\nRemove cron {cron_selected.notification!r}?", abort=True
        )

        if confirm:
            self.remove(cron_selected)

    @staticmethod
    def gen_cron_time(time: pendulum.DateTime) -> str:
        return f"{time.minute:2d} {time.hour:2d} {time.day:2d} {time.month:2d} *"

    def generate_cron_line(self, time: pendulum.DateTime, content: str = "") -> str:
        ts = time.strftime("%Y-%m-%d %H:%M")
        content = f"[{ts}] {content}"
        cron_time = self.gen_cron_time(time)
        fmt = {"title": "Clash of clans", "content": content}
        return cron_time + " " + COMMAND_TEMPLATE.format(**fmt)

    def sort(self):
        super().sort(key=self.sorter)

    @staticmethod
    def splitline(line: str) -> Day:
        mins, hours, day, month, *_ = line.split()
        mins, hours, day, month, *_ = map(int, (mins, hours, day, month))
        return Day(mins, hours, day, month)

    @classmethod
    def sorter(cls, line: CronLine):
        day = cls.splitline(str(line))
        return day.month, day.day, day.hours, day.mins

    def remove_comments(self):
        new_crons = list(filter(lambda x: not x.startswith("#"), self))
        super().__init__(new_crons)

    def remove_old_crons(self, echo=True):
        new_crons = list(filter(self.filter, self))
        removed_crons = set(self) - set(new_crons)

        if echo and removed_crons:
            click.secho("Removing crons:", fg="bright_magenta")
            for line in removed_crons:
                click.secho("-" + line.notification, fg="bright_magenta")

        super().__init__(new_crons)

    @classmethod
    def filter(cls, line):
        current = pendulum.now()
        return current < line.dt

    @classmethod
    def get_current_crons(cls) -> "CrontabManager":
        current_crons = remote_execution("crontab -l").splitlines()
        current_crons = [x.strip("\n") for x in current_crons if x.strip()]

        self = cls(current_crons)
        return self

    def save_to_server(self) -> str:
        if not self:
            return "no cron lines to save"

        commands = []
        for i, cron_line in enumerate(self):
            char = ">>" if i else ">"
            commands.append(f'echo "{cron_line}" {char} {self.cron_tmp_path}')

        commands.append(f"crontab {self.cron_tmp_path}")
        commands.append(f"rm {self.cron_tmp_path}")

        real_command = " && ".join(commands)
        return remote_execution(real_command)

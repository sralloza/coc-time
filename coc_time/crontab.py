from collections import namedtuple
from datetime import datetime
from hashlib import sha256
from shlex import split

import click

from .ssh import remote_execution
from .utils import COMMAND_TEMPLATE, compute_time

Day = namedtuple("Day", "mins hours day month")


class CrontabManager:
    cron_tmp_path = "/tmp/clash-of-clans-cron"

    def __init__(self, iterable):
        self.crons = list(iterable)
        self.original_length = len(self.crons)
        self.original_hash = self.calculate_hash()
        self.remove_comments()
        self.remove_old_crons()
        self.sort()

    def __bool__(self):
        return bool(self.crons)

    def __contains__(self, cron_line: str):
        return cron_line in self.crons

    def __iter__(self):
        return iter(self.crons)

    def __len__(self):
        return len(self.crons)

    def __str__(self) -> str:
        if not self:
            return "<emtpy cron>"
        return "\n".join([split(x)[-1] for x in self])

    @property
    def has_changed(self):
        return self.original_hash != self.calculate_hash()

    def calculate_hash(self) -> str:
        data = str(self).encode("utf8")
        sha = sha256()
        sha.update(data)
        return sha.hexdigest()

    def append(self, cron_line: str):
        if cron_line not in self:
            self.crons.append(cron_line)
            self.sort()

    def add_cron(self, reason: str = None, demo: bool = False, **date_kwargs: int):
        days = date_kwargs.get("days")
        hours = date_kwargs.get("hours")
        mins = date_kwargs.get("mins")

        if days is None:
            days = click.prompt("Insert days", type=int, default=0)

        if hours is None:
            hours = click.prompt("Insert hours", type=int, default=0)

        if mins is None:
            mins = click.prompt("Insert minutes", type=int, default=0)

        time = compute_time(days=days, hours=hours, mins=mins, dec=True)
        if demo:
            click.secho(f'[{time.strftime("%Y-%m-%d %H:%M")}]', fg="bright_green", bold=True)
            return

        if reason is None:
            reason = click.prompt("Insert reason", default="")
            if not reason:
                click.secho("\nCancelled cron add", fg="bright_yellow", bold=True)
                return

        command = self.generate_cron_line(time, reason)
        self.append(command)

    def edit_cron_message(self, cron_number: int):
        split_str = "] "
        cron_selected = self.get_cron(cron_number)
        time_part, message = cron_selected.split(split_str)

        click.echo(f"\nOld message: {message!r}")
        new_message = click.prompt("Type new message", default="")
        new_message = new_message.strip().strip("'")

        if not new_message:
            raise click.Abort()

        if not click.confirm(f"Confirm new message? ({new_message!r})", abort=True):
            raise click.Abort()

        new_cron = split_str.join([time_part, new_message]) + "'"
        self.crons[cron_number - 1] = new_cron

    def get_cron(self, cron_number: int) -> str:
        try:
            return self.crons[cron_number - 1]
        except IndexError:
            raise click.UsageError(f"No cron found with id={cron_number}")

    def remove_cron(self, cron_number: int):
        cron_selected = self.get_cron(cron_number)

        cron_str = split(cron_selected)[-1]
        confirm = click.confirm(f"\nRemove cron {cron_str!r}?", abort=True)

        if confirm:
            self.crons.remove(cron_selected)

    @staticmethod
    def gen_cron_time(time: datetime) -> str:
        return f"{time.minute:2d} {time.hour:2d} {time.day:2d} {time.month:2d} *"

    def generate_cron_line(self, time: datetime, content: str = "") -> str:
        ts = time.strftime("%Y-%m-%d %H:%M")
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

    def remove_comments(self):
        self.crons = list(filter(lambda x: not x.startswith("#"), self.crons))

    def remove_old_crons(self, echo=True):
        new_crons = list(filter(self.filter, self.crons))
        removed_crons = set(self.crons) - set(new_crons)

        if echo and removed_crons:
            click.secho("Removing crons:" ,fg="bright_magenta", bold=True)
            for line in removed_crons:
                click.secho("-" + split(line)[-1],fg="bright_magenta", bold=True)

        self.crons = new_crons

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

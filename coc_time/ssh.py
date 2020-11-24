import sys
from enum import Enum
from subprocess import CalledProcessError, run
from typing import Any

import click
from tenacity import TryAgain, retry, stop_after_attempt

from .utils import escape


class Machines(Enum):
    coc = 0
    test = 1
    volvo = 2
    fenix = 3

    def __str__(self):
        return f"{type(self).__name__}.{self.name}"

    def __repr__(self):
        return f"<{type(self).__name__}.{self.name}>"

    @staticmethod
    def validate(machine: Any) -> "Machines":
        if isinstance(machine, Machines):
            return machine

        machine = str(machine)
        try:
            return Machines[machine]
        except KeyError:
            raise ValueError(f"{machine!r} is not a valid Machine")

    @staticmethod
    def set_current(machine):
        if not isinstance(machine, Machines):
            machine = Machines.validate(machine)
        _Static._current_machine = machine

    @staticmethod
    def get_current() -> "Machines":
        return _Static._current_machine


class _Static:
    _current_machine: Machines = Machines.coc


@retry(stop=stop_after_attempt(5))
def remote_execution(command: str, retries=5) -> str:
    remote_command = f'ssh {Machines.get_current().name} "{escape(command)}"'
    completed = run(remote_command, capture_output=True, shell=True)

    try:
        completed.check_returncode()
        return completed.stdout.decode("utf8")
    except CalledProcessError:
        err = completed.stderr.decode("utf8").lower()
        if "connection timed out" in err:
            retries -= 1
            if retries:
                click.secho(
                    "Connection error, retrying", sys.stderr, fg="bright_yellow"
                )
                raise TryAgain

        msg = f"Error in remote execution: {completed}"
        click.secho(msg, sys.stderr, fg="bright_red")
        raise click.Abort()

from enum import Enum
from subprocess import CalledProcessError, run
import sys

from .utils import escape


class Machines(Enum):
    test = 0
    volvo = 1
    fenix = 2

    def __str__(self):
        return f"{type(self).__name__}.{self.name}"

    def __repr__(self):
        return f"<{type(self).__name__}.{self.name}>"

    @staticmethod
    def set_current(machine):
        if not isinstance(machine, Machines):
            machine = Machines[machine]
        _Static._current_machine = machine

    @staticmethod
    def get_current() -> "Machines":
        return _Static._current_machine


class _Static:
    _current_machine: Machines = Machines.test


def remote_execution(command: str) -> str:
    remote_command = f'ssh {Machines.get_current().name} "{escape(command)}"'
    completed = run(remote_command, capture_output=True, shell=True)

    try:
        completed.check_returncode()
        return completed.stdout.decode("utf8")
    except CalledProcessError:
        print("Error in remote execution: %s" % completed, sys.stderr)
        sys.exit(1)

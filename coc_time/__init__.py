from argparse import ArgumentParser
import sys

from coc_time.crontab import CrontabManager
from coc_time.ssh import Machines


def parse_args():
    parser = ArgumentParser(prog="Clash of Clans")
    parser.add_argument(
        "machine",
        nargs="?",
        default=Machines.coc,
        type=Macines.vahlidate,
        help="machine to use",
    )
    parser.add_argument("--add-cron", "-a", help="Add cron line", action="store_true")
    parser.add_argument(
        "--add-demo", "-d", help="Add cron line in demo mode", action="store_true"
    )
    parser.add_argument("--write", "-w", help="Update cron", action="store_true")

    return parser.parse_args()


def main():
    options = vars(parse_args())
    Machines.set_current(options["machine"])

    print("Using machine %r" % Machines.get_current().name)
    cron_mng = CrontabManager.get_current_crons()

    print(cron_mng)

    if options["add_cron"]:
        cron_mng.add_cron()

    if options["add_demo"]:
        cron_mng.add_cron(demo=True)
        return

    if options["write"] or options["add_cron"] or cron_mng.has_changed:
        if cron_mng.has_changed:
            print(
                "Updating server crontab [old=%d,new=%d]"
                % (cron_mng.original_length, len(cron_mng))
            )

        result = cron_mng.save_to_server()
        print(f"[{result}]")

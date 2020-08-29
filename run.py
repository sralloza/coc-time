import sys

from coc_time.crontab import CrontabManager
from coc_time.ssh import Machines


def main():
    if sys.argv[1:]:
        Machines.set_current(sys.argv[1])
    else:
        Machines.set_current(Machines.volvo)

    print("Using machine %r" % Machines.get_current().name)
    cron_mng = CrontabManager.get_current_crons()
    print(cron_mng)

    cron_mng.add_cron()

    result = cron_mng.save_to_server()
    print(f"[{result}]")


if __name__ == "__main__":
    main()

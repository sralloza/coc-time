import click

from .crontab import CrontabManager
from .ssh import Machines


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument(
    "machine",
    default=Machines.coc,
    type=Machines.validate,
    required=False,
)
@click.option("--add-cron", "-a", is_flag=True)
@click.option("--add-demo", "-d", is_flag=True)
@click.option("--remove", "-r", type=int)
@click.option("--write", "-w", is_flag=True)
def main(machine, add_cron, add_demo, remove, write):
    Machines.set_current(machine)

    print("Using machine %r" % Machines.get_current().name)
    cron_mng = CrontabManager.get_current_crons()

    print(cron_mng)

    if add_cron:
        cron_mng.add_cron()

    if add_demo:
        cron_mng.add_cron(demo=True)
        return

    if remove:
        cron_mng.remove_cron(remove)

    if write or add_cron or cron_mng.has_changed:
        if cron_mng.has_changed:
            print(
                "Updating server crontab [old=%d,new=%d]"
                % (cron_mng.original_length, len(cron_mng))
            )

        result = cron_mng.save_to_server()
        print(f"[{result}]")

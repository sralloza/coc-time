import click

from .crontab import CrontabManager
from .ssh import Machines


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
HELP = {
    "add-cron": "Adds a new cron",
    "add-demo": "Shows the date but doesn't add a new cron",
    "remove": "Removes the nth cron",
    "no-write": "Force the no upload of a new cron",
}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument(
    "machine",
    default=Machines.coc,
    type=Machines.validate,
    required=False,
)
@click.option("--add-cron", "-a", is_flag=True, help=HELP["add-cron"])
@click.option("--add-demo", "-d", is_flag=True, help=HELP["add-demo"])
@click.option("--remove", "-r", type=int, help=HELP["remove"])
@click.option("--no-write", "-w", is_flag=True, help=HELP["no-write"])
def main(machine, add_cron, add_demo, remove, no_write):
    """Clash of clans notifier manager."""

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

    if not no_write and (add_cron or cron_mng.has_changed):
        if cron_mng.has_changed:
            print(
                "Updating server crontab [old=%d,new=%d]"
                % (cron_mng.original_length, len(cron_mng))
            )

        result = cron_mng.save_to_server()
        print(f"[{result}]")

def cli():
    return main(prog_name="coc")

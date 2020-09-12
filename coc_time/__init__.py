import click

from ._version import get_versions
from .crontab import CrontabManager
from .ssh import Machines

__version__ = get_versions()["version"]
del get_versions

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
HELP = {
    "add": "Adds a new cron",
    "demo": "Shows the date adding the given timedelta",
    "edit": "Edits the message of the Nth cron",
    "no-write": "Force the no-upload of a new cron",
    "remove": "Removes the Nth cron",
}


class MyGroup(click.Group):
    def get_first_argument(self) -> click.core.Argument:
        for param in self.params:
            if isinstance(param, click.Argument):
                return param
        raise ValueError

    def parse_args(self, ctx, args):
        ctx.ensure_object(dict)
        if args and args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                args.insert(0, self.get_first_argument().default.name)
        super(MyGroup, self).parse_args(ctx, args)


@click.group(
    cls=MyGroup, context_settings=CONTEXT_SETTINGS, invoke_without_command=True
)
@click.version_option(version=__version__)
@click.pass_context
@click.argument("machine", default=Machines.coc, type=Machines.validate, required=False)
@click.option("--no-write", "-w", is_flag=True, help=HELP["no-write"])
def main(ctx, machine, no_write):
    """Clash of clans notifier manager."""
    Machines.set_current(machine)

    click.echo("Using machine %r" % Machines.get_current().name)
    cron_mng = CrontabManager.get_current_crons()
    ctx.obj = cron_mng

    click.echo(cron_mng)


@main.resultcallback()
@click.pass_obj
def process_result(cron_mng: CrontabManager, result, **kwargs):
    no_write = kwargs.pop("no_write")

    if not no_write and cron_mng.has_changed:
        if cron_mng.has_changed:
            click.echo(
                "Updating server crontab [old=%d,new=%d]"
                % (cron_mng.original_length, len(cron_mng))
            )

        result = cron_mng.save_to_server()
        click.echo(f"[{result}]")


@main.command("add", help=HELP["add"])
@click.pass_obj
def add_cron(cron_mng: CrontabManager):
    cron_mng.add_cron()


@main.command("demo", help=HELP["demo"])
@click.pass_obj
def add_demo(cron_mng: CrontabManager):
    cron_mng.add_cron(demo=True)


@main.command("edit", help=HELP["edit"])
@click.argument("cron_position", type=int)
@click.pass_obj
def edit_cron_message(cron_mng: CrontabManager, cron_position: int):
    cron_mng.edit_cron_message(cron_position)


@main.command("remove", help=HELP["remove"])
@click.argument("cron_position", type=int)
@click.pass_obj
def remove_cron(cron_mng: CrontabManager, cron_position: int):
    cron_mng.remove_cron(cron_position)


def cli():
    return main(prog_name="coc")

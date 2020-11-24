import click

from ._version import get_versions
from .crontab import CrontabManager
from .ssh import Machines

__version__ = get_versions()["version"]
del get_versions

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
HELP = {
    "add-extending": "Adds a new cron based on the datetime of other",
    "add": "Adds a new cron",
    "add-gems": "Adds a new cron given the gem cost",
    "add-gems-demo": "Adds a new cron given the gem cost in demo mode",
    "demo": "Shows the date adding the given timedelta",
    "diff": "Show relative time instead of absolute",
    "edit": "Edits the message of the Nth cron",
    "no-color": "disables colors",
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
@click.option("--diff", is_flag=True, help=HELP["diff"])
@click.option("--no-color", is_flag=True, help=HELP["no-color"])
@click.option("--no-write", "-w", is_flag=True, help=HELP["no-write"])
def main(ctx, machine, no_write, no_color, diff):
    """Clash of clans notifier manager."""
    Machines.set_current(machine)

    click.echo("Using machine %r" % Machines.get_current().name)
    cron_mng = CrontabManager.get_current_crons()
    ctx.obj = cron_mng

    cron_mng.print(color=not no_color, diff=diff)

    # Remove line after installing click-8.0.0
    if ctx.invoked_subcommand is None:
        main.result_callback(None, no_write=no_write)


@main.resultcallback()
@click.pass_obj
def update_cron_if_needed(cron_mng: CrontabManager, result, **kwargs):
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


@main.command("add-extending", help=HELP["add-extending"])
@click.argument("cron_position", type=int)
@click.pass_obj
def add_extending(cron_mng: CrontabManager, cron_position: int):
    cron_mng.add_extending(cron_position)


@main.command("add-gems", help=HELP["add-gems"])
@click.argument("gems", type=int)
@click.pass_obj
def add_gems(cron_mng: CrontabManager, gems: int):
    cron_mng.add_gems(gems)


@main.command("add-gems-demo", help=HELP["add-gems-demo"])
@click.argument("gems", type=int)
@click.pass_obj
def add_gems(cron_mng: CrontabManager, gems: int):
    cron_mng.add_gems(gems, demo=True)


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

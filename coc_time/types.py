from typing import Optional

from fuzzywuzzy import process

from .inversions import manager

from .schemas import InversionType

type_to_color = {
    InversionType.normal_gold: "bright_yellow",
    InversionType.normal_elixir: "bright_magenta",
    InversionType.walls: "",
    InversionType.dark_elixir: "bright_white",
    InversionType.constructor_gold: "bright_yellow",
    InversionType.constructor_elixir: "bright_magenta",
}


def get_type(project: str) -> Optional[InversionType]:
    project = project.strip("¿").strip("?").strip()

    if len(project) < 5:
        return

    inversion_name = process.extractOne(
        project, [x.concept for x in manager.inversions], score_cutoff=1
    )

    if not inversion_name:
        return

    inversion_name = inversion_name[0]

    for inversion in manager.inversions:
        if inversion.concept == inversion_name:
            return inversion.inversion_type
    return


ColorStr = Optional[str]


def get_color(project: str) -> ColorStr:
    default = "bright_cyan"
    cron_type = get_type(project)
    if not cron_type:
        return default
    return type_to_color.get(cron_type, default)

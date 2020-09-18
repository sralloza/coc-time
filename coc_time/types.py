from typing import Optional, Tuple

types = {
    "campamento": "elixir",
    "cuartel": "elixir",
    "laboratorio": "elixir",
    "caldero": "elixir",
    "rey": "dark-elixir",
    "reina": "dark-elixir",
    "recolector": "gold",
    "mina": "elixir",
    "almacén": "elixir",
    "almacen": "elixir",
    "muro": "both",
    "cohetes": "gold",
    "defensa aérea": "gold",
    "defensa aerea": "gold",
    "tesla": "gold",
    "bombardero": "gold",
    "bombardera": "gold",
    "ballesta": "gold",
    "bomba": "gold",
    "trampa": "gold",
    "conjunto": "gold",
    "explosivo": "gold",
    "cañón": "gold",
    "cañon": "gold",
    "arqueras": "gold",
    "magos": "gold",
    "magos": "gold",
    "controlador": "gold",
    "inv": "elixir",
    "investigación": "elixir",
    "investigacion": "elixir",
    "investigar": "elixir",
}

type_to_color = {
    "gold": "bright_yellow",
    "elixir": "bright_magenta",
    "dark-elixir": "bright_white",
}


def get_type(cron_line: str) -> str:
    cron_line = cron_line.split("-")[-1]

    for key, value in types.items():
        if key in cron_line:
            return value
    return ""


ColorStr = Optional[str]


def get_color(cron_line: str) -> ColorStr:
    cron_type = get_type(cron_line)
    return type_to_color.get(cron_type, "bright_cyan")

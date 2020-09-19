from typing import Optional, Tuple

types = {
    "almacen": "elixir",
    "almacén": "elixir",
    "arqueras": "gold",
    "atacar": "attack",
    "ballesta": "gold",
    "bomba": "gold",
    "bombardera": "gold",
    "bombardero": "gold",
    "bonus": "attack",
    "botin": "attack",
    "botín": "attack",
    "caldero": "elixir",
    "campamento": "elixir",
    "cañon": "gold",
    "cañón": "gold",
    "cohetes": "gold",
    "conjunto": "gold",
    "controlador": "gold",
    "cuartel": "elixir",
    "defensa aerea": "gold",
    "defensa aérea": "gold",
    "explosivo": "gold",
    "inv": "elixir",
    "investigacion": "elixir",
    "investigación": "elixir",
    "investigar": "elixir",
    "laboratorio": "elixir",
    "magos": "gold",
    "magos": "gold",
    "mina": "elixir",
    "muro": "both",
    "recolector": "gold",
    "reina": "dark-elixir",
    "rey": "dark-elixir",
    "tesla": "gold",
    "trampa": "gold",
}

type_to_color = {
    "attack": "bright_red",
    "dark-elixir": "bright_white",
    "elixir": "bright_magenta",
    "gold": "bright_yellow",
}


def get_type(project: str) -> str:
    for key, value in types.items():
        if key in project:
            return value
    return ""


ColorStr = Optional[str]


def get_color(project: str) -> ColorStr:
    cron_type = get_type(project)
    return type_to_color.get(cron_type, "bright_cyan")

import json
from pathlib import Path

from characters import Character


def save_character(character: Character, filename):
    data = {"name" : character.name,
            "full_hp": character.full_health,
            "current_hp": character.current_health,
            "base_dmg": character.base_dmg
            }
    Path(filename).write_text(json.dumps(data))
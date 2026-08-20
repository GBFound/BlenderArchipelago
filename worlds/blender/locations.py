from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .world import BlenderWorld

from BaseClasses import Location
from . import items

BASE_ID = 7897897890

# Location IDs need to be unique and greater than 0.
LOCATION_NAME_TO_ID = {}
_PROGRESSIVE_RENDER_RANGE_END = 5

_total_location_ids = 200

_padding = len(str(_total_location_ids))
for i in range(_total_location_ids):
    id = BASE_ID + i
    name = f"Similarity Check {str(i).zfill(_padding)}"
    LOCATION_NAME_TO_ID[name] = id


class BlenderLocation(Location):
    game = "Blender"


def create_locations(world: BlenderWorld) -> None:
    menu = world.get_region("Menu")
    thresholds = world.thresholds
    for i, threshold in enumerate(thresholds):
        name = f"Similarity Check {str(i).zfill(_padding)}"
        id = LOCATION_NAME_TO_ID[name]
        name = f"Similarity {threshold}%"
        menu.add_locations({name: id}, BlenderLocation)


def get_thresholds(world: BlenderWorld) -> list[float]:
    min_percent = world.options.min_percent.value
    max_percent = world.options.max_percent.value
    total_locations = world.options.check_count.value
    interval = (max_percent - min_percent) / (total_locations - 1)

    thresholds = []
    for i in range(total_locations):
        thresholds.append(round(min_percent + interval * i, 3))

    return thresholds

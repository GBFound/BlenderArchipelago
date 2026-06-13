from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .world import BlenderWorld

from BaseClasses import Location
from . import items

BASE_ID = 7897897890

LOCATION_NAME_TO_ID = {}
# Location IDs need to be unique and greater than 0.
for i in range(len(items.ITEM_NAME_TO_CLASSIFICATION)):
    id = BASE_ID + i
    name = f"Similarity Check {i + 1}"
    LOCATION_NAME_TO_ID[name] = id


class BlenderLocation(Location):
    game = "Blender"


def create_locations(world: BlenderWorld) -> None:
    menu = world.get_region("Menu")
    for name, id in world.location_name_to_id.items():
        menu.add_locations({name: id}, BlenderLocation)


def get_thresholds(world: BlenderWorld) -> list[float]:
    min_percent = world.options.min_percent.value
    max_percent = world.options.max_percent.value
    count = len(items.ITEM_NAME_TO_CLASSIFICATION)
    interval = (max_percent - min_percent) / (count - 1)

    thresholds = []
    for i in range(count):
        thresholds.append(round(min_percent + interval * i, 3))

    return thresholds

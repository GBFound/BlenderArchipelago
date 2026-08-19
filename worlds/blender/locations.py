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

_total_location_ids = 0
for item_name in items.ITEM_NAME_TO_CLASSIFICATION:
    if item_name == "Progressive Render Width" or item_name == "Progressive Render Height":
        _total_location_ids += _PROGRESSIVE_RENDER_RANGE_END
    else:
        _total_location_ids += 1

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
    max_w = world.options.progressive_render_width_max
    max_h = world.options.progressive_render_height_max
    missing_items = (2 * _PROGRESSIVE_RENDER_RANGE_END) - (max_w + max_h)
    total_locations = _total_location_ids - missing_items
    interval = (max_percent - min_percent) / (total_locations - 1)

    thresholds = []
    for i in range(total_locations):
        thresholds.append(round(min_percent + interval * i, 3))

    return thresholds

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .world import BlenderWorld

from BaseClasses import Item, ItemClassification

BASE_ID = 7897897890

ITEM_NAME_TO_CLASSIFICATION = {
    "Edit Mode"         : ItemClassification.progression,
    "Sculpt Mode"       : ItemClassification.useful,
    "Vertex Paint Mode" : ItemClassification.useful,
    "Weight Paint Mode" : ItemClassification.useful,
    "Texture Paint Mode": ItemClassification.useful,
    "Materials"         : ItemClassification.progression,
}

ITEM_NAME_TO_ID = {}
for i, name in enumerate(ITEM_NAME_TO_CLASSIFICATION):
    ITEM_NAME_TO_ID[name] = BASE_ID + i


class BlenderItem(Item):
    game = "Blender"


def create_items(world: BlenderWorld) -> None:
    itempool: list[Item] = []
    for name in ITEM_NAME_TO_CLASSIFICATION:
        itempool.append(world.create_item(name))
    world.multiworld.itempool += itempool


def create_item(world: BlenderWorld, name: str) -> None:
    classification = ITEM_NAME_TO_CLASSIFICATION[name]
    id = ITEM_NAME_TO_ID[name]

    return BlenderItem(name, classification, id, world.player)


# TODO
def get_filler_item_name(world: BlenderWorld) -> str:
    return ""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .world import BlenderWorld

from BaseClasses import Item, ItemClassification

BASE_ID = 7897897890

ITEM_NAME_TO_CLASSIFICATION = {
    "Progressive Render Width"  : ItemClassification.progression,
    "Progressive Render Height" : ItemClassification.progression,
    "Edit Mode"                 : ItemClassification.progression,
    "Sculpt Mode"               : ItemClassification.useful,
    "Vertex Paint Mode"         : ItemClassification.useful,
    "Weight Paint Mode"         : ItemClassification.useful,
    "Texture Paint Mode"        : ItemClassification.useful,
    "Grease Pencil Modes"       : ItemClassification.useful,
    "Materials"                 : ItemClassification.progression,
    "Modifiers"                 : ItemClassification.useful,
    "World Shaders"             : ItemClassification.useful,
    "Pop Up"                    : ItemClassification.filler,
    "Undo"                      : ItemClassification.trap,
    "Despair"                   : ItemClassification.trap,
}

ITEM_NAME_TO_ID = {}
for i, name in enumerate(ITEM_NAME_TO_CLASSIFICATION):
    ITEM_NAME_TO_ID[name] = BASE_ID + i

FILLER_AND_TRAP_ITEMS = set()
for name, classification in ITEM_NAME_TO_CLASSIFICATION.items():
    if classification in (ItemClassification.filler, ItemClassification.trap):
        FILLER_AND_TRAP_ITEMS.add(name)


class BlenderItem(Item):
    game = "Blender"


def create_items(world: BlenderWorld) -> None:
    itempool: list[Item] = []
    for name in ITEM_NAME_TO_CLASSIFICATION:
        if name == "Progressive Render Width" or name == "Progressive Render Height":
            for _ in range(3):  # TODO Let YAML customize the number of progressive items
                itempool.append(world.create_item(name))
        else:
            itempool.append(world.create_item(name))
    world.multiworld.itempool += itempool


def create_item(world: BlenderWorld, name: str) -> BlenderItem:
    classification = ITEM_NAME_TO_CLASSIFICATION[name]
    id = ITEM_NAME_TO_ID[name]

    return BlenderItem(name, classification, id, world.player)


# TODO 1 min of use of random unlock
def get_filler_item_name(world: BlenderWorld) -> str:
    random_int = world.random.randint(0, len(FILLER_AND_TRAP_ITEMS) - 1)
    return list(FILLER_AND_TRAP_ITEMS)[random_int]

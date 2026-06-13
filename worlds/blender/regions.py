from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .world import BlenderWorld

from BaseClasses import Region


def create_regions(world: BlenderWorld) -> None:
    menu = Region("Menu", world.player, world.multiworld)
    world.multiworld.regions.append(menu)

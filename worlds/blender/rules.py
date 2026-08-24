from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .world import BlenderWorld

from BaseClasses import CollectionState
from . import locations


def set_rules(world: BlenderWorld) -> None:
    set_all_location_rules(world)
    set_completion_condition(world)
    set_early_items(world)


def set_all_location_rules(world: BlenderWorld) -> None:
    locs = world.multiworld.get_locations(world.player)
    thresholds = world.thresholds
    safety_margin = 0.9
    for loc, threshold in zip(locs, thresholds):
        world.set_rule(
            loc,
            lambda state, threshold=threshold: _calculate_render_percent_available(world, world.player, state) * safety_margin >= threshold
            # Use rule builder instead of lambda?
        )


def set_completion_condition(world: BlenderWorld) -> None:
    world.set_completion_rule(
        lambda state: _calculate_render_percent_available(world, world.player, state) >= world.options.goal_percent
    )


def set_early_items(world: BlenderWorld) -> None: 
    random_int = world.random.randint(0, 1)
    progressive_render_border = "Progressive Render Height"
    if random_int == 0:
        progressive_render_border = "Progressive Render Width"
    world.multiworld.early_items[world.player][progressive_render_border] = 1


def _calculate_render_percent_available(world: "BlenderWorld", player: int, state: CollectionState) -> float:
    w = state.count("Progressive Render Width", player)
    h = state.count("Progressive Render Height", player)
    max_w = world.options.progressive_render_width_max
    max_h = world.options.progressive_render_height_max
    width_fraction = (1 + w) / (1 + max_w)
    height_fraction = (1 + h) / (1 + max_h)
    return min(1, width_fraction) * min(1, height_fraction) * 100

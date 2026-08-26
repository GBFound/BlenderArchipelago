from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .world import BlenderWorld

from BaseClasses import CollectionState

SAFETY_MARGIN = 0.9


def set_rules(world: BlenderWorld) -> None:
    set_all_location_rules(world)
    set_completion_condition(world)
    set_early_items(world)


def set_all_location_rules(world: BlenderWorld) -> None:
    locs = world.multiworld.get_locations(world.player)
    thresholds = world.thresholds
    for loc, threshold in zip(locs, thresholds):
        world.set_rule(
            loc,
            lambda state, threshold=threshold: threshold <= _render_percent_available_from_state(world, world.player, state) * SAFETY_MARGIN 
            # Use rule builder instead of lambda?
        )


def set_completion_condition(world: BlenderWorld) -> None:
    world.set_completion_rule(
        lambda state: world.options.goal_percent <= _render_percent_available_from_state(world, world.player, state) 
    )


def set_early_items(world: BlenderWorld) -> None: 
    random_int = world.random.randint(0, 1)
    progressive_render_border = "Progressive Render Height"
    if random_int == 0:
        progressive_render_border = "Progressive Render Width"
    world.multiworld.early_items[world.player][progressive_render_border] = 1


def render_percent_available(world: BlenderWorld, width: int, height: int) -> float:
    max_width = world.options.progressive_render_width_max
    max_height = world.options.progressive_render_height_max
    width_fraction = (1 + width) / (1 + max_width)
    height_fraction = (1 + height) / (1 + max_height)

    return min(1, width_fraction) * min(1, height_fraction) * 100


def _render_percent_available_from_state(world: BlenderWorld, player: int, state: CollectionState) -> float:
    width = state.count("Progressive Render Width", player)
    height = state.count("Progressive Render Height", player)

    return render_percent_available(world, width, height)

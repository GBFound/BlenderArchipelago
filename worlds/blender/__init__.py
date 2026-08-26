from typing import Any

from worlds.AutoWorld import World
from Options import OptionError
from . import items, locations, regions, rules
from . import options as blender_options  # Rename due to a name conflict with World.options


class BlenderWorld(World):
    game = "Blender"

    options_dataclass = blender_options.BlenderOptions
    options: blender_options.BlenderOptions

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID


    def generate_early(self) -> None:
        self.thresholds = locations.get_thresholds(self)
        if self.options.min_percent.value >= self.options.max_percent.value:
            raise OptionError(
                f"Minimum Similarity Percent ({self.options.min_percent.value}) "
                f"must be lower than Maximum Similarity Percent ({self.options.max_percent.value}). "
                f"Please fix your yaml."
            )
        elif self._is_fill_error_prone():
            raise OptionError(
                f"Progressive Render Width and/or Height Counts are too high. "
                f"This may cause a fill error because there are not enough low similarity checks. "
                f"Please fix your yaml."
            )


    def create_regions(self) -> None:
        regions.create_regions(self)
        locations.create_locations(self)


    def create_items(self) -> None:
        items.create_items(self)


    def set_rules(self) -> None:
        rules.set_rules(self)


    def create_item(self, name: str) -> items.BlenderItem:
        return items.create_item(self, name)
        

    def get_filler_item_name(self) -> str:
        return items.get_filler_item_name(self)


    def fill_slot_data(self) -> dict[str, Any]:
        return {
            "thresholds"                    : self.thresholds,
            "goal_percent"                  : self.options.goal_percent.value,
            "progressive_render_width_max"  : self.options.progressive_render_width_max.value,
            "progressive_render_height_max" : self.options.progressive_render_height_max.value,
            "full_arsenal_duration"         : self.options.full_arsenal_duration.value,
            "death_link"                    : bool(self.options.death_link),
        }

    def _is_fill_error_prone(self) -> bool:
        width = 0
        height = 0
        max_width = self.options.progressive_render_width_max.value
        max_height = self.options.progressive_render_height_max.value
        
        # Grow the larger max dimension first to minimize area growth per step,
        # maximizing the number of steps before the grid is fully filled for worst-case scenario.
        grow_width_first = max_width > max_height

        for threshold in self.thresholds:
            render_percent_available = rules.render_percent_available(self, width, height)
            if threshold > render_percent_available * rules.SAFETY_MARGIN:
                return True
            new_size = self._grow(width, height, max_width, max_height, grow_width_first)
            if new_size is None:
                return False
            width, height = new_size

        return False


    def _grow(self, width: int, height: int, max_width: int, max_height: int, grow_width_first: bool) -> tuple[int, int]:
        if grow_width_first:
            if width < max_width:
                return width + 1, height
            elif height < max_height:
                return width, height + 1
            return None
        else:
            if height < max_height:
                return width, height + 1
            elif width < max_width:
                return width + 1, height
            return None

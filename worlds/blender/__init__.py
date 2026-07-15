from typing import Any

from worlds.AutoWorld import World
from Options import OptionError
from . import items, locations, regions
from . import options as blender_options  # Rename due to a name conflict with World.options


class BlenderWorld(World):
    game = "Blender"

    options_dataclass = blender_options.BlenderOptions
    options: blender_options.BlenderOptions

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID


    def create_regions(self) -> None:
        regions.create_regions(self)
        locations.create_locations(self)


    def create_items(self) -> None:
        items.create_items(self)


    def create_item(self, name: str) -> items.BlenderItem:
        return items.create_item(self, name)


    def fill_slot_data(self) -> dict[str, Any]:
        return {
            "goal_percent": self.options.goal_percent.value,
            "thresholds":   locations.get_thresholds(self),
        }
        

    def get_filler_item_name(self) -> str:
        return items.get_filler_item_name(self)

        
    def generate_early(self) -> None:
        if self.options.min_percent.value >= self.options.max_percent.value:
            raise OptionError(
                f"min_percent ({self.options.min_percent.value}) "
                f"must be lower than max_percent ({self.options.max_percent.value}). "
                f"Please fix your yaml."
            )

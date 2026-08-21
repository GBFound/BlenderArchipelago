from dataclasses import dataclass
from Options import DeathLink, PerGameCommonOptions, Range


class MinPercent(Range):
    """
    Checks will generate at and above this percent.
    """
    display_name = "Minimum Similarity Percent"
    range_start = 0
    range_end = 100
    default = 5


class MaxPercent(Range):
    """
    Checks will generate at and below this percent.
    """
    display_name = "Maximum Similarity Percent"
    range_start = 0
    range_end = 100
    default = 75


class GoalPercent(Range):
    """
    The similarity percentage required to reach the goal.
    """
    display_name = "Goal Similarity Percent"
    range_start = 0
    range_end = 100
    default = 80


# TODO progressive_render_width_max * progressive_render_height_max being too high could be bad but range_end should be higher
class ProgressiveRenderWidthMax(Range):
    """
    The number of Progressive Render Width items in the item pool.
    More items means each one expands your render border by a smaller amount, making it more difficult.
    """
    display_name = "Progressive Render Width Count"
    range_start = 0
    range_end = 3
    default = 2


# TODO progressive_render_width_max * progressive_render_height_max being too high could be bad but range_end should be higher
class ProgressiveRenderHeightMax(Range):
    """
    The number of Progressive Render Height items in the item pool.
    More items means each one expands your render border by a smaller amount, making it more difficult.
    """
    display_name = "Progressive Render Height Count"
    range_start = 0
    range_end = 3
    default = 2


class CheckCount(Range):
    """
    The number of checks that will be available.
    """
    display_name = "Check Count"
    range_start = 20
    range_end = 200
    default = 35


class TrapCount(Range):
    """
    Sets the percentage of filler items to be replaced by random traps.
    """
    display_name = "Trap Fill Percent"
    range_start = 0
    range_end = 100
    default = 50


@dataclass
class BlenderOptions(PerGameCommonOptions):
    min_percent                     : MinPercent
    max_percent                     : MaxPercent
    goal_percent                    : GoalPercent
    progressive_render_width_max    : ProgressiveRenderWidthMax
    progressive_render_height_max   : ProgressiveRenderHeightMax
    check_count                     : CheckCount
    trap_count                      : TrapCount
    death_link                      : DeathLink

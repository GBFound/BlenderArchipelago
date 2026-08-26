from dataclasses import dataclass
from Options import DeathLink, DefaultOnToggle, PerGameCommonOptions, Range


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


class ProgressiveRenderWidthMax(Range):
    """
    The number of Progressive Render Width items in the item pool.
    More items means each one expands your render border by a smaller amount, making it more difficult.
    """
    display_name = "Progressive Render Width Count"
    range_start = 0
    range_end = 5
    default = 2


class ProgressiveRenderHeightMax(Range):
    """
    The number of Progressive Render Height items in the item pool.
    More items means each one expands your render border by a smaller amount, making it more difficult.
    """
    display_name = "Progressive Render Height Count"
    range_start = 0
    range_end = 5
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
    The percentage of filler items to be replaced by random traps.
    """
    display_name = "Trap Fill Percent"
    range_start = 0
    range_end = 100
    default = 25


class FullArsenalDuration(Range):
    """
    The number of seconds full arsenal will last for.
    Receiving the full arsenal item will remove all tool restrictions, as if every tool was unlocked.
    """
    display_name = "Full Arsenal Duration"
    range_start = 10
    range_end = 300
    default = 60


class Despair(DefaultOnToggle):
    """
    Enables the despair item.
    If disabled, the item will instead be undo traps.
    """
    display_name = "Despair"


class BlenderDeathLink(DeathLink):
    """
    When you undo/redo, everyone with deathlink dies.
    When someone with deathlink dies, you will undo to the furthest undo in history.
    Blender's default setting is 32 undos max in history.
    Setting is in Edit -> Preferences -> System -> Memory & Limits -> Undo Steps
    """


@dataclass
class BlenderOptions(PerGameCommonOptions):
    min_percent                   : MinPercent
    max_percent                   : MaxPercent
    goal_percent                  : GoalPercent
    progressive_render_width_max  : ProgressiveRenderWidthMax
    progressive_render_height_max : ProgressiveRenderHeightMax
    check_count                   : CheckCount
    trap_count                    : TrapCount
    full_arsenal_duration         : FullArsenalDuration
    despair                       : Despair
    death_link                    : BlenderDeathLink

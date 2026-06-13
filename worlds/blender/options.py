from dataclasses import dataclass
from Options import PerGameCommonOptions, Range


class MinPercent(Range):
    """
    Checks will generate at and above this percent.
    """
    display_name = "Minimum Similarity Percent"
    range_start = 0
    range_end = 100
    default = 20


class MaxPercent(Range):
    """
    Checks will generate at and below this percent.
    """
    display_name = "Maximum Similarity Percent"
    range_start = 0
    range_end = 100
    default = 50


class GoalPercent(Range):
    """
    The similarity percentage required to reach the goal.
    """
    display_name = "Goal Similarity Percent"
    range_start = 0
    range_end = 100
    default = 50


@dataclass
class BlenderOptions(PerGameCommonOptions):
    min_percent: MinPercent
    max_percent: MaxPercent
    goal_percent: GoalPercent

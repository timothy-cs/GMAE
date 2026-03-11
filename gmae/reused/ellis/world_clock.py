"""WorldClock — reused from Ellis's individual GuildQuest assignment.

Central clock for tracking and advancing world time.
Adapted for GMAE: integrates with GameSession for turn-based time advancement.
"""

from __future__ import annotations
from gmae.reused.ellis.world_time import WorldTime


class WorldClock:
    def __init__(self, start_time: WorldTime | None = None):
        self.current_time = start_time or WorldTime(0, 6, 0)  # Default: Day 0, 06:00

    def compare(self, t1: WorldTime, t2: WorldTime) -> int:
        m1 = t1.to_total_minutes()
        m2 = t2.to_total_minutes()
        if m1 < m2:
            return -1
        elif m1 > m2:
            return 1
        return 0

    def add_minutes(self, time: WorldTime, minutes: int) -> WorldTime:
        total = time.to_total_minutes() + minutes
        return WorldTime.from_total_minutes(max(0, total))

    def advance(self, minutes: int = 10) -> None:
        self.current_time = self.add_minutes(self.current_time, minutes)

    def __str__(self) -> str:
        return f"WorldClock @ {self.current_time}"

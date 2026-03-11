"""
WorldClock — GuildQuest subsystem (Reused from GuildQuest Part 1).

Tracks game time in days, hours, and minutes using a universal internal
clock representation used for storage and ordering of events.

Reuse source : Ethan Votran — GuildQuest Part 1
Used by      : Realm (local time conversion), QuestEvent (time windows),
               EscortQuest (turn/time tracking), GMAE_Engine (global clock)
"""


class WorldClock:
    """Universal game clock that tracks time in days, hours, and minutes."""

    MINUTES_PER_HOUR: int = 60
    HOURS_PER_DAY: int = 24
    MINUTES_PER_DAY: int = MINUTES_PER_HOUR * HOURS_PER_DAY

    def __init__(self, total_minutes: int = 0, time_scale: int = 1):
        """
        Args:
            total_minutes: Absolute time value in minutes.
            time_scale:    How many in-game minutes pass per tick() call.
        """
        self.total_minutes: int = max(0, total_minutes)
        self.time_scale: int = time_scale

    # ------------------------------------------------------------------
    # Time component accessors
    # ------------------------------------------------------------------

    @property
    def days(self) -> int:
        return self.total_minutes // self.MINUTES_PER_DAY

    @property
    def hours(self) -> int:
        return (self.total_minutes % self.MINUTES_PER_DAY) // self.MINUTES_PER_HOUR

    @property
    def minutes(self) -> int:
        return self.total_minutes % self.MINUTES_PER_HOUR

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def tick(self, mins: int = 1) -> None:
        """Advance the clock by mins * time_scale minutes."""
        self.total_minutes += mins * self.time_scale

    # ------------------------------------------------------------------
    # Comparison operators
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WorldClock):
            return NotImplemented
        return self.total_minutes == other.total_minutes

    def __lt__(self, other: "WorldClock") -> bool:
        return self.total_minutes < other.total_minutes

    def __le__(self, other: "WorldClock") -> bool:
        return self.total_minutes <= other.total_minutes

    def __gt__(self, other: "WorldClock") -> bool:
        return self.total_minutes > other.total_minutes

    def __ge__(self, other: "WorldClock") -> bool:
        return self.total_minutes >= other.total_minutes

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return f"Day {self.days}, {self.hours:02d}:{self.minutes:02d}"

    def __repr__(self) -> str:
        return f"WorldClock(total_minutes={self.total_minutes})"

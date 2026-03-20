"""Enumerations used throughout the GMAE."""

from enum import Enum


class VisibilityType(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class PermissionLevel(Enum):
    VIEW_ONLY = "VIEW_ONLY"
    COLLABORATIVE = "COLLABORATIVE"


class ThemeType(Enum):
    CLASSIC = "CLASSIC"
    MODERN = "MODERN"


class RarityType(Enum):
    COMMON = "COMMON"
    RARE = "RARE"
    ULTRA_RARE = "ULTRA_RARE"
    LEGENDARY = "LEGENDARY"


class AdventureStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    WIN = "WIN"
    LOSE = "LOSE"
    DRAW = "DRAW"

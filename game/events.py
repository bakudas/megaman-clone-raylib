# game/events.py
from enum import Enum, auto


class GameEvent(Enum):
    PLAYER_JUMPED = auto()
    PLAYER_LANDED = auto()
    PLAYER_SHOT = auto()
    PLAYER_SHOT_CHARGED = auto()
    PLAYER_HURT = auto()
    PLAYER_DESTROYED = auto()
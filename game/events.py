# game/events.py
from enum import Enum, auto


class PlayerEvent(Enum):
    PLAYER_JUMPED = auto()
    PLAYER_LANDED = auto()
    PLAYER_SHOT = auto()
    PLAYER_SHOT_CHARGED = auto()
    PLAYER_HURT = auto()
    PLAYER_DIED = auto()
    PLAYER_DESTROYED = auto()
    PLAYER_HEALED = auto()
    PLAYER_WANTS_TO_SHOOT = auto()
    PLAYER_RESPAWNED = auto()
    WEAPON_CHARGE_START = auto()
    WEAPON_CHARGE_COMPLETE = auto()


class EnemyEvent(Enum):
    ENEMY_DESTROYED = auto()
    ENEMY_HURT = auto()


class SystemEvent(Enum):
    PLAYER_DIED_EVENT = auto()
    COLLISION = auto()

class GameEvent(Enum):
    NO_LIVES_REMAINING = auto()
    PLAYING = auto()
    PLAYER_DIED = auto()  # <<< Novo estado
    GAME_OVER = auto()


class InputEvent(Enum):
    ACTION = auto()
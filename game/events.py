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
    PLAYER_RESPAWNED = auto()


class EnemyEvent(Enum):
    ENEMY_DESTROYED = auto()

class GameEvent(Enum):
    NO_LIVES_REMAINING = auto()
    PLAYING = auto()
    PLAYER_DIED = auto()  # <<< Novo estado
    GAME_OVER = auto()
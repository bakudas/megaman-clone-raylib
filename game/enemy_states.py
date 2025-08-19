# game/enemy_states.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.enemy import Enemy

class EnemyState(ABC):
    """
    Classe base para os estados do inimigo
    """
    def __str__(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def update(self, enemy: Enemy, world_state: dict, delta_time: float) -> None:
        pass

# --- Estados Concretos ---

class PatrollingState(EnemyState):
    """
    O inimigo deve se mover numa direção até encontrar uma beirada
    """
    def __init__(self, enemy: Enemy) -> None:
        # define a velocidade inicial baseada na direção
        enemy.x_vel = enemy.speed if enemy.facing_direction == "RIGHT" else -enemy.speed

    def update(self, enemy: Enemy, world_state: dict, delta_time: float) -> None:
        # usa o sensor is_ground_ahead para checar a plataforma
        if not enemy.is_ground_ahead(world_state):
            # se não tiver chão, vire
            enemy.change_state_locomotion(TurningState(enemy))

class TurningState(EnemyState):
    """
    O inimigo para, inverte a sua direção e volta a patrulhar
    """
    def __init__(self, enemy: Enemy) -> None:
        # para
        enemy.x_vel = 0

        # inverte a direção
        enemy.facing_direction = "RIGHT" if enemy.facing_direction == "LEFT" else "LEFT"

    def update(self, enemy: Enemy, world_state: dict, delta_time: float) -> None:
        # transição para patrulhar novamente
        # TODO: animação de virada
        enemy.change_state_locomotion(PatrollingState(enemy))

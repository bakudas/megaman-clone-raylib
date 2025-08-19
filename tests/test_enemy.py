# test/test_enemy.py
import pytest

from game.enemy import Enemy
from game.enemy_states import EnemyState, PatrollingState, TurningState
from game.platforms import Platform

def test_patrolling_enemy_turns_at_ledge(patrolling_enemy, world_state):
    # Given: Dado um inimigo no estado de Patrolling
    # posicionado exatamente na beirada esquerda da plataforma
    # indo em direção da borda
    patrolling_enemy.x = 50
    patrolling_enemy.y = 100
    patrolling_enemy.facing_direction = "LEFT"
    patrolling_enemy.ai_state = PatrollingState(patrolling_enemy)
    assert isinstance(patrolling_enemy.ai_state, PatrollingState)

    # When: Quando o inimigo é atualizado
    patrolling_enemy.update(world_state, delta_time=0.016)

    assert patrolling_enemy.facing_direction == "RIGHT"
    assert patrolling_enemy.x_vel > 0




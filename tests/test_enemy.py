# test/test_enemy.py
import pytest
from unittest.mock import Mock

from game.enemy import Enemy
from game.enemy_states import EnemyState, PatrollingState, TurningState
from game.platforms import Platform
from game.events import GameEvent


def test_patrolling_enemy_turns_at_ledge(patrolling_enemy, world_state):
    # Given: Dado um inimigo no estado de Patrolling
    # posicionado na beirada esquerda de uma plataforma,
    # indo em direção à borda.
    platform = world_state["platforms"][2]  # A plataforma em (50, 150)
    patrolling_enemy.x_pos = platform.x  # Exatamente na beirada
    patrolling_enemy.y_pos = platform.y - patrolling_enemy.height  # Em cima da plataforma
    patrolling_enemy.facing_direction = "LEFT"
    patrolling_enemy.change_state_locomotion(PatrollingState(patrolling_enemy))  # Garante o estado e velocidade inicial
    assert isinstance(patrolling_enemy.ai_state, PatrollingState)
    assert patrolling_enemy.x_vel < 0

    # When: Quando o inimigo é atualizado
    patrolling_enemy.update(world_state, delta_time=0.016)

    # Then: ele deve ter virado para a direita e começado a se mover
    # A transição é Patrolling -> Turning
    assert isinstance(patrolling_enemy.ai_state, TurningState)
    assert patrolling_enemy.facing_direction == "RIGHT"
    assert patrolling_enemy.x_vel == 0


def test_enemy_takes_damage(patrolling_enemy, world_state):
    # Given: um inimigo com vida cheia
    initial_health = patrolling_enemy.health
    assert patrolling_enemy.is_flashing is False

    # When: ele toma dano
    patrolling_enemy.take_damage(1, world_state)

    # Then: sua vida diminui e ele pisca
    assert patrolling_enemy.health == initial_health - 1
    assert patrolling_enemy.is_flashing is True


def test_enemy_is_destroyed_when_health_reaches_zero(patrolling_enemy, world_state):
    # Given: um inimigo com 1 de vida
    patrolling_enemy.health = 1
    assert patrolling_enemy.is_destroyed is False

    # When: ele toma 1 de dano
    patrolling_enemy.take_damage(1, world_state)

    # Then: ele é marcado como destruído
    assert patrolling_enemy.health == 0
    assert patrolling_enemy.is_destroyed is True


def test_enemy_notifies_observers_on_death(patrolling_enemy, world_state):
    # Given: um inimigo com um observador mock
    mock_observer = Mock()
    patrolling_enemy.add_observer(mock_observer)
    patrolling_enemy.health = 1

    # When: o inimigo é destruído
    patrolling_enemy.take_damage(1, world_state)

    # Then: o observador é notificado com o evento correto e os dados do inimigo
    mock_observer.on_notify.assert_called_once_with(
        GameEvent.ENEMY_DESTROYED, enemy=patrolling_enemy
    )

# tests/test_interactions.py
import pytest
import random
from unittest.mock import Mock

from game.player import Player
from game.enemy import Enemy
from game.hazards import Hazard
from game.pickup import Pickup
from game.bullet import Bullet
from game.game_event_handler import GameEventHandler


def test_player_is_destroyed_by_hazard(player, hazard, world_state):
    # Given: um jogador e um hazard no mundo
    player.x_pos = hazard.x
    player.y_pos = hazard.y
    world_state["hazards"].append(hazard)
    assert player.is_destroyed is False

    # When: o jogador colide com o hazard (simulado pela lógica do loop principal)
    player.destroy()

    # Then: o jogador é marcado como destruído
    assert player.is_destroyed is True
    assert player.health == 0


def test_player_heals_by_collecting_pickup(player, pickup, world_state):
    # Given: um jogador com vida faltando e um pickup no mundo
    player.health = 10
    world_state["pickups"].append(pickup)

    # When: o jogador colide com o pickup (simulado pela lógica do loop principal)
    player.heal(pickup.heal_amount)

    # Then: a vida do jogador aumenta
    assert player.health == 10 + pickup.heal_amount


def test_player_cannot_overheal(player, pickup, world_state):
    # Given: um jogador com vida quase cheia
    player.health = player.max_health - 1
    world_state["pickups"].append(pickup)

    # When: o jogador coleta um pickup
    player.heal(pickup.heal_amount)

    # Then: a vida do jogador é limitada ao máximo
    assert player.health == player.max_health


def test_enemy_destruction_spawns_pickup(world_state):
    # Given: um GameEventHandler, um inimigo prestes a morrer e uma taxa de drop de 100%
    event_handler = GameEventHandler(world_state)
    enemy = Enemy(x=100, y=100)
    enemy.add_observer(event_handler)
    enemy.drop_rate = 1.0  # Garante o drop
    assert len(world_state["pickups"]) == 0

    # When: o inimigo é destruído e notifica o handler
    enemy.take_damage(enemy.health, world_state)  # Dano letal

    # Then: um pickup é adicionado ao mundo
    assert len(world_state["pickups"]) == 1
    assert isinstance(world_state["pickups"][0], Pickup)
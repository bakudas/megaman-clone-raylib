# tests/test_player.py

import pytest
from game.player import Player


@pytest.fixture
def new_player():
    """
    Esta fixture cria e retorna uma instância
    padrão do Player para ser usada nos testes.
    """
    return Player(x=100, y=200, width=40, height=50, speed=5, jump_strength=15)


def test_player_inicialization(new_player):
    # 1. Arrange
    # (Given) Dado a inicialização do level
    # Não precisamos de configurações adicionais para o level

    # 2. Act
    # (When) Quando o nível é inicializado

    # 3. Assert
    # (Then)
    assert new_player.x_pos == 100
    assert new_player.y_pos == 200
    assert new_player.width == 40
    assert new_player.height == 50
    assert new_player.speed == 5
    assert new_player.jump_strength == 15
    assert new_player.x_vel == 0
    assert new_player.y_vel == 0


def test_player_facing_direction_defaults_right(new_player):
    # 3. Assert
    # (Then) Então o player por padrão na criação deve estar virado para a direita
    assert new_player.facing_direction == "RIGHT"


def test_player_bottom_property(new_player):
    # 3. Assert
    # (Then) Então a propriedade bottom retorna a base do jogador
    assert new_player.bottom == 250  # 200 (y_pos) + 50 (height)

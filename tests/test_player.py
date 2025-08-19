# tests/test_player.py
import pytest

from game.player import Player
from game.player_state import (
    IdleState,
    JumpingState,
    JumpingState,
    FallingState,
    WallSlidingState,
    DashState,
)


def test_player_inicialization(player):
    # 1. Arrange
    # (Given) Dado a inicialização do level
    # Não precisamos de configurações adicionais para o level

    # 2. Act
    # (When) Quando o nível é inicializado

    # 3. Assert
    # (Then)
    assert player.x_pos == 100
    assert player.y_pos == 100
    assert player.width == 40
    assert player.height == 50
    assert player.speed == 5
    assert player.jump_strength == 15
    assert player.x_vel == 0
    assert player.y_vel == 0


def test_player_facing_direction_defaults_right(player):
    # 3. Assert
    # (Then) Então o player por padrão na criação deve estar virado para a direita
    assert player.facing_direction == "RIGHT"


def test_player_bottom_property(player):
    player.y_pos = 200

    # 3. Assert
    # (Then) Então a propriedade bottom retorna a base do jogador
    assert player.bottom == 250  # 200 (y_pos) + 50 (height)


def test_jump_input_from_idle_changes_state_to_jumping(player, world_state):
    # Arrange (Dado)
    # Forçamos o jogador a estar no chão e no estado Idle (o fixture já faz isso)
    player.y_pos = 350  # Posição exata no chão da fixture
    assert isinstance(player.locomotion_state, IdleState)
    assert player.is_on_ground(world_state) is True

    # Act (Quando)
    player.handle_input("JUMP")

    # Assert (Então)
    assert isinstance(player.locomotion_state, JumpingState)
    assert player.y_vel == -player.jump_strength  # A ação de pular foi executada


def test_jumping_player_transitions_to_falling_at_jump_apex(player):
    # Arrange (Dado)
    # Forçamos o jogador para o estado de pulo e com velocidade quase nula
    player.change_locomotion_state(JumpingState())
    player.y_vel = -0.1  # Quase no pico
    assert isinstance(player.locomotion_state, JumpingState)

    # Act (Quando)
    # Simulamos um frame de física que o faz começar a cair
    player.y_vel += 0.2  # Agora y_vel é 0.1 (positivo)
    player.locomotion_state.update(player, {}, 0.0)  # Chamamos o update do estado

    # Assert (Então)
    assert isinstance(player.locomotion_state, FallingState)


def test_wall_jump_action_and_transition(player):
    # Arrange (Dado)
    # Forçamos o jogador para o estado de deslizar na parede
    player.change_locomotion_state(WallSlidingState(player))
    player.facing_direction = "RIGHT"  # Simulando estar na parede da direita
    assert isinstance(player.locomotion_state, WallSlidingState)

    # Act (Quando)
    player.handle_input("JUMP")

    # Assert (Então)
    # 1. A transição de estado ocorreu
    assert isinstance(player.locomotion_state, JumpingState)
    # 2. A ação (wall_jump) foi executada corretamente
    assert player.y_vel < 0  # Pulou para cima
    assert player.x_vel < 0  # Pulou para longe (esquerda) da parede


def test_can_dash_from_idle_state(player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador parado no chão
    player.change_locomotion_state(IdleState(player))  # troca o estado para idle
    assert isinstance(player.locomotion_state, IdleState)  # checa se está em idle

    # 2. Act
    # (When) Quando o input 'DASH' é ativado
    player.handle_input("DASH")

    # 3. Assert
    # (Then) Então o jogador deve estar no estado DashState
    # e sua velocidade em x_vel deve ser diferente de 0.
    assert isinstance(player.locomotion_state, DashState)
    assert player.x_vel != 0
    assert player.x_vel == player.dash_speed


def test_cannot_dash_in_mid_air(player):
    # 1. Arrange
    # (Given) Dado o jogador pulando
    player.change_locomotion_state(JumpingState())
    assert isinstance(player.locomotion_state, JumpingState)

    # 2. Act
    # (When) Quando o input "DASH" é ativado
    player.handle_input("DASH")

    # 3. Assert
    # (Then) Então o estão NÃO deve mudar
    assert isinstance(player.locomotion_state, JumpingState)


def test_dashing_state_reverts_to_idle_after_duration(player, world_state):
    # 1. Arrange
    # (Given) Dado o jogador no estado DashState
    player.change_locomotion_state(DashState(player))
    assert isinstance(player.locomotion_state, DashState)
    delta_time = 1

    # 2. Act
    # (When) Quando a duração do dash acaba
    player.dash_duration = 0
    player.update(world_state, delta_time)

    # 3. Assert
    # (Then) Então o estado do jogador deve mudar para IdleState
    assert isinstance(player.locomotion_state, IdleState)

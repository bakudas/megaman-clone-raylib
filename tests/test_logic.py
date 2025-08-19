# tests/test_logic.py
import pytest

from game.player_state import (
    FallingState,
    WallSlidingState,
    RunningState,
    IdleState,
    JumpingState,
)
from game.player import Player
from game.platforms import Platform


# --- Testes de Lógica de Estado e Input ---


def test_move_right_input_changes_state_to_running_and_sets_velocity(player):
    # Given: um jogador parado no chão
    player.change_locomotion_state(IdleState(player))

    # When: o input "direita" é processado
    player.handle_input("RIGHT")

    # Then: o estado muda para Running e a velocidade e direção são definidas
    assert isinstance(player.locomotion_state, RunningState)
    assert player.x_vel == player.speed
    assert player.facing_direction == "RIGHT"


def test_move_left_input_changes_state_to_running_and_sets_velocity(player):
    # Given: um jogador parado no chão
    player.change_locomotion_state(IdleState(player))

    # When: o input "esquerda" é processado
    player.handle_input("LEFT")

    # Then: o estado muda para Running e a velocidade e direção são definidas
    assert isinstance(player.locomotion_state, RunningState)
    assert player.x_vel == -player.speed
    assert player.facing_direction == "LEFT"


def test_stop_input_changes_state_to_idle(player):
    # Given: um jogador correndo
    player.change_locomotion_state(RunningState())

    # When: o input "parar" é processado
    player.handle_input("STOP")

    # Then: o estado muda para Idle e a velocidade horizontal é zerada
    assert isinstance(player.locomotion_state, IdleState)
    assert player.x_vel == 0


def test_jump_input_while_idle_changes_state_and_applies_velocity(player):
    # Given: um jogador parado no chão
    player.change_locomotion_state(IdleState(player))
    player.y_vel = 0

    # When: o input "pulo" é processado
    player.handle_input("JUMP")

    # Then: o estado muda para Jumping e a velocidade vertical é aplicada
    assert isinstance(player.locomotion_state, JumpingState)
    assert player.y_vel == -player.jump_strength


def test_jump_input_is_ignored_when_falling(player):
    # Given: um jogador caindo
    player.change_locomotion_state(FallingState())
    initial_y_vel = 5
    player.y_vel = initial_y_vel

    # When: o input "pulo" é processado
    player.handle_input("JUMP")

    # Then: o estado e a velocidade vertical não mudam
    assert isinstance(player.locomotion_state, FallingState)
    assert player.y_vel == initial_y_vel


# --- Testes de Física Vertical ---


def test_gravity_increases_vertical_velocity(player, world_state):
    # Given: um jogador no ar, parado verticalmente
    player.y_pos = 100
    player.y_vel = 0

    # When: a física vertical é aplicada
    player._apply_vertical_physics(world_state)

    # Then: a velocidade vertical aumenta devido à gravidade
    assert player.y_vel == world_state["gravity"]


def test_player_lands_on_solid_platform(player, world_state):
    # Given: um jogador caindo em direção a uma plataforma sólida
    player.x_pos = 80
    player.y_pos = 195  # Acima da plataforma para garantir que a colisão ocorra de cima
    player.y_vel = 10  # Caindo
    platform = world_state["platforms"][0]
    platform.x, platform.y, platform.p_type = 80, 250, "solid"

    # When: a física vertical é aplicada
    player._apply_vertical_physics(world_state)

    # Then: o jogador para exatamente em cima da plataforma
    assert player.y_pos == platform.y - player.height
    assert player.y_vel == 0


def test_player_jumps_through_passthrough_platform(player, world_state):
    # Given: um jogador pulando por baixo de uma plataforma pass-through
    player.x_pos = 100
    player.y_pos = 260
    player.y_vel = -10  # Pulando
    platform = world_state["platforms"][0]
    platform.x, platform.y, platform.p_type = 80, 250, "pass-through"

    # When: a física vertical é aplicada
    player._apply_vertical_physics(world_state)

    # Then: o jogador não colide e continua subindo (afetado pela gravidade)
    assert player.y_pos == 250  # 260 (y_pos) + -10 (y_vel)
    assert player.y_vel == -10 + world_state["gravity"]


def test_player_collides_with_bottom_of_solid_platform(player, world_state):
    # Given: um jogador pulando em direção ao fundo de uma plataforma
    player.x_pos = 100
    player.y_pos = 275 # Abaixo da plataforma
    player.y_vel = -10  # Pulando
    platform = world_state["platforms"][0]
    platform.x, platform.y, platform.height, platform.p_type = 80, 250, 20, "solid"

    # When: a física vertical é aplicada
    player._apply_vertical_physics(world_state)

    # Then: o jogador para no fundo da plataforma e sua velocidade de subida é zerada
    assert player.y_pos == platform.y + platform.height
    assert player.y_vel == 0


# --- Testes de Física Horizontal e Wall Slide ---


def test_player_starts_wall_sliding_when_touching_wall_in_air(player, world_state):
    # Given: um jogador no ar, se movendo em direção a uma parede
    player.x_pos = 175
    player.y_pos = 100
    player.x_vel = 10  # Movendo para a direita
    player.y_vel = 1  # Caindo
    wall = world_state["platforms"][0]
    wall.x, wall.y, wall.width, wall.height, wall.p_type = 180, 80, 20, 100, "solid"

    # When: a física horizontal é aplicada
    player._apply_horizontal_physics(world_state, 0.0)

    # Then: o jogador para de se mover horizontalmente e o estado de wall slide é ativado
    assert player.is_wall_sliding is True
    assert player.x_pos == wall.x - player.width
    assert player.x_vel == 0


def test_wall_sliding_reduces_gravity_effect(player, world_state):
    # Given: um jogador em estado de wall slide, caindo e com input na direção da parede
    player.is_wall_sliding = True
    player.horizontal_input_active = True # Essencial para a gravidade reduzida
    player.y_vel = 1 # Caindo

    # When: a física vertical é aplicada
    player._apply_vertical_physics(world_state)

    # Then: a velocidade de queda é a de slide, não a normal
    assert player.y_vel == 1 + player.wall_slide_gravity


def test_wall_jump_propels_player_up_and_away(player, world_state):
    # Given: um jogador em estado de wall slide na parede direita
    player.change_locomotion_state(WallSlidingState(player))
    player.facing_direction = "RIGHT" # Virado para a parede

    # When: o input de pulo é processado
    player.handle_input("JUMP")

    # Then: o jogador deve pular para cima e para longe da parede
    assert player.y_vel < 0
    assert player.x_vel < 0  # Longe da parede (para a esquerda)
    assert player.x_vel == -player.wall_jump_x_velocity


# --- Testes de Ações ---


def test_shoot_bullet_moves_right_when_facing_right(player, world_state):
    # Given: um jogador virado para a direita
    player.facing_direction = "RIGHT"

    # When: o jogador atira
    player.fire_normal_shot(world_state)

    # Then: uma bala é criada se movendo para a direita
    assert len(world_state['bullets']) == 1
    bullet = world_state['bullets'][0]
    assert bullet.x_vel > 0


def test_shoot_bullet_moves_left_when_facing_left(player, world_state):
    # Given: um jogador virado para a esquerda
    player.facing_direction = "LEFT"

    # When: o jogador atira
    player.fire_normal_shot(world_state)

    # Then: uma bala é criada se movendo para a esquerda
    assert len(world_state['bullets']) == 1
    bullet = world_state['bullets'][0]
    assert bullet.x_vel < 0

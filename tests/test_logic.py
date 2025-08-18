# tests/test_logic.py
import pytest

from game.player_state import FallingState, WallSlidingState
from game.player import Player
from game.platforms import Platform
from game.logic import (
    shoot,
)


def test_gravity_increase_vertical_velocity(player, world_state):
    # 1. Arrange (Preparar)
    # (Given) Dado um jogador que começa no ar (y=100) e parado (y_vel=0).
    player.x_pos = 100
    player.y_vel = 0

    # 2. Act (agir)
    # A 'física' do jogo acontece aqui
    # A velocidade vertical deve ser afetada pela gravida
    player.update(world_state)

    # 3. Assert (Verificar)
    # Verificamos se a velocidade vertical é maior que zero
    assert player.y_vel > 0


def test_velocity_updates_position(player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador parado
    player.x_pos = 200
    player.y_pos = 100
    player.y_vel = 10
    player.x_vel += player.speed

    # 2. Act
    # (When) Quando a física é aplicada
    player.update(world_state)

    # 3. Assert
    # (Then) Então o jogador dever ser mover de acordo com as velocidades em x (x_vel) e y (y_vel)
    assert player.y_pos == 110  # 100 (y_pos) + 10 (y_vel)
    assert player.x_pos == 205  # 200 (x_pos) + 5 (speed)


def test_move_right_input_sets_positive_horizontal_velocity(player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador parado horizontalmente
    player.x_pos = 200
    player.y_pos = 390
    player.x_vel = 0

    # 2. Act
    # (When) Quando o input "direita" é processo
    player.handle_input("RIGHT")

    # 3. Assert
    # (Then) Então a velocidade horizontal deve ser positiva
    assert player.x_vel > 0
    assert player.x_vel == 5


def test_move_left_input_sets_negative_horizontal_velocity(player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador parado
    player.x_pos = 200
    player.y_pos = 390
    player.x_vel = 0

    # 2. Act
    # (When) Quando o input "direita" é processo
    player.handle_input("LEFT")

    # 3. Assert
    # (Then) Então a velocidade horizontal deve ser negativa
    assert player.x_vel < 0
    assert player.x_vel == -5


def test_player_jumps_from_a_platform(player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador no chão
    # y=350 significa que player.bottom está em 400, exatamente sob a plataforma
    # x=80 significa que o jogador está alinhado horizontalmente com a plataforma
    player.x_pos = 80
    player.y_pos = 350
    player.y_vel = 0  # parado verticalmente
    player.jump_strength = 15  # força do pulo

    # 2. Act
    # (When) quando o input "JUMP" é processado
    player.handle_input("JUMP")

    # 3. Assert
    # (Then) Então a velocidade vertical do jogador deve ser negativa (para cima)
    assert player.y_vel < 0
    assert player.y_vel == -player.jump_strength


def test_player_cannot_jump_in_mid_air(player, world_state):
    # Given (Dado) um jogador no ar
    player.y_vel = 5  # Caindo
    player.change_state(FallingState())

    # When (Quando) o input "JUMP" é processado
    player.handle_input("JUMP")
    player.update(world_state)

    # Then (Então) a velocidade vertical NÃO deve mudar
    assert player.y_vel == 6  # 5 (player.y_vel) + 1 (gravidade)


def test_moving_right_updates_facing_direction(player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador

    # 2. Act
    # (When) Quando o input "RIGHT" é processdo
    player.handle_input("RIGHT")
    player.update(world_state)  # world_state não é necessário aqui

    # 3. Assert
    # (Then) Então a direção deve ser "RIGHT"
    assert player.facing_direction == "RIGHT"


def test_moving_left_updates_facing_direction(player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador

    # 2. Act
    # (When) Quando o input "LEFT" é processdao
    player.handle_input("LEFT")
    player.update(world_state)  # world_state não é necessário aqui

    # 3. Assert
    # (Then) Então a direção deve ser "LEFT"
    assert player.facing_direction == "LEFT"


def test_shoot_bullet_moving_in_player_direction(player):
    # 1. Arrange
    # (Given) Dado um jogador virado para a direita
    player.facing_direction = "RIGHT"
    bullet_speed = 10

    # 2. Act
    # (When) Quando o jogador atira
    bullet = shoot(player, bullet_speed)

    # 3. Assert
    # (Then) Então a bala deve se mover para a direita
    assert bullet.x_vel > 0

    # 1. Arrang
    # (Given) Dado um jogador virado para a esquerda
    player.facing_direction = "LEFT"

    # 2. Act
    # (When) Quando o jogador atira
    bullet = shoot(player, bullet_speed)

    # 3. Assert
    # (Then) Então a bala deve se mover para a direita
    assert bullet.x_vel < 0


def test_player_lands_on_solid_platform(player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador caindo em direção a uma plataforma sólida
    player.x_pos = 80
    player.y_pos = 195
    player.y_vel = 10  # caindo
    world_state["platforms"][0].x = 80
    world_state["platforms"][0].y = 250
    world_state["platforms"][0].p_type = "solid"

    # 2. Act
    # (When) Quando a física é aplicada
    player.update(world_state)

    # 3. Assert
    # (Then) Então o jogador de parar exatamente em cima da plataforma
    assert player.y_pos == 200  # 250 (topo da plataforma) - 50 (altura do player)
    assert player.y_vel == 0


def test_player_jumps_through_passthrough_platform(player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador pulando por baixo de uma plataforma pass-through
    player.x_pos = 100
    player.y_pos = 260
    player.y_vel = -10  # pulando
    world_state["platforms"][0].x = 80
    world_state["platforms"][0].y = 250
    world_state["platforms"][0].p_type = "pass-through"

    # 2. Act
    # (When) Quando a física é aplicada
    player.update(world_state)

    # 3. Assert
    # (Then) Então o jogador NÃO deve colidir e deve continuar subindo (afetado pela gravidade)
    assert player.y_pos == 250  # 260 (player.y_pos) - 10 (player.y_vel)
    assert player.y_vel == -9  # -10 + 1 (gravidade)


def test_player_lands_on_passthrough_platform(player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador caindo em direção a uma plataforma pass-through
    player.x_pos = 100
    player.y_pos = 195
    player.y_vel = 10  # caindo
    world_state["platforms"][0].x = 80
    world_state["platforms"][0].y = 250
    world_state["platforms"][0].p_type = "pass-through"

    # 2. Act
    # (When) Quando a física é aplicada
    player.update(world_state)

    # 3. Assert
    # (Then) Então o jogador deve parar em cima da plataforma
    assert player.y_pos == 200
    assert player.y_vel == 0


def test_player_collides_with_bottom_of_solid_platform(player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador pulando em direção ao fundo de uma plataforma
    player.x_pos = 100
    player.y_pos = 270
    player.y_vel = -10  # pulando
    world_state["platforms"][0].x = 80
    world_state["platforms"][0].y = 250
    world_state["platforms"][0].p_type = "solid"

    # 2. Act
    # (When) Quando a física é aplicada
    player.update(world_state)

    # 3. Assert
    # (Then) Então o jogador deve parar no fundo da plataforma e sua velocidade de subida de ser zero
    assert player.y_pos == 270  # 250 (player.x_pos) + 20 (altura plataforma)
    assert player.y_vel == 0


def test_player_starts_wall_sliding_when_touching_wall_in_air(player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador no, se movendo em direção a uma parede sólida
    player.x_pos = 145
    player.y_pos = 100
    player.width = 40
    player.height = 50
    player.x_vel = 5  # movendo para a direita
    player.y_vel = 5  # movendo para baixo
    world_state["platforms"][0].x = 180
    world_state["platforms"][0].y = 80
    world_state["platforms"][0].width = 20
    world_state["platforms"][0].height = 100
    world_state["platforms"][0].p_type = "solid"

    # 2. Act
    # (When) Quando a física horizontal é aplicada
    player.update(world_state)

    # 3. Assert
    # (Then) O jogador deveria parar de se mover horizontalmente e entrar no estado de wall slide
    assert player.is_wall_sliding is True
    assert player.x_pos == 140
    assert player.x_vel == 0


def test_wall_sliding_reduces_gravity_effect():
    # Given um jogador deslizando na parede
    player = Player(x=140, y=100, width=40, height=50, speed=5, jump_strength=15)
    player.is_wall_sliding = True
    world_state = {
        "gravity": 1.0,
        "wall_slide_gravity": 0.2,
        "platforms": [],
    }  # Gravidade de slide especial

    # When a física vertical é aplicada
    player.update(world_state)

    # Then a velocidade de queda deve ser a da gravidade de slide, não a normal
    assert player.y_vel == 0.2


def test_wall_jump_propels_player_up_and_away(player):
    # Given um jogador deslizando na parede direita
    player.is_wall_sliding = True
    player.change_state(WallSlidingState())

    # When o input de pulo é processado
    player.handle_input("JUMP")

    # Then o jogador deve ter velocidade para cima e para a esquerda (longe da parede)
    assert player.y_vel < 0  # Subindo
    assert player.x_vel != 0  # Longe da parede

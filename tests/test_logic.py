# tests/test_logic.py
import pytest

from game.logic import (
    apply_horizontal_physics,
    apply_vertical_physics,
    handle_input,
    shoot,
)
from game.platforms import Platform
from game.player import Player


@pytest.fixture
def new_player():
    """
    Esta fixture cria e retorna uma instância
    padrão do Player para ser usada nos testes.
    """
    return Player(x=0, y=0, width=40, height=50, speed=5, jump_strength=15)


@pytest.fixture
def world_state():
    """
    Esta fixture cria e retorna um dicionário
    com algumas configurações do mundo do jogo.
    """
    platforms = [Platform(x=80, y=400, width=100, height=20, p_type="solid")]
    return {"platforms": platforms, "gravity": 1}


def test_gravity_increase_vertical_velocity(new_player, world_state):
    # 1. Arrange (Preparar)
    # (Given) Dado um jogador que começa no ar (y=100) e parado (y_vel=0).
    new_player.x_pos = 100
    new_player.y_vel = 0

    # 2. Act (agir)
    # A 'física' do jogo acontece aqui
    # A velocidade vertical deve ser afetada pela gravida
    apply_vertical_physics(new_player, world_state)

    # 3. Assert (Verificar)
    # Verificamos se a velocidade vertical é maior que zero
    assert new_player.y_vel > 0


def test_velocity_updates_position(new_player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador parado
    new_player.x_pos = 200
    new_player.y_pos = 100
    new_player.y_vel = 10
    new_player.x_vel += new_player.speed

    # 2. Act
    # (When) Quando a física é aplicada
    apply_vertical_physics(new_player, world_state)
    apply_horizontal_physics(new_player, world_state)

    # 3. Assert
    # (Then) Então o jogador dever ser mover de acordo com as velocidades em x (x_vel) e y (y_vel)
    assert new_player.y_pos == 110  # 100 (y_pos) + 10 (y_vel)
    assert new_player.x_pos == 205  # 200 (x_pos) + 5 (speed)


def test_move_right_input_sets_positive_horizontal_velocity(new_player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador parado horizontalmente
    new_player.x_pos = 200
    new_player.y_pos = 390
    new_player.x_vel = 0

    # 2. Act
    # (When) Quando o input "direita" é processo
    handle_input(new_player, "RIGHT", world_state)

    # 3. Assert
    # (Then) Então a velocidade horizontal deve ser positiva
    assert new_player.x_vel > 0
    assert new_player.x_vel == 5


def test_move_left_input_sets_negative_horizontal_velocity(new_player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador parado
    new_player.x_pos = 200
    new_player.y_pos = 390
    new_player.x_vel = 0

    # 2. Act
    # (When) Quando o input "direita" é processo
    handle_input(new_player, "LEFT", world_state)

    # 3. Assert
    # (Then) Então a velocidade horizontal deve ser negativa
    assert new_player.x_vel < 0
    assert new_player.x_vel == -5


def test_player_jumps_from_a_platform(new_player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador no chão
    # y=350 significa que player.bottom está em 400, exatamente sob a plataforma
    # x=80 significa que o jogador está alinhado horizontalmente com a plataforma
    new_player.x_pos = 80
    new_player.y_pos = 350
    new_player.y_vel = 0  # parado verticalmente
    new_player.jump_strength = 15  # força do pulo

    # 2. Act
    # (When) quando o input "JUMP" é processado
    handle_input(new_player, "JUMP", world_state)

    # 3. Assert
    # (Then) Então a velocidade vertical do jogador deve ser negativa (para cima)
    assert new_player.y_vel < 0
    assert new_player.y_vel == -new_player.jump_strength


def test_player_cannot_jump_in_mid_air(new_player, world_state):
    # Given (Dado) um jogador no ar
    new_player.y_vel = 5  # Caindo
    new_player.jump_strength = 15

    # When (Quando) o input "JUMP" é processado
    handle_input(new_player, "JUMP", world_state)

    # Then (Então) a velocidade vertical NÃO deve mudar
    assert new_player.y_vel == 5


def test_moving_right_updates_facing_direction(new_player):
    # 1. Arrange
    # (Given) Dado um jogador

    # 2. Act
    # (When) Quando o input "RIGHT" é processdao
    handle_input(new_player, "RIGHT", {})  # world_physics não é necessário aqui

    # 3. Assert
    # (Then) Então a direção deve ser "RIGHT"
    assert new_player.facing_direction == "RIGHT"


def test_moving_left_updates_facing_direction(new_player):
    # 1. Arrange
    # (Given) Dado um jogador

    # 2. Act
    # (When) Quando o input "LEFT" é processdao
    handle_input(new_player, "LEFT", {})  # world_physics não é necessário aqui

    # 3. Assert
    # (Then) Então a direção deve ser "LEFT"
    assert new_player.facing_direction == "LEFT"


def test_shoot_bullet_moving_in_player_direction(new_player):
    # 1. Arrange
    # (Given) Dado um jogador virado para a direita
    new_player.facing_direction = "RIGHT"
    bullet_speed = 10

    # 2. Act
    # (When) Quando o jogador atira
    bullet = shoot(new_player, bullet_speed)

    # 3. Assert
    # (Then) Então a bala deve se mover para a direita
    assert bullet.x_vel > 0

    # 1. Arrang
    # (Given) Dado um jogador virado para a esquerda
    new_player.facing_direction = "LEFT"

    # 2. Act
    # (When) Quando o jogador atira
    bullet = shoot(new_player, bullet_speed)

    # 3. Assert
    # (Then) Então a bala deve se mover para a direita
    assert bullet.x_vel < 0


def test_player_lands_on_solid_platform(new_player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador caindo em direção a uma plataforma sólida
    new_player.x_pos = 80
    new_player.y_pos = 195
    new_player.y_vel = 10  # caindo
    world_state["platforms"][0].x = 80
    world_state["platforms"][0].y = 250
    world_state["platforms"][0].p_type = "solid"

    # 2. Act
    # (When) Quando a física é aplicada
    apply_vertical_physics(new_player, world_state)

    # 3. Assert
    # (Then) Então o jogador de parar exatamente em cima da plataforma
    assert new_player.y_pos == 200  # 250 (topo da plataforma) - 50 (altura do player)
    assert new_player.y_vel == 0


def test_player_jumps_through_passthrough_platform(new_player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador pulando por baixo de uma plataforma pass-through
    new_player.x_pos = 100
    new_player.y_pos = 260
    new_player.y_vel = -10  # pulando
    world_state["platforms"][0].x = 80
    world_state["platforms"][0].y = 250
    world_state["platforms"][0].p_type = "pass-through"

    # 2. Act
    # (When) Quando a física é aplicada
    apply_vertical_physics(new_player, world_state)

    # 3. Assert
    # (Then) Então o jogador NÃO deve colidir e deve continuar subindo (afetado pela gravidade)
    assert new_player.y_pos == 250  # 260 (player.y_pos) - 10 (player.y_vel)
    assert new_player.y_vel == -9  # -10 + 1 (gravidade)


def test_player_lands_on_passthrough_platform(new_player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador caindo em direção a uma plataforma pass-through
    new_player.x_pos = 100
    new_player.y_pos = 195
    new_player.y_vel = 10  # caindo
    world_state["platforms"][0].x = 80
    world_state["platforms"][0].y = 250
    world_state["platforms"][0].p_type = "pass-through"

    # 2. Act
    # (When) Quando a física é aplicada
    apply_vertical_physics(new_player, world_state)

    # 3. Assert
    # (Then) Então o jogador deve parar em cima da plataforma
    assert new_player.y_pos == 200
    assert new_player.y_vel == 0


def test_player_collides_with_bottom_of_solid_platform(new_player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador pulando em direção ao fundo de uma plataforma
    new_player.x_pos = 100
    new_player.y_pos = 270
    new_player.y_vel = -10  # pulando
    world_state["platforms"][0].x = 80
    world_state["platforms"][0].y = 250
    world_state["platforms"][0].p_type = "solid"

    # 2. Act
    # (When) Quando a física é aplicada
    apply_vertical_physics(new_player, world_state)

    # 3. Assert
    # (Then) Então o jogador deve parar no fundo da plataforma e sua velocidade de subida de ser zero
    assert new_player.y_pos == 270  # 250 (player.x_pos) + 20 (altura plataforma)
    assert new_player.y_vel == 0


def test_player_starts_wall_sliding_when_touching_wall_in_air(new_player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador no, se movendo em direção a uma parede sólida
    new_player.x_pos = 145
    new_player.y_pos = 100
    new_player.width = 40
    new_player.height = 50
    new_player.x_vel = 5  # movendo para a direita
    new_player.y_vel = 5  # movendo para baixo
    world_state["platforms"][0].x = 180
    world_state["platforms"][0].y = 80
    world_state["platforms"][0].width = 20
    world_state["platforms"][0].height = 100
    world_state["platforms"][0].p_type = "solid"

    # 2. Act
    # (When) Quando a física horizontal é aplicada
    apply_horizontal_physics(new_player, world_state)
    apply_vertical_physics(new_player, world_state)

    # 3. Assert
    # (Then) O jogador deveria parar de se mover horizontalmente e entrar no estado de wall slide
    assert new_player.is_wall_sliding is True
    assert new_player.x_pos == 140
    assert new_player.x_vel == 0


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
    apply_vertical_physics(player, world_state)

    # Then a velocidade de queda deve ser a da gravidade de slide, não a normal
    assert player.y_vel == 0.2


def test_wall_jump_propels_player_up_and_away():
    # Given um jogador deslizando na parede direita
    player = Player(x=140, y=100, width=40, height=50, speed=5, jump_strength=15)
    player.is_wall_sliding = True
    player.facing_direction = (
        "RIGHT"  # A direção importa para saber de qual parede pular
    )

    # When o input de pulo é processado
    handle_input(player, "JUMP", {})  # world_state não é necessário aqui

    # Then o jogador deve ter velocidade para cima e para a esquerda (longe da parede)
    assert player.y_vel < 0  # Subindo
    assert player.x_vel < 0  # Longe da parede

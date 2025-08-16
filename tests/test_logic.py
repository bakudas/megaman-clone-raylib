# tests/test_logic.py
from game.logic import apply_physics, handle_input, jump
from game.player import Player


def test_gravity_increase_vertical_velocity():
    # 1. Arrange (Preparar)
    # Nosso jogador é só um dicionério com seus dadso.
    # Ele começa no ar (y=100) e parado (y_vel=0).
    player = Player(x=200, y=100, width=40, height=50, speed=5)
    world_physics = {"gravity": 1, "floor": 400}  # Uma força de gravidade simples

    # 2. Act (agir)
    # A 'física' do jogo acontece aqui
    # A velocidade vertical deve ser afetada pela gravida
    apply_physics(player, world_physics)

    # 3. Assert (Verificar)
    # Verificamos se a velocidade vertical é maior que zero
    assert player.y_vel > 0


def test_velocity_updates_position():
    # 1. Arrange
    player = Player(x=200, y=100, width=40, height=50, speed=5)
    world_physics = {"gravity": 1, "floor": 400}
    player.y_vel = 10
    player.x_vel += player.speed

    # 2. Act
    apply_physics(player, world_physics)

    # 3. Assert
    assert player.y_pos == 110
    assert player.x_pos == 205


def test_player_jump():
    # 1. Arrange
    player = {"y_pos": 200, "y_vel": 0, "jump_force": 10, "on_ground": True}

    # 2. Act
    if player["on_ground"]:
        player = jump(player)

    # 3. Assert
    assert player["y_vel"] < 0
    assert not player["on_ground"]


def test_player_stops_at_the_floor():
    # 1. Arrange
    player = Player(x=200, y=390, width=40, height=50, speed=5)
    world_physics = {"gravity": 1, "floor": 400}
    player.y_vel = 10

    # 2. Act
    apply_physics(player, world_physics)

    # 3. Assert
    # A base do jogador (y_pos + height) não deve passar do chão
    # Então, a nova y_pos deve ser floor - height
    assert player.y_pos == 350
    assert player.y_vel == 0


def test_move_right_input_sets_positive_horizontal_velocity():
    # 1. Arrange
    # (Given) Dado um jogador parado
    player = Player(x=200, y=390, width=40, height=50, speed=5)

    # 2. Act
    # (When) Quando o input "direita" é processo
    handle_input(player, "RIGHT")

    # 3. Assert
    # (Then) Então a velocidade horizontal deve ser positiva
    assert player.x_vel > 0
    assert player.x_vel == 5


def test_move_left_input_sets_negative_horizontal_velocity():
    # 1. Arrange
    # (Given) Dado um jogador parado
    player = Player(x=200, y=390, width=40, height=50, speed=5)

    # 2. Act
    # (When) Quando o input "direita" é processo
    handle_input(player, "LEFT")

    # 3. Assert
    # (Then) Então a velocidade horizontal deve ser negativa
    assert player.x_vel < 0
    assert player.x_vel == -5

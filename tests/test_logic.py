# tests/test_logic.py
from game.logic import apply_physics, handle_input, shoot
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
    world_physics = {"floor": 400, "gravity": 1}

    # 2. Act
    # (When) Quando o input "direita" é processo
    handle_input(player, "RIGHT", world_physics)

    # 3. Assert
    # (Then) Então a velocidade horizontal deve ser positiva
    assert player.x_vel > 0
    assert player.x_vel == 5


def test_move_left_input_sets_negative_horizontal_velocity():
    # 1. Arrange
    # (Given) Dado um jogador parado
    player = Player(x=200, y=390, width=40, height=50, speed=5)
    world_physics = {"floor": 400, "gravity": 1}

    # 2. Act
    # (When) Quando o input "direita" é processo
    handle_input(player, "LEFT", world_physics)

    # 3. Assert
    # (Then) Então a velocidade horizontal deve ser negativa
    assert player.x_vel < 0
    assert player.x_vel == -5


def test_player_jumps_from_the_ground():
    # 1. Arrange
    # (Given) Dado um jogador no chão
    world_physics = {"floor": 400, "gravity": 1}
    player = Player(x=100, y=350, width=40, height=50, speed=5)
    # x=350 significa que player.bottom está em 400, exatamente no chão
    player.jump_strength = 15  # força do pulo

    # 2. Act
    # (When) quando o input "JUMP" é processado
    handle_input(player, "JUMP", world_physics)

    # 3. Assert
    # (Then) Então a velocidade vertical do jogador deve ser negativa (para cima)
    assert player.y_vel < 0
    assert player.y_vel == -player.jump_strength


def test_player_cannot_jump_in_mid_air():
    # Given (Dado) um jogador no ar
    world_physics = {"floor": 400, "gravity": 1}
    player = Player(x=100, y=200, width=40, height=50, speed=5)
    player.y_vel = 5  # Caindo
    player.jump_strength = 15

    # When (Quando) o input "JUMP" é processado
    handle_input(player, "JUMP", world_physics)

    # Then (Então) a velocidade vertical NÃO deve mudar
    assert player.y_vel == 5


def test_moving_right_updates_facing_direction():
    # 1. Arrange
    # (Given) Dado um jogador
    player = Player(x=100, y=350, width=40, height=50, speed=5, jump_strength=15)

    # 2. Act
    # (When) Quando o input "RIGHT" é processdao
    handle_input(player, "RIGHT", {})  # world_physics não é necessário aqui

    # 3. Assert
    # (Then) Então a direção deve ser "RIGHT"
    assert player.facing_direction == "RIGHT"


def test_moving_left_updates_facing_direction():
    # 1. Arrange
    # (Given) Dado um jogador
    player = Player(x=100, y=350, width=40, height=50, speed=5, jump_strength=15)

    # 2. Act
    # (When) Quando o input "LEFT" é processdao
    handle_input(player, "LEFT", {})  # world_physics não é necessário aqui

    # 3. Assert
    # (Then) Então a direção deve ser "LEFT"
    assert player.facing_direction == "LEFT"


def test_shoot_bullet_moving_in_player_direction():
    # 1. Arrange
    # (Given) Dado um jogador virado para a direita
    player = Player(x=100, y=200, width=40, height=50, speed=5, jump_strength=15)
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

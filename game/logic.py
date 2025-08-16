# game/logic.py
from game.player import Player
from game.bullet import Bullet


def apply_physics(player: Player, world_physics: dict) -> None:
    """
    Aplica as forças de física (por enquanto, só gravidade) ao estado do jogador.
    :param player_state: player state.
    :param world_physics: world general physics.
    """
    # Copiamos o estado para não modificar o original diretamente (boa prática)
    gravity = world_physics["gravity"]
    floor_level = world_physics["floor"]

    # Atualização da Posição
    # A posição é atualizada pela velocidade do frame anterior
    player.x_pos += player.x_vel
    player.y_pos += player.y_vel

    # Atualização da velocidade
    # A velocidade é atualizada pela gravidade para o próximo frame
    player.y_vel += gravity

    # Checagem de colisão com o chão
    if player.bottom >= floor_level:
        player.y_pos = floor_level - player.height  # corrige a posição do player
        player.y_vel = 0  # zera a velocidade vertival


def handle_input(player: Player, input_direction: str, world_physics: dict) -> None:
    """
    Atualiza o estado do jogador com base no input
    """
    speed = player.speed
    player.facing_direction = input_direction

    # Movimento horizontal
    if input_direction == "RIGHT":
        player.x_vel += speed
    elif input_direction == "LEFT":
        player.x_vel -= speed

    # Lógica do Pulo
    if input_direction == "JUMP":
        if player.is_on_ground(world_physics):
            player.y_vel = -player.jump_strength


def shoot(player: Player, bullet_speed: float):
    """
    Cria e retorna uma nova instância de Bullet com base no estado do jogador
    """
    # A bala inicialmente vai sair do meio do jogador
    start_y = player.y_pos + (player.height / 2)
    start_x = player.x_pos

    if player.facing_direction == "RIGHT":
        start_x = player.x_pos + player.width
        velocity = bullet_speed
    else:
        velocity = -bullet_speed

    return Bullet(start_x, start_y, velocity)

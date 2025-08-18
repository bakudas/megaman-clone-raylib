# game/logic.py

from game.player import Player
from game.bullet import Bullet


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

# game/logic.py
from game.player import Player


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


def handle_input(player: Player, input) -> None:
    """
    Atualiza o estado do jogador com base no input
    """
    speed = player.speed

    if input == "RIGHT":
        player.x_vel += speed
    elif input == "LEFT":
        player.x_vel -= speed


def jump(player_state):
    """
    Player Jump
    """
    # Copiamos o estado para não modificar o original diretamente (boa prática)
    new_state = player_state.copy()

    # A lógica mais simples para passar no teste
    new_state["y_vel"] -= new_state["jump_force"]
    new_state["on_ground"] = False

    return new_state

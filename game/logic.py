# game/logic.py


def apply_physics(player_state, world_physics):
    """
    Aplica as forças de física (por enquanto, só gravidade) ao estado do jogador.
    :param player_state: player state.
    :param world_physics: world general physics.
    """
    # Copiamos o estado para não modificar o original diretamente (boa prática)
    new_state = player_state.copy()
    gravity = world_physics["gravity"]
    floor_level = world_physics["floor"]

    # Atualização da Posição
    # A posição é atualizada pela velocidade do frame anterior
    new_state["y_pos"] += new_state["y_vel"]

    # Atualização da velocidade
    # A velocidade é atualizada pela gravidade para o próximo frame
    new_state["y_vel"] += gravity

    # Checagem de colisão com o chão
    playe_bottom = new_state["y_pos"] + new_state["height"]
    if playe_bottom >= floor_level:
        new_state["y_pos"] = (
            floor_level - player_state["height"]
        )  # corrige a posição do player
        new_state["y_vel"] = 0

    return new_state


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

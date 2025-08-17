# game/logic.py
import pyray as pr

from game.player import Player
from game.bullet import Bullet


def apply_vertical_physics(player: Player, world_state: dict) -> None:
    """
    Aplica as forças de física (por enquanto, só gravidade) ao estado do jogador.
    :param player_state: player state.
    :param world_physics: world general physics.
    """
    # Armazena a posição anterior para checagem de colisão
    previous_y_pos = player.y_pos

    # Copiamos o estado para não modificar o original diretamente (boa prática)
    gravity = world_state["gravity"]

    # Aplica a velocidade vertical
    player.y_pos += player.y_vel

    # Checa colisão com plataformas
    collision_occurred = False
    player_rect = pr.Rectangle(player.x_pos, player.y_pos, player.width, player.height)

    for plat in world_state.get("platforms", []):
        plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)

        # Condições para aterrissar:
        # 1) os retângulos colidem
        # 2) o jogador está caido (ou parado)
        # 3) a base do jogador estava ACIMA do topo da plataforma no frame anterior
        is_colliding = pr.check_collision_recs(player_rect, plat_rect)
        is_falling = player.y_vel >= 0
        is_rising = player.y_vel < 0
        was_above = (previous_y_pos + player.height) <= plat.y
        was_bellow = previous_y_pos >= (plat.y + plat.height)

        if is_colliding:
            # CASO 1: ATERRISSANDO NA PLATAFORMA
            if is_falling and was_above:
                # Para plataformas 'pass-through', a condição de queda é obrigatória
                # Para 'solid', aterrissar é o comportamento padrão
                if plat.type == "solid" or plat.type == "pass-through":
                    player.y_pos = plat.y - player.height  # corrige a posição do player
                    player.y_vel = 0  # parada súbita pela colição
                    collision_occurred = True
                    break
            # CASO 2: BATENDO A CABEÇA NO FUNDO DA PLATAFORMA
            if plat.type == "solid" and is_rising and was_bellow:
                player.y_pos = plat.y + plat.height  # corrige a posição do player
                player.y_vel = 0
                collision_occurred = True
                break

    # Aplica gravidade se não estivermos no chão de uma plataforma
    if not collision_occurred:
        if player.is_wall_sliding:
            # Aplica uma gravidade reduzida e limita a velocidade de queda
            gravity = world_state.get("wall_slide_gravity", player.y_vel)
            player.y_vel += gravity
            if player.y_vel > 2:  # Limite de velocidade de slide
                player.y_vel = 2
        else:
            player.y_vel += world_state["gravity"]


def apply_horizontal_physics(player: Player, world_state: dict):
    # Aplica movimento horizontal
    player.x_pos += player.x_vel

    # Reseta o estado do wall slide a cada frame
    player.is_wall_sliding = False

    # Checa colisão com plataformas
    player_rect = pr.Rectangle(player.x_pos, player.y_pos, player.width, player.height)

    for plat in world_state.get("platforms", []):
        if plat.type == "solid":
            plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)

            is_colliding = pr.check_collision_recs(player_rect, plat_rect)
            collision_from_left = player.x_vel > 0
            collistion_from_right = player.x_vel < 0

            if is_colliding:
                # colisão pela esquerda (o jogador vem da esquerda)
                if collision_from_left:
                    player.x_pos = plat.x - player.width
                    player.x_vel = 0
                    if player.y_vel > 0:  # só pode deslizar se estiver caindo
                        player.is_wall_sliding = True
                # colisão pela direita (o jogador vem da direita)
                elif collistion_from_right:
                    player.x_pos = plat.x + plat.width
                    player.x_vel = 0
                    if player.y_vel > 0:  # só pode deslizer se estiver caindo
                        player.is_wall_sliding = True


def apply_physics(player: Player, world_state: dict):
    apply_vertical_physics(player, world_state)
    apply_horizontal_physics(player, world_state)


def handle_input(player: Player, input_direction: str, world_state: dict) -> None:
    """
    Atualiza o estado do jogador com base no input
    """
    speed = player.speed

    # Movimento horizontal
    if input_direction == "RIGHT":
        player.facing_direction = "RIGHT"
        player.x_vel += speed
    elif input_direction == "LEFT":
        player.x_vel -= speed
        player.facing_direction = "LEFT"

    # Lógica do Pulo
    if input_direction == "JUMP":
        if player.is_wall_sliding:
            # Wall Jump!
            player.y_vel = (
                -player.jump_strength * 0.5
            )  # Um pouco menos forte que o pulo normal
            # Impulsiona para longe da parede em que está
            player.x_vel = -10 if player.facing_direction == "RIGHT" else 10
        elif player.is_on_ground(world_state):
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

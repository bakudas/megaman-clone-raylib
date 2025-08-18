# game/self.py
from __future__ import annotations
from typing import TYPE_CHECKING
import pyray as pr

from game.player_state import PlayerState, IdleState, JumpingState, WallSlidingState

if TYPE_CHECKING:
    from game.platforms import Platform


class Player:
    def __init__(self, x, y, width=0, height=0, speed=0, jump_strength=0) -> None:
        self.x_pos: float = x
        self.y_pos: float = y
        self.x_vel: float = 0
        self.y_vel: float = 0
        self.width: int = width
        self.height: int = height

        # atributos de GAMEPLAY
        self.speed: float = speed
        self.jump_strength: float = jump_strength
        self.facing_direction: str = "RIGHT"
        self.is_wall_sliding: bool = False
        self.wall_slide_gravity: float = 0.1
        self.wall_jump_x_velocity: float = 5
        self.wall_jump_scale_factor: float = 0.8

        # state machine
        self.state: PlayerState = IdleState()

    def change_state(self, new_state: PlayerState):
        # guarda o estado anterior
        previous_state: PlayerState = self.state

        # debug
        print(f"mudando do estado {previous_state} para {new_state}")

        # troca o estado
        self.state = new_state

    def update(self, world_state: dict):
        """
        Atualiza toda a lógica do player
        """
        # aplica a física
        self._apply_vertical_physics(world_state)
        self._apply_horizontal_physics(world_state)

        # atualiza a state machine
        self.state.update(self, world_state)

    def handle_input(self, input_direction: str):
        """
        Delega o input para o estado atual
        """
        if input_direction == "RIGHT":
            self.x_vel = self.speed
            self.facing_direction = "RIGHT"
        elif input_direction == "LEFT":
            self.x_vel = -self.speed
            self.facing_direction = "LEFT"
        elif input_direction == "STOP":
            self.x_vel = 0

        self.state.handle_input(self, input_direction)

    # --- Métodos de Ação ---

    def jump(self) -> None:
        self.y_vel = -self.jump_strength

    def wall_jump(self) -> None:
        self.y_vel = -self.jump_strength * self.wall_jump_scale_factor
        self.x_vel = (
            -self.wall_jump_x_velocity
            if self.facing_direction == "RIGHT"
            else self.wall_jump_x_velocity
        )

    # --- Métodos de verificação

    @property
    def bottom(self) -> float:
        """
        Calcula a posição da baso do jogador
        """
        return self.y_pos + self.height

    def is_on_ground(self, world_physics: dict) -> bool:
        """
        Verifica se o jogador está no chão.
        """

        for plat in world_physics.get("platforms", []):
            # Verifica se o jogador está horizontalmente alinhado com a plataforma
            is_horizontaly_aligned = (
                self.x_pos < plat.x + plat.width and self.x_pos + self.width > plat.x
            )

            # Verifica se a base do jogador está exatamente no topo de alguma plataforma
            is_on_top = self.bottom == plat.y

            if is_horizontaly_aligned and is_on_top:
                return True  # encontrou um chão, pode parar de procurar

        return False  # segue o baile

    def is_touching_wall(self, world_state: dict) -> bool:
        player_rect = pr.Rectangle(self.x_pos, self.y_pos, self.width, self.height)

        for plat in world_state.get("platforms", []):
            if plat.type == "solid":
                plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)

                is_colliding = pr.check_collision_recs(player_rect, plat_rect)
                collision_from_left = self.x_vel > 0
                collistion_from_right = self.x_vel < 0

                if is_colliding:
                    # colisão pela esquerda (o jogador vem da esquerda)
                    if collision_from_left:
                        self.x_pos = plat.x - self.width
                        self.x_vel = 0
                        if self.y_vel > 0:  # só pode deslizar se estiver caindo
                            return True
                    # colisão pela direita (o jogador vem da direita)
                    elif collistion_from_right:
                        self.x_pos = plat.x + plat.width
                        self.x_vel = 0
                        if self.y_vel > 0:  # só pode deslizer se estiver caindo
                            return True

        return False

    # --- Métodos de física ---

    def _apply_vertical_physics(self, world_state: dict) -> None:
        """
        Aplica as forças de física (por enquanto, só gravidade) ao estado do jogador.
        :param player_state: player state.
        :param world_physics: world general physics.
        """
        # Armazena a posição anterior para checagem de colisão
        previous_y_pos = self.y_pos

        # Copiamos o estado para não modificar o original diretamente (boa prática)
        gravity = world_state["gravity"]

        # Aplica a velocidade vertical
        self.y_pos += self.y_vel

        # Checa colisão com plataformas
        collision_occurred = False
        player_rect = pr.Rectangle(self.x_pos, self.y_pos, self.width, self.height)

        for plat in world_state.get("platforms", []):
            plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)

            # Condições para aterrissar:
            # 1) os retângulos colidem
            # 2) o jogador está caido (ou parado)
            # 3) a base do jogador estava ACIMA do topo da plataforma no frame anterior
            is_colliding = pr.check_collision_recs(player_rect, plat_rect)
            is_falling = self.y_vel >= 0
            is_rising = self.y_vel < 0
            was_above = (previous_y_pos + self.height) <= plat.y
            was_bellow = previous_y_pos >= (plat.y + plat.height)

            if is_colliding:
                # CASO 1: ATERRISSANDO NA PLATAFORMA
                if is_falling and was_above:
                    # Para plataformas 'pass-through', a condição de queda é obrigatória
                    # Para 'solid', aterrissar é o comportamento padrão
                    if plat.type == "solid" or plat.type == "pass-through":
                        self.y_pos = plat.y - self.height  # corrige a posição do player
                        self.y_vel = 0  # parada súbita pela colição
                        collision_occurred = True
                        break
                # CASO 2: BATENDO A CABEÇA NO FUNDO DA PLATAFORMA
                if plat.type == "solid" and is_rising and was_bellow:
                    self.y_pos = plat.y + plat.height  # corrige a posição do player
                    self.y_vel = 0
                    collision_occurred = True
                    break

        # Aplica gravidade se não estivermos no chão de uma plataforma
        if not collision_occurred:
            if self.is_wall_sliding:
                # Aplica uma gravidade reduzida e limita a velocidade de queda
                gravity = world_state.get("wall_slide_gravity", self.y_vel)
                self.y_vel += gravity
                if self.y_vel > 2:  # Limite de velocidade de slide
                    self.y_vel = 2
            else:
                self.y_vel += world_state["gravity"]

    def _apply_horizontal_physics(self, world_state: dict):
        # Aplica movimento horizontal
        self.x_pos += self.x_vel

        # Reseta o estado do wall slide a cada frame
        self.is_wall_sliding = False

        # Checa colisão com plataformas
        player_rect = pr.Rectangle(self.x_pos, self.y_pos, self.width, self.height)

        for plat in world_state.get("platforms", []):
            if plat.type == "solid":
                plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)

                is_colliding = pr.check_collision_recs(player_rect, plat_rect)
                collision_from_left = self.x_vel > 0
                collistion_from_right = self.x_vel < 0

                if is_colliding:
                    # colisão pela esquerda (o jogador vem da esquerda)
                    if collision_from_left:
                        self.x_pos = plat.x - self.width
                        self.x_vel = 0
                        if self.y_vel > 0:  # só pode deslizar se estiver caindo
                            self.is_wall_sliding = True
                    # colisão pela direita (o jogador vem da direita)
                    elif collistion_from_right:
                        self.x_pos = plat.x + plat.width
                        self.x_vel = 0
                        if self.y_vel > 0:  # só pode deslizer se estiver caindo
                            self.is_wall_sliding = True

# game/self.py
from __future__ import annotations

from typing import TYPE_CHECKING
from raylib.defines import KEY_LEFT, KEY_RIGHT, GLFW_KEY_SPACE, GLFW_KEY_X, GLFW_KEY_Z, GLFW_KEY_R
import pyray as pr

from game.player_states import PlayerState, IdleState, JumpingState, WallSlidingState, DashState, HurtingState, \
    FallingState
from game.weapon_states import WeaponState, ReadyState
from game.bullet import Bullet
from game.events import PlayerEvent, GameEvent
from game.observer import Subject

if TYPE_CHECKING:
    from game.platforms import Platform


class Player(Subject):
    def __init__(self, x, y, width=0, height=0, speed=0, jump_strength=0) -> None:
        super().__init__()

        # atributos de estado físico
        self.x_pos: float = x
        self.y_pos: float = y
        self.x_vel: float = 0
        self.y_vel: float = 0
        self.width: int = width
        self.height: int = height
        self.color = pr.SKYBLUE
        self.start_pos: tuple = (x, y)
        self.last_checkpoint: tuple = self.start_pos

        # atributos de GAMEPLAY
        self.MAX_HEALTH: int = 28
        self.health: int = self.MAX_HEALTH
        self.knockback_force: float = 2
        self.is_destroyed: bool = False
        self.is_permanently_destroyed: bool = False
        self.is_visible = True
        self.lives: int = 3

        # SHOOT
        self.charge_duration: float = 1.0
        self.bullet_speed: float = speed * 2.5
        self.bullet_spawn_point: pr.Vector2 = pr.Vector2(
            self.y_pos + (self.height / 2),
            self.x_pos
        )

        # MOVEMENT
        self.speed: float = speed
        self.charge_run_speed: float = speed * 1.25
        self.horizontal_input_active: bool = False
        self.facing_direction: str = "RIGHT"
        self.air_control_factor: float = 0.75

        # JUMP
        self.jump_strength: float = jump_strength
        self.coyote_timer: float = 0.0
        self.COYOTE_TIMER_DURATION: float = 0.1
        self.JUMP_BUFFER_DURATION = 0.1
        self.jump_buffer_timer: float = 0.0

        # WALL SLIDE
        self.is_wall_sliding: bool = False
        self.wall_slide_gravity: float = 0.25
        self.wall_jump_x_velocity: float = self.jump_strength * 0.20
        self.wall_jump_scale_factor: float = 0.8

        # DASH
        self.dash_speed: float = speed * 2.5
        self.dash_duration: float = 0.2
        self.dash_cooldown: float = 0.1
        self.dash_cooldown_timer: float = 0.0

        # state machine
        self.locomotion_state: PlayerState = IdleState(self)
        self.weapon_state: WeaponState = ReadyState()

    # --- Métodos de gerenciamento de estado ---
    def change_locomotion_state(self, new_state: PlayerState):
        # guarda o estado anterior
        previous_state: PlayerState = self.locomotion_state

        # debug
        #print(f"Movement state: {previous_state} -> {new_state}")

        # troca o estado
        self.locomotion_state = new_state

    def change_weapon_state(self, new_state: WeaponState):
        """Muda o estado da arma do jogador."""
        # guarda o estado anterior
        previous_state: WeaponState = self.weapon_state

        # debug
        #print(f"Weapon state: {previous_state} -> {new_state}")

        # troca o estado da arma
        self.weapon_state = new_state

    # --- Métodos principais ---

    def update(self, world_state: dict, delta_time: float):
        """
        Atualiza toda a lógica do player
        """
        # self.x_vel = 0 # Reseta a intenção de movimento
        self.horizontal_input_active = False

        if pr.is_key_down(KEY_RIGHT):
            self.handle_input("RIGHT")
            self.horizontal_input_active = True
        elif pr.is_key_down(KEY_LEFT):
            self.handle_input("LEFT")
            self.horizontal_input_active = True

        if pr.is_key_pressed(GLFW_KEY_SPACE):
            self.handle_input("JUMP")

        if pr.is_key_released(pr.KEY_SPACE):  # <<< NOVO INPUT
            self.handle_input("JUMP_RELEASE")

        if pr.is_key_pressed(GLFW_KEY_Z):
            self.handle_input("DASH")
            self.horizontal_input_active = True

        if pr.is_key_pressed(GLFW_KEY_X):
            self.weapon_state.handle_input(self,"SHOOT_PRESS", world_state)

        if pr.is_key_released(GLFW_KEY_X):
            self.weapon_state.handle_input(self, "SHOOT_RELEASE", world_state)

        # if pr.is_key_released(GLFW_KEY_R):
        #     self.respawn()

        if not self.horizontal_input_active:
            self.handle_input("STOP")

        # atualiza o cooldown do dash
        if self.dash_cooldown > 0:
            self.dash_cooldown_timer -= delta_time

        # aplica a física
        self._apply_vertical_physics(world_state)
        self._apply_horizontal_physics(world_state, delta_time)

        # atualiza a state machine
        self.locomotion_state.update(self, world_state, delta_time)
        self.weapon_state.update(self, delta_time, world_state)

        # coyote timer
        if self.coyote_timer > 0:
            self.coyote_timer -= delta_time

        # jump buffer timer
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= delta_time

    def handle_input(self, input_direction: str):
        """
        Delega o input para o estado atual
        """
        self.locomotion_state.handle_input(self, input_direction)

    def draw(self) -> None:
        if self.is_visible:
            pr.draw_rectangle(
                int(self.x_pos),
                int(self.y_pos),
                int(self.width),
                int(self.height),
                self.color,
            )

    # --- Métodos de Ação ---

    def jump(self) -> None:
        self.y_vel = -self.jump_strength
        self.notify(PlayerEvent.PLAYER_JUMPED)

    def wall_jump(self) -> None:
        self.y_vel = -self.jump_strength * self.wall_jump_scale_factor
        self.x_vel = (
            -self.wall_jump_x_velocity
            if self.facing_direction == "RIGHT"
            else self.wall_jump_x_velocity
        )
        self.notify(PlayerEvent.PLAYER_JUMPED)

    def fire_normal_shot(self, world_state: dict):
        """Cria e adiciona um projétil normal ao mundo."""
        start_y = self.y_pos + (self.height / 2) - 2
        velocity = world_state.get("bullet_speed", 6.0)

        if self.facing_direction == 'RIGHT':
            start_x = self.x_pos + self.width
        else:  # LEFT
            start_x = self.x_pos
            velocity = -velocity

        new_bullet = Bullet(start_x, start_y, velocity, 'normal')
        world_state["bullets"].append(new_bullet)
        self.notify(PlayerEvent.PLAYER_SHOT)

    def fire_charged_shot(self, world_state: dict):
        """Cria e adiciona um projétil carregado ao mundo."""
        start_y = self.y_pos + (self.height / 2) - 6
        velocity = world_state.get("bullet_speed", 6.0) * 1.2  # Um pouco mais rápido

        if self.facing_direction == 'RIGHT':
            start_x = self.x_pos + self.width
        else:  # LEFT
            start_x = self.x_pos
            velocity = -velocity

        new_bullet = Bullet(start_x, start_y, velocity, 'charged')
        world_state["bullets"].append(new_bullet)
        self.notify(PlayerEvent.PLAYER_SHOT_CHARGED)

    def take_damage(self, amount: int):
        # invencibilidade temporária, checa se já está a tomar dado
        if isinstance(self.locomotion_state, HurtingState):
            return

        self.health -= amount
        print(f'Player took: {amount} damage, {self.health} left')
        if self.health <= 0:
            self.destroy()
        else:
            # transição para estado hurt
            self.change_locomotion_state(HurtingState(self))
            # mensagem para notificar os observadores
            self.notify(PlayerEvent.PLAYER_HURT)

    def heal(self, amount: int):
        """
        Cura o jogador com a quantidade especificada.
        """
        self.health += amount
        if self.health > self.MAX_HEALTH:
            self.health = self.MAX_HEALTH
        self.notify(PlayerEvent.PLAYER_HEALED)

    def respawn(self):
        """
        Restaura o jogador ao seu último checkpoint
        """
        self.x_pos, self.y_pos = self.last_checkpoint
        self.health = self.MAX_HEALTH
        self.is_destroyed = False
        self.is_permanently_destroyed = False
        self.x_vel = 0
        self.y_vel = 0
        self.change_locomotion_state(FallingState())
        self.notify(PlayerEvent.PLAYER_RESPAWNED)

    def destroy(self):
        """
        Marca o jogador para destruição imediata
        """
        if not self.is_destroyed:
            self.health = 0
            self.on_destroy()

    # --- Callbacks ---
    def on_destroy(self):
        """
        Callback chamado quando o jogador é destruído.
        """
        if self.is_destroyed: return

        print("Player was destroyed!")
        self.lives -= 1
        self.is_destroyed = True

        if self.lives <= 0:
            self.is_permanently_destroyed = True
            self.notify(PlayerEvent.PLAYER_DESTROYED)
            self.notify(GameEvent.NO_LIVES_REMAINING)
        else:
            self.notify(PlayerEvent.PLAYER_DIED)

    # --- Métodos de verificação ---

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
        player_feet = pr.Rectangle(self.x_pos, self.bottom, self.width, 1)

        for plat in world_physics.get("platforms", []):
            plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)
            if pr.check_collision_recs(player_feet, plat_rect):
                return True

        return False  # segue o baile

    def is_touching_wall_in_air(self, world_state: dict) -> bool:
        if self.is_on_ground(world_state):
            return False

        check_rect_right = pr.Rectangle(
            self.x_pos + self.width, self.y_pos + 5, 1, self.height
        )
        check_rect_left = pr.Rectangle(self.x_pos - 1, self.y_pos + 5, 1, self.height)

        for plat in world_state.get("platforms", []):
            if plat.type == "solid":
                plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)
                if pr.check_collision_recs(
                    check_rect_right, plat_rect
                ) or pr.check_collision_recs(check_rect_left, plat_rect):
                    return True

        return False

    # --- Métodos de física ---

    def _apply_vertical_physics(self, world_state: dict) -> None:
        """
        Aplica as forças de física (por enquanto, só gravidade) ao estado do jogador.
        :param world_state: world general physics.
        """
        # Armazena a posição anterior para checagem de colisão
        previous_y_pos = self.y_pos

        # Aplica a velocidade vertical
        self.y_pos += self.y_vel

        # Checa colisão com plataformas
        collision_occurred = False
        player_rect = pr.Rectangle(self.x_pos, self.y_pos, self.width, self.height)

        for plat in world_state.get("platforms", []):
            plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)

            is_colliding = pr.check_collision_recs(player_rect, plat_rect)
            is_falling = self.y_vel >= 0
            is_rising = self.y_vel < 0
            was_above = (previous_y_pos + self.height) <= plat.y
            was_bellow = previous_y_pos >= (plat.y + plat.height)

            if is_colliding:
                # CASO 1: ATERRISSANDO NA PLATAFORMA
                if is_falling and was_above:
                    if plat.type == "solid" or plat.type == "pass-through":
                        if isinstance(self.locomotion_state, FallingState):  # Só notifica se estava caindo
                            self.notify(PlayerEvent.PLAYER_LANDED)
                        self.y_pos = plat.y - self.height
                        self.y_vel = 0
                        collision_occurred = True
                        break
                # CASO 2: BATENDO A CABEÇA NO FUNDO DA PLATAFORMA
                if plat.type == "solid" and is_rising and was_bellow:
                    self.y_pos = plat.y + plat.height
                    self.y_vel = 0
                    collision_occurred = True
                    break

        # Aplica gravidade se não estivermos no chão de uma plataforma
        if not collision_occurred:
            if self.is_wall_sliding and self.horizontal_input_active:
                # Aplica uma gravidade reduzida e limita a velocidade de queda
                self.y_vel += self.wall_slide_gravity
                if self.y_vel > 2:
                    self.y_vel = 2
            else:
                self.y_vel += world_state["gravity"]

    def _apply_horizontal_physics(self, world_state: dict, delta_time: float):
        # Aplica movimento horizontal
        self.x_pos += self.x_vel

        player_rect = pr.Rectangle(self.x_pos, self.y_pos, self.width, self.height)
        is_colliding_with_wall = False

        for plat in world_state.get("platforms", []):
            if plat.type == "solid":
                plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)
                if pr.check_collision_recs(player_rect, plat_rect):
                    is_colliding_with_wall = True
                    # Corrige a posição baseado na direção do movimento original
                    if self.x_vel > 0:  # Movendo para a direita
                        self.x_pos = plat.x - self.width
                        self.x_vel = 0
                    elif self.x_vel < 0:  # Movendo para a esquerda
                        self.x_pos = plat.x + plat.width
                        self.x_vel = 0
                    # Se x_vel é 0, a posição já foi corrigida no frame anterior.
                    break  # Para após a primeira colisão

        # Atualiza o estado de wall slide baseado na colisão
        if is_colliding_with_wall and self.y_vel > 0 and not self.is_on_ground(world_state):
            self.is_wall_sliding = True
        else:
            self.is_wall_sliding = False

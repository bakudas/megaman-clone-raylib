# game/Player_state.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import pyray as pr

from game.weapon_states import ChargingState, FullyChargedState
from game.effects import AfterImage

# Forward declaration para evitar import circular
if TYPE_CHECKING:
    from game.player import Player


class PlayerState(ABC):
    """
    A classe base para todos os estados do jogador.
    Define a interface comum.
    """

    def __str__(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def handle_input(self, player: Player, input_direction: str) -> None:
        pass

    @abstractmethod
    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        pass


# --- Estados Concretos ---


class IdleState(PlayerState):
    def __init__(self, player: Player):
        player.x_vel = 0
        player.anim_manager.play("idle")

    def handle_input(self, player: Player, input_direction: str) -> None:
        if input_direction == "JUMP":
            player.jump()
            player.change_locomotion_state(JumpingState(player))
        elif input_direction == "DASH":
            if player.dash_cooldown_timer <= 0:
                player.change_locomotion_state(DashState(player))
        elif input_direction in ["LEFT", "RIGHT"]:
            # Ao receber um input de movimento, transiciona para Running
            # e imediatamente processa o input para definir a velocidade e a direção.
            new_state = RunningState(player)
            player.change_locomotion_state(new_state)
            new_state.handle_input(player, input_direction)

    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        # Consome o buffer de pulo se ele existir
        if player.jump_buffer_timer > 0:
            player.jump()
            player.jump_buffer_timer = 0
            player.change_locomotion_state(JumpingState(player))
            return

        if not player.is_on_ground(world_state):
            if player.y_vel < 0:
                player.change_locomotion_state(JumpingState(player))
            elif player.y_vel > 0:
                player.coyote_timer = player.COYOTE_TIMER_DURATION
                player.change_locomotion_state(FallingState(player))
            elif player.is_touching_wall_in_air(world_state):
                player.change_locomotion_state(WallSlidingState(player))


class RunningState(PlayerState):
    def __init__(self, player: Player):
        player.anim_manager.play("run")

    def handle_input(self, player: Player, input_direction: str) -> None:
        if input_direction == "JUMP":
            player.jump()
            player.change_locomotion_state(JumpingState(player))
        elif input_direction == "DASH":
            if player.dash_cooldown_timer <= 0:
                player.change_locomotion_state(DashState(player))
        elif input_direction == "STOP":
            player.x_vel = 0
            player.change_locomotion_state(IdleState(player))

        # A lógica de definir a velocidade agora considera o estado da arma
        current_speed = player.speed
        if isinstance(player.weapon_state, (ChargingState, FullyChargedState)):
            current_speed = player.charge_run_speed

        if input_direction == "RIGHT":
            player.x_vel = current_speed
            player.facing_direction = 'RIGHT'
        elif input_direction == "LEFT":
            player.x_vel = -current_speed
            player.facing_direction = 'LEFT'

    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        # Consome o buffer de pulo se ele existir
        if player.jump_buffer_timer > 0:
            player.jump()
            player.jump_buffer_timer = 0
            player.change_locomotion_state(JumpingState(player))
            return

        if not player.is_on_ground(world_state):
            player.coyote_timer = player.COYOTE_TIMER_DURATION
            player.change_locomotion_state(FallingState(player))


class JumpingState(PlayerState):
    def __init__(self, player: Player):
        player.anim_manager.play("jump")

    def handle_input(self, player: Player, input_direction: str) -> None:
        if input_direction == "JUMP":
            player.jump_buffer_timer = player.JUMP_BUFFER_DURATION

        if input_direction == "JUMP_RELEASE":
            if player.y_vel < 0:
                player.y_vel *= 0.5

        if input_direction == "RIGHT":
            player.x_vel = player.speed * player.air_control_factor
            player.facing_direction = 'RIGHT'
        elif input_direction == "LEFT":
            player.x_vel = -player.speed * player.air_control_factor
            player.facing_direction = 'LEFT'

    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        if player.y_vel >= 0:  # pico do pulo, começa a cair
            player.change_locomotion_state(FallingState(player))
        elif player.is_touching_wall_in_air(world_state) and player.horizontal_input_active:
            player.change_locomotion_state(WallSlidingState(player))


class FallingState(PlayerState):
    def __init__(self, player: Player) -> None:
        if player.first_fall:
            player.anim_manager.play("start")
            player.first_fall = False
        else:
            player.anim_manager.play("fall")

    def handle_input(self, player: Player, input_direction: str) -> None:
        if input_direction == "JUMP":
            if player.coyote_timer > 0:
                player.jump()
                player.coyote_timer = 0
                player.change_locomotion_state(JumpingState(player))
            else:
                player.jump_buffer_timer = player.JUMP_BUFFER_DURATION
        elif input_direction == "RIGHT":
            player.x_vel = player.speed * player.air_control_factor
            player.facing_direction = 'RIGHT'
        elif input_direction == "LEFT":
            player.x_vel = -player.speed * player.air_control_factor
            player.facing_direction = 'LEFT'

    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        if player.is_on_ground(world_state):
            player.change_locomotion_state(IdleState(player))
        elif player.is_touching_wall_in_air(world_state) and player.horizontal_input_active:
            player.change_locomotion_state(WallSlidingState(player))


class WallSlidingState(PlayerState):
    def __init__(self, player: Player) -> None:
        player.x_vel = 0
        player.anim_manager.play("wall_slide")

    def handle_input(self, player: Player, input_direction: str) -> None:
        if input_direction == "JUMP":
            player.wall_jump()
            player.change_locomotion_state(JumpingState(player))
        elif input_direction == "RIGHT":
            player.x_vel = player.speed
            player.facing_direction = 'RIGHT'
        elif input_direction == "LEFT":
            player.x_vel = -player.speed
            player.facing_direction = 'LEFT'

    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        if not player.is_wall_sliding:
            player.change_locomotion_state(FallingState(player))
        elif player.is_on_ground(world_state):
            player.change_locomotion_state(IdleState(player))


class DashState(PlayerState):
    def __init__(self, player: Player) -> None:
        # seta o timer
        self.timer = player.dash_duration
        self.spawn_fx_timer = 0.05
        player.anim_manager.play("dash")

        # aplica a velocidade do dach
        player.x_vel = (
            player.dash_speed
            if player.facing_direction == "RIGHT"
            else -player.dash_speed
        )

    def handle_input(self, player: Player, input_direction: str) -> None:
        if input_direction == "JUMP":
            player.jump()
            player.change_locomotion_state(JumpingState(player))

    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        # timer para o cooldown
        self.timer -= delta_time
        self.spawn_fx_timer -= delta_time

        # o dash ignora a gravidade momentaneamente
        player.y_vel = 0

        # pinta o player para feedback visual do dash
        player.color = pr.WHITE

        # Lógica para criar o rastro
        if self.spawn_fx_timer <= 0:
            self.spawn_fx_timer = 0.05
            after_image = AfterImage(player.x_pos, player.y_pos, player.width, player.height)
            world_state["after_images"].append(after_image)

        # estouro do timer
        if self.timer <= 0:
            # o dash ignora a gravidade momentaneamente
            player.x_vel = 0
            player.color = pr.SKYBLUE
            player.change_locomotion_state(IdleState(player))
            player.dash_cooldown_timer = player.dash_cooldown  # inicia o cooldown

class HurtingState(PlayerState):
    def __init__(self, player: Player) -> None:
        self.invincibility_timer = 1.0
        self.flash_timer = 0.0
        self.flash_interval = 0.1
        player.is_visible = False
        player.anim_manager.play("hit")

        # empurra o player para trás (knockback)
        player.y_vel = -player.jump_strength * 0.4
        player.x_vel = -player.knockback_force if player.facing_direction == 'RIGHT' else player.knockback_force

    def handle_input(self, player: Player, input_direction: str) -> None:
        pass

    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        self.invincibility_timer -= delta_time
        self.flash_timer -= delta_time

        if self.flash_timer <=0:
            self.flash_timer = self.flash_interval
            player.is_visible = not player.is_visible

        if self.invincibility_timer <= 0:
            player.is_visible = True
            player.change_locomotion_state(FallingState(player))

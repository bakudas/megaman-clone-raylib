# game/Player_state.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import pyray as pr


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

    def handle_input(self, player: Player, input_direction: str) -> None:
        if input_direction == "JUMP":
            player.jump()
            player.change_state(JumpingState())
        elif input_direction == "DASH":
            if player.dash_cooldown_timer <= 0:
                player.change_state(DashState(player))
        elif input_direction in ["LEFT", "RIGHT"]:
            player.change_state(RunningState())

    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        if player.is_touching_wall_in_air(world_state):
            player.change_state(WallSlidingState(player))
        elif not player.is_on_ground(world_state):
            if player.y_vel < 0:
                player.change_state(JumpingState())
            elif player.y_vel > 0:
                player.change_state(FallingState())


class RunningState(PlayerState):
    def handle_input(self, player: Player, input_direction: str) -> None:
        if input_direction == "JUMP":
            player.jump()
            player.change_state(JumpingState())
        elif input_direction == "DASH":
            if player.dash_cooldown_timer <= 0:
                player.change_state(DashState(player))
        elif input_direction == "RIGHT":
            player.x_vel = player.speed
            player.facing_direction = 'RIGHT'
        elif input_direction == "LEFT":
            player.x_vel = -player.speed
            player.facing_direction = 'LEFT'
        elif input_direction == "STOP":
            player.x_vel = 0
            player.change_state(IdleState(player))

    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        if not player.is_on_ground(world_state):
            player.change_state(FallingState())


class JumpingState(PlayerState):
    def handle_input(self, player: Player, input_direction: str) -> None:
        if input_direction == "RIGHT":
            player.x_vel = player.speed
            player.facing_direction = 'RIGHT'
        elif input_direction == "LEFT":
            player.x_vel = -player.speed
            player.facing_direction = 'LEFT'

    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        if player.y_vel >= 0:  # pico do pulo, começa a cair
            player.change_state(FallingState())
        elif player.is_touching_wall_in_air(world_state):
            player.change_state(WallSlidingState(player))


class FallingState(PlayerState):
    def handle_input(self, player: Player, input_direction: str) -> None:
        if input_direction == "RIGHT":
            player.x_vel = player.speed
            player.facing_direction = 'RIGHT'
        elif input_direction == "LEFT":
            player.x_vel = -player.speed
            player.facing_direction = 'LEFT'

    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        if player.is_on_ground(world_state):
            player.change_state(IdleState(player))
        elif player.is_touching_wall_in_air(world_state):
            player.change_state(WallSlidingState(player))


class WallSlidingState(PlayerState):
    def __init__(self, player: Player):
        player.x_vel = 0

    def handle_input(self, player: Player, input_direction: str) -> None:
        if input_direction == "JUMP":
            player.wall_jump()
            player.change_state(JumpingState())

    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        if not player.is_touching_wall_in_air(world_state):
            player.change_state(FallingState())
        elif player.is_on_ground(world_state):
            player.change_state(IdleState(player))


class DashState(PlayerState):
    def __init__(self, player: Player):
        # seta o timer
        self.timer = player.dash_duration

        # aplica a velocidade do dach
        player.x_vel = (
            player.dash_speed
            if player.facing_direction == "RIGHT"
            else -player.dash_speed
        )

        # o dash ignora a gravidade momentaneamente
        player.y_vel = 0

    def handle_input(self, player: Player, input_direction: str) -> None:
        # o jogador não tem controle durante o dash
        pass

    def update(self, player: Player, world_state: dict, delta_time: float) -> None:
        # timer para o cooldown
        self.timer -= delta_time

        # pinta o player para feedback visual do dash
        player.color = pr.WHITE

        # estou do timer
        if self.timer <= 0:
            # o dash ignora a gravidade momentaneamente
            player.x_vel = 0
            player.color = pr.SKYBLUE
            player.change_state(IdleState(player))
            player.dash_cooldown_timer = player.dash_cooldown  # inicia o cooldown
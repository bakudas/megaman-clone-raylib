# game/Player_state.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

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
    def update(self, player: Player, world_state: dict) -> None:
        pass


# --- Estados Concretos ---


class IdleState(PlayerState):
    def handle_input(self, player: Player, input_direction: str) -> None:
        if input_direction == "JUMP":
            player.jump()
            player.change_state(JumpingState())
        elif input_direction in ["LEFT", "RIGHT"] and not player.is_wall_sliding:
            player.change_state(RunningState())

    def update(self, player: Player, world_state: dict) -> None:
        if player.is_touching_wall(world_state):
            player.change_state(WallSlidingState())
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
        # se o jogador parar, o main.py enviará um input "STOP"
        elif input_direction == "STOP":
            player.change_state(IdleState())

    def update(self, player: Player, world_state: dict) -> None:
        if not player.is_on_ground(world_state):
            player.change_state(FallingState())
        elif player.is_wall_sliding:
            player.change_state(IdleState())


class JumpingState(PlayerState):
    def handle_input(self, player: Player, input_direction: str) -> None:
        # TODO: ajustar o air control
        pass

    def update(self, player: Player, world_state: dict) -> None:
        if player.y_vel >= 0:  # pico do pulo, começa a cair
            player.change_state(FallingState())
        elif player.is_wall_sliding:
            player.change_state(WallSlidingState())


class FallingState(PlayerState):
    def handle_input(self, player: Player, input_direction: str) -> None:
        # TODO: ajustar o air control
        pass

    def update(self, player: Player, world_state: dict) -> None:
        if player.is_on_ground(world_state):
            player.change_state(IdleState())
        elif player.is_wall_sliding:
            player.change_state(WallSlidingState())


class WallSlidingState(PlayerState):
    def handle_input(self, player: Player, input_direction: str) -> None:
        if input_direction == "JUMP":
            player.wall_jump()
            player.change_state(JumpingState())

    def update(self, player: Player, world_state: dict) -> None:
        if not player.is_wall_sliding:
            player.change_state(FallingState())
        elif player.is_on_ground(world_state):
            player.change_state(IdleState())

# game/weapon_states.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.player import Player

# --- Classe Base Abstrata para os Estados da Arma ---
class WeaponState(ABC):
    """
    A classe base para todos os estados da arma do jogador.
    Funciona como um contrato para garantir que todos os estados tenham os mesmos métodos.
    """
    def __str__(self):
        return self.__class__.__name__

    def handle_input(self, player: Player, input_action: str, world_state: dict):
        """Processa inputs relacionados à arma (pressionar/soltar o botão de tiro)."""
        pass

    def update(self, player: Player, delta_time: float, world_state: dict):
        """Atualiza a lógica interna do estado (ex: timers)."""
        pass

# --- Estados Concretos da Arma ---

class ReadyState(WeaponState):
    """A arma está ociosa e pronta para atirar ou começar a carregar."""
    def handle_input(self, player: Player, input_action: str, world_state: dict):
        # Quando o jogador APERTA o botão de tiro, começamos a carregar.
        if input_action == "SHOOT_PRESS":
            player.change_weapon_state(ChargingState())
            # TODO: add audio inicio carregando

class ChargingState(WeaponState):
    """A arma está acumulando energia."""
    def __init__(self):
        self.charge_timer = 0.0

    def update(self, player: Player, delta_time: float, world_state: dict):
        self.charge_timer += delta_time
        # Quando o tempo de carga é atingido, transita para o estado de carga completa.
        if self.charge_timer >= player.charge_duration:
            player.change_weapon_state(FullyChargedState())
            # TODO: add audio carga completa

    def handle_input(self, player: Player, input_action: str, world_state: dict):
        # Se o jogador SOLTAR o botão antes de carregar completamente...
        if input_action == "SHOOT_RELEASE":
            # ...dispara um tiro normal.
            player.fire_normal_shot(world_state)
            player.change_weapon_state(ReadyState())

class FullyChargedState(WeaponState):
    """A arma atingiu a carga máxima e a mantém até o jogador soltar o botão."""
    def handle_input(self, player: Player, input_action: str, world_state: dict):
        # Quando o jogador finalmente SOLTAR o botão...
        if input_action == "SHOOT_RELEASE":
            # ...dispara o tiro carregado.
            player.fire_charged_shot(world_state)
            player.change_weapon_state(ReadyState())
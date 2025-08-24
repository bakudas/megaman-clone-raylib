# game/weapon_states.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from game.world import World
from game.components import StateMachineComponent, CharacterControllerComponent
from game.events import PlayerEvent

# --- Classe Base Abstrata para os Estados da Arma ---
class WeaponState(ABC):
    """
    A classe base para todos os estados da arma do jogador.
    Funciona como um contrato para garantir que todos os estados tenham os mesmos métodos.
    """
    def __str__(self):
        return self.__class__.__name__

    def handle_input(self, world: World, entity_id: int, input_action: str, event_bus):
        """Processa inputs relacionados à arma (pressionar/soltar o botão de tiro)."""
        pass

    def update(self, world: World, entity_id: int, delta_time: float, event_bus):
        """Atualiza a lógica interna do estado (ex: timers)."""
        pass

# --- Estados Concretos da Arma ---

class ReadyState(WeaponState):
    """A arma está ociosa e pronta para atirar ou começar a carregar."""
    def handle_input(self, world: World, entity_id: int, input_action: str, event_bus):
        # Quando o jogador APERTA o botão de tiro, começamos a carregar.
        if input_action == "SHOOT_PRESS":
            event_bus.publish(PlayerEvent.WEAPON_CHARGE_START)
            state_machine = world.components[StateMachineComponent][entity_id]
            state_machine.weapon_state = ChargingState()

class ChargingState(WeaponState):
    """A arma está acumulando energia."""
    def __init__(self):
        self.charge_timer = 0.0

    def update(self, world: World, entity_id: int, delta_time: float, event_bus):
        self.charge_timer += delta_time
        control = world.components[CharacterControllerComponent][entity_id]
        state_machine = world.components[StateMachineComponent][entity_id]

        # Quando o tempo de carga é atingido, transita para o estado de carga completa.
        if self.charge_timer >= control.dash_duration: # Usando dash_duration como placeholder para charge_duration
            event_bus.publish(PlayerEvent.WEAPON_CHARGE_COMPLETE)
            state_machine.weapon_state = FullyChargedState()

    def handle_input(self, world: World, entity_id: int, input_action: str, event_bus):
        # Se o jogador SOLTAR o botão antes de carregar completamente...
        if input_action == "SHOOT_RELEASE":
            # ...dispara um tiro normal.
            event_bus.publish(PlayerEvent.PLAYER_WANTS_TO_SHOOT, shooter_id=entity_id, shot_type='normal')
            state_machine = world.components[StateMachineComponent][entity_id]
            state_machine.weapon_state = ReadyState()

class FullyChargedState(WeaponState):
    """A arma atingiu a carga máxima e a mantém até o jogador soltar o botão."""
    def handle_input(self, world: World, entity_id: int, input_action: str, event_bus):
        # Quando o jogador finalmente SOLTAR o botão...
        if input_action == "SHOOT_RELEASE":
            # ...dispara o tiro carregado.
            event_bus.publish(PlayerEvent.PLAYER_WANTS_TO_SHOOT, shooter_id=entity_id, shot_type='charged')
            state_machine = world.components[StateMachineComponent][entity_id]
            state_machine.weapon_state = ReadyState()
# game/enemy_states.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from game.world import World
from game.components import PhysicsComponent, EnemyAIComponent, PhysicsStatusComponent

class EnemyState(ABC):
    """
    Classe base para os estados do inimigo
    """
    def __init__(self, world: World, entity_id: int):
        pass

    def __str__(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def update(self, world: World, entity_id: int, delta_time: float) -> None:
        pass

# --- Estados Concretos ---

class PatrollingState(EnemyState):
    """
    O inimigo deve se mover numa direção até encontrar uma beirada
    """
    def __init__(self, world: World, entity_id: int) -> None:
        physics = world.components[PhysicsComponent][entity_id]
        ai = world.components[EnemyAIComponent][entity_id]
        # define a velocidade inicial baseada na direção
        physics.x_vel = ai.speed if physics.facing_direction == "RIGHT" else -ai.speed

    def update(self, world: World, entity_id: int, delta_time: float) -> None:
        ai = world.components[EnemyAIComponent][entity_id]
        status = world.components[PhysicsStatusComponent].get(entity_id)

        # usa o sensor is_ground_ahead para checar a plataforma
        # A checagem de "ground_ahead" agora é parte do PhysicsSystem e reflete no status.
        # Por simplicidade aqui, vamos assumir que se o inimigo está no chão mas não tem chão à frente, ele vira.
        # Uma implementação mais robusta teria um "sensor" no PhysicsSystem.
        if status and status.is_on_ground:
            # se não tiver chão, vire
            # TODO: Adicionar uma checagem de "chão à frente" no PhysicsSystem
            pass

class TurningState(EnemyState):
    """
    O inimigo para, inverte a sua direção e volta a patrulhar
    """
    def __init__(self, world: World, entity_id: int) -> None:
        physics = world.components[PhysicsComponent][entity_id]
        # para
        physics.x_vel = 0
        # inverte a direção
        physics.facing_direction = "RIGHT" if physics.facing_direction == "LEFT" else "LEFT"

    def update(self, world: World, entity_id: int, delta_time: float) -> None:
        ai = world.components[EnemyAIComponent][entity_id]
        # transição para patrulhar novamente
        # TODO: animação de virada
        ai.state = PatrollingState(world, entity_id)


# --- Estados do Inimigo Jumper ---

class JumperIdleState(EnemyState):
    """O inimigo jumper espera no lugar."""
    def __init__(self, world: World, entity_id: int) -> None:
        physics = world.get_component(entity_id, PhysicsComponent)
        if physics:
            physics.x_vel = 0
            physics.y_vel = 0

    def update(self, world: World, entity_id: int, delta_time: float, status: PhysicsStatusComponent) -> None:
        # A lógica de decisão (quando pular) será feita pelo AISystem.
        # Este estado apenas espera.
        pass

    def handle_input(self, world: World, entity_id: int, action_name: str) -> None:
        """Reage a comandos do AISystem."""
        if action_name == "JUMP_ATTACK":
            ai = world.get_component(entity_id, EnemyAIComponent)
            if ai:
                ai.state = JumperJumpAttackState(world, entity_id)


class JumperJumpAttackState(EnemyState):
    """O inimigo pula em direção ao seu alvo."""
    def __init__(self, world: World, entity_id: int) -> None:
        ai_control = world.get_component(entity_id, AIControllerComponent)
        char_control = world.get_component(entity_id, CharacterControllerComponent)
        physics = world.get_component(entity_id, PhysicsComponent)
        transform = world.get_component(entity_id, TransformComponent)
        
        if not all([ai_control, char_control, physics, transform]):
            return

        # Pula
        physics.y_vel = -char_control.jump_strength

        # Define a velocidade X para ir em direção ao alvo
        target_transform = world.get_component(ai_control.target_entity_id, TransformComponent)
        if target_transform:
            direction_to_target = 1 if target_transform.x > transform.x else -1
            physics.x_vel = char_control.speed * direction_to_target
            physics.facing_direction = "RIGHT" if direction_to_target > 0 else "LEFT"

    def update(self, world: World, entity_id: int, delta_time: float, status: PhysicsStatusComponent) -> None:
        # Quando o inimigo atingir o chão, ele volta para o estado Idle.
        ai = world.get_component(entity_id, EnemyAIComponent)
        if status and ai and status.landed_this_frame:
            ai.state = JumperIdleState(world, entity_id)

    def handle_input(self, world: World, entity_id: int, action_name: str) -> None:
        pass # Não reage a inputs enquanto estiver no ar

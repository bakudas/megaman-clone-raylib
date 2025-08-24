# game/components.py
from dataclasses import dataclass
import pyray as pr
from typing import Any
from game.animation import AnimationManager

@dataclass
class TransformComponent:
    x: float
    y: float
    width: int
    height: int

@dataclass
class PhysicsComponent:
    x_vel: float = 0.0
    y_vel: float = 0.0
    facing_direction: str = "RIGHT"

@dataclass
class HealthComponent:
    current_health: int
    max_health: int
    lives: int = 3

@dataclass
class InputReceiverComponent:
    """Marca uma entidade como sendo controlável pelo jogador."""
    pass


@dataclass
class CharacterControllerComponent:
    """Dados para controle de um personagem (jogador ou IA)."""
    speed: float
    charge_run_speed: float
    jump_strength: float
    dash_speed: float
    dash_duration: float
    dash_cooldown: float
    dash_cooldown_timer: float = 0.0
    horizontal_input_active: bool = False
    coyote_timer: float = 0.0
    jump_buffer_timer: float = 0.0
    jump_buffer_duration: float = 0.1 # O tempo que um pulo fica na "memória"
    air_control_factor: float = 0.75 # A porcentagem de controle no ar

@dataclass
class AnimationComponent:
    anim_manager: AnimationManager
    is_visible: bool = True

@dataclass
class StateMachineComponent:
    # O 'Any' é usado aqui porque os estados ainda não foram totalmente refatorados
    # para remover a dependência do objeto Player.
    state: Any
    weapon_state: Any

@dataclass
class CollisionComponent:
    """Define a forma e o tipo de colisão de uma entidade."""
    # Usaremos isso mais tarde para um sistema de colisão genérico
    collider_rect: pr.Rectangle
    collision_layer: str # ex: 'player', 'enemy', 'player_bullet'

@dataclass
class PhysicsStatusComponent:
    """Armazena o resultado das checagens de física para que outros sistemas possam reagir."""
    is_on_ground: bool = False
    is_on_wall: bool = False
    landed_this_frame: bool = False
    # Adicione outras flags conforme necessário (ex: is_on_ceiling)

@dataclass
class EnemyAIComponent:
    """Armazena dados e estado para a IA de um inimigo."""
    speed: float
    state: Any # O estado atual da FSM da IA

@dataclass
class AIControllerComponent:
    """Marca uma entidade como sendo controlada por IA e guarda seus dados."""
    target_entity_id: int = -1
    attack_cooldown: float = 2.0 # segundos
    cooldown_timer: float = 0.0


@dataclass
class BulletComponent:
    """Marca uma entidade como uma bala e armazena seus dados."""
    damage: int
    lifespan: float = 2.0 # segundos

@dataclass
class ToBeDestroyedComponent:
    """Um componente marcador para sinalizar que uma entidade deve ser removida no final do frame."""
    pass

@dataclass
class InvincibilityComponent:
    """Adiciona invencibilidade temporária a uma entidade."""
    duration: float = 0.5 # Duração em segundos
    timer: float = 0.5

@dataclass
class LootDropComponent:
    """Define os itens e as chances de drop de uma entidade ao ser destruída."""
    # Dicionário: { "caminho/do/archetipo.json": chance (0.0 a 1.0) }
    drop_table: dict[str, float]


@dataclass
class PickupComponent:
    """Marca uma entidade como um item coletável."""
    type: str  # ex: "HEALTH"
    value: int # ex: 10 (quantidade de vida a curar)


@dataclass
class SpriteComponent:
    """Um componente para entidades que têm um sprite simples em vez de uma animação completa."""
    color: pr.Color
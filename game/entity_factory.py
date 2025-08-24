# game/entity_factory.py
import pyray as pr
from game.world import World
from game.components import (
    TransformComponent, PhysicsComponent, HealthComponent, CharacterControllerComponent, InputReceiverComponent,
    AnimationComponent, StateMachineComponent, CollisionComponent, PhysicsStatusComponent, SpriteComponent,
    EnemyAIComponent, BulletComponent
)
from game.animation import AnimationManager
from game.player_states import FallingState, IdleState
from game.enemy_states import PatrollingState
from game.weapon_states import ReadyState, WeaponState

from game.archetype_loader import create_entity_from_archetype

def create_player(world: World, x: float, y: float) -> int:
    """Cria a entidade do jogador a partir de seu arquétipo."""
    return create_entity_from_archetype(world, "levels/archetypes/player.json", x, y)



def create_bullet(world: World, x: float, y: float, x_vel: float, shot_type: str) -> int:
    """Cria uma entidade de bala no mundo."""
    bullet_id = world.create_entity()
    width, height, damage = (24, 12, 2) if shot_type == 'charged' else (10, 5, 1)
    world.add_component(bullet_id, TransformComponent(x=x, y=y, width=width, height=height))
    world.add_component(bullet_id, PhysicsComponent(x_vel=x_vel))
    world.add_component(bullet_id, BulletComponent(damage=damage))
    world.add_component(bullet_id, SpriteComponent(color=pr.YELLOW if shot_type == 'normal' else pr.RED))
    world.add_component(bullet_id, CollisionComponent(collider_rect=pr.Rectangle(x, y, width, height), collision_layer='player_bullet'))
    return bullet_id
# game/systems.py
import random
from game.world import World
from game.input_manager import InputManager, GameAction
from game.components import TransformComponent, PhysicsComponent, CharacterControllerComponent, InputReceiverComponent, StateMachineComponent, AnimationComponent, PhysicsStatusComponent, CollisionComponent, BulletComponent, HealthComponent, ToBeDestroyedComponent, EnemyAIComponent, AIControllerComponent, SpriteComponent
from game.camera import Camera
from game.quadtree import Quadtree
from game.event_bus import EventBus
from game.events import PlayerEvent, SystemEvent, EnemyEvent, InputEvent
from game.sfx_manager import SFXManager
from game.pickup import Pickup
from game.entity_factory import create_bullet
import pyray as pr

class System:
    def update(self, world: World, delta_time: float):
        pass


class InputSystem(System):
    def __init__(self, input_manager: InputManager, event_bus: EventBus):
        self.input_manager = input_manager
        self.event_bus = event_bus

    def update(self, world: World, delta_time: float):
        # Encontra a entidade do jogador
        player_entities = world.get_entities_with_components(InputReceiverComponent, CharacterControllerComponent)
        if not player_entities:
            return

        player_id = player_entities[0]
        control = world.components[CharacterControllerComponent][player_id]

        # --- Inputs da Arma ---
        if self.input_manager.is_action_pressed(GameAction.SHOOT):
            self.event_bus.publish(InputEvent.ACTION, entity_id=player_id, action_name="SHOOT_PRESS")
        if self.input_manager.is_action_released(GameAction.SHOOT):
            self.event_bus.publish(InputEvent.ACTION, entity_id=player_id, action_name="SHOOT_RELEASE")

        # --- Inputs de Locomoção ---
        if self.input_manager.is_action_pressed(GameAction.JUMP):
            self.event_bus.publish(InputEvent.ACTION, entity_id=player_id, action_name="JUMP")
        if self.input_manager.is_action_released(GameAction.JUMP):
            self.event_bus.publish(InputEvent.ACTION, entity_id=player_id, action_name="JUMP_RELEASE")
        if self.input_manager.is_action_pressed(GameAction.DASH):
            self.event_bus.publish(InputEvent.ACTION, entity_id=player_id, action_name="DASH")

        # Movimento Horizontal
        control.horizontal_input_active = False
        if self.input_manager.is_action_down(GameAction.MOVE_RIGHT):
            self.event_bus.publish(InputEvent.ACTION, entity_id=player_id, action_name="RIGHT")
            control.horizontal_input_active = True
        elif self.input_manager.is_action_down(GameAction.MOVE_LEFT):
            self.event_bus.publish(InputEvent.ACTION, entity_id=player_id, action_name="LEFT")
            control.horizontal_input_active = True

        if not control.horizontal_input_active:
            self.event_bus.publish(InputEvent.ACTION, entity_id=player_id, action_name="STOP")


class StateMachineSystem(System):
    def __init__(self, world: World, event_bus: EventBus):
        self.world = world
        self.event_bus = event_bus
        self.event_bus.subscribe(InputEvent.ACTION, self.on_input_action)

    def on_input_action(self, entity_id: int, action_name: str):
        state_machine = self.world.get_component(entity_id, StateMachineComponent)
        if state_machine:
            # O input da arma é direcionado para a FSM da arma
            if "SHOOT" in action_name:
                 state_machine.weapon_state.handle_input(self.world, entity_id, action_name, self.event_bus)
            # O resto vai para a FSM de locomoção
            else:
                state_machine.state.handle_input(self.world, entity_id, action_name)

    def update(self, world: World, delta_time: float):
        player_entities = world.get_entities_with_components(StateMachineComponent, CharacterControllerComponent, PhysicsStatusComponent)
        for entity_id in player_entities:
            state_machine = world.components[StateMachineComponent][entity_id]
            status = world.components[PhysicsStatusComponent][entity_id]
            # Passa o status da física para o estado, permitindo que ele reaja
            state_machine.state.update(world, entity_id, delta_time, status)
            state_machine.weapon_state.update(world, entity_id, delta_time, self.event_bus)

class EnemyAISystem(System):
    def update(self, world: World, delta_time: float):
        entities = world.get_entities_with_components(EnemyAIComponent, PhysicsComponent, TransformComponent)
        for entity_id in entities:
            ai = world.components[EnemyAIComponent][entity_id]
            ai.state.update(world, entity_id, delta_time)


class PhysicsSystem(System):
    def __init__(self, gravity: float, quadtree: Quadtree):
        self.gravity = gravity
        self.quadtree = quadtree

    def update(self, world: World, delta_time: float):
        entities = world.get_entities_with_components(TransformComponent, PhysicsComponent, PhysicsStatusComponent)
        for entity_id in entities:
            transform = world.components[TransformComponent][entity_id]
            physics = world.components[PhysicsComponent][entity_id]
            status = world.components[PhysicsStatusComponent][entity_id]

            # Reset status flags for this frame
            status.landed_this_frame = False
            status.is_on_ground = False
            status.is_on_wall = False

            # 1. Aplica gravidade
            physics.y_vel += self.gravity

            # --- Colisão e Movimento no Eixo X ---
            transform.x += physics.x_vel
            entity_rect = pr.Rectangle(transform.x, transform.y, transform.width, transform.height)

            nearby_platforms = []
            self.quadtree.retrieve(nearby_platforms, entity_rect)

            for plat in nearby_platforms:
                if plat.type == 'no_collision': continue
                
                plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)
                if pr.check_collision_recs(entity_rect, plat_rect):
                    if physics.x_vel > 0:  # Movendo para a direita
                        transform.x = plat.x - transform.width
                    elif physics.x_vel < 0:  # Movendo para a esquerda
                        transform.x = plat.x + plat.width
                    physics.x_vel = 0
                    status.is_on_wall = True
                    entity_rect.x = transform.x # Atualiza o rect para a próxima checagem no mesmo frame

            # --- Colisão e Movimento no Eixo Y ---
            previous_y = transform.y
            transform.y += physics.y_vel
            entity_rect.y = transform.y

            for plat in nearby_platforms:
                if plat.type == 'no_collision': continue

                plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)
                if pr.check_collision_recs(entity_rect, plat_rect):
                    # Checa se a entidade está caindo
                    if physics.y_vel > 0:
                        # A condição was_above garante que só colidimos com o topo da plataforma
                        was_above = (previous_y + transform.height) <= plat.y
                        if was_above:
                            transform.y = plat.y - transform.height
                            physics.y_vel = 0
                            if not status.is_on_ground: # Evita que landed_this_frame seja True por vários frames
                                status.landed_this_frame = True
                            status.is_on_ground = True
                            entity_rect.y = transform.y
                    
                    # Checa se a entidade está subindo (e se a plataforma é sólida)
                    elif physics.y_vel < 0 and plat.type == 'solid':
                        was_below = previous_y >= (plat.y + plat.height)
                        if was_below:
                            transform.y = plat.y + plat.height
                            physics.y_vel = 0
                            entity_rect.y = transform.y

            # Atualiza o collider para o próximo frame/sistema
            collision_comp = world.get_component(entity_id, CollisionComponent)
            if collision_comp:
                collision_comp.collider_rect.x = transform.x
                collision_comp.collider_rect.y = transform.y


class AnimationSystem(System):
    def update(self, world: World, delta_time: float):
        entities = world.get_entities_with_components(AnimationComponent, PhysicsComponent)
        for entity_id in entities:
            animation = world.components[AnimationComponent][entity_id]
            physics = world.components[PhysicsComponent][entity_id]

            animation.anim_manager.flip_horizontal = (physics.facing_direction == 'LEFT')
            animation.anim_manager.update(delta_time)


class CameraSystem(System):
    def __init__(self, camera: Camera):
        self.camera = camera

    def update(self, world: World, delta_time: float):
        player_entities = world.get_entities_with_components(InputReceiverComponent, TransformComponent)
        if player_entities:
            player_id = player_entities[0]
            self.camera.update_ecs(world, player_id)


class RenderSystem(System):
    def draw(self, world: World):
        # Desenha entidades animadas
        animated_entities = world.get_entities_with_components(TransformComponent, AnimationComponent)
        for entity_id in animated_entities:
            transform = world.components[TransformComponent][entity_id]
            animation = world.components[AnimationComponent][entity_id]

            if animation.is_visible:
                # O offset de desenho pode precisar de ajuste para alinhar o sprite com a caixa de colisão
                draw_y = transform.y - 13 # Valor ajustado para o sprite sheet
                animation.anim_manager.draw(transform.x, draw_y)

        # Desenha entidades com sprites simples (como balas)
        sprite_entities = world.get_entities_with_components(TransformComponent, SpriteComponent)
        for entity_id in sprite_entities:
            transform = world.components[TransformComponent][entity_id]
            sprite = world.components[SpriteComponent][entity_id]
            pr.draw_rectangle(int(transform.x), int(transform.y), transform.width, transform.height, sprite.color)

class ShootingSystem(System):
    """Ouve por eventos de tiro e cria as entidades de bala."""
    def __init__(self, world: World, event_bus: EventBus):
        self.world = world
        self.event_bus = event_bus
        self.event_bus.subscribe(PlayerEvent.PLAYER_WANTS_TO_SHOOT, self.on_wants_to_shoot)

    def on_wants_to_shoot(self, shooter_id: int, shot_type: str):
        transform = self.world.components.get(TransformComponent, {}).get(shooter_id)
        physics = self.world.components.get(PhysicsComponent, {}).get(shooter_id)
        if not transform or not physics: return

        bullet_speed = 6.0
        start_y = transform.y + (transform.height / 2) - (6 if shot_type == 'charged' else 2)
        start_x = transform.x + transform.width if physics.facing_direction == 'RIGHT' else transform.x
        final_vel = bullet_speed if physics.facing_direction == 'RIGHT' else -bullet_speed

        create_bullet(self.world, start_x, start_y, final_vel, shot_type)
        self.event_bus.publish(PlayerEvent.PLAYER_SHOT)

class GameStateSystem(System):
    """Gerencia o estado geral do jogo, como morte e game over."""
    def __init__(self, world: World, event_bus: EventBus):
        self.world = world
        self.event_bus = event_bus
        self.event_bus.subscribe(SystemEvent.PLAYER_DIED_EVENT, self.on_player_death)

    def on_player_death(self, player_id: int):
        health = self.world.components[HealthComponent].get(player_id)
        if not health: return

        health.lives -= 1
        print(f"Player died. Lives remaining: {health.lives}")
        # TODO: Implementar a lógica de respawn ou game over aqui.
        # Por exemplo, publicar um evento de GAME_OVER se health.lives <= 0

class CollisionSystem(System):
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def update(self, world: World, delta_time: float):
        collidables = world.get_entities_with_components(TransformComponent, CollisionComponent)
        # Otimização: N^2 é ruim, mas para poucos objetos é aceitável.
        # Uma Quadtree seria a solução ideal para jogos maiores.
        for i in range(len(collidables)):
            for j in range(i + 1, len(collidables)):
                entity_a_id = collidables[i]
                entity_b_id = collidables[j]

                rect_a = world.components[CollisionComponent][entity_a_id].collider_rect
                rect_b = world.components[CollisionComponent][entity_b_id].collider_rect

                if pr.check_collision_recs(rect_a, rect_b):
                    self.event_bus.publish(SystemEvent.COLLISION, entity_a=entity_a_id, entity_b=entity_b_id)

class DamageSystem(System):
    def __init__(self, world: World, event_bus: EventBus):
        self.world = world
        self.event_bus = event_bus
        self.event_bus.subscribe(SystemEvent.COLLISION, self.on_collision)

    def on_collision(self, entity_a: int, entity_b: int):
        # Lógica de dano: Bala do jogador vs Inimigo
        self._handle_bullet_vs_enemy(entity_a, entity_b)
        self._handle_bullet_vs_enemy(entity_b, entity_a) # Checa na ordem inversa também

        # Lógica de dano: Jogador vs Inimigo
        self._handle_player_vs_enemy(entity_a, entity_b)
        self._handle_player_vs_enemy(entity_b, entity_a)

    def _handle_bullet_vs_enemy(self, id_a: int, id_b: int):
        # Checa se A é uma bala e B é um inimigo
        if (BulletComponent in self.world.components and id_a in self.world.components[BulletComponent] and
            EnemyAIComponent in self.world.components and id_b in self.world.components[EnemyAIComponent]):

            # Pega os componentes relevantes
            bullet = self.world.components[BulletComponent][id_a]
            enemy_health = self.world.components[HealthComponent].get(id_b)

            if enemy_health:
                enemy_health.current_health -= bullet.damage
                print(f"Enemy {id_b} took {bullet.damage} damage. Health is now {enemy_health.current_health}")
                self.event_bus.publish(EnemyEvent.ENEMY_HURT, enemy_id=id_b) # Para som de hit

                if enemy_health.current_health <= 0:
                    self.world.add_component(id_b, ToBeDestroyedComponent())
                    self.event_bus.publish(EnemyEvent.ENEMY_DESTROYED, enemy_id=id_b)

            # Marca a bala para ser destruída
            self.world.add_component(id_a, ToBeDestroyedComponent())

    def _handle_player_vs_enemy(self, id_a: int, id_b: int):
        # Checa se A é o jogador e B é um inimigo
        if (InputReceiverComponent in self.world.components and id_a in self.world.components[InputReceiverComponent] and
            EnemyAIComponent in self.world.components and id_b in self.world.components[EnemyAIComponent]):

            # Se o jogador já estiver invencível, não faz nada
            if self.world.get_component(id_a, InvincibilityComponent):
                return

            player_health = self.world.components[HealthComponent].get(id_a)
            if player_health:
                player_health.current_health -= 5 # Dano de toque
                self.event_bus.publish(PlayerEvent.PLAYER_HURT, player_id=id_a)
                
                # Adiciona invencibilidade
                self.world.add_component(id_a, InvincibilityComponent())

                if player_health.current_health <= 0:
                    self.event_bus.publish(SystemEvent.PLAYER_DIED_EVENT, player_id=id_a)

class PickupSystem(System):
    """Lida com a colisão entre o jogador e os itens coletáveis."""
    def __init__(self, world: World, event_bus: EventBus):
        self.world = world
        self.event_bus = event_bus
        self.event_bus.subscribe(SystemEvent.COLLISION, self.on_collision)

    def on_collision(self, entity_a: int, entity_b: int):
        # Checa ambas as direções da colisão
        self._handle_pickup(entity_a, entity_b)
        self._handle_pickup(entity_b, entity_a)

    def _handle_pickup(self, id_a: int, id_b: int):
        # Checa se A é o jogador e B é um pickup
        is_player = self.world.get_component(id_a, InputReceiverComponent) is not None
        pickup = self.world.get_component(id_b, PickupComponent)

        if not is_player or not pickup:
            return

        if pickup.type == "HEALTH":
            player_health = self.world.get_component(id_a, HealthComponent)
            if player_health and player_health.current_health < player_health.max_health:
                player_health.current_health = min(player_health.max_health, player_health.current_health + pickup.value)
                self.event_bus.publish(PlayerEvent.PLAYER_HEALED, amount=pickup.value)
                self.world.add_component(id_b, ToBeDestroyedComponent()) # Destroi o pickup


class SoundSystem(System):
    """Ouve eventos do jogo e toca os sons correspondentes."""
    def __init__(self, event_bus: EventBus, sfx_manager: SFXManager):
        self.sfx_manager = sfx_manager
        event_bus.subscribe(PlayerEvent.PLAYER_JUMPED, lambda **kwargs: self.sfx_manager.play("jump"))
        event_bus.subscribe(PlayerEvent.PLAYER_SHOT, lambda **kwargs: self.sfx_manager.play("shoot"))
        event_bus.subscribe(EnemyEvent.ENEMY_HURT, lambda **kwargs: self.sfx_manager.play("hit"))
        event_bus.subscribe(PlayerEvent.PLAYER_HEALED, lambda **kwargs: self.sfx_manager.play("heal"))
        event_bus.subscribe(PlayerEvent.PLAYER_LANDED, lambda **kwargs: self.sfx_manager.play("jump"))
        event_bus.subscribe(EnemyEvent.ENEMY_DESTROYED, lambda **kwargs: self.sfx_manager.play("explosion"))
        event_bus.subscribe(PlayerEvent.WEAPON_CHARGE_START, lambda **kwargs: self.sfx_manager.play("charge_start"))
        event_bus.subscribe(PlayerEvent.WEAPON_CHARGE_COMPLETE, lambda **kwargs: self.sfx_manager.play("charge_complete"))

from game.archetype_loader import create_entity_from_archetype

class DropSystem(System):
    """Ouve a morte de inimigos e gerencia o drop de itens."""
    def __init__(self, world: World, event_bus: EventBus):
        self.world = world
        self.event_bus = event_bus
        self.event_bus.subscribe(EnemyEvent.ENEMY_DESTROYED, self.on_enemy_destroyed)

    def on_enemy_destroyed(self, enemy_id: int):
        loot_comp = self.world.get_component(enemy_id, LootDropComponent)
        transform = self.world.get_component(enemy_id, TransformComponent)

        if not loot_comp or not transform:
            return

        for archetype_path, chance in loot_comp.drop_table.items():
            if random.random() < chance:
                print(f"Inimigo {enemy_id} dropou {archetype_path}")
                create_entity_from_archetype(self.world, archetype_path, transform.x, transform.y)


# TODO: Implementar um VFXSystem que ouve eventos e cria entidades de partículas.

class CleanupSystem(System):
    """Remove entidades marcadas para destruição no final do frame."""
    def update(self, world: World, delta_time: float):
        entities_to_destroy = world.get_entities_with_components(ToBeDestroyedComponent)
        for entity_id in entities_to_destroy:
            # Remove todos os componentes associados a esta entidade
            for component_list in world.components.values():
                if entity_id in component_list:
                    del component_list[entity_id]


class AISystem(System):
    """Sistema de decisão para entidades controladas por IA."""
    def __init__(self, world: World, event_bus: EventBus):
        self.world = world
        self.event_bus = event_bus
        self.detection_radius = 200 # Raio para o inimigo detectar o jogador

    def update(self, world: World, delta_time: float):
        # 1. Encontra o jogador
        player_entities = world.get_entities_with_components(InputReceiverComponent, TransformComponent)
        if not player_entities:
            return # Sem jogador, sem IA
        player_id = player_entities[0]
        player_transform = world.get_component(player_id, TransformComponent)

        # 2. Itera sobre todas as entidades com IA
        ai_entities = world.get_entities_with_components(AIControllerComponent, TransformComponent, EnemyAIComponent)
        for entity_id in ai_entities:
            ai_control = world.get_component(entity_id, AIControllerComponent)
            ai_transform = world.get_component(entity_id, TransformComponent)
            enemy_fsm = world.get_component(entity_id, EnemyAIComponent)

            # Atualiza o alvo da IA
            ai_control.target_entity_id = player_id

            # Atualiza o timer de cooldown
            if ai_control.cooldown_timer > 0:
                ai_control.cooldown_timer -= delta_time

            # 3. Lógica de Decisão (apenas se estiver no estado Idle)
            is_idle = isinstance(enemy_fsm.state, JumperIdleState)
            if not is_idle or ai_control.cooldown_timer > 0:
                continue

            # Calcula a distância até o jogador
            distance_x = abs(player_transform.x - ai_transform.x)
            distance_y = abs(player_transform.y - ai_transform.y)

            # 4. Se estiver no alcance, publica o evento de ataque
            if distance_x < self.detection_radius and distance_y < self.detection_radius:
                print(f"[AISystem] Inimigo {entity_id} detectou o jogador. Atacando!")
                self.event_bus.publish(InputEvent.ACTION, entity_id=entity_id, action_name="JUMP_ATTACK")
                ai_control.cooldown_timer = ai_control.attack_cooldown # Reseta o cooldown


class InvincibilitySystem(System):
    """Gerencia os timers de invencibilidade e o piscar do sprite."""
    def update(self, world: World, delta_time: float):
        entities = world.get_entities_with_components(InvincibilityComponent, AnimationComponent)
        
        entities_to_remove_inv = []

        for entity_id in entities:
            inv_comp = world.get_component(entity_id, InvincibilityComponent)
            anim_comp = world.get_component(entity_id, AnimationComponent)

            inv_comp.timer -= delta_time

            if inv_comp.timer <= 0:
                entities_to_remove_inv.append(entity_id)
                anim_comp.is_visible = True # Garante que a entidade esteja visível ao final
            else:
                # Lógica para piscar o sprite
                anim_comp.is_visible = int(inv_comp.timer * 10) % 2 == 0

        # Remove o componente das entidades cujo timer expirou
        for entity_id in entities_to_remove_inv:
            world.remove_component(entity_id, InvincibilityComponent)
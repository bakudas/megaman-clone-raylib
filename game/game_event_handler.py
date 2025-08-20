# game/game_event_handler.py
import random

from game.observer import Observer
from game.events import PlayerEvent, EnemyEvent
from game.pickup import Pickup
from game.sfx_manager import SFXManager
from game.effects import spawn_explosion, Particle


class SoundEventHandler(Observer):
    """Ouve eventos do jogo e toca os sons correspondentes."""
    def __init__(self, sfx_manager: SFXManager):
        self.sfx_manager = sfx_manager

    def on_notify(self, event, **kwargs):
        if event == PlayerEvent.PLAYER_JUMPED:
            self.sfx_manager.play("jump")
        elif event == PlayerEvent.PLAYER_SHOT:
            self.sfx_manager.play("shoot")
        elif event == PlayerEvent.PLAYER_HURT:
            self.sfx_manager.play("hit")
        elif event == PlayerEvent.PLAYER_HEALED:
            self.sfx_manager.play("heal")
        elif event == EnemyEvent.ENEMY_DESTROYED:
            self.sfx_manager.play("explosion")


class VFXEventHandler(Observer):
    """Ouve eventos do jogo e cria os efeitos visuais correspondentes."""
    def __init__(self, world_state: dict):
        self.world_state = world_state

    def on_notify(self, event, **kwargs):
        if event == EnemyEvent.ENEMY_DESTROYED:
            enemy = kwargs.get("enemy")
            spawn_explosion(self.world_state, enemy.x_pos + enemy.width / 2, enemy.y_pos + enemy.height / 2)

    def spawn_explosion(self, world_state: dict, x, y):
        """
        Cria uma explosão na posição especificada.
        """
        fx = Particle(world_state, x, y)
        self.world_state["particles"].append(fx)


class DropSystemHandler(Observer):
    """
    Ouve a morte de inimigos e gerencia o drop de itens.
    """
    def __init__(self, world_state: dict):
        self.world_state = world_state

    def on_notify(self, event, **kwargs):
        if event == EnemyEvent.ENEMY_DESTROYED:
            enemy = kwargs.get("enemy")
            if not enemy: return

            if random.random() < enemy.drop_rate:
                print(f"Spawning pickup at ({enemy.x_pos}, {enemy.y_pos})")
                pickup = Pickup(enemy.x_pos, enemy.y_pos)
                self.world_state["pickups"].append(pickup)

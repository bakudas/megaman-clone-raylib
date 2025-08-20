# game/game_event_handler.py
import random
from game.observer import Observer
from game.events import PlayerEvent, EnemyEvent
from game.pickup import Pickup
from game.sfx_manager import SFXManager

class GameEventHandler(Observer):
    def __init__(self, world_state: dict, sfx_manager: SFXManager):
        self.world_state = world_state
        self.sfx_manager = sfx_manager

    def on_notify(self, event, **kwargs):
        if event == EnemyEvent.ENEMY_DESTROYED:
            enemy = kwargs.get("enemy")
            if not enemy: return

            if random.random() < enemy.drop_rate:
                print(f"Spawning pickup at ({enemy.x_pos}, {enemy.y_pos})")
                pickup = Pickup(enemy.x_pos, enemy.y_pos)
                self.world_state["pickups"].append(pickup)
        elif event == PlayerEvent.PLAYER_JUMP:
            self.sfx_manager.play("jump")
        elif event == PlayerEvent.PLAYER_SHOOT:
            self.sfx_manager.play("shoot")
        elif event == PlayerEvent.PLAYER_HURT:
            self.sfx_manager.play("hit")
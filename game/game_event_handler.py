# game/game_event_handler.py
import random
from game.observer import Observer
from game.events import GameEvent
from game.pickup import Pickup

class GameEventHandler(Observer):
    def __init__(self, world_state: dict):
        self.world_state = world_state

    def on_notify(self, event, **kwargs):
        if event == GameEvent.ENEMY_DESTROYED:
            enemy = kwargs.get("enemy")
            if not enemy: return

            if random.random() < enemy.drop_rate:
                print(f"Spawning pickup at ({enemy.x_pos}, {enemy.y_pos})")
                pickup = Pickup(enemy.x_pos, enemy.y_pos)
                self.world_state["pickups"].append(pickup)
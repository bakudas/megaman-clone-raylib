# game/enemy.py
from __future__ import annotations

import random
import pyray as pr
from typing import TYPE_CHECKING

from game.enemy_states import EnemyState, PatrollingState, TurningState
from game.pickup import Pickup
from game.events import EnemyEvent
from game.observer import Subject

if TYPE_CHECKING:
    from game.platforms import Platform

class Enemy(Subject):
    def __init__(self, x, y):
        super().__init__()

        # atributos de estado físico
        self.x_pos: float = x
        self.y_pos: float = y
        self.y_vel: float = 0
        self.x_vel: float = 0
        self.width: int = 32
        self.height: int = 32

        # atributos de gameplay
        self.speed: float = 0.4
        self.facing_direction: str = "LEFT"
        self.health: int = 2
        self.is_destroyed: bool = False
        self.is_flashing: bool = False
        self.flash_duration: float = 0.1  # Duração do piscar em segundos
        self.flash_timer: float = 0.0
        self.drop_rate: float = 0.3

        # state machine
        self.ai_state: EnemyState = PatrollingState(self)

    # --- Métodos principais ---

    def update(self, world_state: dict, delta_time: float) -> None:
        """
        Atualiza toda a lógica do inimigo
        """
        if self.is_flashing:
            self.flash_timer -= delta_time
            if self.flash_timer <= 0:
                self.is_flashing = False

        self._apply_horizontal_physics(world_state)
        self.ai_state.update(self, world_state, delta_time)

    def _apply_horizontal_physics(self, world_state: dict):
        quadtree = world_state.get("quadtree")
        if not quadtree:
            self.x_pos += self.x_vel
            return

        self.x_pos += self.x_vel
        enemy_rect = pr.Rectangle(self.x_pos, self.y_pos, self.width, self.height)

        nearby_platforms = quadtree.query(enemy_rect)

        for plat in nearby_platforms:
            if plat.type == "solid":
                plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)
                if pr.check_collision_recs(enemy_rect, plat_rect):
                    if self.x_vel > 0:  # Movendo para a direita
                        self.x_pos = plat.x - self.width
                    elif self.x_vel < 0:  # Movendo para a esquerda
                        self.x_pos = plat.x + plat.width
                    
                    self.change_state_locomotion(TurningState(self))
                    break


    def draw(self) -> None:
        """
        Desenha o inimigo na tela
        """
        color = pr.WHITE if self.is_flashing else pr.ORANGE
        pr.draw_rectangle(
            int(self.x_pos),
            int(self.y_pos),
            self.width,
            self.height,
            color
        )

    # --- Métodos de verificação ---

    def is_ground_ahead(self, world_state: dict) -> bool:
        """
        Verifica se há uma plataforma sólida à frente do inimigo para ele pisar.
        Este é o "sensor" de beirada do inimigo.
        """
        quadtree = world_state.get("quadtree")
        if not quadtree:
            return True # Failsafe para não cair de beiradas se a quadtree não existir

        check_x = 0
        if self.facing_direction == 'LEFT':
            check_x = self.x_pos - 1
        else: # RIGHT
            check_x = self.x_pos + self.width + 1

        check_y = self.y_pos + self.height + 5

        # O retângulo de busca é pequeno, apenas na área do sensor
        sensor_box = pr.Rectangle(check_x - 5, check_y - 5, 10, 10)
        nearby_platforms = quadtree.query(sensor_box)

        for plat in nearby_platforms:
            plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)
            if pr.check_collision_point_rec(pr.Vector2(check_x, check_y), plat_rect):
                return True

        return False

    # --- Métodos State Machine

    def change_state_locomotion(self, new_state: EnemyState) -> None:
        """
        Muda o estado do inimigo
        """
        # guarda o estado anterior
        previous_state: EnemyState = self.ai_state

        # debug
        #print(f'Change: {previous_state} -> {new_state}')

        self.ai_state = new_state

    # --- Métodos de ação ---

    def take_damage(self, amount: int, world_state):
        self.health -= amount

        # Ativa o flash de dano
        self.is_flashing = True
        self.flash_timer = self.flash_duration

        if self.health <= 0:
            self.destroy()

    def destroy(self):
        if self.is_destroyed: return

        self.health = 0
        self.is_destroyed = True
        self.on_destroy()

    def on_destroy(self):
        print("Enemy has been destroyed!")
        # Notifica observadores (para drops E agora para efeitos visuais/sonoros)
        self.notify(EnemyEvent.ENEMY_DESTROYED, enemy=self)

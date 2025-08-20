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
        self.drop_rate: float = 1

        # state machine
        self.ai_state: EnemyState = PatrollingState(self)

    # --- Métodos principais ---

    def update(self, world_state: dict, delta_time: float) -> None:
        """
        Atualiza toda a lógica do inimigo
        """
        # flash de dano
        if self.is_flashing:
            self.flash_timer -= delta_time
            if self.flash_timer <= 0:
                self.is_flashing = False

        self.x_pos += self.x_vel
        self.ai_state.update(self, world_state, delta_time)


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
        check_x = 0
        # O ponto de checagem fica à frente do inimigo, na direção que ele está olhando
        if self.facing_direction == 'LEFT':
            check_x = self.x_pos - 1 # 1 pixel à frente da sua borda esquerda
        else: # RIGHT
            check_x = self.x_pos + self.width + 1 # 1 pixel à frente da sua borda direita

        # O ponto de checagem vertical é um pouco abaixo dos "pés" do inimigo
        check_y = self.y_pos + self.height + 5

        # debug
        #print(check_x, check_y)
        #pr.draw_rectangle(int(check_x), int(check_y), 1, 5, pr.BLACK)

        for plat in world_state.get("platforms", []):
            plat_rect = pr.Rectangle(plat.x, plat.y, plat.width, plat.height)
            # Se o ponto de checagem está dentro de alguma plataforma, há chão à frente.
            if pr.check_collision_point_rec(pr.Vector2(check_x, check_y), plat_rect):
                return True

        # Se o loop terminar sem encontrar chão, não há nada à frente.
        return False

    # --- Métodos State Machine

    def change_state_locomotion(self, new_state: EnemyState) -> None:
        """
        Muda o estado do inimigo
        """
        # guarda o estado anterior
        previous_state: EnemyState = self.ai_state

        # debug
        print(f'Change: {previous_state} -> {new_state}')

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

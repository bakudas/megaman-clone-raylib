# game/game_states.py
from __future__ import annotations
import pyray as pr
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.game import Game

from game.input_manager import GameAction
from game.player_states import DashState

class GameState(ABC):
    def __init__(self, game: Game):
        self.game = game
        self.used_bullets = []
        self.collected_pickups = []

    def handle_input(self):
        pass

    @abstractmethod
    def update(self, delta_time: float):
        pass

    @abstractmethod
    def draw(self):
        pass


class PlayingState(GameState):
    def handle_input(self):
        # O handle_input do estado agora consulta o InputManager
        input_manager = self.game.input_manager

        # --- Inputs da Arma ---
        if input_manager.is_action_pressed(GameAction.SHOOT):
            self.game.player.weapon_state.handle_input(self.game.player, "SHOOT_PRESS", self.game.world_state)

        if input_manager.is_action_released(GameAction.SHOOT):
            self.game.player.weapon_state.handle_input(self.game.player, "SHOOT_RELEASE", self.game.world_state)

        # --- Inputs de Locomoção ---
        if input_manager.is_action_pressed(GameAction.JUMP):
            self.game.player.handle_input("JUMP")
        if input_manager.is_action_released(GameAction.JUMP):
            self.game.player.handle_input("JUMP_RELEASE")

        if input_manager.is_action_pressed(GameAction.DASH):
            self.game.player.handle_input("DASH")

        # Movimento Horizontal
        if not isinstance(self.game.player.locomotion_state, DashState):
            self.game.player.horizontal_input_active = False
            if input_manager.is_action_down(GameAction.MOVE_RIGHT):
                self.game.player.handle_input("RIGHT")
                self.game.player.horizontal_input_active = True
            elif input_manager.is_action_down(GameAction.MOVE_LEFT):
                self.game.player.handle_input("LEFT")
                self.game.player.horizontal_input_active = True

            if not self.game.player.horizontal_input_active:
                self.game.player.handle_input("STOP")

    def update(self, delta_time: float):
        # A lógica de update principal do jogo agora vive aqui.
        self.game.player.update(self.game.world_state, delta_time)

        for enemy in self.game.world_state['enemies']:
            enemy.update(self.game.world_state, delta_time)

        for bullet in self.game.world_state["bullets"]:
            bullet.update()

        for particle in self.game.world_state["particles"]:
            particle.update(delta_time)

        for after_image in self.game.world_state["after_images"]:
            after_image.update(delta_time)

        self.game.camera.update(self.game.player)
        self.handle_collisions()
        self.cleanup_entities()

        # Lógica de transição de estado
        if self.game.player.is_destroyed:
            if self.game.player.lives > 0:
                self.game.change_state(PlayerDiedState(self.game))
            else:
                self.game.change_state(GameOverState(self.game))

    def draw(self):
        # A lógica de desenho principal vive aqui.
        self.game.camera.begin_mode()
        for plat in self.game.world_state["platforms"]:
            plat.draw()
            pass
        for hazard in self.game.world_state["hazards"]:
            hazard.draw()
        for cp in self.game.world_state["checkpoints"]:
            cp.draw()
        for pickup in self.game.world_state["pickups"]:
            pickup.draw()
        for enemy in self.game.world_state['enemies']:
            enemy.draw()
        for bullet in self.game.world_state["bullets"]:
            bullet.draw()
        for after_image in self.game.world_state["after_images"]:
            after_image.draw()
        for particle in self.game.world_state["particles"]:
            particle.draw()

        self.game.level_content.draw()
        self.game.player.draw()
        self.game.camera.end_mode()
        self.game.ui.draw()

    def handle_collisions(self):
        # Colisão das Balas com os Inimigos
        self.used_bullets = []
        for bullet in self.game.world_state["bullets"]:
            bullet_rect = pr.Rectangle(bullet.x_pos, bullet.y_pos, bullet.width, bullet.height)
            for enemy in self.game.world_state['enemies']:
                enemy_rect = pr.Rectangle(enemy.x_pos, enemy.y_pos, enemy.width, enemy.height)
                if pr.check_collision_recs(bullet_rect, enemy_rect):
                    damage = 2 if bullet.type == 'charged' else 1
                    enemy.take_damage(damage, self.game.world_state)
                    self.used_bullets.append(bullet)  # Marca a bala para ser removida
                    break  # Uma bala só pode atingir um inimigo

        # Colisão do Jogador com os Inimigos
        player_rect = pr.Rectangle(self.game.player.x_pos + self.game.player.width/2, self.game.player.y_pos, self.game.player.width/2, self.game.player.height)
        for enemy in self.game.world_state['enemies']:
            enemy_rect = pr.Rectangle(enemy.x_pos, enemy.y_pos, enemy.width, enemy.height)
            if pr.check_collision_recs(player_rect, enemy_rect):
                self.game.player.take_damage(5)  # Dano de colisão

        # colisão do jogador com pickups
        self.collected_pickups = []
        for pickup in self.game.world_state["pickups"]:
            pickup_rect = pr.Rectangle(pickup.x_pos, pickup.y_pos, pickup.width, pickup.height)
            if pr.check_collision_recs(player_rect, pickup_rect):
                self.game.player.heal(pickup.heal_amount)
                self.collected_pickups.append(pickup)

        # colisão do jogador com hazards
        for hazard in self.game.world_state["hazards"]:
            hazard_rect = pr.Rectangle(hazard.x, hazard.y, hazard.width, hazard.height)
            if pr.check_collision_recs(player_rect, hazard_rect):
                self.game.player.destroy()

        # colisão com checkpoints
        for cp in self.game.world_state["checkpoints"]:
            if not cp.is_activated:
                cp_rect = pr.Rectangle(cp.x, cp.y, cp.width, cp.height)
                if pr.check_collision_recs(player_rect, cp_rect):
                    print("Checkpoint activated!")
                    cp.is_activated = True
                    self.game.player.last_checkpoint = (cp.x, cp.y - self.game.player.height)

    def cleanup_entities(self):
        # LIMPEZA
        # Remover balas fora da tela
        self.game.world_state['bullets'] = [b for b in self.game.world_state['bullets'] if -4000 < b.x_pos < 6000]
        # Remove as balas que atingiram um alvo
        self.game.world_state["bullets"] = [b for b in self.game.world_state["bullets"] if b not in self.used_bullets]
        # Remove os inimigos destruídos
        self.game.world_state['enemies'] = [e for e in self.game.world_state['enemies'] if not e.is_destroyed]
        # Remove os pickups coletados
        self.game.world_state["pickups"] = [p for p in self.game.world_state["pickups"] if p not in self.collected_pickups]
        # Remove os efeitos
        self.game.world_state["particles"] = [p for p in self.game.world_state["particles"] if p.lifespan > 0]
        self.game.world_state["after_images"] = [a for a in self.game.world_state["after_images"] if a.lifespan > 0]


class PlayerDiedState(GameState):
    def __init__(self, game: Game):
        super().__init__(game)
        self.respawn_timer = 1.0 # 1 segundo de espera

    def update(self, delta_time: float):
        self.respawn_timer -= delta_time
        if self.respawn_timer <= 0:
            self.game.player.respawn()
            self.game.change_state(PlayingState(self.game))

    def draw(self):
        # Desenha a cena do jogo anterior, mas com um overlay escuro
        self.game.get_previous_state().draw() # Precisaremos de um helper para isso
        pr.draw_rectangle(0, 0, self.game.VIRTUAL_SCREEN_WIDTH, self.game.VIRTUAL_SCREEN_HEIGHT, pr.Color(0, 0, 0, 150))


class GameOverState(GameState):
    def draw(self):
        self.game.get_previous_state().draw()
        pr.draw_rectangle(0, 0, self.game.VIRTUAL_SCREEN_WIDTH, self.game.VIRTUAL_SCREEN_HEIGHT, pr.Color(0, 0, 0, 200))
        pr.draw_text("GAME OVER", 80, 100, 20, pr.WHITE)

    def update(self, delta_time: float):
        pass


class MenuState(GameState):
    pass
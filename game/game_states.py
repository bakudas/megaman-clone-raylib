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

    def update(self, delta_time: float):
        # A lógica de update agora é gerenciada pelos sistemas no loop principal do Game.
        # O PlayingState pode, no futuro, gerenciar pausas, etc.
        pass

        # TODO: A lógica de transição de estado (morte do jogador, game over)
        # será movida para um sistema que observa os eventos de vida.

    def draw(self):
        # A lógica de desenho principal vive aqui.
        self.game.camera.begin_mode()

        # 1. Desenha o mapa
        self.game.level_content.draw(self.game.camera.get_view_rect())

        # 2. Usa o RenderSystem para desenhar todas as entidades
        self.game.render_system.draw(self.game.world)

        # TODO: Desenhar outras entidades (inimigos, balas, etc.)
        # que ainda não foram migradas para o ECS.

        # 3. Encerra o modo da câmera e desenha a UI por cima
        self.game.camera.end_mode()
        self.game.ui.draw()

class PlayerDiedState(GameState):
    def __init__(self, game: Game):
        super().__init__(game)
        self.respawn_timer = 1.0 # 1 segundo de espera

    def update(self, delta_time: float):
        self.respawn_timer -= delta_time
        # if self.respawn_timer <= 0:
        #     self.game.player.respawn()
        #     self.game.change_state(PlayingState(self.game))

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
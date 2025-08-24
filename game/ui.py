# game/ui.py
import pyray as pr
from game.observer import Observer
from game.events import PlayerEvent
from game.world import World
from game.components import HealthComponent

class PlayerUI:
    def __init__(self, world: World, player_id: int):
        self.world = world
        self.player_id = player_id
        # TODO: A UI deveria se inscrever em um EventBus global para reações
        # como piscar a barra de vida ao tomar dano.

    # def on_notify(self, event, **kwargs):
    #     if event == PlayerEvent.PLAYER_HURT:
    #         print('Ui received PLAYER_HURT event!')

    def draw(self):
        """
        Desenha os elementos de UI
        """
        # Busca o componente de vida do jogador no mundo a cada frame
        health_comp = self.world.components[HealthComponent].get(self.player_id)
        if not health_comp:
            return # Não desenha nada se o jogador não tiver vida (ou não existir)

        # --- barra de vida ---
        pr.draw_rectangle(10, 10, health_comp.max_health * 2, 10, pr.BLACK)
        pr.draw_rectangle(10, 10, health_comp.current_health * 2, 10, pr.YELLOW)
        pr.draw_rectangle_lines(10, 10, health_comp.max_health * 2, 10, pr.WHITE)

        # --- Contador de Vidas ---
        pr.draw_text(f"x {health_comp.lives}", 10, 25, 10, pr.WHITE)
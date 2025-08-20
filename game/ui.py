# game/ui.py
import pyray as pr
from game.observer import Observer
from game.player import Player
from game.events import GameEvent, PlayerEvent

class PlayerUI(Observer):
    def __init__(self, player: Player):
        self.player = player
        # Inscreve a UI para receber notificações do jogador
        self.player.add_observer(self)

    def on_notify(self, event, **kwargs):
        # A UI pode reagir a diferentes eventos
        if event == PlayerEvent.PLAYER_HURT:
            print('Ui received PLAYER_HURT event!')

    def draw(self):
        """
        Desenha os elementos de UI
        """
        # --- barra de vida ---
        # (um simples container)
        pr.draw_rectangle(10, 10, self.player.max_health * 2, 10, pr.BLACK)
        # vida atual
        pr.draw_rectangle(10, 10, self.player.health * 2, 10, pr.YELLOW)
        # borda
        pr.draw_rectangle_lines(10, 10, self.player.max_health * 2, 10, pr.WHITE)

        # --- Contador de Vidas ---
        # (Um simples texto "x LIVES")
        pr.draw_text(f"x {self.player.lives}", 10, 25, 10, pr.WHITE)
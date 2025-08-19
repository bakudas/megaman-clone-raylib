# game/ui.py
import pyray as pr
from game.observer import Observer
from game.player import Player
from game.events import GameEvent

class PlayerUI(Observer):
    def __init__(self, player: Player):
        self.player = player
        # Inscreve a UI para receber notificações do jogador
        self.player.add_observer(self)

    def on_notify(self, event: str):
        # A UI pode reagir a diferentes eventos
        if event == GameEvent.PLAYER_HURT:
            print('Ui received PLAYER_HURT event!')

    def draw(self):
        """
        Desenha os elementos de UI
        """
        # barra de vida (container)
        pr.draw_rectangle(10, 10, self.player.max_health * 2, 10, pr.PRETO)
        # vida atual
        pr.draw_rectangle(10, 10, self.player.health * 2, 10, pr.YELLOW)
        # borda
        pr.draw_rectangle_lines(10, 10, self.player.max_health * 2, 10, pr.WHITE)
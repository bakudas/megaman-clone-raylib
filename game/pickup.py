# game/pickup.py
import pyray as pr
import math


class Pickup:
    def __init__(self, x: float, y: float, p_type: str = "HEALTH_SMALL"):
        self.x_pos = x
        self.y_pos = y
        self.initial_y = y
        self.width = 10
        self.height = 10
        self.type = p_type
        self.heal_amount = 4
        self.bob_timer = 0.0  # Timer para o efeito de flutuação

    def update(self, delta_time: float):
        """
        Atualiza a lógica do item
        """
        self.bob_timer += delta_time
        # Move o item para cima e para baixo usando uma função seno
        self.y_pos = self.initial_y + math.sin(self.bob_timer * 4) * 2

    def draw(self):
        """
        Desenha o item
        """
        pr.draw_rectangle(int(self.x_pos), int(self.y_pos), self.width, self.height, pr.LIME)

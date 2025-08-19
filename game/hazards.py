# game/hazards.py
import pyray as pr

class Hazard:
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self):
        # Por enquanto, um simples retângulo amarelo-escuro para representar os espinhos.
        pr.draw_rectangle(int(self.x), int(self.y), self.width, self.height, pr.GOLD)
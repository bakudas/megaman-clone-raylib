# game/checkpoint.py
import pyray as pr

class Checkpoint:
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_activated = False

    def draw(self):
        # Um checkpoint desativado é cinza, um ativado é ciano.
        color = pr.WHITE if self.is_activated else pr.BLACK
        pr.draw_rectangle_lines(int(self.x), int(self.y), int(self.width), int(self.height), color)
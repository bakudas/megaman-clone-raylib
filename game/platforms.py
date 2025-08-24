# game/platforms.py
from typing import Literal
import pyray as pr

# Usamos Literal para garantir que o tipo só possa ser 'solid' ou 'pass-through'
PlatformType = Literal["solid", "pass_through", "no_collision"]


class Platform:
    def __init__(
        self, x: float, y: float, width: float, height: float, p_type: PlatformType
    ) -> None:
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.type: str = p_type

    def draw(self):
        """
        Desenha o inimigo na tela
        """
        color = pr.BROWN if self.type == 'solid' else pr.DARKBROWN
        pr.draw_rectangle(
            int(self.x),
            int(self.y),
            self.width,
            self.height,
            color
        )
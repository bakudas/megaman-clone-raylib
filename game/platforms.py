# game/platforms.py
from typing import Literal, Optional
import pyray as pr

# Usamos Literal para garantir que o tipo só possa ser 'solid' ou 'pass-through'
PlatformType = Literal["solid", "pass-through"]


class Platform:
    def __init__(
        self, x: float, y: float, width: float, height: float, p_type: PlatformType, source_rec: Optional[pr.Rectangle] = None
    ) -> None:
        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.height: float = height
        self.type: str = p_type
        self.source_rec = source_rec # Retângulo de origem na textura do tileset

    def draw(self, tileset: pr.Texture):
        """
        Desenha a plataforma na tela usando a textura do tileset.
        """
        # Se não houver source_rec, desenha um retângulo para debug
        if self.source_rec is None:
            color = pr.BROWN if self.type == 'solid' else pr.DARKBROWN
            pr.draw_rectangle(
                int(self.x),
                int(self.y),
                int(self.width),
                int(self.height),
                color
            )
        else:
            dest_rec = pr.Rectangle(self.x, self.y, self.width, self.height)
            pr.draw_texture_pro(tileset, self.source_rec, dest_rec, pr.Vector2(0, 0), 0.0, pr.WHITE)
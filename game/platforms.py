# game/platforms.py
from typing import Literal

# Usamos Literal para garantir que o tipo só possa ser 'solid' ou 'pass-through'
PlatformType = Literal["solid", "pass-through"]


class Platform:
    def __init__(
        self, x: float, y: float, width: float, height: float, p_type: PlatformType
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = p_type

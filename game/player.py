# game/player.py


class Player:
    def __init__(self, x, y, width, height, speed) -> None:
        self.x_pos: float = x
        self.y_pos: float = y
        self.x_vel: float = 0
        self.y_vel: float = 0
        self.width: int = width
        self.height: int = height
        self.speed: float = speed

    @property
    def bottom(self) -> float:
        """
        Calcula a posição da baso do jogador
        """
        return self.y_pos + self.height

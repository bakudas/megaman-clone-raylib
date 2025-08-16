# game/player.py


class Player:
    def __init__(self, x, y, width=0, height=0, speed=0, jump_strength=0) -> None:
        self.x_pos: float = x
        self.y_pos: float = y
        self.x_vel: float = 0
        self.y_vel: float = 0
        self.width: int = width
        self.height: int = height
        self.speed: float = speed
        self.jump_strength: float = jump_strength

    @property
    def bottom(self) -> float:
        """
        Calcula a posição da baso do jogador
        """
        return self.y_pos + self.height

    def is_on_ground(self, world_physics: dict) -> bool:
        """
        Verifica se o jogador está no chão.
        """
        return self.bottom >= world_physics["floor"]

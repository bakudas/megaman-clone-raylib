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
        self.facing_direction: str = "RIGHT"
        self.is_wall_sliding: bool = False
        self.wall_slide_gravity: float = 0.1

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

        for plat in world_physics.get("platforms", []):
            # Verifica se o jogador está horizontalmente alinhado com a plataforma
            is_horizontaly_aligned = (
                self.x_pos < plat.x + plat.width and self.x_pos + self.width > plat.x
            )

            # Verifica se a base do jogador está exatamente no topo de alguma plataforma
            is_on_top = self.bottom == plat.y

            if is_horizontaly_aligned and is_on_top:
                return True  # encontrou um chão, pode parar de procurar

        return False  # segue o baile

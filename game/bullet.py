# game/bullet.py
import pyray as pr

class Bullet:
    def __init__(self, x: float, y: float, x_vel: float, b_type: str = 'normal'):
        self.x_pos: float = x
        self.y_pos: float = y
        self.x_vel: float = x_vel
        self.type: str = b_type
        self.color: pr.Color = pr.RED

        # O tamanho do projétil agora depende do seu tipo.
        if self.type == 'charged':
            self.width: int = 24
            self.height: int = 12
        else:  # normal
            self.width: int = 10
            self.height: int = 5

    def update(self):
        """Move o projétil horizontalmente."""
        self.x_pos += self.x_vel

    def draw(self):
        """Desenha o projétil na tela."""
        # O tiro carregado será laranja em vez de amarelo.
        color = pr.RED if self.type == 'charged' else pr.YELLOW
        pr.draw_rectangle(
            int(self.x_pos),
            int(self.y_pos),
            self.width,
            self.height,
            color
        )
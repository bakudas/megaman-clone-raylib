# game/bullet.py


class Bullet:
    def __init__(self, x, y, x_vel):
        self.x_pos: float = x
        self.y_pos: float = y
        self.x_vel: float = x_vel
        self.width: int = 10
        self.height: int = 5

    def update(self):
        self.x_pos += self.x_vel

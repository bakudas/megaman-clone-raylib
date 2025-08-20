# game/effects.py
import pyray as pr
import random

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        # Damos uma velocidade inicial aleatória para a partícula
        self.x_vel = random.uniform(-2, 2)
        self.y_vel = random.uniform(-3, 1)
        self.lifespan = 0.5 # A partícula viverá por 0.5 segundos

    def update(self, delta_time: float):
        self.x += self.x_vel
        self.y += self.y_vel
        self.lifespan -= delta_time

    def draw(self):
        # A partícula fica menor conforme se aproxima do fim da vida
        size = int(self.lifespan * 8)
        if size > 0:
            pr.draw_rectangle(int(self.x), int(self.y), size, size, self.color)

def spawn_explosion(world_state: dict, x: float, y: float):
    """Cria várias partículas para simular uma explosão."""
    particle_count = 15
    for _ in range(particle_count):
        # Inimigos são vermelhos, então a explosão pode ser uma mistura de vermelho, laranja e amarelo
        color = random.choice([pr.RED, pr.ORANGE, pr.YELLOW])
        particle = Particle(x, y, color)
        world_state["particles"].append(particle)

class AfterImage:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.lifespan = 0.2 # Vida útil muito curta
        self.initial_alpha = 150 # Começa semi-transparente

    def update(self, delta_time: float):
        self.lifespan -= delta_time

    def draw(self):
        # A transparência diminui com o tempo
        alpha = (self.lifespan / 0.2) * self.initial_alpha
        color = pr.Color(100, 200, 255, int(alpha)) # Azul claro semi-transparente
        pr.draw_rectangle(int(self.x), int(self.y), self.width, self.height, color)


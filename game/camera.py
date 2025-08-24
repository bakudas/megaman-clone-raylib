# game/camera.py

import pyray as pr
from game.world import World
from game.components import TransformComponent, PhysicsComponent

class Camera:
    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.camera = pr.Camera2D()
        self.camera.target = pr.Vector2(0, 0)  # o ponto que a camera olha
        self.camera.offset = pr.Vector2(
            screen_width / 2, screen_height / 2
        )  # centro da tela
        self.camera.rotation = 0.0
        self.camera.zoom = 1.0

        self.smoothing_factor: float = 0.05
        self.looking_ahead_distance: float = 2.5
        self.vertical_offset: float = -32

    def update_ecs(self, world: World, player_id: int) -> None:
        """
        Atualiza a posição da câmera para seguir a entidade do jogador.
        """
        transform = world.components[TransformComponent][player_id]
        physics = world.components[PhysicsComponent][player_id]

        # Atualizar o alvo da camera
        # o alvo inicial é um pocuo a frente do jogador
        look_ahead = self.looking_ahead_distance * (
            1 if physics.facing_direction == "RIGHT" else -1
        )
        target_x = transform.x + (transform.width / 2) * look_ahead
        target_y = (
            transform.y + (transform.height / 2) - self.vertical_offset
        )  # olhar um pocuo para cima

        # Suavizar o movimento da camera usando interpolação linear 'lerp'
        # a camera se move 5% da distância até o alvo a cada frame
        self.camera.target.x += (
            target_x - self.camera.target.x
        ) * self.smoothing_factor
        self.camera.target.y += (
            target_y - self.camera.target.y
        ) * 0.1

    def get_view_rect(self) -> pr.Rectangle:
        """
        Calcula e retorna o retângulo de visão da câmera no espaço do mundo.
        Isso é útil para o culling (não renderizar o que está fora da tela).
        """
        view_x = self.camera.target.x - self.camera.offset.x
        view_y = self.camera.target.y - self.camera.offset.y
        view_width = self.camera.offset.x * 2
        view_height = self.camera.offset.y * 2
        return pr.Rectangle(int(view_x), int(view_y), int(view_width), int(view_height))

    def begin_mode(self) -> None:
        """
        Inicia o modo de renderização 2D com a camera
        """
        pr.begin_mode_2d(self.camera)

    def end_mode(self) -> None:
        """
        Encerra o modo de renderização
        """
        pr.end_mode_2d()

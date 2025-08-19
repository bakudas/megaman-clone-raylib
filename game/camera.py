# game/camera.py

import pyray as pr
from game.player import Player  # type hinting


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
        self.vertical_offset: float = -16

    def update(self, player: Player) -> None:
        """
        Atualiza a posição da câmera para seguir o jogador
        """
        # Atualizar o alvo da camera
        # o alvo inicial é um pocuo a frente do jogador
        look_ahead = self.looking_ahead_distance * (
            1 if player.facing_direction == "RIGHT" else -1
        )
        target_x = player.x_pos + (player.width / 2) * look_ahead
        target_y = (
            player.y_pos + (player.height / 2) - self.vertical_offset
        )  # olhar um pocuo para cima

        # Suavizar o movimento da camera usando interpolação linear 'lerp'
        # a camera se move 5% da distância até o alvo a cada frame
        self.camera.target.x += (
            target_x - self.camera.target.x
        ) * self.smoothing_factor
        self.camera.target.y += (
            target_y - self.camera.target.y
        ) * 0.1

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

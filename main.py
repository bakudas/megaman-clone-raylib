# main.py

import pyray as pr
from raylib.defines import KEY_LEFT, KEY_RIGHT, GLFW_KEY_SPACE, GLFW_KEY_X

from game.logic import apply_physics, handle_input, shoot
from game.player import Player
from game.bullet import Bullet
from game.platforms import Platform

# 1. Inicialização
# -------------------------------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FLOOR_LEVEL = 400

pr.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Mega Man TDD Curso")
pr.set_target_fps(60)

# Cria uma lista de plataformas para definir o nível
level_platforms = [
    # Chão
    Platform(0, 400, SCREEN_WIDTH, 50, "solid"),
    # Plataformas no ar
    Platform(100, 300, 150, 20, "solid"),
    Platform(300, 250, 100, 20, "pass-through"),
    Platform(500, 200, 200, 20, "solid"),
]

# Estado inicial do jogador
player = Player(x=SCREEN_WIDTH / 2, y=0, width=40, height=50, speed=5, jump_strength=12)

# Configuração da física do nosso mundo
world_physics = {
    "gravity": 0.5,  # um valor menor funciona melhor para 60 FPS
    "platforms": level_platforms,
}

# Lista para guardar as balas ativas
bullets = []
BULLET_SPEED = 8.0
# ---------------------------------------------------


def run_game():
    global bullets

    # 2. Game Loop Principal
    while not pr.window_should_close():
        # 3. Update
        # Lida com os inputs
        player.x_vel = 0
        if pr.is_key_down(KEY_RIGHT):
            handle_input(player, "RIGHT", world_physics)
        elif pr.is_key_down(KEY_LEFT):
            handle_input(player, "LEFT", world_physics)

        # is_key_pressed para o pulo para evitar pulos repetidos se segurar a tecla
        if pr.is_key_pressed(GLFW_KEY_SPACE):
            handle_input(player, "JUMP", world_physics)

        # Aplica a Física
        apply_physics(player, world_physics)

        # Lógica do tiro
        if pr.is_key_pressed(GLFW_KEY_X):
            new_bullet = shoot(player, BULLET_SPEED)
            bullets.append(new_bullet)

        # Atualizar as balas
        for bullet in bullets:
            bullet.update()

        # Remover baloas fora da tela
        # List comprehension para criar uma nova lista apenas com as balas visíveis
        bullets = [b for b in bullets if 0 < b.x_pos < SCREEN_WIDTH]

        # 4. Draw
        pr.begin_drawing()

        pr.clear_background(pr.DARKGRAY)

        # Desenha as plataformas
        for plat in world_physics["platforms"]:
            color = pr.GRAY if plat.type == "solid" else pr.LIGHTGRAY
            pr.draw_rectangle(plat.x, plat.y, plat.width, plat.height, color)

        # Texto debug
        pr.draw_text("Nosso 'Mega Man' caindo!", 200, 20, 20, pr.LIGHTGRAY)

        # Desenha o jogador
        # Usamos os dados do nosso dic 'player_state'
        pr.draw_rectangle(
            int(player.x_pos),
            int(player.y_pos),
            int(player.width),
            int(player.height),
            pr.SKYBLUE,
        )

        # Desenha as balas
        for bullet in bullets:
            pr.draw_rectangle(
                int(bullet.x_pos),
                int(bullet.y_pos),
                bullet.width,
                bullet.height,
                pr.YELLOW,
            )

        pr.end_drawing()

    # 5. Final
    pr.close_window()


if __name__ == "__main__":
    run_game()

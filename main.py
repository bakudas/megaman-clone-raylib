# main.py

import pyray as pr
from raylib.defines import KEY_LEFT, KEY_RIGHT, GLFW_KEY_SPACE, GLFW_KEY_X

from game.logic import apply_physics, handle_input, shoot
from game.player import Player
from game.bullet import Bullet
from game.platforms import Platform

# 1. Inicialização
# -------------------------------------------------
VIRTUAL_SCREEN_WIDTH = 256
VIRTUAL_SCREEN_HEIGHT = 224
SCALE_MULTIPLIER = 3
SCREEN_WIDTH = VIRTUAL_SCREEN_WIDTH * SCALE_MULTIPLIER
SCREEN_HEIGHT = VIRTUAL_SCREEN_HEIGHT * SCALE_MULTIPLIER
KILL_Y = 1000

pr.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Mega Man TDD Curso")
pr.set_target_fps(60)

# Cria uma tela virtual para renderização do jogo
target_texture = pr.load_render_texture(VIRTUAL_SCREEN_WIDTH, VIRTUAL_SCREEN_HEIGHT)

# Inicializar a Camera
camera = pr.Camera2D()
camera.target = pr.Vector2(0, 0)  # o ponto que a camera olha
camera.offset = pr.Vector2(
    VIRTUAL_SCREEN_WIDTH / 2, VIRTUAL_SCREEN_HEIGHT / 2
)  # centro da tela
camera.rotation = 0.0
camera.zoom = 1.0

# Cria uma lista de plataformas para definir o nível
level_platforms = [
    # Chão
    Platform(0, 224, SCREEN_WIDTH, 16, "solid"),
    # Plataformas no ar
    Platform(96, 96, 64, 16, "solid"),
    Platform(128, 128, 96, 16, "pass-through"),
    Platform(156, 156, 64, 16, "solid"),
]

# Estado inicial do jogador
player = Player(x=SCREEN_WIDTH / 2, y=0, width=32, height=35, speed=4, jump_strength=8)

# Configuração da física do nosso mundo
world_physics = {
    "gravity": 0.3,  # um valor menor funciona melhor para 60 FPS
    "platforms": level_platforms,
}

# Lista para guardar as balas ativas
bullets = []
BULLET_SPEED = 2.0
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

        # Atualizar o alvo da camera
        # o alvo inicial é um pocuo a frente do jogador
        look_ahead = 2.5 * (1 if player.facing_direction == "RIGHT" else -1)
        target_x = player.x_pos + (player.width / 2) * look_ahead
        target_y = player.y_pos + (player.height / 2) - 16  # olhar um pocuo para cima

        # Suavizar o movimento da camera usando interpolação linear 'lerp'
        # a camera se move 5% da distância até o alvo a cada frame
        smoothing_factor = 0.025
        camera.target.x += (target_x - camera.target.x) * smoothing_factor
        camera.target.y += (target_y - camera.target.y) * smoothing_factor

        # 4. Draw
        # Começa a desenhar a tela virtual
        pr.begin_texture_mode(target_texture)

        # limpa a tela
        pr.clear_background(pr.DARKGRAY)

        # inicia o modo de camera 2D
        pr.begin_mode_2d(camera)

        # Desenha as plataformas
        for plat in world_physics["platforms"]:
            color = pr.GRAY if plat.type == "solid" else pr.LIGHTGRAY
            pr.draw_rectangle(plat.x, plat.y, plat.width, plat.height, color)

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

        pr.draw_text(
            f"""
            player starts:
            x: {player.x_pos}
            y: {player.y_pos}
            x_vel: {player.x_vel}
            y_vel: {player.y_vel}
            is_grounded: {player.is_on_ground(world_physics)}
            """,
            50,
            50,
            9,
            pr.LIGHTGRAY,
        )

        # termina o modo de camera 2D
        pr.end_mode_2d()

        # UI
        # Texto debug
        pr.draw_text("Just another Megaman clone...", 50, 50, 10, pr.LIGHTGRAY)

        # terminar o desenho na tela virtual
        pr.end_texture_mode()

        # Começa o desenho na tela real
        pr.begin_drawing()

        pr.clear_background(
            pr.RAYWHITE
        )  # Limpa a janela real (fundo das "letterboxes")

        # Definimos a origem, o tamanho de origem e o tamanho de destino para escalar
        source_rec = pr.Rectangle(
            0, 0, target_texture.texture.width, -target_texture.texture.height
        )
        dest_rec = pr.Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        """
        *Nota sobre height negativo: 
        Isso é um truque necessário porque as texturas em OpenGL 
        (que o Raylib usa) têm a coordenada Y (vertical) invertida 
        em relação a como o Raylib desenha. 
        Usar um valor negativo para a altura na origem corrige isso.
        """
        pr.draw_texture_pro(
            target_texture.texture,  # tela virtual
            source_rec,  # a área de origem (a textura inteira, com Y invertido*)
            dest_rec,  # a área de destino (a janela inteira)
            pr.Vector2(0, 0),  # origem da rotação
            0.0,  # rotação
            pr.WHITE,  # cor/tinta
        )

        # finaliza o desenho na tela real
        pr.end_drawing()

    # 5. Final
    pr.close_window()


if __name__ == "__main__":
    run_game()

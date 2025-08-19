# main.py
import pyray as pr
from raylib.defines import GLFW_KEY_R

from game.player import Player
from game.bullet import Bullet
from game.platforms import Platform
from game.camera import Camera
from game.enemy import Enemy

# 1. Inicialização
# -------------------------------------------------
VIRTUAL_SCREEN_WIDTH = 256
VIRTUAL_SCREEN_HEIGHT = 224
SCALE_MULTIPLIER = 3
SCREEN_WIDTH = VIRTUAL_SCREEN_WIDTH * SCALE_MULTIPLIER
SCREEN_HEIGHT = VIRTUAL_SCREEN_HEIGHT * SCALE_MULTIPLIER
KILL_Y = 1000

pr.init_window(
    SCREEN_WIDTH, SCREEN_HEIGHT, "Mega Man Clone w/ TDD - Curso raylib (pyray)"
)
pr.set_target_fps(60)

# Cria uma tela virtual para renderização do jogo
target_texture = pr.load_render_texture(VIRTUAL_SCREEN_WIDTH, VIRTUAL_SCREEN_HEIGHT)

# Inicializar a Camera
camera = Camera(VIRTUAL_SCREEN_WIDTH, VIRTUAL_SCREEN_HEIGHT)

# Cria uma lista de plataformas para definir o nível
level_platforms = [
    # Chão
    Platform(0, 400, 280, 50, "solid"),
    Platform(376, 400, 300, 50, "solid"),
    # Paredes do poço
    Platform(280, 0, 20, 450, "solid"),
    Platform(356, 0, 20, 450, "solid"),
    # Plataforma voadora
    Platform(96, 300, 150, 32, "solid")

]

# Estado inicial do jogador
player = Player(
    x=VIRTUAL_SCREEN_WIDTH / 2 + 50,
    y=0,
    width=32,
    height=35,
    speed=4,
    jump_strength=8
)

# Configuração da física do nosso mundo
world_state = {
    "gravity": 0.3,  # um valor menor funciona melhor para 60 FPS
    "wall_slide_gravity": 0.1,
    "platforms": level_platforms,
    "bullets": []
}

# Cria os inimigos
enemies = [
    Enemy(x= 100, y=300-32)
]

# ---------------------------------------------------

def reset_game():
    global world_state, player
    player = Player(
        x=VIRTUAL_SCREEN_WIDTH / 2 + 50,
        y=0,
        width=32,
        height=35,
        speed=4,
        jump_strength=8
    )
    world_state = {
        "gravity": 0.3,  # um valor menor funciona melhor para 60 FPS
        "wall_slide_gravity": 0.1,
        "platforms": level_platforms,
        "bullets": []
    }

def run_game():
    global enemies

    # 2. Game Loop Principal
    while not pr.window_should_close():
        # 3. Update
        delta_time = pr.get_frame_time()

        # inputs
        if pr.is_key_pressed(GLFW_KEY_R):
            print("reset")
            reset_game()

        # atualiza a lógica do player
        player.update(world_state, delta_time)

        # atualiza as balas
        for b in world_state["bullets"]:
            b.update()

        # atualiza os inimigos
        for e in enemies:
            e.update(world_state, delta_time)

        # Atualizar a camera
        camera.update(player)

        # 1. Colisão das Balas com os Inimigos
        used_bullets = []
        for bullet in world_state["bullets"]:
            bullet_rect = pr.Rectangle(bullet.x_pos, bullet.y_pos, bullet.width, bullet.height)
            for enemy in enemies:
                enemy_rect = pr.Rectangle(enemy.x_pos, enemy.y_pos, enemy.width, enemy.height)
                if pr.check_collision_recs(bullet_rect, enemy_rect):
                    damage = 2 if bullet.type == 'charged' else 1
                    enemy.take_damage(damage)
                    used_bullets.append(bullet)  # Marca a bala para ser removida
                    break  # Uma bala só pode atingir um inimigo

        # 2. Colisão do Jogador com os Inimigos
        player_rect = pr.Rectangle(player.x_pos, player.y_pos, player.width, player.height)
        for enemy in enemies:
            enemy_rect = pr.Rectangle(enemy.x_pos, enemy.y_pos, enemy.width, enemy.height)
            if pr.check_collision_recs(player_rect, enemy_rect):
                player.take_damage(5)  # Dano de colisão

        # Remover balas fora da tela
        # List comprehension para criar uma lista apenas com as balas visíveis
        world_state['bullets'] = [b for b in world_state['bullets'] if -400 < b.x_pos < 1200]
        # Remove as balas que atingiram um alvo
        world_state["bullets"] = [b for b in world_state["bullets"] if b not in used_bullets]
        # Remove os inimigos destruídos
        enemies = [e for e in enemies if not e.is_destroyed]

        # 4. Draw
        pr.draw_fps(10, 10)

        # Começa a desenhar a tela virtual
        pr.begin_texture_mode(target_texture)

        # limpa a tela
        pr.clear_background(pr.DARKGRAY)

        # inicia o modo de camera 2D
        camera.begin_mode()

        # Desenha as plataformas
        for plat in world_state["platforms"]:
            color = pr.GRAY if plat.type == "solid" else pr.LIGHTGRAY
            pr.draw_rectangle(
                int(plat.x),
                int(plat.y),
                int(plat.width),
                int(plat.height),
                color
            )

        # Desenha o jogador
        player.draw()

        # desenha os inimigos
        for e in enemies:
            pr.draw_text('enemy patrol', int(e.x_pos - e.width/2), int(e.y_pos - 15), 10, pr.WHITE)
            e.draw()

        # Desenha as balas
        for bullet in world_state['bullets']:
            bullet.draw()

        # termina o modo de camera 2D
        camera.end_mode()

        # UI
        # Texto debug
        # pr.draw_text("Just another Megaman clone...", 10, 10, 10, pr.LIGHTGRAY)
        # pr.draw_text(
        #     f"""
        #     player starts:
        #     x: {player.x_pos}
        #     y: {player.y_pos}
        #     x_vel: {player.x_vel}
        #     y_vel: {player.y_vel}
        #     is_grounded: {player.is_on_ground(world_state)}
        #     state: {player.state}
        #     """,
        #     10,
        #     10,
        #     9,
        #     pr.LIGHTGRAY,
        # )

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

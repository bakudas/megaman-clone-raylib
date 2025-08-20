# main.py
import pyray as pr
from raylib.defines import GLFW_KEY_R
from enum import Enum, auto

from game.game_event_handler import GameEventHandler
from game.player import Player
from game.bullet import Bullet
from game.platforms import Platform
from game.camera import Camera
from game.enemy import Enemy
from game.sfx_manager import SFXManager
from game.ui import PlayerUI
from game.hazards import Hazard
from game.checkpoints import Checkpoint
from game.events import GameEvent
from game.level_loader import load_level

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

# --- CARREGANDO O NÍVEL ---
level_content = load_level("levels/level_01.json")

# Estado inicial do jogador
player = Player(
    x=level_content["start_position"]["x"],
    y=level_content["start_position"]["y"],
    width=32,
    height=35,
    speed=3,
    jump_strength=7
)

# Player UI
ui = PlayerUI(player)

# Inicializar o Audio
pr.init_audio_device()
sfx_manager = SFXManager()
sfx_manager.load_sounds()

# Configuração da física do nosso mundo
world_state = {
    "player_start_x_pos": level_content["start_position"]["x"],
    "player_start_y_pos": level_content["start_position"]["y"],
    "gravity": 0.3,  # um valor menor funciona melhor para 60 FPS
    "wall_slide_gravity": 0.1,
    "platforms": level_content["platforms"],
    "bullets": [],
    "pickups": [],
    "enemies": level_content["enemies"],
    "hazards": level_content["hazards"],
    "checkpoints": level_content["checkpoints"]
}

# Cria o gerenciador de eventos
event_handler = GameEventHandler(world_state, sfx_manager)

# inscreve os inimigos no observador
for e in world_state['enemies']:
    e.add_observer(event_handler)

# --- ESTADO INICIAL DO JOGO ---
game_state = GameEvent.PLAYING
respawn_timer = 0.0
RESPAWN_DELAY = 1.0 # 1 segundo de tela preta antes de renascer
# ------------------------------

def reset_game(player: Player, state: dict):
    global world_state
    world_state = state
    player.x_pos = world_state["player_start_x_pos"]
    player.y_pos = world_state["player_start_y_pos"]

def run_game():
    global  game_state, respawn_timer, world_state

    # 2. Game Loop Principal
    while not pr.window_should_close():
        if game_state == GameEvent.PLAYING:
            # 3. Update
            delta_time = pr.get_frame_time()

            # inputs
            if pr.is_key_pressed(GLFW_KEY_R):
                print("reset")
                reset_game(player, world_state)

            # atualiza a lógica do player
            player.update(world_state, delta_time)

            # atualiza as balas
            for b in world_state["bullets"]:
                b.update()

            # atualiza os inimigos
            for e in world_state['enemies']:
                e.update(world_state, delta_time)

            # atualiza os pickups
            for pickup in world_state["pickups"]:  # <<< ATUALIZE OS PICKUPS
                pickup.update(delta_time)

            # atualiza os efeitos
            for p in world_state["particles"]: p.update(delta_time)
            for a in world_state["after_images"]: a.update(delta_time)

            # Atualizar a camera
            camera.update(player)

            # Colisão das Balas com os Inimigos
            used_bullets = []
            for bullet in world_state["bullets"]:
                bullet_rect = pr.Rectangle(bullet.x_pos, bullet.y_pos, bullet.width, bullet.height)
                for enemy in world_state['enemies']:
                    enemy_rect = pr.Rectangle(enemy.x_pos, enemy.y_pos, enemy.width, enemy.height)
                    if pr.check_collision_recs(bullet_rect, enemy_rect):
                        damage = 2 if bullet.type == 'charged' else 1
                        enemy.take_damage(damage, world_state)
                        used_bullets.append(bullet)  # Marca a bala para ser removida
                        break  # Uma bala só pode atingir um inimigo

            # Colisão do Jogador com os Inimigos
            player_rect = pr.Rectangle(player.x_pos, player.y_pos, player.width, player.height)
            for enemy in world_state['enemies']:
                enemy_rect = pr.Rectangle(enemy.x_pos, enemy.y_pos, enemy.width, enemy.height)
                if pr.check_collision_recs(player_rect, enemy_rect):
                    player.take_damage(5)  # Dano de colisão

            # colisão do jogador com pickups
            collected_pickups = []
            for pickup in world_state["pickups"]:
                pickup_rect = pr.Rectangle(pickup.x_pos, pickup.y_pos, pickup.width, pickup.height)
                if pr.check_collision_recs(player_rect, pickup_rect):
                    player.heal(pickup.heal_amount)
                    collected_pickups.append(pickup)

            # colisão do jogador com hazards
            for hazard in world_state["hazards"]:
                hazard_rect = pr.Rectangle(hazard.x, hazard.y, hazard.width, hazard.height)
                if pr.check_collision_recs(player_rect, hazard_rect):
                    player.destroy()

            # colisão com checkpoints
            player_rect = pr.Rectangle(player.x_pos, player.y_pos, player.width, player.height)
            for cp in world_state["checkpoints"]:
                if not cp.is_activated:
                    cp_rect = pr.Rectangle(cp.x, cp.y, cp.width, cp.height)
                    if pr.check_collision_recs(player_rect, cp_rect):
                        print("Checkpoint activated!")
                        cp.is_activated = True
                        player.last_checkpoint = (cp.x, cp.y - player.height)

            # Lógica de transição de estado
            if player.is_destroyed:
                if player.lives > 0:
                    game_state = GameEvent.PLAYER_DIED
                    respawn_timer = RESPAWN_DELAY
                else:
                    game_state = GameEvent.GAME_OVER

            # LIMPEZA
            # Remover balas fora da tela
            # List comprehension para criar uma lista apenas com as balas visíveis
            world_state['bullets'] = [b for b in world_state['bullets'] if -400 < b.x_pos < 1200]
            # Remove as balas que atingiram um alvo
            world_state["bullets"] = [b for b in world_state["bullets"] if b not in used_bullets]
            # Remove os inimigos destruídos
            world_state['enemies'] = [e for e in world_state['enemies'] if not e.is_destroyed]
            # Remove os pickups coletados
            world_state["pickups"] = [p for p in world_state["pickups"] if p not in collected_pickups]
            # Remove os efeitos
            world_state["particles"] = [p for p in world_state["particles"] if p.lifespan > 0]
            world_state["after_images"] = [a for a in world_state["after_images"] if a.lifespan > 0]
            
        elif game_state == GameEvent.PLAYER_DIED:
            respawn_timer -= delta_time
            if respawn_timer <= 0:
                player.respawn()
                game_state = GameEvent.PLAYING

        # 4. DRAW
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

        # desenha os hazards
        for hazard in world_state["hazards"]:
            hazard.draw()

        # Desenha o jogador
        player.draw()

        # desenha os inimigos
        for e in world_state["enemies"]:
            pr.draw_text('enemy patrol', int(e.x_pos - e.width/2), int(e.y_pos - 15), 10, pr.WHITE)
            e.draw()

        # Desenha as balas
        for bullet in world_state['bullets']:
            bullet.draw()

        # desenha os pickups
        for pickup in world_state["pickups"]:
            pickup.draw()

        # desenha os checkpoints
        for cp in world_state["checkpoints"]:
            cp.draw()

        # Desenha os efeitos
        for a in world_state["after_images"]: a.draw()
        for p in world_state["particles"]: p.draw()

        # termina o modo de camera 2D
        camera.end_mode()

        # UI
        # show fps
        pr.draw_fps(VIRTUAL_SCREEN_WIDTH - 80, 10)

        # desenha a UI do player
        ui.draw()

        if game_state == GameEvent.PLAYER_DIED:
            pr.draw_rectangle(0, 0, VIRTUAL_SCREEN_WIDTH, VIRTUAL_SCREEN_HEIGHT, pr.Color(0, 0, 0, 150))

        # --- DESENHO DA TELA DE GAME OVER ---
        if game_state == GameEvent.GAME_OVER:
            pr.draw_rectangle(0, 0, VIRTUAL_SCREEN_WIDTH, VIRTUAL_SCREEN_HEIGHT, pr.Color(0, 0, 0, 150))
            pr.draw_text("GAME OVER", 80, 100, 20, pr.WHITE)
        # -------------------------------------

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

    # finaliza o audio
    sfx_manager.unload_sounds()
    pr.close_audio_device()

    # 5. Final
    pr.close_window()


if __name__ == "__main__":
    run_game()

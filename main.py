# main.py

import pyray as pr

from game.logic import apply_physics

# 1. Inicialização
# -------------------------------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FLOOR_LEVEL = 400

pr.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Mega Man TDD Curso")
pr.set_target_fps(60)

# Estado inicial do jogador
player_state = {
    "x_pos": SCREEN_WIDTH / 2,
    "y_pos": 0,
    "y_vel": 0,
    "width": 40,
    "height": 50,
}

# Configuração da física do nosso mundo
world_physics = {
    "gravity": 0.25,  # um valor menor funciona melhor para 60 FPS
    "floor": FLOOR_LEVEL,
}
# ---------------------------------------------------

# 2. Game Loop Principal
while not pr.window_should_close():
    # 3. Update
    player_state = apply_physics(player_state, world_physics)

    # 4. Draw
    pr.begin_drawing()

    pr.clear_background(pr.DARKGRAY)

    # Desenha o chão
    pr.draw_rectangle(
        0, FLOOR_LEVEL, SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_LEVEL, pr.GREEN
    )

    # Texto debug
    pr.draw_text("Nosso 'Mega Man' caindo!", 200, 20, 20, pr.LIGHTGRAY)

    # Desenha o jogador
    # Usamos os dados do nosso dic 'player_state'
    pr.draw_rectangle(
        int(player_state["x_pos"]),
        int(player_state["y_pos"]),
        int(player_state["width"]),
        int(player_state["height"]),
        pr.SKYBLUE,
    )

    pr.end_drawing()

# 5. Final
pr.close_window()

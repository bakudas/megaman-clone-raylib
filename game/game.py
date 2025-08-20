# game/game.py
import pyray as pr

from game.game_event_handler import DropSystemHandler, VFXEventHandler, SoundEventHandler
from game.player import Player
from game.bullet import Bullet
from game.platforms import Platform
from game.camera import Camera
from game.enemy import Enemy
from game.sfx_manager import SFXManager
from game.ui import PlayerUI
from game.hazards import Hazard
from game.checkpoints import Checkpoint
from game.game_states import GameState, PlayingState, PlayerDiedState, GameOverState, MenuState
from game.level_loader import load_level


class Game:
    def __init__(self):
        # 1. Inicialização
        # -------------------------------------------------
        self.VIRTUAL_SCREEN_WIDTH = 256
        self.VIRTUAL_SCREEN_HEIGHT = 224
        self.SCALE_MULTIPLIER = 4
        self.SCREEN_WIDTH = self.VIRTUAL_SCREEN_WIDTH * self.SCALE_MULTIPLIER
        self.SCREEN_HEIGHT = self.VIRTUAL_SCREEN_HEIGHT * self.SCALE_MULTIPLIER
        self.world_state: dict = {}
        self.player: Player
        self.KILL_Y: int = 1000
        self.FPS: int = 60

        pr.set_config_flags(pr.FLAG_WINDOW_TRANSPARENT)
        pr.init_window(
            self.SCREEN_WIDTH, self.SCREEN_HEIGHT, "Mega Man Clone w/ TDD - Curso raylib (pyray)"
        )
        pr.set_target_fps(self.FPS)
        # Cria uma tela virtual para renderização do jogo
        self.target_texture = pr.load_render_texture(self.VIRTUAL_SCREEN_WIDTH, self.VIRTUAL_SCREEN_HEIGHT)

        # Inicializar a Camera
        self.camera = Camera(self.VIRTUAL_SCREEN_WIDTH, self.VIRTUAL_SCREEN_HEIGHT)

        # --- CARREGANDO O NÍVEL ---
        self.level_content = load_level("levels/level_02.json")

        # Estado inicial do jogador
        self.player = Player(
            x=self.level_content["start_position"]["x"],
            y=self.level_content["start_position"]["y"],
            width=32,
            height=35,
            speed=3,
            jump_strength=7
        )

        # Player UI
        self.ui = PlayerUI(self.player)

        # Inicializar o Audio
        pr.init_audio_device()
        self.sfx_manager = SFXManager()
        self.sfx_manager.load_sounds()

        # Configuração da física do nosso mundo
        self.world_state = {
            "player_start_x_pos": self.level_content["start_position"]["x"],
            "player_start_y_pos": self.level_content["start_position"]["y"],
            "gravity": 0.3,  # um valor menor funciona melhor para 60 FPS
            "wall_slide_gravity": 0.1,
            "platforms": self.level_content["platforms"],
            "bullets": [],
            "pickups": [],
            "enemies": self.level_content["enemies"],
            "hazards": self.level_content["hazards"],
            "checkpoints": self.level_content["checkpoints"],
            "particles": [],
            "after_images": []
        }

        # Cria o gerenciador de eventos
        self.sound_handler = SoundEventHandler(self.sfx_manager)
        self.vfx_handler = VFXEventHandler(self.world_state)
        self.drop_handler = DropSystemHandler(self.world_state)

        # inscreve o player e os inimigos no observador (sfx e vfx)
        self.player.add_observer(self.sound_handler)
        self.player.add_observer(self.vfx_handler)

        # inscreve os inimigos no observadores (sfx, vfx e drop)
        for e in self.world_state['enemies']:
            e.add_observer(self.sound_handler)
            e.add_observer(self.vfx_handler)
            e.add_observer(self.drop_handler)

        # --- Máquina de Estados ---
        self.current_state: GameState = PlayingState(self)
        self.previous_state: GameState = None
        self.respawn_timer = 0.0
        self.RESPAWN_DELAY = 1.0  # 1 segundo de tela preta antes de renascer

    def reset_game(self, player: Player, state: dict):
        self.world_state = state
        player.x_pos = self.world_state["player_start_x_pos"]
        player.y_pos = self.world_state["player_start_y_pos"]

    def change_state(self, new_state: GameState):
        self.previous_state = self.current_state
        self.current_state = new_state

    def get_previous_state(self) -> GameState:
        return self.previous_state

    def run(self):
        """O game loop principal agora vive aqui."""
        while not pr.window_should_close():
            delta_time = pr.get_frame_time()

            # Delege tudo para o estado atual
            self.current_state.handle_input()
            self.current_state.update(delta_time)

            # Lógica de desenho
            pr.begin_texture_mode(self.target_texture)
            pr.clear_background(pr.BLACK)  # Fundo das letterboxes
            backgroun_visibility = True
            pr.clear_background(pr.BLANK if pr.is_window_state(pr.FLAG_WINDOW_TRANSPARENT) and not backgroun_visibility else pr.BLUE)
            self.current_state.draw()
            pr.end_texture_mode()

            if pr.is_key_pressed(pr.KEY_D):
                if pr.is_window_state(pr.FLAG_WINDOW_UNDECORATED):
                    pr.clear_window_state(pr.FLAG_WINDOW_UNDECORATED)
                    backgroun_visibility = True
                else:
                    pr.set_window_state(pr.FLAG_WINDOW_UNDECORATED)
                    backgroun_visibility = False

            pr.begin_drawing()

            pr.clear_background(pr.BLANK if pr.is_window_state(pr.FLAG_WINDOW_TRANSPARENT) and not backgroun_visibility else pr.BLUE)

            # Desenha a textura final na tela
            source_rec = pr.Rectangle(0, 0, self.target_texture.texture.width, -self.target_texture.texture.height)
            dest_rec = pr.Rectangle(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            """
                    *Nota sobre height negativo: 
                    Isso é um truque necessário porque as texturas em OpenGL 
                    (que o Raylib usa) têm a coordenada Y (vertical) invertida 
                    em relação a como o Raylib desenha. 
                    Usar um valor negativo para a altura na origem corrige isso.
                    """
            pr.draw_texture_pro(
                self.target_texture.texture,  # tela virtual
                source_rec,  # a área de origem (a textura inteira, com Y invertido*)
                dest_rec,  # a área de destino (a janela inteira)
                pr.Vector2(0, 0),  # origem da rotação
                0.0,  # rotação
                pr.WHITE,  # cor/tinta
            )

            pr.draw_fps(pr.get_screen_width() - 95, 10)
            pr.end_drawing()

    def cleanup(self):
        """Libera todos os recursos."""
        self.sfx_manager.unload_sounds()
        pr.close_audio_device()
        pr.unload_render_texture(self.target_texture)
        pr.close_window()
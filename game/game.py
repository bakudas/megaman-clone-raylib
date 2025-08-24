# game/game.py
import pyray as pr

from game.camera import Camera
from game.sfx_manager import SFXManager
from game.ui import PlayerUI
from game.game_states import GameState, PlayingState
from game.level_loader import LevelManager
from .input_manager import InputManager, GameAction
from .world import World
from .event_bus import EventBus
from .systems import InputSystem, StateMachineSystem, PhysicsSystem, AnimationSystem, CameraSystem, RenderSystem, ShootingSystem, CollisionSystem, DamageSystem, CleanupSystem, AISystem, SoundSystem, DropSystem, GameStateSystem, InvincibilitySystem, PickupSystem
from .entity_factory import create_player # Uma nova factory para criar entidades


class Game:
    def __init__(self):
        # 1. Inicialização
        # -------------------------------------------------
        self.VIRTUAL_SCREEN_WIDTH = 256
        self.VIRTUAL_SCREEN_HEIGHT = 224
        self.SCALE_MULTIPLIER = 4
        self.SCREEN_WIDTH = self.VIRTUAL_SCREEN_WIDTH * self.SCALE_MULTIPLIER
        self.SCREEN_HEIGHT = self.VIRTUAL_SCREEN_HEIGHT * self.SCALE_MULTIPLIER
        
        # --- Arquitetura ECS ---
        self.world = World()
        self.event_bus = EventBus()
        self.systems = [] # Lista de sistemas a serem executados

        self.KILL_Y: int = 1000
        self.FPS: int = 60
        self.input_manager = InputManager()

        pr.init_window(
            self.SCREEN_WIDTH, self.SCREEN_HEIGHT, "Mega Man Clone w/ TDD - Curso raylib (pyray)"
        )
        pr.set_target_fps(self.FPS)
        # Cria uma tela virtual para renderização do jogo
        self.target_texture = pr.load_render_texture(self.VIRTUAL_SCREEN_WIDTH, self.VIRTUAL_SCREEN_HEIGHT)

        # Inicializar a Camera
        self.camera = Camera(self.VIRTUAL_SCREEN_WIDTH, self.VIRTUAL_SCREEN_HEIGHT)

        # --- CARREGANDO O NÍVEL ---
        self.level_content = LevelManager("levels/level_03.json")

        # Carrega os dados do nível (plataformas, posições de entidades, etc.) e cria as entidades no mundo.
        self.level_content.load_level(self.world)

        # --- Criação de Entidades ---
        player_start_pos = self.level_content.level_objects["player_start"]
        self.player_id = create_player(self.world, player_start_pos['x'], player_start_pos['y'])

        # Player UI
        self.ui = PlayerUI(self.world, self.player_id)

        # Inicializar o Áudio
        pr.init_audio_device()
        self.sfx_manager = SFXManager()
        self.sfx_manager.load_sounds()

        # Instâncias dos Sistemas
        self.render_system = RenderSystem()

        # --- Configuração dos Sistemas ---
        # A ordem é importante!
        self.systems.append(InputSystem(self.input_manager, self.event_bus))
        self.systems.append(StateMachineSystem(self.world, self.event_bus))
        self.systems.append(AISystem(self.world, self.event_bus))
        self.systems.append(ShootingSystem(self.world, self.event_bus)) # Reage aos eventos de input/state machine
        self.systems.append(PhysicsSystem(gravity=0.3, quadtree=self.level_content.level_objects["quadtree"]))
        self.systems.append(AnimationSystem())
        self.systems.append(CameraSystem(self.camera))
        self.systems.append(CollisionSystem(self.event_bus))
        self.systems.append(DamageSystem(self.world, self.event_bus))
        self.systems.append(PickupSystem(self.world, self.event_bus))
        self.systems.append(InvincibilitySystem())

        # Sistemas reativos a eventos
        self.systems.append(SoundSystem(self.event_bus, self.sfx_manager))
        self.systems.append(DropSystem(self.world, self.event_bus))
        self.systems.append(GameStateSystem(self.world, self.event_bus))

        # Sistemas de limpeza devem rodar por último
        self.systems.append(CleanupSystem())

        # --- Máquina de Estados ---
        self.current_state: GameState = PlayingState(self)
        self.previous_state: GameState = None
        self.respawn_timer = 0.0
        self.RESPAWN_DELAY = 1.0  # 1 segundo de tela preta antes de renascer

        # Debug: Verificar se o gamepad foi detectado
        self.gamepad = 1

    def change_state(self, new_state: GameState):
        self.previous_state = self.current_state
        self.current_state = new_state

    def get_previous_state(self) -> GameState:
        return self.previous_state

    def run(self):
        """O game loop principal agora vive aqui."""
        while not pr.window_should_close():
            delta_time = pr.get_frame_time()

            # O loop principal agora itera sobre os sistemas
            for system in self.systems:
                system.update(self.world, delta_time)

            self.current_state.update(delta_time)

            # Lógica de desenho
            pr.begin_texture_mode(self.target_texture)
            pr.clear_background(pr.BLACK)  # Fundo das letterboxes
            pr.clear_background(pr.BLUE)
            self.current_state.draw()
            pr.end_texture_mode()

            pr.begin_drawing()
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

            if pr.is_gamepad_available(self.gamepad):
                gamepad_name = pr.glfw_get_joystick_name(self.gamepad)
                if gamepad_name:  # Check if gamepad_name is not None
                    pr.draw_text(f"GP{self.gamepad}: {gamepad_name}", 10, 10, 10, pr.BLACK)
                    pr.draw_text(f"GP{pr.is_gamepad_button_pressed(2, pr.GamepadButton.GAMEPAD_BUTTON_RIGHT_FACE_DOWN)}", 10, 20, 10, pr.BLACK)
                else:
                    pr.draw_text(f"GP{self.gamepad}: UNKNOWN", 10, 10, 10, pr.BLACK)

            pr.draw_fps(pr.get_screen_width() - 95, 10)
            pr.end_drawing()

    def cleanup(self):
        """Libera todos os recursos."""
        self.level_content.unload()
        self.sfx_manager.unload_sounds()
        pr.close_audio_device()
        pr.unload_render_texture(self.target_texture)
        pr.close_window()
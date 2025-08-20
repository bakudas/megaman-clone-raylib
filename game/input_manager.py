# game/input_manager.py
import pyray as pr
from enum import Enum, auto


class GameAction(Enum):
    """Define as ações semânticas do jogo."""
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    JUMP = auto()
    SHOOT = auto()
    DASH = auto()


class InputManager:
    def __init__(self, gamepad_id: int = 0):
        self.gamepad_id = gamepad_id

        # Mapeia nossas ações a botões específicos do teclado e gamepad
        self.action_map = {
            GameAction.MOVE_LEFT: {
                "keys": [pr.KEY_LEFT, pr.KEY_A],
                "pad_buttons": [pr.GAMEPAD_BUTTON_LEFT_FACE_LEFT],
                "pad_axis": (pr.GAMEPAD_AXIS_LEFT_X, -1)  # Eixo X, direção negativa
            },
            GameAction.MOVE_RIGHT: {
                "keys": [pr.KEY_RIGHT, pr.KEY_D],
                "pad_buttons": [pr.GAMEPAD_BUTTON_LEFT_FACE_RIGHT],
                "pad_axis": (pr.GAMEPAD_AXIS_LEFT_X, 1)  # Eixo X, direção positiva
            },
            GameAction.JUMP: {
                "keys": [pr.KEY_SPACE],
                # Botão inferior do "rosto" (A no Xbox, X no PlayStation)
                "pad_buttons": [pr.GAMEPAD_BUTTON_RIGHT_FACE_DOWN]
            },
            GameAction.SHOOT: {
                "keys": [pr.GLFW_KEY_X],
                # Botão esquerdo do "rosto" (X no Xbox, Quadrado no PlayStation)
                "pad_buttons": [pr.GAMEPAD_BUTTON_RIGHT_FACE_LEFT]
            },
            GameAction.DASH: {
                "keys": [pr.GLFW_KEY_Z],
                # Botão direito do "rosto" (B no Xbox, Círculo no PlayStation)
                "pad_buttons": [pr.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT]
            }
        }

    def is_action_down(self, action: GameAction) -> bool:
        """Verifica se uma ação está sendo mantida pressionada."""
        map_entry = self.action_map.get(action, {})

        # Teclado
        for key in map_entry.get("keys", []):
            if pr.is_key_down(key):
                return True

        # Gamepad (se disponível)
        if pr.is_gamepad_available(self.gamepad_id):
            for button in map_entry.get("pad_buttons", []):
                if pr.is_gamepad_button_down(self.gamepad_id, button):
                    return True

            # Checagem do analógico/D-Pad
            if "pad_axis" in map_entry:
                axis, direction = map_entry["pad_axis"]
                axis_value = pr.get_gamepad_axis_movement(self.gamepad_id, axis)
                if direction * axis_value > 0.5:  # 0.5 é a "deadzone"
                    return True

        return False

    def is_action_pressed(self, action: GameAction) -> bool:
        """Verifica se uma ação foi pressionada neste frame."""
        # ... (A lógica é similar a is_action_down, mas usando is_key_pressed e is_gamepad_button_pressed)
        # Por brevidade, vou deixar a implementação completa para o passo seguinte, se concordar.
        map_entry = self.action_map.get(action, {})
        for key in map_entry.get("keys", []):
            if pr.is_key_pressed(key): return True
        if pr.is_gamepad_available(self.gamepad_id):
            for button in map_entry.get("pad_buttons", []):
                if pr.is_gamepad_button_pressed(self.gamepad_id, button): return True
        return False

    def is_action_released(self, action: GameAction) -> bool:
        """Verifica se uma ação foi solta neste frame."""
        map_entry = self.action_map.get(action, {})
        for key in map_entry.get("keys", []):
            if pr.is_key_released(key): return True
        if pr.is_gamepad_available(self.gamepad_id):
            for button in map_entry.get("pad_buttons", []):
                if pr.is_gamepad_button_released(self.gamepad_id, button): return True
        return False
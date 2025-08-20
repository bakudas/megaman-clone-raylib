# game/sfx_manager.py
import pyray as pr


class SFXManager():
    def __init__(self):
        self.sounds = {}

    def load_sounds(self):
        # O ideal é usar um bloco try/except para o caso de o arquivo não ser encontrado
        try:
            self.sounds["jump"] = pr.load_sound("assets/sfx/jump.mp3")
            self.sounds["shoot"] = pr.load_sound("assets/sfx/shoot.mp3")
            self.sounds["explosion"] = pr.load_sound("assets/sfx/explosion.mp3")
            self.sounds["hit"] = pr.load_sound("assets/sfx/hit.mp3")
            self.sounds["heal"] = pr.load_sound("assets/sfx/heal.mp3")
            self.sounds["game_over"] = pr.load_sound("assets/sfx/game_over.mp3")
        except Exception as e:
            print(f"Error loading sounds: {e}")

    def play(self, name: str):
        if name in self.sounds:
            pr.play_sound(self.sounds[name])

    def unload_sounds(self):
        for sound in self.sounds.values():
            pr.unload_sound(sound)

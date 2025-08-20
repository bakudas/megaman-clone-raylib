# game/sfx_manager.py
import pyray as pr

class SFXManager:
    def __init__(self):
        self.sounds = {}

    def load_sounds(self):
        # O ideal é usar um bloco try/except para o caso de o arquivo não ser encontrado
        try:
            self.sounds["jump"] = pr.load_sound("assets/sfx/jump.wav")
            self.sounds["shoot"] = pr.load_sound("assets/sfx/shoot.wav")
            self.sounds["explosion"] = pr.load_sound("assets/sfx/explosion.wav")
            self.sounds["hit"] = pr.load_sound("assets/sfx/hit.wav")
        except Exception as e:
            print(f"Error loading sounds: {e}")

    def play(self, name: str):
        if name in self.sounds:
            pr.play_sound(self.sounds[name])

    def unload_sounds(self):
        for sound in self.sounds.values():
            pr.unload_sound(sound)
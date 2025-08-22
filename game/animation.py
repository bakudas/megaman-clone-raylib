# game/animation.py
import pyray as pr


class AnimationManager:
    def __init__(self, texture_path: str):
        self.texture = pr.load_texture(texture_path)
        self.animations = {}  # Dicionário para guardar as animações
        self.current_animation = None
        self.current_frame = 0
        self.frame_timer = 0.0
        self.is_playing = True
        self.flip_horizontal = False

    def add_animation(self, name: str, frames: list[pr.Rectangle], frame_speed: float, loop: bool = True):
        """Adiciona uma nova animação ao manager."""
        self.animations[name] = {
            "frames": frames,
            "frame_speed": frame_speed,
            "loop": loop
        }

    def play(self, name: str):
        """Começa a tocar uma nova animação."""
        if name not in self.animations or self.current_animation == name:
            return

        self.current_animation = name
        self.current_frame = 0
        self.frame_timer = 0.0
        self.is_playing = True

    def update(self, delta_time: float):
        if not self.is_playing or self.current_animation is None:
            return

        anim_data = self.animations[self.current_animation]
        self.frame_timer += delta_time

        if self.frame_timer >= anim_data["frame_speed"]:
            self.frame_timer = 0.0
            self.current_frame += 1

            # Lógica de loop
            if self.current_frame >= len(anim_data["frames"]):
                if anim_data["loop"]:
                    self.current_frame = 0
                else:
                    self.current_frame = len(anim_data["frames"]) - 1
                    self.is_playing = False

    def draw(self, x: float, y: float):
        if self.current_animation is None:
            return

        grid_size = (38, 48)
        anim_data = self.animations[self.current_animation]
        source_rec = anim_data["frames"][self.current_frame]

        # Lógica para virar o sprite horizontalmente
        if self.flip_horizontal:
            source_rec.width = -abs(source_rec.width)
        else:
            source_rec.width = abs(source_rec.width)

        dest_rec = pr.Rectangle(int(x), int(y), abs(source_rec.width), source_rec.height)
        origin = pr.Vector2(0, 0)

        pr.draw_texture_pro(self.texture, source_rec, dest_rec, origin, 0.0, pr.WHITE)
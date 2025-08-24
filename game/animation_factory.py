# game/animation_factory.py
import pyray as pr
from game.animation import AnimationManager

def setup_player_animations(anim_manager: AnimationManager):
    """Helper function to configure all player animations."""
    grid_size = (38, 48)
    start_frames = [pr.Rectangle(grid_size[0] * i, 0, grid_size[0], grid_size[1]) for i in range(7)]
    idle_frames = [pr.Rectangle(grid_size[0] * i, 0, grid_size[0], grid_size[1]) for i in range(7, 11)]
    run_frames = [pr.Rectangle(grid_size[0] * i, grid_size[1], grid_size[0], grid_size[1]) for i in range(11)]
    jump_frames = [pr.Rectangle(grid_size[0] * i, grid_size[1] * 3, grid_size[0], grid_size[1]) for i in range(3)]
    fall_frames = [pr.Rectangle(grid_size[0] * i, grid_size[1] * 3, grid_size[0], grid_size[1]) for i in range(3, 7)]
    dash_frames = [pr.Rectangle(grid_size[0] * i, grid_size[1] * 2, grid_size[0], grid_size[1]) for i in range(10, 12)]
    hit_frames = [pr.Rectangle(grid_size[0] * i, grid_size[1] * 2, grid_size[0], grid_size[1]) for i in range(12, 14)]
    wall_slide_frames = [pr.Rectangle(grid_size[0] * 2, grid_size[1] * 4, grid_size[0], grid_size[1])]

    anim_manager.add_animation("start", start_frames, 0.85, loop=False)
    anim_manager.add_animation("idle", idle_frames, 0.2)
    anim_manager.add_animation("run", run_frames, 0.05)
    anim_manager.add_animation("jump", jump_frames, 0.2)
    anim_manager.add_animation("fall", fall_frames, 0.2)
    anim_manager.add_animation("dash", dash_frames, 0.1)
    anim_manager.add_animation("wall_slide", wall_slide_frames, 0.1)
    anim_manager.add_animation("hit", hit_frames, 0.1)
    anim_manager.play("start")

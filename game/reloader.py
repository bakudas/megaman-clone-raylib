# game/reloader.py
import importlib
import sys

# A ordem é importante! Recarregamos as "folhas" da árvore de dependência primeiro.
# Por exemplo, Player depende de PlayerState, então recarregamos PlayerState antes.
MODULES_TO_RELOAD = [
    "game.observer",
    "game.animation",
    "game.effects",
    "game.pickups",
    "game.hazards",
    "game.checkpoint",
    "game.bullet",
    "game.platforms",
    "game.player_states",
    "game.weapon_states",
    "game.enemy_states",
    "game.player",
    "game.enemy",
    "game.sfx_manager",
    "game.event_handlers",
    "game.tilemap_renderer",
    "game.ui",
    "game.game_states",
    "game.game",
]

def reload_modules():
    """Recarrega todos os módulos de jogo na ordem correta."""
    print("--- HOT RELOAD TRIGGERED ---")
    for module_name in MODULES_TO_RELOAD:
        if module_name in sys.modules:
            try:
                importlib.reload(sys.modules[module_name])
                print(f"Reloaded: {module_name}")
            except Exception as e:
                print(f"!!! FAILED to reload {module_name}: {e}")
    print("--- HOT RELOAD COMPLETE ---")
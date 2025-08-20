# game/level_loader.py
import json
from game.platforms import Platform
from game.hazards import Hazard
from game.enemy import Enemy
from game.checkpoints import Checkpoint


def load_level(file_path: str) -> dict:
    """
    Carrega um nível a partir de um arquivo JSON e retorna um dicionário
    com listas de todos os objetos do jogo.
    """
    with open(file_path, 'r') as f:
        level_data = json.load(f)

    # Usa "List Comprehensions" para criar os objetos de forma concisa
    platforms = [Platform(**p_data) for p_data in level_data["platforms"]]
    walls = [Platform(**w_data) for w_data in level_data["walls"]]
    all_platforms = platforms + walls  # Junta as duas listas

    enemies = [Enemy(**e_data) for e_data in level_data["enemies"]]
    hazards = [Hazard(**h_data) for h_data in level_data["hazards"]]
    checkpoints = [Checkpoint(**c_data) for c_data in level_data["checkpoints"]]

    start_pos = level_data["start_position"]

    return {
        "platforms": all_platforms,
        "enemies": enemies,
        "hazards": hazards,
        "checkpoints": checkpoints,
        "start_position": start_pos
    }
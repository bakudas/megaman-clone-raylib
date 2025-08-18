# tests/conftest.py
import pytest

from game.player import Player
from game.platforms import Platform


@pytest.fixture
def player():
    """Retorna uma instância padrão do Player para os testes."""
    return Player(x=100, y=100, width=40, height=50, speed=5, jump_strength=15)


@pytest.fixture
def world_state():
    """Retorna um dicionário de estado de mundo com algumas plataformas."""
    return {
        "gravity": 1.0,
        "wall_slide_gravity": 0.1,
        "platforms": [
            Platform(0, 400, 500, 20, "solid"),  # Chão
            Platform(200, 300, 100, 20, "solid"),  # Plataforma no ar
        ],
    }

# tests/conftest.py
import pytest
from typing import Dict, Any

from game.player import Player
from game.platforms import Platform
from game.enemy import Enemy
from game.hazards import Hazard
from game.pickup import Pickup


@pytest.fixture
def player() -> Player:
    """Retorna uma instância padrão do Player para os testes."""
    return Player(x=100, y=100, width=40, height=50, speed=5, jump_strength=15)

@pytest.fixture
def patrolling_enemy():
    """
    Retorna uma instância padrão do inimigo para os testes
    """
    return Enemy(x=100,y=100)

@pytest.fixture
def hazard() -> Hazard:
    """Retorna uma instância padrão de Hazard para os testes."""
    return Hazard(x=100, y=380, width=50, height=20)

@pytest.fixture
def pickup() -> Pickup:
    """Retorna uma instância padrão de Pickup para os testes."""
    return Pickup(x=150, y=380)

@pytest.fixture
def world_state() -> Dict[str, Any]:
    """Retorna um dicionário de estado de mundo com algumas plataformas."""
    return {
        "gravity": 1.0,
        "wall_slide_gravity": 0.2,
        "platforms": [
            Platform(0, 400, 500, 20, "solid"),  # Chão
            Platform(200, 300, 100, 20, "solid"),  # Plataforma no ar
            Platform(x=50, y=150, width=100, height=20, p_type='solid')
        ],
        "bullets": [],
        "enemies": [],
        "hazards": [],
        "pickups": [],
    }

# tests/test_player.py
from game.events import GameEvent, PlayerEvent
from game.player import Player
from game.player_state import (
    IdleState,
    JumpingState,
    JumpingState,
    FallingState,
    WallSlidingState,
    DashState,
    HurtingState,
)
from game.weapon_states import ReadyState, ChargingState, FullyChargedState
from game.observer import Observer
from unittest.mock import Mock

# --- Mock Observer para Testes ---
class MockObserver(Observer):
    def __init__(self):
        self.last_event = None

    def on_notify(self, event, **kwargs):
        print(f"MockObserver received: {event} with kwargs: {kwargs}")
        self.last_event = event

def test_player_inicialization(player):
    # 1. Arrange
    # (Given) Dado a inicialização do level
    # Não precisamos de configurações adicionais para o level

    # 2. Act
    # (When) Quando o nível é inicializado

    # 3. Assert
    # (Then)
    assert player.x_pos == 100
    assert player.y_pos == 100
    assert player.width == 40
    assert player.height == 50
    assert player.speed == 5
    assert player.jump_strength == 15
    assert player.x_vel == 0
    assert player.y_vel == 0


def test_player_facing_direction_defaults_right(player):
    # 3. Assert
    # (Then) Então o player por padrão na criação deve estar virado para a direita
    assert player.facing_direction == "RIGHT"


def test_player_bottom_property(player):
    player.y_pos = 200

    # 3. Assert
    # (Then) Então a propriedade bottom retorna a base do jogador
    assert player.bottom == 250  # 200 (y_pos) + 50 (height)


def test_jump_input_from_idle_changes_state_to_jumping(player, world_state):
    # Arrange (Dado)
    # Forçamos o jogador a estar no chão e no estado Idle (o fixture já faz isso)
    player.y_pos = 350  # Posição exata no chão da fixture
    assert isinstance(player.locomotion_state, IdleState)
    assert player.is_on_ground(world_state) is True

    # Act (Quando)
    player.handle_input("JUMP")

    # Assert (Então)
    assert isinstance(player.locomotion_state, JumpingState)
    assert player.y_vel == -player.jump_strength  # A ação de pular foi executada


def test_jumping_player_transitions_to_falling_at_jump_apex(player):
    # Arrange (Dado)
    # Forçamos o jogador para o estado de pulo e com velocidade quase nula
    player.change_locomotion_state(JumpingState())
    player.y_vel = -0.1  # Quase no pico
    assert isinstance(player.locomotion_state, JumpingState)

    # Act (Quando)
    # Simulamos um frame de física que o faz começar a cair
    player.y_vel += 0.2  # Agora y_vel é 0.1 (positivo)
    player.locomotion_state.update(player, {}, 0.0)  # Chamamos o update do estado

    # Assert (Então)
    assert isinstance(player.locomotion_state, FallingState)


def test_wall_jump_action_and_transition(player):
    # Arrange (Dado)
    # Forçamos o jogador para o estado de deslizar na parede
    player.change_locomotion_state(WallSlidingState(player))
    player.facing_direction = "RIGHT"  # Simulando estar na parede da direita
    assert isinstance(player.locomotion_state, WallSlidingState)

    # Act (Quando)
    player.handle_input("JUMP")

    # Assert (Então)
    # 1. A transição de estado ocorreu
    assert isinstance(player.locomotion_state, JumpingState)
    # 2. A ação (wall_jump) foi executada corretamente
    assert player.y_vel < 0  # Pulou para cima
    assert player.x_vel < 0  # Pulou para longe (esquerda) da parede


def test_can_dash_from_idle_state(player, world_state):
    # 1. Arrange
    # (Given) Dado um jogador parado no chão
    player.change_locomotion_state(IdleState(player))  # troca o estado para idle
    assert isinstance(player.locomotion_state, IdleState)  # checa se está em idle

    # 2. Act
    # (When) Quando o input 'DASH' é ativado
    player.handle_input("DASH")

    # 3. Assert
    # (Then) Então o jogador deve estar no estado DashState
    # e sua velocidade em x_vel deve ser diferente de 0.
    assert isinstance(player.locomotion_state, DashState)
    assert player.x_vel != 0
    assert player.x_vel == player.dash_speed


def test_cannot_dash_in_mid_air(player):
    # 1. Arrange
    # (Given) Dado o jogador pulando
    player.change_locomotion_state(JumpingState())
    assert isinstance(player.locomotion_state, JumpingState)

    # 2. Act
    # (When) Quando o input "DASH" é ativado
    player.handle_input("DASH")

    # 3. Assert
    # (Then) Então o estão NÃO deve mudar
    assert isinstance(player.locomotion_state, JumpingState)


def test_dashing_state_reverts_to_idle_after_duration(player, world_state):
    # 1. Arrange
    # (Given) Dado o jogador no estado DashState
    player.change_locomotion_state(DashState(player))
    assert isinstance(player.locomotion_state, DashState)
    dash_state = player.locomotion_state

    # 2. Act
    # (When) Quando a duração do dash acaba
    dash_state.update(player, world_state, player.dash_duration)

    # 3. Assert
    # (Then) Então o estado do jogador deve mudar para IdleState
    assert isinstance(player.locomotion_state, IdleState)


# --- Testes de Dano e Vida ---

def test_player_takes_damage_and_enters_hurting_state(player):
    # Given: um jogador com vida cheia
    initial_health = player.health
    assert not isinstance(player.locomotion_state, HurtingState)

    # When: o jogador toma dano
    player.take_damage(5)

    # Then: sua vida diminui e ele entra no estado de "machucado"
    assert player.health == initial_health - 5
    assert isinstance(player.locomotion_state, HurtingState)

def test_player_is_invincible_while_in_hurting_state(player):
    # Given: um jogador que acabou de tomar dano
    player.take_damage(5)
    health_after_first_hit = player.health
    assert isinstance(player.locomotion_state, HurtingState)

    # When: ele tenta tomar dano novamente
    player.take_damage(5)

    # Then: sua vida não muda
    assert player.health == health_after_first_hit

def test_player_is_destroyed_when_health_reaches_zero(player):
    # Given: um jogador com pouca vida
    player.health = 5
    assert player.is_destroyed is False

    # When: ele toma dano fatal
    player.take_damage(5)

    # Then: ele é marcado como destruído
    assert player.is_destroyed is True
    assert player.health == 0


# --- Testes da Máquina de Estados da Arma ---

def test_weapon_starts_charging_on_shoot_press(player, world_state):
    # Given: a arma está pronta
    assert isinstance(player.weapon_state, ReadyState)

    # When: o botão de tiro é pressionado
    player.weapon_state.handle_input(player, "SHOOT_PRESS", world_state)

    # Then: o estado da arma muda para Charging
    assert isinstance(player.weapon_state, ChargingState)

def test_weapon_fires_normal_shot_on_early_release(player, world_state):
    # Given: a arma está carregando
    player.change_weapon_state(ChargingState())
    player.fire_normal_shot = Mock()  # Mock para não depender da classe Bullet

    # When: o botão de tiro é solto antes de carregar completamente
    player.weapon_state.handle_input(player, "SHOOT_RELEASE", world_state)

    # Then: um tiro normal é disparado e o estado volta para Ready
    player.fire_normal_shot.assert_called_once()
    assert isinstance(player.weapon_state, ReadyState)

def test_weapon_becomes_fully_charged(player, world_state):
    # Given: a arma está carregando
    player.change_weapon_state(ChargingState())

    # When: tempo suficiente passa
    player.weapon_state.update(player, player.charge_duration, world_state)

    # Then: o estado muda para FullyCharged
    assert isinstance(player.weapon_state, FullyChargedState)

def test_weapon_fires_charged_shot_on_release(player, world_state):
    # Given: a arma está totalmente carregada
    player.change_weapon_state(FullyChargedState())
    player.fire_charged_shot = Mock()  # Mock para não depender da classe Bullet

    # When: o botão de tiro é solto
    player.weapon_state.handle_input(player, "SHOOT_RELEASE", world_state)

    # Then: um tiro carregado é disparado e o estado volta para Ready
    player.fire_charged_shot.assert_called_once()
    assert isinstance(player.weapon_state, ReadyState)

def test_player_loses_a_life_when_health_reaches_zero(player):
    # Given: um jogador com pouca vida
    player.health = 1
    initial_lives = player.lives

    # When: ele toma dano fatal
    player.take_damage(1)

    # Then: ele perde uma vida
    assert player.lives == initial_lives - 1
    assert player.is_destroyed is True

def test_player_is_permanently_destroyed_when_out_of_lives(player):
    # Given: um jogador com pouca vida
    player.health = 1
    player.lives = 1

    # When: ele toma dano fatal
    player.destroy()

    # Then: ele perde uma vida
    assert player.lives == 0
    assert player.is_permanently_destroyed is True

def test_player_death_notifies_PLAYER_DIED_event(player):
    # Arrange (Dado) um observador e um jogador com vidas
    mock_observer = MockObserver()
    player.add_observer(mock_observer)
    player.lives = 2

    # Act (Quando) o jogador é destruído
    player.on_destroy()

    # Assert (Então) o evento correto deve ser notificado
    assert mock_observer.last_event == PlayerEvent.PLAYER_DIED


def test_final_death_notifies_NO_LIVES_REMAINING_event(player):
    # Arrange (Dado) um observador e um jogador na última vida
    mock_observer = MockObserver()
    player.add_observer(mock_observer)
    player.lives = 1

    # Act (Quando) o jogador é destruído
    player.on_destroy()

    # Assert (Então) o evento de fim de jogo deve ser notificado
    assert mock_observer.last_event == GameEvent.NO_LIVES_REMAINING
# main.py
import cProfile
import pstats
from game.game import Game

profile = False

def main():
    """
    Ponto de entrada do Game
    """
    game = Game()
    try:
        game.run()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        game.cleanup()

if __name__ == "__main__":
    if not profile:
        main()

    # --- CÓDIGO DE PROFILING ---
    # Cria a instância do jogo aqui
    game_instance = Game()

    # Executa o jogo sob o profiler e salva os resultados em 'profile_stats'
    cProfile.run('game_instance.run()', 'profile_stats')

    # Faz a limpeza depois que o jogo fecha
    game_instance.cleanup()
    # -------------------------
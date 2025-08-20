# main.py
from game.game import Game

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
    main()
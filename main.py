import sys
sys.stdout.reconfigure(encoding='utf-8')

from engine.game_engine import GameEngine

def main():
    engine = GameEngine()
    engine.run_game()

if __name__ == "__main__":
    main()
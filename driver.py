#!/opt/anaconda3/bin/python3
from gameplay import Gameplay


if __name__ == '__main__':
    size = (640, 480)
    game = Gameplay(size=size)
    game.start()
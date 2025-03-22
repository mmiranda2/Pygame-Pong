#!/opt/anaconda3/bin/python3
import os
from gameplay import Gameplay


RESOURCES_PATH = 'pygame-pong/resources'


def load_resource(filename, mode='rb'):
    resource_path = RESOURCES_PATH
    if filename[0] == '.':
        resource_path = os.getcwd()
    with open(os.path.join(resource_path, filename), mode=mode) as rsrc:
        resource = rsrc.read()
    return resource


if __name__ == '__main__':
    ball_img = load_resource(BALL_IMG_PATH)
    paddle_img = load_resource(BALL_PADDLE_PATH)
    game = Gameplay(size=size, on_hit_acceleration=ON_HIT_ACCELERATION, on_score_pause=ON_SCORE_PAUSE)
    game.start()
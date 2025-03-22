import os
import time
import random
import json
import yaml
import pygame


class DisplayException(Exception):
    def __init_(self, resolution=0, size=0, supported={}):
        msg = 'Resolution=%s or size=%s not supported. Supported=\n%s\n in settings' % (resolution, size, supported)
        super().__init__(msg)


class Resources:
    objects = [Ball, Paddle, Scoreboard]
    def __init__(self, static_folder):
        self.static_folder = static_folder
        self.resources = self.load_resource('resources.yml', load=yaml.safe_load)
        self.load_settings()

    def load_resource(self, filename, mode='r', load=lambda f: f.read()):
        resource_path = self.static_folder
        if filename[0] == '.':
            resource_path = os.getcwd()
        with open(os.path.join(resource_path, filename), mode=mode) as rsrc:
            resource = load(rsrc)
        return resource

    def load_settings(self):
        self.static = self.resources.get('static')
        self.settings = self.load_resource(self.resources.get('settings'))
        self.screen_sizes = self.load_resource(self.settings.get('screens'))
    
    def get_display(self, display, resolution="HD", size=720):
        heights = self.screen_sizes.get(resolution, [])
        if size not in heights:
            raise DisplayException(resolution, size, supported=json.dumps(self.screen_sizes))

        aspect = self.screen_sizes["RATIOS"][resolution]
        aspect_ratio = aspect[0] / aspect[1]
        width, height = size, size * aspect_ratio

        return display.set_mode((width, height))

    def get_resources(self, screen):
        def get_obj(obj_type, **kwargs):
            obj_name = obj_type.__name__.lower()
            filename = self.static.get(obj_name, '%s.png' % obj_name)
            img = self.load_resource(filename, mode='rb', load=pygame.image.load)
            return obj_type(screen, img, **kwargs)

        self.ball = get_obj(Ball)
        self.right_paddle = get_obj(Paddle, side='right')
        self.left_paddle = get_obj(Paddle, side='left')
        self.scoreboard = get_obj(Scoreboard)
        self.objects = [self.ball, self.right_paddle, self.left_paddle, self.scoreboard]

        return self.objects


class Item:
    def __init__(self, screen, img):
        self.screen = screen
        self.img = img
        self.position = (0, 0)

    def width(self):
        return self.img.get_width()
    
    def height(self):
        return self.img.get_height()
    
    def size(self):
        return self.width(), self.height()

    def set_pos(self, tup):
        self.position = tup
    
    def move(self, tup):
        # tup is change in position
        next_pos = (self.position[0] + tup[0], self.position[1] + tup[1])
        next_pos = self._inbounds(next_pos)
        self.set_pos(next_pos)
    
    def show(self):
        self.screen.blit(self.img, self.position)
    
    def goto(self, pos):
        self.set_pos(pos)
        self.show()
    
    def _inbounds(self, tup):
        width = self.screen.get_width()
        height = self.screen.get_height()

        x_max = width - self.img.get_width()
        y_max = height - self.img.get_height()

        new_x = min(x_max, max(0, tup[0]))
        new_y = min(y_max, max(0, tup[1]))

        return (new_x, new_y)


class Paddle(Item):
    def __init__(self, screen, img, side):
        super().__init__(screen, img)
        self.side = side
        if side == 'left':
            self.x_fixed = -int(self.img.get_width() / 2) - 1
        elif side == 'right':
            self.x_fixed = self.screen.get_width() - int(self.img.get_width() / 2) - 1

        mid_height = int(self.screen.get_height() / 2)
        self.set_pos((self.x_fixed, mid_height))
        
    def set_pos(self, tup):
        super().set_pos((self.x_fixed, tup[1]))
    
    def up(self):
        self.move((0, -10))
    
    def down(self):
        self.move((0, 10))
    
    def get_window(self):
        radius_x = int(self.img.get_width() / 2)

        window_x = (self.x_fixed, radius_x) if self.side == 'left' else (self.x_fixed - radius_x, self.x_fixed)
        window_y = (self.position[1], self.position[1] + self.img.get_height())
        
        window = (window_x, window_y)
        return window


class Ball(Item):
    ON_HIT_ACCELERATION = 1
    ON_SCORE_PAUSE = 1
    def __init__(self, screen, img, velocity_rate_inc=None, score_pause_secs=None):
        super().__init__(screen, img)
        if not velocity_rate_inc:
            velocity_rate_inc = Ball.ON_HIT_ACCELERATION
        if not score_pause_secs:
            score_pause_secs = Ball.ON_SCORE_PAUSE
        self.velocity_rate_inc = velocity_rate_inc
        self.score_pause_secs = score_pause_secs
        self.initialize(self.score_pause_secs)
    
    def lock(self, locked=True):
        self.locked = locked
    
    def unlock(self):
        self.locked = False

    def initialize(self):
        self.sleep(self.velcity_rate_inc)
        mid_height = int(self.screen.get_height() / 2)
        mid_width = int(self.screen.get_width() / 2)
        self.set_pos((mid_width, mid_height))

        x_velocity = random.uniform(0.4, 1)
        y_velocity = random.uniform(0.4, x_velocity)

        x_velocity, y_velocity = 10*x_velocity, 10*y_velocity
        self.velocity = [x_velocity, y_velocity]

    def next(self, left_window, right_window):
        if self.locked:
            return 0

        hit_left_paddle = self.in_window(left_window)
        hit_right_paddle = self.in_window(right_window)

        if hit_left_paddle or hit_right_paddle:
            self.velocity[0] *= -1
            self.velocity = [ self.velocity_rate_inc * v for v in self.velocity ]
        else:
            goal = self.scored()
            if goal != 0:
                self.initialize()
                return goal

        if self.hit_rails():
            self.velocity[1] *= -1

        self.move(self.velocity)
        return 0

    def in_window(self, window):
        x_window, y_window = window
        in_x = x_window[0] <= self.position[0] and self.position[0] <= x_window[1]
        in_y = y_window[0] <= self.position[1] and self.position[1] <= y_window[1]
        in_window = in_x and in_y

        return in_window
    
    def hit_rails(self):
        if self.position[1] <= 0:
            return True
        elif self.position[1] >= self.screen.get_height() - self.img.get_height():
            return True
        return False
    
    def scored(self):
        if self.position[0] <= 0:
            return -1
        elif self.position[0] >= self.screen.get_width() - self.img.get_width():
            return 1
        return 0


class TextBox(Item):
    COLOR_WHITE = (255, 255, 255)
    def __init__(self, screen, img, text, color=None):
        super().__init__(screen, img)
        if not color:
            self.color = TextBox.COLOR_WHITE
        self.set_text(text)

    def set_text(self, text, color=None):
        self.text = text
        if color:
            self.color = color
        self.label = self.img.render(self.text, False, self.color)


class Scoreboard:
    def __init__(self, screen, label='SCORE', font='Comic Sans MS'):
        self.right_score = 0
        self.left_score = 0
        self.screen = screen

        pygame.font.init()
        self.font = pygame.font.SysFont(font, 30)
        self.label = TextBox(self.screen, self.font, label)
        self.right_text = TextBox(self.screen, self.font, str(self.right_score))
        self.left_text = TextBox(self.screen, self.font, str(self.left_score))

        self.show()

        # self.left_text = self.font.render(str(self.left_score), False, (255, 255, 255))
        # self.label = self.font.render('SCORE', False, (255, 255, 255))
        # self.right_text = self.font.render(str(self.right_score), False, (255, 255, 255))
        # self.left_text = self.font.render(str(self.left_score), False, (255, 255, 255))

        # self.label_loc = (int(self.screen.get_width() / 2) - 35, 10)
        # self.right_text_loc = (self.label_loc[0] + self.label.get_width() + 10, 10)
        # self.left_text_loc = (self.label_loc[0] - self.left_text.get_width() - 10, 10)
        
        # self.objects = [(self.label, self.label_loc), (self.right_text, self.right_text_loc), (self.left_text, self.left_text_loc)]

    def show(self):
        label_pos = (int(self.screen.get_width() / 2) - 35, 10)
        right_text_pos =  (label_pos[0] + self.label.width() + 10, 10)
        left_text_pos = (label_pos[0] - self.left_text.width() - 10, 10)

        self.label.goto(label_pos)
        self.right_text.goto(right_text_pos)
        self.left_text.goto(left_text_pos)

        # for obj in self.objects:
        #     self.screen.blit(*obj)
    
    def score(self, goal):
        if goal != 0:
            if goal == 1:
                self.right_score += 1
                self.right_text.set_text(str(self.right_score))
                # self.right_text = self.font.render(str(self.right_score), False, (255, 255, 255))
            if goal == -1:
                self.left_score += 1
                self.left_text.set_text(str(self.left_score))
                # self.left_text = self.font.render(str(self.left_score), False, (255, 255, 255))
            # self.objects = [(self.label, self.label_loc), (self.right_text, self.right_text_loc), (self.left_text, self.left_text_loc)]

import pygame
import random


class Item:
    def __init__(self, screen, img_path):
        self.screen = screen
        self.img = pygame.image.load(img_path)
        self.position = (0, 0)

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
    def __init__(self, screen, img_path, side):
        super().__init__(screen, img_path)
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
    def __init__(self, screen, img_path):
        super().__init__(screen, img_path)
        self.initialize()
    
    def initialize(self):
        mid_height = int(self.screen.get_height() / 2)
        mid_width = int(self.screen.get_width() / 2)
        self.set_pos((mid_width, mid_height))

        x_velocity = random.uniform(0.4, 1)
        y_velocity = random.uniform(0.4, x_velocity)

        x_velocity, y_velocity = 10*x_velocity, 10*y_velocity
        self.velocity = [x_velocity, y_velocity]

    def next(self, left_window, right_window):
        hit_left_paddle = self.in_window(left_window)
        hit_right_paddle = self.in_window(right_window)

        if hit_left_paddle or hit_right_paddle:
            self.velocity[0] *= -1
            self.velocity = [ 1.1 * v for v in self.velocity ]
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


class Scoreboard:
    def __init__(self, screen):
        self.right_score = 0
        self.left_score = 0
        self.screen = screen

        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.label = self.font.render('SCORE', False, (255, 255, 255))
        self.right_text = self.font.render(str(self.right_score), False, (255, 255, 255))
        self.left_text = self.font.render(str(self.left_score), False, (255, 255, 255))

        self.label_loc = (int(self.screen.get_width() / 2) - 35, 10)
        self.right_text_loc = (self.label_loc[0] + self.label.get_width() + 10, 10)
        self.left_text_loc = (self.label_loc[0] - self.left_text.get_width() - 10, 10)
        
        self.objects = [(self.label, self.label_loc), (self.right_text, self.right_text_loc), (self.left_text, self.left_text_loc)]
    
    def show(self):
        for obj in self.objects:
            self.screen.blit(*obj)
    
    def score(self, goal):
        if goal != 0:
            if goal == 1:
                self.right_score += 1
                self.right_text = self.font.render(str(self.right_score), False, (255, 255, 255))
            elif goal == -1:
                self.left_score += 1
                self.left_text = self.font.render(str(self.left_score), False, (255, 255, 255))
            self.objects = [(self.label, self.label_loc), (self.right_text, self.right_text_loc), (self.left_text, self.left_text_loc)]


import pygame
import time
from objects import Ball, Paddle, Scoreboard
from pygame.locals import *


class Gameplay:
    def __init__(self, size):
        self.width, self.height = size
        self.size = size
        
    def start(self):
        print("Let's play!")
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)

        self.ball = Ball(self.screen, img_path='./ball.png')
        self.right_paddle = Paddle(self.screen, img_path='./paddle.png', side='right')
        self.left_paddle = Paddle(self.screen, img_path='./paddle.png', side='left')
        self.scoreboard = Scoreboard(self.screen)
        self.objects = [self.ball, self.right_paddle, self.left_paddle, self.scoreboard]

        self.reset = True
        counter = 0
        fps_start = time.time()
        while True:
            if self.reset:
                self.scoreboard.display_banner(True)
                start = time.time()
                while time.time() - start < 3:
                    self.play(True)
                self.reset = False
                self.scoreboard.display_banner(False)
            else:
                self.play()
            counter += 1
            fps_end = time.time()
            if fps_end - fps_start > 1:
                self.scoreboard.set_fps(counter)
                counter = 0
                fps_start = fps_end

    def play(self, lock_ball=False):
        self.screen.fill(0)
        for obj in self.objects:
            obj.show()
        pygame.display.flip()

        self.apply_pressed_bars()
        self.apply_events()
        if not lock_ball:
            self.apply_ball_movement()

    def apply_pressed_bars(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            self.right_paddle.down()
        if keys[pygame.K_UP]:
            self.right_paddle.up()
        if keys[pygame.K_s]:
            self.left_paddle.down()
        if keys[pygame.K_w]:
            self.left_paddle.up()

    def apply_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.quit()
                elif event.key == pygame.K_DOWN:
                    self.right_paddle.down()
                elif event.key == pygame.K_UP:
                    self.right_paddle.up()
                elif event.key == pygame.K_s:
                    self.left_paddle.down()
                elif event.key == pygame.K_w:
                    self.left_paddle.up()

    def apply_ball_movement(self):
        left_paddle_window, right_paddle_window = self.left_paddle.get_window(), self.right_paddle.get_window()
        goal = self.ball.next(left_paddle_window, right_paddle_window)
        if goal != 0:
            self.scoreboard.score(goal)
            self.reset = True

    def quit(self):
        print('Goodbye.')
        pygame.quit()
        exit()
        




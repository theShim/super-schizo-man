import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import cv2
import numpy as np
import random
import math

from scripts.config.SETTINGS import WIDTH, HEIGHT
from scripts.config.CORE_FUNCS import gaussian_blur

    ##############################################################################################

class Text_Box(pygame.sprite.Sprite):
    def __init__(self, text, pos, font, box_size = None, border_colour = None, background_colour = None):
        super().__init__()
        self.text = text
        self.font = font
        self.pos = pos

        self.box_size = box_size
        self.border_colour = border_colour
        self.background_colour = background_colour

        self.t = 0
        self.speed = 0.4
        self.finished = False

    def reset(self):
        self.t = 0
        self.finished = False

    def change_speed(self, speed):
        self.speed = speed

    def update(self):
        if self.t < len(self.text):
            self.t += self.speed
        else:
            self.finished = True
            return

        if self.text[min(len(self.text)-1, int(self.t))] == "\t":
            self.change_speed(0.05)
        elif self.text[min(len(self.text)-1, int(self.t))] == ".":
            self.change_speed(0.075)
        elif self.text[min(len(self.text)-1, int(self.t))] == ",":
            self.change_speed(0.1)
        else:
            self.change_speed(0.4)

    def render(self, screen, col=(255, 255, 255)):
        if self.box_size != None:
            if self.background_colour != None:
                pygame.draw.rect(screen, self.background_colour, [*self.pos, *self.box_size])

            pygame.draw.rect(screen, self.border_colour, [*self.pos, *self.box_size], 4)

        text = f"{self.text[:int(self.t)]}"
        self.font.render(screen, text, col, self.pos)

#MAX LINE LENGTH = 76 FOR CUTSCENES
        
class Rainbow_Text_Box(Text_Box):

    def __init__(self, text, pos, font, box_size, border_radius=3):
        super().__init__(text, pos, font, box_size)

        self.window = pygame.Surface((box_size[0]*3, box_size[1]))
        x, y = np.meshgrid(np.linspace(0, 1, box_size[1]), np.linspace(0, 1, box_size[0]))
        rainbow_colors = [
            (255, 0, 0),    # Red
            (255, 64, 0),
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 200, 200),
            (0, 0, 255),    # Blue
            (75, 0, 130),   # Indigo
            (148, 0, 211),   # Violet,
        ]
        rainbow_array = np.array(rainbow_colors) / 255.0
        distance = np.sqrt((x-0.15)**2 + (y-0.3)**2)

        color_index = np.clip((distance * (len(rainbow_colors) - 1)).astype(int), 0, len(rainbow_colors) - 2)
        color_fraction = distance * (len(rainbow_colors) - 1) - color_index
        interpolated_color = (1 - color_fraction[:, :, np.newaxis]) * rainbow_array[color_index] + \
                            color_fraction[:, :, np.newaxis] * rainbow_array[color_index + 1]
        interpolated_color = (np.clip(interpolated_color, 0, 1))
        surf = pygame.surfarray.make_surface((interpolated_color * 255))

        self.window.blit(surf, (0, 0))
        self.window.blit(pygame.transform.flip(surf, True, False), (box_size[0], 0))
        self.window.blit(surf, (box_size[0]*2, 0))
        self.x = 0

        self.border_radius = border_radius
        self.inner = pygame.Surface((self.box_size[0] - self.border_radius*2, self.box_size[1] - self.border_radius*2), pygame.SRCALPHA)
        self.inner.fill((255, 255, 230))

    def render(self, screen, col=(255, 255, 255)):
        # self.window = pygame.Surface((self.box_size[0]*2, self.box_size[1]))
        try:
            rainbow = gaussian_blur(self.window.subsurface([self.x, 0, *self.box_size]), radius=3)
            rainbow.set_alpha(230)
            screen.blit(rainbow, self.pos)
        except:
            self.x = 0
            rainbow = gaussian_blur(self.window.subsurface([self.x, 0, *self.box_size]), radius=3)
            rainbow.set_alpha(230)
            screen.blit(rainbow, self.pos)
        self.x += 1
        
        screen.blit(self.inner, (self.pos[0] + self.border_radius, self.pos[1] + self.border_radius))
        # pygame.draw.rect(screen, (255, 255, 230), [self.pos[0] + self.border_radius, self.pos[1] + self.border_radius, self.box_size[0] - self.border_radius*2, self.box_size[1] - self.border_radius*2])

        text = f"{self.text[:int(self.t)]}"
        self.font.render(screen, text, col, self.pos)
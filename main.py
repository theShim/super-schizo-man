import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['SDL_VIDEO_CENTERED'] = '1'

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    
import random
import sys
import math
import time
import numpy as np

from config.SETTINGS import *
from config.CORE_FUNCS import *

if DEBUG:
    #code profiling for performance optimisations
    import pstats
    import cProfile
    import io

    ##############################################################################################

class Game:
    def __init__(self):
        #intiaising pygame stuff
        self.initialise()

        #initalising pygame window
        flags = pygame.RESIZABLE | pygame.SCALED
        self.screen = pygame.display.set_mode(SIZE, flags)
        self.clock = pygame.time.Clock()

    def initialise(self):
        pygame.init()  #general pygame
        pygame.font.init() #font stuff
        pygame.display.set_caption(WINDOW_TITLE) #Window Title 

        pygame.mixer.pre_init(44100, 16, 2, 4096) #music stuff
        pygame.mixer.init()

        pygame.event.set_blocked(None) #setting allowed events to reduce lag
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEWHEEL])


    def run(self):
        if DEBUG:
            PROFILER = cProfile.Profile()
            PROFILER.enable()

        running = True
        while running:
            #deltatime
            dt = self.clock.tick(FPS) / (1000 * (60 / FPS))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    
            self.screen.fill((30, 30, 30))


            if DEBUG or not DEBUG:
                debug_info = f"FPS: {int(self.clock.get_fps())}"
                pygame.display.set_caption(f"{WINDOW_TITLE} | {debug_info}")

            pygame.display.update()

        if DEBUG:
            PROFILER.disable()
            PROFILER.dump_stats("config/profiler.stats")
            pstats.Stats("config/profiler.stats", stream=(s:=io.StringIO())).sort_stats((sortby:=pstats.SortKey.CUMULATIVE)).print_stats()
            print(s.getvalue())

        pygame.quit()
        sys.exit()
    

    ##############################################################################################

if __name__ == "__main__":
    game = Game()
    game.run()
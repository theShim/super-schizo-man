import contextlib
with contextlib.redirect_stdout(None):
    import pygame; pygame.init()
    from pygame.locals import *
    
import math
import random
import os
import numpy as np

from scripts.world_loading.grass import Grass_Manager
from scripts.config.SETTINGS import TILE_SIZE, Z_LAYERS
from scripts.config.CORE_FUNCS import euclidean_distance

    ##############################################################################################

class Nature_Manager:
    def __init__(self, game):
        self.game = game
        
        self.grass_manager = Grass_Manager(game)

    def add_tile(self, type, pos, variant):
        if type == "grass":
            loc = f"{int(pos[0]//TILE_SIZE)};{int(pos[1]//TILE_SIZE)}"
            self.grass_manager.add_tile(loc, pos, variant)

    def render_tiles(self, offset):
        self.grass_manager.t += 5
        grass_tiles = [t for t in self.grass_manager.tiles_to_render(offset)]
        for tile in grass_tiles: yield tile
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['SDL_VIDEO_CENTERED'] = '1'

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    
import sys
import time

from scripts.config.SETTINGS import (DEBUG, WINDOW_TITLE, SIZE, WIDTH, HEIGHT, LOADED_SPRITE_NUMBER, 
                                     MAX_LOADED_SPRITES, FPS, CAMERA_FOLLOW_SPEED)
from scripts.config.CORE_FUNCS import vec

from scripts.entities.player import Player
from scripts.entities.butterfly import Butterfly

from scripts.gui.cursor import Cursor
from scripts.gui.overlay import CRT_Overlay
from scripts.gui.custom_fonts import Custom_Font

from scripts.music.music_player import Music_Player

from scripts.world_loading.tilemap import Tile, Offgrid_Tile
from scripts.world_loading.stages import Stage_Loader
from scripts.world_loading.backgrounds import Forest_Background
from scripts.world_loading.nature_tiles import Grass, Grass_Blade
from scripts.world_loading.light_tiles import Torch

from screen_recorder import ScreenRecorder

    ##############################################################################################

if DEBUG:
    #code profiling for performance optimisations
    import pstats
    import cProfile
    import io
    
    PROFILER = cProfile.Profile()

    ##############################################################################################

class Game:
    def __init__(self):
        #initialising pygame stuff
        self.initialise()
        
        #initalising pygame window
        flags = pygame.RESIZABLE | pygame.SCALED | pygame.DOUBLEBUF | pygame.HWSURFACE
        self.screen = pygame.display.set_mode(SIZE, flags)
        pygame.display.toggle_fullscreen()

        self.running = True #"global" flag for if the window is running
        self.clock = pygame.time.Clock()
        self.dt = 1
        self.offset = vec() #screen offset for every object to blit onto, possibly better to just blit an entire window after but whatever

        #loading screen with pseudo loading, just increments a counter with every img loaded
        self.startup_loadscreen()

        #only load other stuff once everything has been cached
        self.entities = pygame.sprite.Group()
        self.player = Player(self, self.entities, 2)
        self.stage_loader = Stage_Loader(self)

        self.cursor = Cursor()

        self.camera_flag = False
        self.screen_recorder = None
        self.record_label = self.font.render("REC", False, (255, 255, 255))
        self.record_label_pos = self.record_label.get_rect(topright=(WIDTH-10, 8))

        self.music_player = Music_Player(channel_num=20)

        self.overlay = CRT_Overlay(self)

        ######################################################################################

    def initialise(self):
        pygame.init()  #general pygame
        pygame.display.set_caption(WINDOW_TITLE)

        pygame.font.init() #font stuff
        self.font = pygame.font.SysFont('Verdana', 10)

        #music stuff
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.mixer.init()

        #setting allowed events to reduce lag
        pygame.event.set_blocked(None) 
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEWHEEL])

    def startup_loadscreen(self):
        Custom_Font.init() #my own fonts
    
        #number of sprites/stuff already been loaded
        global LOADED_SPRITE_NUMBER

        LOADED_SPRITE_NUMBER = 0 #reset
        font = pygame.font.SysFont('Verdana', 30)

        #every object to cache sprites of at the beginning of the game, tiles, offgrid_tiles and backgrounds mostly
        objects = [t.cache_sprites() for t in [Tile, Offgrid_Tile, 
                                               Forest_Background,
                                               Player, Butterfly,
                                               Grass_Blade,
                                               Torch,]]

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False

            self.screen.fill((0, 0, 0))

            #cache every sprite of every object
            for o in objects:
                try:
                    next(o)
                    LOADED_SPRITE_NUMBER += 1 #increment
                    break
                except StopIteration:
                    continue

            #if the number of loaded sprites reaches the pre-defined number of existing sprites exit the loading screen
            if LOADED_SPRITE_NUMBER >= MAX_LOADED_SPRITES:
                self.running = False
            # print(LOADED_SPRITE_NUMBER)

            #displaying current load percentage
            percentage = font.render(f"{int(100 * LOADED_SPRITE_NUMBER / MAX_LOADED_SPRITES)}%", False, (255, 255, 255))
            self.screen.blit(percentage, (WIDTH - percentage.get_width() - 20, HEIGHT - percentage.get_height() - 10))

            pygame.display.update()
            self.clock.tick(FPS)

        #resetting the running flag for actual game window
        self.running = True

        ######################################################################################

    def calculate_offset(self):
        #have the screen offset kinda lerp to the player location
        self.offset.x += (self.player.rect.centerx - WIDTH/2 - self.offset.x) / CAMERA_FOLLOW_SPEED
        self.offset.y += (self.player.rect.centery - HEIGHT/2 - self.offset.y) / CAMERA_FOLLOW_SPEED

        #restricting the offsets
        #MAKE THIS DIFFERENT ACCORDING TO CUSTOM STAGE SIZES LATER
        if self.offset.x < 0:
            self.offset.x = 0
        # if self.offset.x > math.inf:
        #     self.offset.x = math.inf

    def run(self):
        if DEBUG:   
            PROFILER.enable()

        last_time = time.perf_counter()
        while self.running:  
            #deltatime
            self.dt = time.perf_counter() - last_time
            self.dt *= FPS
            last_time = time.perf_counter()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False

                    elif event.key == pygame.K_F7:
                        self.camera_flag = not self.camera_flag

                        if self.camera_flag:
                            self.screen_recorder = ScreenRecorder(
                                WIDTH, 
                                HEIGHT, 
                                FPS, 
                                f"recordings/{time.strftime('%d.%m.%Y_%H.%M_REC', time.localtime())}.mp4")
                        else:
                            self.screen_recorder.end_recording()

            
            # self.calculate_offset()
            # self.screen.fill((30, 30, 30))
            
            self.stage_loader.render(self.player)
            self.cursor.update(self.screen)
            # self.overlay.update()

            #FPS
            if DEBUG:
                debug_info = (
f"""FPS: {int(self.clock.get_fps())}
Pos: {[int(self.player.rect.x), int(self.player.rect.y)*-1]}
Vel: {list(map(lambda x: round(x, 1), self.player.vel))}
Jumps: {self.player.jumps}
Landed: {self.player.landed}"""
                )
                label = self.font.render(debug_info, False, (255, 255, 255))
                self.screen.blit(label, (0, 0))

                music_info = f"Music Playing: {self.music_player.background.get_sound().name}"
                music_label = self.font.render(music_info, False, (255, 255, 255))
                self.screen.blit(music_label, (0, HEIGHT-music_label.get_height()))
                

                #rects around the player
                for rect in self.stage_loader.tilemap.physics_rects_around(self.player.hitbox.center):
                    pygame.draw.rect(self.screen, (255, 0, 255), [rect.x - self.offset.x, rect.y - self.offset.y, *rect.size], 2)

            if self.camera_flag:
                self.screen.blit(self.record_label, self.record_label_pos)
                pygame.draw.circle(self.screen, (255, 0, 0), (WIDTH - 16 - self.record_label.get_width(), 10 + self.record_label.get_height()/2), 4)
                self.screen_recorder.capture_frame(self.screen)

            pygame.display.update()
            self.clock.tick(FPS)

    ##############################################################################################

if __name__ == "__main__":
    g = Game()
    g.run()


if DEBUG:
    PROFILER.disable()
    PROFILER.dump_stats("scripts/config/profiler.stats")
    pstats.Stats("scripts/config/profiler.stats", stream=(s:=io.StringIO())).sort_stats((sortby:=pstats.SortKey.CUMULATIVE)).print_stats()
    print(s.getvalue())

    print(LOADED_SPRITE_NUMBER, 'total sprites initially cached.')

pygame.quit()
sys.exit()
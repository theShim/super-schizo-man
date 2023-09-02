import pygame; pygame.init()
import random
import math


#renaming common functions
vec = pygame.math.Vector2


#useful functions
def gen_rand_colour() -> tuple[float]:
    return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

def euclidean_distance(point1: list[float], point2: list[float]) -> float:
    return (((point1[0] - point2[0]) ** 2) + ((point1[1] - point2[1]) ** 2) ** 0.5)

def rotate(origin: list, point: list, angle: float) -> list[float]:
    ox, oy = origin
    px, py = point
    angle = math.radians(angle)

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return [qx, qy]

def lerp(a: float, b: float, lerp_factor: float) -> float:
    return (lerp_factor * a) + ((1 - lerp_factor) * b)


def read_file(path):
    file = open(path)
    data = file.readlines()
    file.close()
    return data

def write_file(path, data):
    file = open(path)
    file.write(data + '\n')
    file.close()


def convert_transparent_image(path, colourkey=(255, 255, 254)): #convert image in place
    screen = pygame.display.set_mode((1, 1), flags=pygame.HIDDEN)
    img = pygame.image.load(path).convert_alpha()
    img.set_colorkey(colourkey)
    pygame.image.save(img, path)
    pygame.quit()
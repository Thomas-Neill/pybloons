import pygame
from util import *
from copy import copy
import math

LEVEL_SPEEDS = [1,1,2,2,3]

LEVEL_COLORS = [(255,0,0),(0,0,255),(0,200,100),(255,255,0),(125,125,125)]
FROZEN_LEVEL_COLORS = [(200,192,238),(126,192,238),(126,240,238),(100,200,238),(125,125,255)]

TANK_COLOR = None
FROZEN_TANK_COLOR = None

BLOON_SIZE = (30,30)
BLOON_OFFSET = ((.5 * BLOON_SIZE[0]**2)**.5,(.5 * BLOON_SIZE[1]**2)**.5)

def init_bloon_sprites():
    global LEVEL_COLORS,FROZEN_LEVEL_COLORS,TANK_COLOR,FROZEN_TANK_COLOR
    def bloon_with_color(color):
        surf = pygame.Surface(BLOON_SIZE).convert_alpha()
        surf.fill(color)
        surf = pygame.transform.rotate(surf,45)
        return surf
    LEVEL_COLORS = list(map(bloon_with_color,LEVEL_COLORS))
    FROZEN_LEVEL_COLORS = list(map(bloon_with_color,FROZEN_LEVEL_COLORS))
    TANK_COLOR = bloon_with_color((0,0,0))
    FROZEN_TANK_COLOR = bloon_with_color((50,0,0))

X,Y = 0,1
class Bloon:
    def __init__(self,path,level=0,customspeed=None):
        self.x = path[0][X]
        self.y = path[0][Y]
        self.path = path[1:]
        self.dead = False #tell the bullets!
        self.level = level
        self.customspeed = customspeed
        self.frozen = 0

    def update(self,game):
        if(self.frozen > 0):
            self.frozen -= 1
            return
        new = self.after(self.customspeed or LEVEL_SPEEDS[self.level])
        if(not new):
            game.end(self)
        else:
            self.x,self.y,self.path = new

    def move(self,x,y,path): #-> (x1,y1,path1)
        if(round(x) == path[0][X] and round(y) == path[0][Y]):
            path = path[1:]
            if(len(path) == 0):
                return None
        dx,dy = path[0][X]-x,path[0][Y]-y
        norm = math.sqrt(dx**2 + dy**2)
        dx /= norm
        dy /= norm
        x,y = x+dx,y+dy
        return x,y,path

    def after(self,ticks):
        x = self.x
        y = self.y
        path = copy(self.path)
        for i in range(ticks):
            new = self.move(x,y,path)
            if(not new):
                return new
            x,y,path = new
        return x,y,path

    def draw(self,window):
        col = LEVEL_COLORS[self.level] if not self.frozen else FROZEN_LEVEL_COLORS[self.level]
        window.blit(col,(self.x-BLOON_OFFSET[0],self.y-BLOON_OFFSET[1]))

    def damage(self,game):
        if(self.level == 0):
            self.dead = True
            game.kill(self)
            return True
        else:
            self.level -= 1
            return False


class TankBloon(Bloon):
    def __init__(self,path,hp):
        super().__init__(path,hp,customspeed=2)
    def draw(self,window):
        col = TANK_COLOR if not self.frozen else FROZEN_TANK_COLOR
        window.blit(col,(self.x-BLOON_OFFSET[0],self.y-BLOON_OFFSET[1]))

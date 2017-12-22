from util import dist
from effects import ColorFadeCircle
from copy import copy

import pygame,time
class Bullet:
    def __init__(self,tower,target):
        delta_t = dist(tower.x,tower.y,target.x,target.y) // 10 #kinda works...
        if(delta_t == 0): delta_t = 1
        self.tower = tower
        self.valid = True
        self.x = tower.x
        self.y = tower.y
        self.target = target

        self.remaining = delta_t
        self.dx =  (target.x - tower.x) / delta_t
        self.dy = (target.y - tower.y) / delta_t
    def update(self,game):
        if(self.target.dead):
            self.valid = False
            return
        if(self.remaining == 1):
            self.target.damage(game)
            self.valid = False
            return
        self.x += self.dx
        self.y += self.dy
        self.remaining = self.remaining - 1
    def draw(self,window):
        pygame.draw.rect(window,(0,0,0),(self.x-2.5,self.y-2.5,5,5))

class ExplodingBullet(Bullet):
    def __init__(self,tower,target,range):
        super().__init__(tower,target)
        self.range = range
    def update(self,game):
        if(self.remaining == 1):
            for i in copy(game.bloons):
                if(dist(self.x,self.y,i.x,i.y) < self.range + 10):
                    i.damage(game)
            self.valid = False
            game.add_effect(ColorFadeCircle(self.x+self.dx,self.y+self.dy,(255,0,0),self.range,100,20))
            return
        super().update(game)

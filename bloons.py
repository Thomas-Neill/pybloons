import pygame
from pygame.locals import *
import random
import math
import itertools
import threading

from bloon import Bloon,init_bloon_sprites
from tower import *
import copy
from util import *
from config import GameConfig

DISP_SIZE = 1000

class Game:
    def __init__(self):
        #pygame
        pygame.init()
        self.fnt = pygame.font.Font(pygame.font.get_default_font(),30)
        self.smallfnt = pygame.font.Font(pygame.font.get_default_font(),20)
        self.window = pygame.display.set_mode((DISP_SIZE,DISP_SIZE))
        #entities
        self.bloons = []
        self.towers = []
        self.bullets = []
        self.effects = []
        #load config file
        self.conf = GameConfig("testlevels.json")
        self.pathimg = pygame.image.load(self.conf.pathimg)
        #state
        self.ticks = 0
        self.money = 100
        self.life = 100
        #gui state
        self.selectedTowerType = None
        self.selectedTower = None
        self.remarkText = None

        init_bloon_sprites()

    def draw(self):
        self.window.blit(self.pathimg,(0,150))
        for bloon in self.bloons:
            bloon.draw(self.window)
        for tower in self.towers:
            tower.draw(self.window)
        for bullet in self.bullets:
            bullet.draw(self.window)
        for effect in self.effects:
            effect.draw(self.window)
        if(self.selectedTowerType):
            self.selectedTowerType.draw_(self.window,*pygame.mouse.get_pos())
        self.render_hud()
        pygame.display.update()

    def render_hud(self):
        pygame.draw.rect(self.window,(210,190,190),(0,0,1000,150))
        x = 200
        for tow in tower_types: # draw 'store window'
            self.window.blit(self.smallfnt.render(f"${tow.price}",False,(0,0,0)),(x,0))
            pygame.draw.rect(self.window,tow.color,(x,20,30,30))
            x += 50
        self.window.blit(self.fnt.render(f"Money: ${self.money}",False,(0,0,0)),(0,0))
        self.window.blit(self.fnt.render(f"Life:   {self.life}",False,(0,0,0)),(0,30))

        #main text display
        pygame.draw.line(self.window,(0,0,0),(0,75),(1000,75))
        if(self.selectedTowerType):
            self.window.blit(self.fnt.render(self.selectedTowerType.desc,False,(0,0,0)),(0,80))
        elif(self.remarkText):
            self.window.blit(self.fnt.render(self.remarkText,False,(0,0,0)),(0,80))

        #upgrade sidebar
        pygame.draw.line(self.window,(0,0,0),(700,0),(700,150))
        if(self.selectedTower):
            y = 0
            for up in self.selectedTower.upgrades:
                if(up):
                    self.window.blit(self.fnt.render(f"{up.name}: ${up.price}",False,(0,0,0)),(700,y))
                    self.window.blit(self.smallfnt.render(f"{up.desc}",False,(0,0,0)),(700,y+30))
                else:
                    self.window.blit(self.fnt.render("No upgrade",False,(0,0,0)),(700,y))
                y += 75

    def inputs(self):
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                stop_after_first_true(
                    [self.choose_new_tower,
                     self.place_new_tower,
                     self.select_tower,
                     self.choose_upgrade,
                     self.bad_click],
                    event)
            if event.type == QUIT:
                self.stop()

    def choose_new_tower(self,event):
        x = 200
        for tow in tower_types:
            if(in_box(event.pos[0],event.pos[1],x,20,30,centered=False)):
                self.selectedTowerType = tow
                self.selectedTower = None
                return True
            x += 50

    def place_new_tower(self,event):
        if(self.selectedTowerType):
            if(self.money >= self.selectedTowerType.price):
                if(self.is_good_place_pos(event.pos)):
                    self.towers.append(self.selectedTowerType(event.pos[0],event.pos[1],self.ticks))
                    self.money -= self.selectedTowerType.price
                    self.selectedTowerType = None
                    return True

    def is_good_place_pos(self,pos):
        for tower in self.towers:
            if(box_collide(pos[0],pos[1],tower.x,tower.y,TOWER_SIZE)):
                return False
        return True

    def select_tower(self,event):
        for tower in self.towers:
            if(in_box(event.pos[0],event.pos[1],tower.x,tower.y,TOWER_SIZE,centered=True)):
                self.selectedTowerType = None
                self.selectedTower = tower
                return True

    def choose_upgrade(self,event):
        if(self.selectedTower):
            y = 0
            for up in self.selectedTower.upgrades:
                if(in_rect(event.pos[0],event.pos[1],700,y,300,75)):
                    if(self.money >= up.price):
                        self.money -= up.price
                        up.action(self.selectedTower)
                        self.selectedTower.upgrades.remove(up)
                        if(up.next):
                            self.selectedTower.upgrades.append(up.next)
                        return True
                y += 75

    def bad_click(self,event):
        self.selectedTowerType = None
        self.selectedTower = None

    def update(self):
        nxt = self.conf.next_bloon()
        if(self.conf.done and not self.bloons):
            self.win()
        if(self.conf.intermission and not self.bloons):
            self.level_intermission(self.conf.remark,self.conf.reward)
        if(nxt):
            self.bloons.append(nxt)
        for bloon in self.bloons:
            bloon.update(self)
        for tower in self.towers:
            tower.update(self)
        nb = []
        for bullet in self.bullets:
            bullet.update(self)
            if(bullet.valid):
                nb.append(bullet)
        self.bullets = nb
        ne = []
        for effect in self.effects:
            effect.update(self)
            if(effect.valid):
                ne.append(effect)
        self.effects = ne

    def loop(self):
        clock = pygame.time.Clock()
        while(self.life > 0):
            self.ticks += 1
            self.draw()
            self.inputs()
            self.update()
            clock.tick_busy_loop(60)
        self.lose()

    def level_intermission(self,remark,reward):
        self.money += reward
        clock = pygame.time.Clock()
        self.remarkText = f"{remark} : You got ${reward}!"
        self.bullets = []
        self.effects = []
        t = 0
        while(t < 60*5):
            self.draw()
            self.inputs()
            t += 1
            clock.tick_busy_loop(60)
        self.remarkText = None
        self.conf.end_intermission()

    def remove(self,bloon):
        self.bloons.remove(bloon)

    def end(self,bloon): # bloon reaches end
        self.remove(bloon)
        self.life -= bloon.level + 1

    def kill(self,bloon): #bloon is killed
        self.remove(bloon)
        self.money += 1

    def spawn_bullet(self,bullet):
        self.bullets.append(bullet)

    def add_effect(self,effect):
        self.effects.append(effect)

    def win(self):
        self.game_over_text("You win!")
        self.stop()

    def lose(self):
        self.game_over_text("You lose!")
        self.stop()

    def game_over_text(self,text):
        t = 0
        clock = pygame.time.Clock()
        while(t < 60*5):
            for event in pygame.event.get():
                if(event.type == QUIT):
                    self.stop()
            pygame.draw.rect(self.window,(0,0,0),(0,0,1000,1000))
            self.window.blit(self.fnt.render(text,False,(255,255,255)),(400,400))
            pygame.display.update()
            t += 1
            clock.tick_busy_loop(60)

    def stop(self):
        pygame.quit()
        quit()

g = Game()
g.loop()

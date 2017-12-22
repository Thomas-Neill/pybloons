import itertools
import pygame
import pyperclip
import json
from pygame.locals import *
pygame.init()
img = input("Background image? ")
image = pygame.image.load(img)
win = pygame.display.set_mode((1000,1000))
points = []
cont = True
while(cont):
    for event in pygame.event.get():
        if(event.type == QUIT):
            cont = False
        if(event.type == MOUSEBUTTONDOWN):
            points.append(event.pos)
    win.fill((255,255,255))
    pygame.draw.rect(win,(0,0,0),(0,0,1000,150))
    win.blit(image,(0,150))
    if(len(points) > 1): pygame.draw.lines(win,(255,0,0),False,points)
    pygame.display.flip()
pyperclip.copy(json.dumps(points))
print("Output copied to clipboard.")

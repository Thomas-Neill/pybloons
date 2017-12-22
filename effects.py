import pygame
class ColorFadeCircle:
    def __init__(self,x,y,color,r,initial,dec):
        self.valid = True
        self.pos = (x-r,y-r)
        self.r = r
        self.trans = initial
        self.dec = dec
        self.circ = pygame.Surface((r*2,r*2))
        self.circ.set_colorkey((255,255,255))
        self.circ.fill((255,255,255))
        self.color = color
        pygame.draw.circle(self.circ,color,(r,r),r)
    def update(self,game):
        self.trans -= self.dec
        if(self.trans <= 0):
            self.valid = False
    def draw(self,win):
        self.circ.set_alpha(self.trans)
        win.blit(self.circ,self.pos)

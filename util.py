import math
import copy

def dist(x1,y1,x2,y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def in_box(x,y,x1,y1,sz,centered=None):
    if(centered == None):
        assert False
    if(centered == False):
        return (x1 <= x <= x1 + sz) and (y1 <= y <= y1 + sz)
    if(centered == True):
        return (x1 - sz/2 <= x <= x1 + sz/2) and (y1 - sz/2 <= y <= y1 + sz/2)

def in_rect(x,y,x1,y1,w1,h1):
    return (x1 <= x <= x1 + w1) and (y1 <= y <= y1 + h1)

def box_collide(x,y,x1,y1,sz):
    for i in corners(x,y,sz):
        if(in_box(i[0],i[1],x1,y1,sz,centered=True)):
            return True
    return False

def corners(x,y,sz):
    return [(x-sz/2,y-sz/2),(x+sz/2,y-sz/2),(x+sz/2,y+sz/2),(x-sz/2,y+sz/2)]

def stop_after_first_true(actions,*args):
    for i in actions:
        if(i(*args)):
            return

def nonnull(x):
    return x != None

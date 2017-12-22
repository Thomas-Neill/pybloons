from bullet import ExplodingBullet,Bullet
import pygame
import random
from util import dist
from effects import *
from copy import deepcopy,copy
import math

class Upgrade:
    def __init__(self,name=None,desc=None,price=None,action=None,next=None):
        self.name = name
        self.desc = desc
        self.price = price
        self.action = action
        self.next = next

TOWER_SIZE = 30

#a horribly customizable way to set up a tower class
#maybe it's a little "unique", but it looks nice when they are declared
def build_tower_class(*args,selections=None,range=None,color=None,speed=None,price=None,
                      desc=None,reaction=None,upgrades=None,setup=lambda _:None,
                      after_shoot=lambda _,__:None,custom_update=None,extra_draw=lambda _,__:None):
    assert (not args),"Please use keyword arguments"
    def drawT(window,x,y,rng=range):
        pygame.draw.rect(window,color,(x-TOWER_SIZE/2,y-TOWER_SIZE/2,TOWER_SIZE,TOWER_SIZE))
        pygame.draw.circle(window,(0,0,0),(x,y),rng,1)
    class T:
        def __init__(self,x,y,ticks=0):
            self.x = x
            self.y = y
            self.can_fire = False
            self.range = range
            self.speed = speed
            self.offset = ticks % speed
            self.upgrades = deepcopy(upgrades)
            setup(self)

        def update(self,game):
            if((game.ticks + self.offset) % self.speed == 0):
                self.can_fire = True
            bloons = list(filter(
                lambda bloon:
                    dist(self.x,self.y,bloon.x,bloon.y) < self.range, game.bloons))
            if(self.can_fire):
                self.can_fire = False
                bloons_ = selections(bloons)
                for bloon in bloons_:
                    reaction(self,game,bloon)
                after_shoot(self,game)

        def draw(self,window):
            drawT(window,self.x,self.y,rng=self.range)
            extra_draw(self,window)

    T.color = color
    T.price = price
    T.draw_ = drawT
    T.desc = desc
    if(custom_update != None):
        T.update = custom_update
    return T

def choose(bloons):
    return [] if not bloons else [random.choice(bloons)]

def every(bloons):
    return bloons

def shoot(self,game,bloon):
    game.spawn_bullet(Bullet(self,bloon))

def throw_grenade(self,game,bloon):
    game.spawn_bullet(ExplodingBullet(self,bloon,self.explosion_range))

def changeBy(attr,n):
    return lambda tower: setattr(tower,attr,getattr(tower,attr)+n)

def changeTo(attr,new):
    return lambda tower: setattr(tower,attr,copy(new))

def doAll(*args):
    def ret(tower):
        for i in args:
            i(tower)
    return ret

Tower = build_tower_class(
    selections = choose,
    range = 110,
    color = (0,0,0),
    speed = 80,
    price = 100,
    desc = "Normal tower",
    reaction = shoot,
    upgrades = [
        Upgrade(
            name = "Better Scope",
            desc = "Increase Range",
            price=30,
            action= changeBy("range",40),
            next=Upgrade(
                name = "Crystal Zoom",
                desc = "Further Increase Range",
                price = 40,
                action = changeBy("range",40)
            )
        ),
        Upgrade(
            name = "Greased Gears",
            desc = "Fire Rate Up",
            price = 50,
            action = changeBy("speed",-10),
            next = Upgrade(
                name = "Zero Friction",
                desc = "Fire Rate Up",
                price = 60,
                action = changeBy("speed",-20)
            )
        )
    ])

AOETower = build_tower_class(
    selections = every,
    range = 100,
    color = (255,200,200),
    speed = 100,
    price = 150,
    desc = "Shotgun tower",
    reaction = shoot,
    upgrades = [
        Upgrade(
            name="Dist Booster",
            desc="Increase Range",
            price=40,
            action=changeBy("range",20),
            next=Upgrade(
                name="Titanic Zone",
                desc="Greatly Increase Range",
                price=90,
                action=doAll(changeBy("range",50),changeBy("speed",10))
            )
        ),
        Upgrade(
            name="Auto Reload",
            desc="Fire Rate Up",
            price=60,
            action=changeBy("speed",-10),
            next=Upgrade(
                name="Hyper Gears",
                desc = "Fire Rate Up",
                price=80,
                action=changeBy("speed",-25)
            )
        )
    ])

RapidFireTower = build_tower_class(
    selections = choose,
    range = 150,
    color = (50,255,175),
    speed = 50,
    price = 200,
    desc = "Machine Gun tower",
    reaction = shoot,
    upgrades = [
        Upgrade(
            name = "Far Sight",
            desc = "Increase Range",
            price = 40,
            action = changeBy("range",40),
            next = Upgrade(
                name = "Ultra Vision",
                desc = "Further Increase Range",
                price = 50,
                action=changeBy("range",60)
            )
        ),
        Upgrade(
            name = "Load Boost",
            desc = "Increase Speed",
            price = 100,
            action = changeBy("speed",-15),
            next = Upgrade(
                name = "Unreal Speed",
                desc = "Further Increase Speed",
                price = 130,
                action = changeBy("speed",-10)
            )
        )
    ])

def freeze(self,game,bloon):
    bloon.frozen = self.freeze_time

def freeze_effect(self,game):
    game.add_effect(ColorFadeCircle(self.x,self.y,(0,0,255),self.range,min(self.freeze_time*10,255),10))

FreezeTower = build_tower_class(
    selections = every,
    range = 120,
    color = (0,0,255),
    speed = 60,
    price = 150,
    desc = "Freeze tower",
    reaction = freeze,
    after_shoot = freeze_effect,
    setup = changeTo("freeze_time",20),
    upgrades = [
        Upgrade(
            name = "Nitro Freezers",
            desc = "Longer Freeze Time",
            price = 50,
            action = changeBy("freeze_time",5)
        ),
        Upgrade(
            name = "Mist Sprayers",
            desc = "Larger Area",
            price = 30,
            action = changeBy("range",30),
            next = Upgrade(
                name = "Frost Jets",
                desc = "Larger Area",
                price = 40,
                action = changeBy("range",40)
            )
        )
    ])

ExplodingTower = build_tower_class(
    selections = choose,
    range = 150,
    color = (255,0,255),
    speed = 70,
    price = 300,
    desc = "Grenade Tower",
    reaction = throw_grenade,
    setup = changeTo("explosion_range",100),
    upgrades = [
        Upgrade(
            name = "More Explosions",
            desc = "Lgr Explosion Range",
            price = 50,
            action = changeBy("explosion_range",10),
            next = Upgrade(
                name = "Even More!!!",
                desc = "Huge Expl. Range",
                price = 70,
                action = changeBy("explosion_range",10)
            )
        ),
        Upgrade(
            name = "Bomb Boosters",
            desc = "Larger Range",
            price = 30,
            action = changeBy("range",20),
            next = Upgrade(
                name = "Bomb Blasters",
                desc = "Bigger Range",
                price = 50,
                action = changeBy("range",30)
            )
        )
    ]
)

def laser_update(self,game):
    for i in range(len(self.targets)):
        if(self.targets[i] and dist(self.x,self.y,self.targets[i].x,self.targets[i].y) > self.range):
            self.targets[i] = None
        if(self.targets[i] and self.targets[i].dead):
            self.targets[i] = None
        if(self.targets[i] == None):
            bloons = list(filter(
                lambda bloon:
                    dist(self.x,self.y,bloon.x,bloon.y) < self.range and (bloon not in self.targets), game.bloons))
            if(bloons):
                self.targets[i] = random.choice(bloons)
                self.offsets[i] = game.ticks
            else:
                continue
        if(game.ticks - self.offsets[i] >= self.speed):
            self.offsets[i] = game.ticks
            dead = self.targets[i].damage(game)
            if(dead):
                self.targets[i] = None

def laser_draw(self,window):
    r,g,b = None,None,None
    frequency = .3;
    if(self.rainbow != None):
        r = math.sin(frequency*self.rainbow + 0) * 127 + 128
        g = math.sin(frequency*self.rainbow + 2) * 127 + 128
        b = math.sin(frequency*self.rainbow + 4) * 127 + 128
        self.rainbow += 1
    else:
        r = 255
        g = 0
        b = 0

    for i in self.targets:
        if(i):
            pygame.draw.line(window, (r,g,b), (self.x,self.y), (i.x,i.y))

def add_target(self):
    self.targets.append(None)
    self.offsets.append(-1)

LaserTower = build_tower_class(
        selections = lambda _: None,
        range = 150,
        color = (255,0,0),
        speed = 50,
        price = 350,
        desc = "Laser Tower",
        setup = doAll(changeTo("targets",[None]),changeTo("offsets",[-1]),changeTo("rainbow",None)),
        upgrades = [
            Upgrade(
                name="Dual Beams",
                desc="Two Beams?!?",
                price=80,
                action=add_target,
                next=Upgrade(
                    name="Quad Beams",
                    desc="Four Beams!",
                    price=160,
                    action=doAll(add_target,add_target)
                )
            ),
            Upgrade(
                name="Rainbeams",
                desc="Style & Speed",
                price=200,
                action=doAll(changeTo("rainbow",0),changeBy("speed",-20))
            )
        ],
        custom_update = laser_update,
        extra_draw = laser_draw
    )

tower_types = [Tower,AOETower,RapidFireTower,FreezeTower,ExplodingTower,LaserTower]

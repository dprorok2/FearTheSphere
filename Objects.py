#Created by David Prorok, 2013 
__author__ = "David Prorok"
__email__ = "DavidJamesProrok@gmail.com"
from random import *
from math import *
import pygame

def init(size):
    global Screen
    Screen = size

class Player:
    def __init__(self):
        self.alive = True
        self.position = [int(Screen[0]/3),int(Screen[1]/2)]
        self.rotation = 0.0
        self.mass = 40
        self.size = 11+int(self.mass/8)
        self.speed = [0.0,0.0]
        self.maxSpeed = 1.7
        self.accel = 0.02
        self.decel = .991
        self.being_hit = 0
        self.color = pygame.Color(255,0,0)
    def calcSize(self):
        self.size = 11+self.mass/8

class Enemy:
    def __init__(self,level):
        self.alive = True
        if level > 1:
            self.position = [randint(200,Screen[0]-200),randint(200,Screen[1]-200)]
            l = level
            if l>30: l=30
            self.goalLimits = [Screen[0]/2-150+2*l,Screen[1]/2-100+2*l,Screen[0]/2+150-2*l,Screen[1]/2+100-2*l] 
            self.goal = [randint(self.goalLimits[0],self.goalLimits[2]),randint(self.goalLimits[1],self.goalLimits[3])]
        else: self.position=[Screen[0]/2.0,Screen[1]/2.0]
        self.rotation = 0.0
        self.mass = 28+int(2.1*level) + (level/10)*8+randint(1,4)*randint(-1,1)
        if level==1: self.mass=30
        self.size = 11+int(self.mass/8)
        self.speed = [0.0,0.0]
        self.maxSpeed = 1.1+.11*level-.1*(level/10)
        self.accel = 0.009+.00065*level-.0007*(level/10)
        self.decel = .991
        if level%10 ==5: 
            self.mass = 20*(level/10+1); self.size=13+int(1.8*(level/10))
            self.maxSpeed = .85+.09*level-.09*(level/10)
            self.accel = 0.0075+.00065*level-.0007*(level/10)
        if level%10==0: 
            self.mass=100*(level/10)-100*((level-10)/20)
            self.maxSpeed = 1.7+(level/10)*.08
            self.accel=.01 + (level/10)*.0002
            self.size = 15+int(self.mass/8)
            self.goalLimits = [Screen[0]/2-90,Screen[1]/2-45,Screen[0]/2+90,Screen[1]/2+45] 
        self.being_hit = 0
        self.color = pygame.Color(randint(0,255),randint(0,255),randint(0,255))

def calcDistance(ball1, ball2):
    return sqrt(abs(ball1.position[0]-ball2.position[0])*abs(ball1.position[0]-ball2.position[0])+abs(ball1.position[1]-ball2.position[1])*abs(ball1.position[1]-ball2.position[1]))

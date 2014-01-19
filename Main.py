#Created by David Prorok, 2013 
__author__ = "David Prorok"
__email__ = "DavidJamesProrok@gmail.com"

import pygame, sys, os
from pygame.locals import *
from math import *
from random import *
import Objects

pygame.init()

Screen = (800,600)
FPS = 100
fpsClock = pygame.time.Clock()
Font  = pygame.font.SysFont("Times New Roman",  32)
Font1 = pygame.font.SysFont("Times New Roman",  24)
Font2 = pygame.font.SysFont("Times New Roman",  16)
Font3 = pygame.font.SysFont("Times New Roman",  60)


Objects.init(Screen)
Surface = pygame.display.set_mode(Screen)
pygame.display.set_caption("Fear The Sphere - David Prorok - 2013")
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)

stageColor = pygame.Color(250,250,250)
backgroundColor = pygame.Color(0,0,0)
coins=0
massPrice=35
speedPrice=100
accelPrice=150
lifePrice=500
multiplier = 1
multiplierPrice=100

level = 0
lives = 3
StoreOpen=False
bankPurchased=False
p1 = Objects.Player()
Enemies = []

def noEnemies():
    allDead = True
    for e in Enemies:
        if e.alive == True: allDead = False
    return allDead
	
def GameOver():
    global level, p1
    p1.alive = False
    DrawEnvironment(); DrawObjects()
    GameOverText = Font3.render("GAME OVER", True, (255,25,25))
    Surface.blit(GameOverText, ((Screen[0]/2.0)-(GameOverText.get_width()/2.0), (Screen[1]/2.0)-(GameOverText.get_height()/2.0)))
    PlayAgainText = Font.render("Play Again? (Y/N)", True, (255,25,25))
    Surface.blit(PlayAgainText, ((Screen[0]/2.0)-(PlayAgainText.get_width()/2.0), (Screen[1]/2.0)+(GameOverText.get_height())-(PlayAgainText.get_height()/2.0)))
    if lives>0: 
        p1.alive = True; level-=1; DrawEnvironment(); newLevel()

def GetInput():
    global level, lives, p1, StoreOpen, coins, massPrice, speedPrice, accelPrice, lifePrice, bankPurchased, multiplier, multiplierPrice
    key = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT or key[K_ESCAPE]:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN: 
            if StoreOpen==True: 
                StoreOpen=False;  DrawEnvironment();  
                if noEnemies() and p1.alive==True: 
                    newLevel()
                else:
                    DrawObjects(); pygame.display.flip();  pygame.time.wait(1000)
            else: StoreOpen =True
        if StoreOpen==True:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m and coins>=massPrice: 
                p1.mass+=1; coins-=massPrice; massPrice=int(massPrice+level*.55 - 1); Objects.Player.calcSize(p1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s and coins>=speedPrice: 
                p1.maxSpeed*=1.05; coins -=speedPrice; speedPrice=int(speedPrice*1.2)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a and coins>=accelPrice: 
                p1.accel*=1.05; coins -=accelPrice; accelPrice=int(accelPrice*1.2)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l and coins>=lifePrice: 
                lives+=1; coins -=lifePrice; lifePrice=int(lifePrice*1.1)
            if event.type==pygame.KEYDOWN and event.key==pygame.K_b and bankPurchased==False and coins>=500: 
                bankPurchased=True; coins -=500
            if event.type==pygame.KEYDOWN and event.key==pygame.K_x and coins>=multiplierPrice: 
                coins -=multiplierPrice; multiplierPrice=multiplierPrice*1.5; multiplier = multiplier*1.1
    if p1.alive:
        if StoreOpen==False:
            if (key[K_LEFT] or key[K_a]) and p1.speed[0] > p1.maxSpeed*-1:  p1.speed[0] -= p1.accel
            if (key[K_RIGHT] or key[K_d]) and p1.speed[0] < p1.maxSpeed: p1.speed[0] += p1.accel
            if (key[K_UP] or key[K_w]) and p1.speed[1] < p1.maxSpeed: p1.speed[1] += p1.accel
            if (key[K_DOWN] or key[K_s]) and p1.speed[1] > p1.maxSpeed*-1: p1.speed[1] -= p1.accel

    else:
        if key[K_y]: 
            level=0;  coins=0; massPrice = 35; speedPrice= 100; accelPrice=150; lifePrice=500;
            lives=3; multiplier=1; multiplierPrice=100; bankPurchased=False; p1=Objects.Player(); 
            DrawEnvironment(); newLevel()
        elif key[K_n]:
            pygame.quit(); sys.exit()
         
def calcOrientation(ball):
    ball.rotation = atan2(ball.speed[1],ball.speed[0]) 

def calcFinalSpeeds(ball1, ball2):
    mass1 = ball1.mass
    mass2 = ball2.mass
    phi = atan2(-(ball1.position[1]-ball2.position[1]),(ball1.position[0]-ball2.position[0]))
    theta1 = ball1.rotation
    theta2 = ball2.rotation
    v1i = sqrt(ball1.speed[0]*ball1.speed[0]+ball1.speed[1]*ball1.speed[1])
    v2i = sqrt(ball2.speed[0]*ball2.speed[0]+ball2.speed[1]*ball2.speed[1])
    ball1.speed[0] = ((v1i*cos(theta1-phi)*(mass1-mass2)+2*mass2*v2i*cos(theta2-phi))*cos(phi)/(mass1+mass2)+v1i*sin(theta1-phi)*cos(phi+pi/2))
    ball1.speed[1] = ((v1i*cos(theta1-phi)*(mass1-mass2)+2*mass2*v2i*cos(theta2-phi))*sin(phi)/(mass1+mass2)+v1i*sin(theta1-phi)*sin(phi+pi/2))
    ball2.speed[0] = (v2i*cos(theta2-phi)*(mass2-mass1)+2*mass1*v1i*cos(theta1-phi))*cos(phi)/(mass1+mass2)+v2i*sin(theta2-phi)*cos(phi+pi/2)
    ball2.speed[1] = ((v2i*cos(theta2-phi)*(mass2-mass1)+2*mass1*v1i*cos(theta1-phi))*sin(phi)/(mass1+mass2)+v2i*sin(theta2-phi)*sin(phi+pi/2))
    ball1.being_hit=0
    ball2.being_hit=0

def Move():
    p1.position[0] += p1.speed[0]
    p1.position[1] -= p1.speed[1]
    if p1.position[0]<150 or p1.position[0]>650 or p1.position[1]<150 or p1.position[1]>450: Die(p1)
    p1.speed[0] *= p1.decel
    p1.speed[1] *= p1.decel
    if abs(p1.speed[0])<.01: p1.speed[0] = 0
    if abs(p1.speed[1])<.01: p1.speed[1] = 0
    for e in Enemies:
        distance = Objects.calcDistance(p1, e)
        if p1.being_hit == 0 and e.being_hit==0 and distance < (p1.size+e.size-1):
            p1.being_hit = 1
            e.being_hit = 1
            calcOrientation(p1)
            calcOrientation(e)
            distance = Objects.calcDistance(p1, e)
            while distance < p1.size+e.size: 
                if p1.position[0]!=e.position[0]: 
                    e.position[0]+=.1*(e.position[0]-p1.position[0])/abs(p1.position[0]-e.position[0])*abs(e.position[0]-p1.position[0])/(abs(e.position[1]-p1.position[1])+1)
                    p1.position[0]-=.1*(e.position[0]-p1.position[0])/abs(p1.position[0]-e.position[0])*abs(e.position[0]-p1.position[0])/(abs(e.position[1]-p1.position[1])+1)
                if p1.position[1]!=e.position[1]: 
                    e.position[1]+=.1*(e.position[1]-p1.position[1])/abs(p1.position[1]-e.position[1])
                    p1.position[1]-=.1*(e.position[1]-p1.position[1])/abs(p1.position[1]-e.position[1])
                distance = Objects.calcDistance(p1, e)
            calcFinalSpeeds(p1, e)

    for i in range(len(Enemies)):
        try:
            if Enemies[i].alive==True:
                e = Enemies[i]
                if level>1:
                    if i==3:
                        e.goal[0] = p1.position[0]
                        e.goal[1] = p1.position[1]
                    else:
                        while abs(e.position[0]-e.goal[0])<3: e.goal[0] = randint(e.goalLimits[0],e.goalLimits[2])
                        while abs(e.position[1]-e.goal[1])<3: e.goal[1] = randint(e.goalLimits[1],e.goalLimits[3])
                    e.speed[0] -= e.accel * (e.position[0]-e.goal[0])/abs(e.position[0]-e.goal[0])
                    e.speed[1] += e.accel * (e.position[1]-e.goal[1])/abs(e.position[1]-e.goal[1])
                e.position[0] += e.speed[0]
                e.position[1] -= e.speed[1]
                if e.position[0]<150 or e.position[0]>650 or e.position[1]<150 or e.position[1]>450: Die(e)
                e.speed[0] *= e.decel
                e.speed[1] *= e.decel
                if abs(e.speed[0])<.01: e.speed[0] = 0
                if abs(e.speed[1])<.01: e.speed[1] = 0
                for j in range(i,len(Enemies)):
                    try:
                        if Enemies[j].alive==True:
                            g = Enemies[j]
                        if e!=g:
                            distance = Objects.calcDistance(e,g)
                            if e.being_hit == 0 and g.being_hit==0 and distance < (e.size+g.size):
                                e.being_hit = 1
                                g.being_hit = 1
                                calcOrientation(e)
                                calcOrientation(g)
                                distance = Objects.calcDistance(e, g)
                                while distance < e.size+g.size: 
                                  if e.position[0]!=g.position[0]:
                                    e.position[0]+=.5*(e.position[0]-g.position[0])/abs(e.position[0]-g.position[0])
                                  if e.position[1]!=g.position[1]: 
                                    e.position[1]+=.5*(e.position[1]-g.position[1])/abs(g.position[1]-e.position[1])
                                  distance = Objects.calcDistance(e, g)
                                calcFinalSpeeds(e, g)
                    except: continue
        except: continue

def DrawEnvironment():
    pygame.draw.rect(Surface, backgroundColor, (0,0,800,600))
    pygame.draw.rect(Surface, stageColor, (150, 150, 500, 300))
    LevelInfoText = Font.render("Level: " + str(level) + "        Coins: " + str(int(coins))+ "        Lives: " + str(lives), True, (150,150,150))
    Surface.blit(LevelInfoText, ((Screen[0]/2.0)-(LevelInfoText.get_width()/2.0), 5))
    StoreInfoText = Font.render("Press Enter to open store", True, (150,150,150))
    StartInfoText = Font.render("Press Enter to begin", True, (150,150,150))
    if noEnemies() and StoreOpen==False:
        Surface.blit(StartInfoText, ((Screen[0]/2.0)-(StartInfoText.get_width()/2.0), 
                                      Screen[1]-StartInfoText.get_height()))
    else: Surface.blit(StoreInfoText, ((Screen[0]/2.0)-(StoreInfoText.get_width()/2.0), 
                                        Screen[1]-StoreInfoText.get_height()))


def DrawObjects():
    if p1.alive==True:
        pygame.draw.circle(Surface, p1.color, (int(p1.position[0]), int(p1.position[1])), p1.size)
        PlayerMassText = Font2.render(str(p1.mass), False, (0,0,0))
        Surface.blit(PlayerMassText, ((p1.position[0])-(PlayerMassText.get_width()/2.0), p1.position[1]-(PlayerMassText.get_height()/2.0)))
    for e in Enemies:
        pygame.draw.circle(Surface, e.color, (int(e.position[0]), int(e.position[1])), e.size)
        EnemyMassText = Font2.render(str(e.mass), False, (0,0,0))
        Surface.blit(EnemyMassText, ((e.position[0])-(EnemyMassText.get_width()/2.0), e.position[1]-(EnemyMassText.get_height()/2.0)))
        e.being_hit=0

def spawnEnemy():
    e= Objects.Enemy(level)
    Enemies.append(e)
    distance = Objects.calcDistance(p1,e)
    if distance < e.size+p1.size+5: 
        if e in Enemies:
            Enemies.remove(e)
            spawnEnemy()
    else:
        for g in Enemies:
            if e!=g:
                distance = Objects.calcDistance(e,g)
                if distance < e.size+g.size+5: 
                    if e in Enemies:
                        Enemies.remove(e)
                        spawnEnemy()

def Die(ball):
    global coins, level, lives, StoreOpen, p1, multiplier, lifePrice
    if ball == p1 and p1.alive == True:
         lives-=1
         if lives<=0:
             GameOver()
         else: 
             p1.alive=False; DrawEnvironment(); DrawObjects();  pygame.display.flip(); 
             p1.alive=True;  pygame.time.wait(500); level-=1; newLevel()
    elif ball!=p1: 
        ball.alive = False
        ball.position = [0,0]
        if ball in Enemies:
            Enemies.remove(ball)
        coins += ball.mass * multiplier+level+5
        if level%10==0: coins+=ball.mass*multiplier
        if noEnemies() and p1.alive==True: 
            if bankPurchased==True: coins= int(coins*1.1)
            StoreOpen=True; multiplier = multiplier*1.02; lifePrice=lifePrice*1.015; DrawEnvironment(); 
            DrawObjects(); pygame.display.flip(); pygame.time.wait(500)

def newLevel():
    global Enemies, level
    Enemies=[]
    if p1.alive == True:
        p1.being_hit=0
        level+=1
        p1.speed = [0.0,0.0]
        p1.position = [int(Screen[0]/3),int(Screen[1]/2)]
        numEnemies = level
        if numEnemies>7: numEnemies =7-((level)/10)
        if numEnemies<5 and level>5: numEnemies= 5
        if level%10==0: numEnemies = 1
        if level%20==0: numEnemies = 2
        if level%10==5: numEnemies = 12
        for i in range(0,numEnemies):
            try:
                spawnEnemy()
            except: continue
        NewLevelText = Font3.render("Beginning Level: "+ str(level), True, (255,25,25))
        Surface.blit(NewLevelText, ((Screen[0]/2.0)-(NewLevelText.get_width()/2.0), 
                                                    (Screen[1]/2.0)-(NewLevelText.get_height()/2.0)))
        pygame.display.flip()
        timeWaited=0
        if level==1:
            while(timeWaited<1500):
                for event in pygame.event.get():
                    if event.type==pygame.KEYDOWN and (event.key==pygame.K_RETURN 
                                                  or event.key==pygame.K_SPACE): timeWaited=3000
                    if event.type == QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
                        pygame.quit(); sys.exit()
        else: 
            while(timeWaited<1500):
                pygame.time.wait(1)
                timeWaited+=1
                for event in pygame.event.get():
                    if event.type==pygame.KEYDOWN and (event.key==pygame.K_RETURN 
                                                  or event.key==pygame.K_SPACE): timeWaited=3000
                    if event.type == QUIT or event.key==pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
        pygame.draw.rect(Surface, backgroundColor, (0,0,800,600))
        LevelInfoText = Font.render("Level: " + str(level) + "        Coins: " + str(int(coins))+ 
                                    "        Lives: " + str(lives), True, (150,150,150))
        Surface.blit(LevelInfoText, ((Screen[0]/2.0)-(LevelInfoText.get_width()/2.0), 5))
        pygame.display.flip()
        pygame.time.wait(250)

def DrawStore():
    global p1, massPrice, speedPrice, accelPrice, lives, lifePrice, bankPurchased, multiplier, multiplierPrice
    pygame.draw.rect(Surface, backgroundColor, (0,0,800,600))
    LevelInfoText = Font.render("Level: " + str(level) + "        Coins: " + str(int(coins))+ "        Lives: " + str(lives), True, (150,150,150))
    Surface.blit(LevelInfoText, ((Screen[0]/2.0)-(LevelInfoText.get_width()/2.0), 5))
    CompletedLevelText = Font3.render("Level "+str(level)+" Complete",True, (255,25,25))
    StoreInfoText = Font.render("Press Enter to close store", True, (150,150,150))
    StoreInfoText2 = Font.render("Press Enter to begin next level.", True, (150,150,150))
    if noEnemies():
        Surface.blit(CompletedLevelText, ((Screen[0]/2.0)-(CompletedLevelText.get_width()/2.0), 100))
        Surface.blit(StoreInfoText2, ((Screen[0]/2.0)-(StoreInfoText2.get_width()/2.0), Screen[1]-StoreInfoText.get_height()))
    else: Surface.blit(StoreInfoText, ((Screen[0]/2.0)-(StoreInfoText.get_width()/2.0), Screen[1]-StoreInfoText.get_height()))
    StoreItemsText1 = Font1.render("Current Mass: " + str(p1.mass) + "                      To increase Mass, press 'm' ("+str(massPrice)+" coins)",True, (255,255,255))
    StoreItemsText2 = Font1.render("Current Max Speed: " + "%.2f" %round(p1.maxSpeed,2) + "         To increase Max Speed, press 's' ("+str(speedPrice)+" coins)",True, (255,255,255))
    StoreItemsText3 = Font1.render("Current Acceleration: " + "%.2f" %round(p1.accel*100,2) + "       To increase Acceleration, press 'a' ("+str(accelPrice)+" coins)",True, (255,255,255))
    StoreItemsText4 = Font1.render("Current Weapon: NONE.         To purchase rockets, press 'r' (1,000,000 coins)",True, (255,255,255))
    StoreItemsText5 = Font1.render("Current Lives: " + str(lives) + "                        To add a life, press 'l' ("+str(int(lifePrice))+" coins)",True, (255,255,255))
    StoreItemsText6 = Font1.render("Bank Purchased: "+ str(bankPurchased)+"              To purchase bank, press 'b' (500 coins)",True, (255,255,255))
    StoreItemsText7 = Font1.render("Earns 10% interest per round",True, (255,255,255))
    StoreItemsText8 = Font1.render("Current Multiplier: "+ "%.2f" %multiplier+"            To  increase multiplier, press 'x' ("+str(int(multiplierPrice))+" coins)",True, (255,255,255))
    StoreItemsText9 = Font1.render("Increases coins from enemies by 10%", True, (255,255,255))
    Surface.blit(StoreItemsText1, (25, Screen[1]/2.0-StoreItemsText1.get_height()/2.0-StoreItemsText2.get_height()-StoreItemsText3.get_height()-StoreItemsText4.get_height()))
    Surface.blit(StoreItemsText2, (25, Screen[1]/2.0-StoreItemsText2.get_height()/2.0-StoreItemsText3.get_height()-StoreItemsText4.get_height()+5))
    Surface.blit(StoreItemsText3, (25, Screen[1]/2.0-StoreItemsText3.get_height()/2.0-StoreItemsText4.get_height()+10))
    Surface.blit(StoreItemsText4, (25, Screen[1]/2.0-StoreItemsText4.get_height()/2.0+15))
    Surface.blit(StoreItemsText5, (25, Screen[1]/2.0-StoreItemsText5.get_height()/2.0+50))
    Surface.blit(StoreItemsText6, (25, Screen[1]/2.0-StoreItemsText6.get_height()/2.0+145))
    Surface.blit(StoreItemsText7, (330, Screen[1]/2.0-StoreItemsText7.get_height()/2.0+170))
    Surface.blit(StoreItemsText8, (25, Screen[1]/2.0-StoreItemsText8.get_height()/2.0+85))
    Surface.blit(StoreItemsText9, (330, Screen[1]/2.0-StoreItemsText9.get_height()/2.0+110))

def main():
    while True:
        global level, coins, bankPurchased
        GetInput()
        if StoreOpen==False:
            DrawEnvironment()
            if noEnemies(): newLevel()
            DrawObjects()
            Move()
            if p1.alive==False: GameOver()
        else: DrawStore()
        pygame.display.flip()
        fpsClock.tick(FPS)

if __name__ == '__main__': main()

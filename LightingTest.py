import pygame as pyg
from pygame import gfxdraw
import sys
import time as t
import CollisionHandler as CH
import random as r
class CannonBall:
    def __init__(self, pos: pyg.Vector2, vel: pyg.Vector2,img):
        self.pos = pos
        self.vel = vel
        self.Gravity = pyg.Vector2(0,200)
        self.img = img
    def InWindow(self,win: pyg.Surface):
        Buffer = 0
        if self.pos[0] < - Buffer or self.pos[0] > win.get_width() + Buffer or \
                self.pos[1] > win.get_height()-2 + Buffer:
            return False
        return True
    def Move(self,DeltaTime,Sparks, SparkImages):
        self.pos += self.vel * DeltaTime
        self.vel += self.Gravity * DeltaTime
        if r.randint(0,1 + max(0, int(200-self.vel.length()))) < 1:
            for particle in range(1):
                Sparks.append(Spark(pyg.Vector2(self.pos),
                                    pyg.Vector2(0, r.randint(1, 100)).rotate(r.randint(0, 360)) / 3, False,
                                    SparkImages[r.randint(0, len(SparkImages) - 1)]))


    def Draw(self,win,ShadowSurf, ShadowLevel):

        LightSurf = pyg.Surface((31,31), pyg.SRCALPHA)
        LightSurf.convert_alpha()
        LightSurf.fill((0,0,0,230))
        LightSurf.set_colorkey((0,0,0))

        Transparency = ShadowLevel
        for i in range(15):
            pyg.draw.circle(LightSurf, (0, 0, 0, Transparency), (15,15), 15 - i,2)
            Transparency -= ShadowLevel//15
        ShadowSurf.blit(LightSurf,self.pos - pyg.Vector2(15,15),special_flags=pyg.BLEND_RGBA_MIN)
        win.blit(self.img,(self.pos.x - self.img.get_width()//2,self.pos.y - self.img.get_height()//2))
class Tank:
    def __init__(self, pos: pyg.Vector2):
        self.pos = pos
        self.intpos = pyg.Vector2(int(pos[0]),int(pos[1]))
        self.vel = 0
        image = pyg.image.load('Data/DrivingPlayer.png')
        self.DriveFrames = CH.GetFramesOutOfSpriteSheet(image,2,21,17,(0,0,0))
        self.FrameIndex = 0
        self.DrawOffset = pyg.Vector2(-image.get_width()/4,-image.get_height()/2)
        self.SparkOffsets = [pyg.Vector2(-5,8),pyg.Vector2(5,8)]
        self.CannonVec = pyg.Vector2(9,0)
        self.CannonPos = pyg.Vector2(0,-5)
        self.CannonImg = pyg.image.load('Data/CannonImg.png')
        self.CannonImg.convert()
        self.ShotStrength = 20
        self.PowerShotStrength = 35
        self.RotatedCannonImg = self.CannonImg.copy()
    def RotateCannon(self,Degrees):
        self.CannonVec = self.CannonVec.rotate(Degrees)
        #self.CannonVec.angle_to(pyg.Vector2(0, -1))
    def Shoot(self,CannonBalls: list,CannonBallImg, PowerShot):
        #for i in range(50):
        #    Sparks.append(Spark(pyg.Vector2(self.pos + self.CannonPos + self.CannonVec),
        #                        (self.CannonVec * r.randint(300,330)/10).rotate(r.randint(-10,10)/10), False,
        #                        SparkImages[r.randint(0, len(SparkImages) - 1)]))
        CannonBalls.append(CannonBall(self.pos + self.CannonPos + self.CannonVec,self.CannonVec*(self.PowerShotStrength if PowerShot else self.ShotStrength),CannonBallImg))
    def Move(self,DeltaTime, Sparks, SparkImages):
        self.pos[0] += self.vel * DeltaTime
        self.intpos = pyg.Vector2(int(self.pos[0]), int(self.pos[1]))
        if self.vel != 0 and r.randint(0, int(40 - abs(self.vel))) == 0:
            Sparks.append(Spark(pyg.Vector2(self.pos) + self.SparkOffsets[0 if self.vel > 0 else 1],
                                pyg.Vector2(0, r.randint(1, 100)).rotate(r.randint(0, 360)) / 3, False,
                                SparkImages[r.randint(0, len(SparkImages) - 1)]))
    def HandleJoystickInput(self,joysticks, DeltaTime):
        if len(joysticks) > 0:
            AxisValue = joysticks[0].get_axis(0)
            if abs(AxisValue) > 0.1:
                self.vel = AxisValue * 35
            else:
                self.vel = 0
            AxisValue = joysticks[0].get_axis(2)
            if abs(AxisValue) > 0.1:
                angle = self.CannonVec.angle_to(pyg.Vector2(0, -1))
                if not (angle <= -90 and angle > -180 and AxisValue > 0) and not (angle <= -180 and AxisValue < 0):
                    self.RotateCannon(AxisValue * DeltaTime * 100)
                    self.RotatedCannonImg = pyg.transform.rotozoom(self.CannonImg,
                                                                     self.CannonVec.angle_to(pyg.Vector2(0, -1)) + 90,
                                                                     1.2)

    def Draw(self,win, ShadowSurf, ShadowLevel):

        win.blit(self.RotatedCannonImg,self.intpos + pyg.Vector2(0,-4) + pyg.Vector2(-self.RotatedCannonImg.get_width()/2,-self.RotatedCannonImg.get_height()/2))
        win.blit(self.DriveFrames[self.FrameIndex],self.intpos + self.DrawOffset)
class Spark:
    def __init__(self, pos: pyg.Vector2, vel: pyg.Vector2,IsBig,img):
        self.pos = pos
        self.vel = vel
        self.Gravity = pyg.Vector2(0,200)
        self.img = img
        self.Bounces = 0
    def Move(self,DeltaTime,windowheight,SparkSound):
        self.pos += self.vel * DeltaTime
        self.vel += self.Gravity * DeltaTime
        self.vel[0] -=DeltaTime * self.vel[0]
        if self.pos[1] >= windowheight-2 and self.vel[1] > 0:
            if self.Bounces != 2:
                if self.vel[1] > 10 and r.randint(0,5)==0:
                    pyg.mixer.find_channel(True).play(SparkSound)
                self.pos[1] = windowheight
                self.vel[1] *= -r.randint(5,30)/100
                self.vel[0] *= 0.6
                self.Bounces += 1


    def Draw(self,win,ShadowSurf, ShadowLevel):

        LightSurf = pyg.Surface((21,21), pyg.SRCALPHA)
        LightSurf.convert_alpha()
        LightSurf.fill((0,0,0,230))
        LightSurf.set_colorkey((0,0,0))

        Transparency = ShadowLevel
        for i in range(10):
            pyg.draw.circle(LightSurf, (0, 0, 0, Transparency), (10,10), 10 - i,2)
            Transparency -= ShadowLevel//10
        ShadowSurf.blit(LightSurf,self.pos - pyg.Vector2(10,10),special_flags=pyg.BLEND_RGBA_MIN)
        win.blit(self.img,(self.pos.x - self.img.get_width()//2,self.pos.y - self.img.get_height()//2))
def DrawLedLines(win):
    LedLineColor = (99, 186, 178)
    LineDistance = (36,20)
    for row in range(int(win.get_width()/LineDistance[0]+1)):
        pyg.gfxdraw.vline(win, row * LineDistance[0], 0, win.get_height(),LedLineColor)
    for column in range(int(win.get_height()/LineDistance[1]+1)):
        pyg.gfxdraw.hline(win, 0, win.get_width(), win.get_height()-column * LineDistance[1],LedLineColor)


def Main(WeakShots = True):
    pyg.init()

    screen = pyg.display.set_mode((1920,1080),pyg.FULLSCREEN)
    screen.convert_alpha()
    PIXELSIZE = (5,5)
    win = pyg.Surface((screen.get_width()//PIXELSIZE[0] + 4, screen.get_height()//PIXELSIZE[1] + 4))
    win.convert()
    SparkImages = [pyg.image.load('Data/Spark1.png'),pyg.image.load('Data/Spark2.png')]
    for img in SparkImages:
        img.convert_alpha()
    CannonBallImage = pyg.image.load('Data/CannonBall.png')
    SmallCannonBallImage = pyg.image.load('Data/SmallCannonBall.png')
    CannonBalls = []
    LaserSound = pyg.mixer.Sound('Data/LaserShot.wav')
    ShootSound = pyg.mixer.Sound('Data/ShatterShot.wav')
    SparkSound = pyg.mixer.Sound('Data/SparkleSound2.wav')
    PowerSound = pyg.mixer.Sound('Data/StartUp.wav')
    SparkSound.set_volume(0.3)
    Sparks = []
    CurrentTime = t.time()
    joysticks = [pyg.joystick.Joystick(x) for x in range(pyg.joystick.get_count())]
    if len(joysticks) == 0:
        print('WARNING: without controller, you can only use the mouse to see the lighting')
    Player = Tank(pyg.Vector2(win.get_width()/2,win.get_height()-9))
    Clock = pyg.time.Clock()
    ShadowLevel = 230
    ShadowSurf = pyg.Surface(win.get_size(), pyg.SRCALPHA)
    ShadowSurf.convert_alpha()
    pyg.mixer.set_num_channels(50)
    QuakeList = [(-1,1),(1,-1),(-1,-1),(1,1),(-1,1)]
    QuakeFrameTime = 0.01
    QuakeStartTime = 0

    PowerShot = not WeakShots

    Clicking = False
    while True:
        #Set starting conditions
        Clock.tick(750)
        DeltaTime, CurrentTime = CH.GetDeltaTime(CurrentTime, t.time())
        win.fill((21,32,31))
        ShadowSurf.fill((0, 0, 0, ShadowLevel))

        #handle events
        for ev in pyg.event.get():
            if ev.type == pyg.QUIT or ev.type == pyg.KEYDOWN and ev.key == pyg.K_ESCAPE:
                sys.exit()
            if ev.type == pyg.MOUSEBUTTONDOWN and ev.button == 1:
                Clicking = True
            if ev.type == pyg.MOUSEBUTTONUP and ev.button == 1:
                Clicking = False
            if ev.type == pyg.JOYBUTTONDOWN:
                if ev.button == 5:
                    Player.Shoot(CannonBalls, CannonBallImage if PowerShot else SmallCannonBallImage, PowerShot = PowerShot)
                    pyg.mixer.find_channel(True).play(ShootSound if PowerShot else LaserSound)
                    QuakeStartTime = t.time() if PowerShot else 0
                    joysticks[0].rumble(1 if PowerShot else 0.5,1 if PowerShot else 0.5,200 if PowerShot else 100)
                    if WeakShots:
                        PowerShot = False
                elif ev.button == 0:
                    if not PowerShot:
                        pyg.mixer.find_channel(True).play(PowerSound)
                        PowerShot = True


        #Handle joysticks
        Player.HandleJoystickInput(joysticks,DeltaTime)
        #Spawn sparks with mouseclick
        if Clicking:
            SpawnRate = round(100 * DeltaTime) + 1
            for i in range(SpawnRate):
                Sparks.append(Spark(pyg.Vector2(pyg.mouse.get_pos()) / PIXELSIZE[0],pyg.Vector2(0, r.randint(1, 100)).rotate(r.randint(0, 360))/2, False,SparkImages[r.randint(0, len(SparkImages) - 1)]))
        #Move Entities
        Player.Move(DeltaTime, Sparks, SparkImages)
        for spark in Sparks:
            spark.Move(DeltaTime,win.get_height(),SparkSound)
        for cannonball in CannonBalls:
            cannonball.Move(DeltaTime,Sparks, SparkImages)

        #remove useless sparks and cannonballs
        for ind in range(len(Sparks)-1,-1,-1):
            if Sparks[ind].pos[1] > win.get_height() + 5:
                Sparks.pop(ind)
        for ind in range(len(CannonBalls)-1,-1,-1):
            if not CannonBalls[ind].InWindow(win):
                CannonBalls.pop(ind)

        #Render window
        if QuakeStartTime > t.time()-QuakeFrameTime * len(QuakeList):
            QuakeVec = pyg.Vector2(QuakeList[int((t.time()-QuakeStartTime)/QuakeFrameTime)])
        else:
            QuakeVec = pyg.Vector2(0,0)
        DrawLedLines(win)
        for cannonball in CannonBalls:
            cannonball.Draw(win,ShadowSurf,ShadowLevel)
        for spark in Sparks:
            spark.Draw(win,ShadowSurf,ShadowLevel)
        Player.Draw(win, ShadowSurf, ShadowLevel)
        win.blit(ShadowSurf, (0, 0))

        #update screen
        screen.blit(pyg.transform.scale(win, pyg.Vector2(win.get_size())*PIXELSIZE[0]), QuakeVec*PIXELSIZE[0] + (-2*PIXELSIZE[0], -2*PIXELSIZE[1]))
        pyg.display.update()


if __name__ == '__main__':
    pyg.init()
    Main(WeakShots=True)

# image = pyg.Surface(self.CannonImg.get_size(), pyg.SRCALPHA)
# MiddleOfImage = pyg.Vector2(self.CannonImg.get_size())/2
# CannonOffset = pyg.Vector2(0,-4)
# image.blit(self.RotatedCannonImg, MiddleOfImage - pyg.Vector2(self.RotatedCannonImg.get_size())/2)
# image.blit(self.DriveFrames[self.FrameIndex],MiddleOfImage - CannonOffset + self.DrawOffset)
# ImgMask = pyg.mask.from_surface(image,threshold=127)
# mask_outline =ImgMask.outline()
# ImgMask.invert()
# mask_surf = ImgMask.to_surface()
# mask_surf.convert_alpha()
# mask_surf.set_colorkey((255,255,255))
# mask_surf.set_alpha(200)
# for point in mask_outline:
#    mask_surf.set_at(point, (255,255,255))
# ShadowSurf.blit(mask_surf,self.intpos - pyg.Vector2(self.CannonImg.get_size())/2 + CannonOffset)
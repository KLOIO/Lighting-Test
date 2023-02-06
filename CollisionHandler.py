import string

import pygame as pyg
#TODO set camera borders
def GetTypeIDName(typeIDdict:dict,typeID:int)->str:
    name = ''
    for typeName in typeIDdict:
        if typeID in typeIDdict[typeName]:
            name = typeName
    return name

#Camera handling
class BaseCollisionCameraClass:
    def __init__(self,BorderTolerance=0):
        self.EndTarget = pyg.Vector2(0,0)#If nothing happens, the topleft of the screen will be this point
        self.FollowPlayersMode = True #This decides whether the camera should focus on Players or not change at all
        self.CameraSpeed = 0.5
        self.RoundedXoffset = 0
        self.RoundedYoffset = 0
        self.RealXoffset = 0
        self.RealYoffset = 0
        self.OldXoffset = 0
        self.OldYoffset = 0
        self.BorderTolerance = BorderTolerance #This decides how much air can be on the window's edges

    def Updateoffsets(self,TileSize,win: pyg.Surface,TileMap2D: list[list]) -> None:
        self.RealXoffset = -self.EndTarget[0]
        self.RealYoffset = -self.EndTarget[1]
        #self.RealXoffset = min(max(-(TileSize[0] * len(TileMap2D[0]) - win.get_width()/2) - self.BorderTolerance, self.RealXoffset), self.BorderTolerance + win.get_width()/2)
        #self.RealYoffset = min(max(-(TileSize[1] * len(TileMap2D) - win.get_height()/2) - self.BorderTolerance, self.RealYoffset), self.BorderTolerance + win.get_height()/2)
        self.RealXoffset = self.OldXoffset * (1-self.CameraSpeed) + (self.RealXoffset - self.OldXoffset) * self.CameraSpeed
        self.RealYoffset = self.OldYoffset * (1-self.CameraSpeed) + (self.RealYoffset - self.OldYoffset) * self.CameraSpeed
        self.OldXoffset = self.RealXoffset
        self.OldYoffset = self.RealYoffset
        self.RoundedXoffset = int(self.RealXoffset)
        self.RoundedYoffset = int(self.RealYoffset)

    def CalculateEndTarget(self,TileMap2D: list,BlockSize: pyg.Vector2,Players:list,win: pyg.Surface) -> None:
        #Players list should contain all players. It should contain at least 1 player
        if len(Players) == 0:
            print('CameraError: No Players to target')
        if self.FollowPlayersMode:
            target = pyg.Vector2(0,0)
            for player in Players:
                target += (player.MidPos - pyg.Vector2(win.get_width()/2,win.get_height()/2))
            target /= len(Players)
            self.EndTarget = target
        else:
            self.EndTarget = pyg.Vector2(len(TileMap2D) * BlockSize[0]/2, len(TileMap2D[0]) * BlockSize[1]/2) - pyg.Vector2(win.get_width()/2,win.get_height()/2)

#Delta time handling
def GetDeltaTime(StartTime: float,CurrentTime: float) -> (float, float):
    #This returns the DeltaTime and the new StartTime
    return (CurrentTime - StartTime), CurrentTime

#Load level Functions
def LoadLevel(filename: str) -> list[list[int]]:
    with open(filename, 'r') as f:
        lines = f.read().split('\n')
    Map = []
    for i in range(len(lines)):
        Map.append([])
        Map[-1] = lines[i].split('-')
    for row in range(len(Map)):
        for column in range(len(Map[row])):
            Map[row][column] = int(Map[row][column])
    return Map

#Image Handling
class spread_sheet():
    def __init__(self,image):
        self.sheet=image
    def get_Image(self,frame,width,height,color):
        image = pyg.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0, 0), pyg.Rect((frame * width), 0, width, height))
        image.set_colorkey(color)
        return image
def GetFramesOutOfSpriteSheet(SpriteSheetImg,frames,width,height,color) -> list[pyg.Surface]:
    Spreadsheet = spread_sheet(SpriteSheetImg)
    Frames = []
    for i in range(frames):
        Frames.append(Spreadsheet.get_Image(i, width, height, color).convert())
    return Frames

#Collision Functions
class BaseCollisionPlayer:
    #This class handles a base velocity and a hitbox
    def __init__(self,MidPos:pyg.Vector2,HitboxWidth:int,HitboxHeight:int) -> None:
        self.MidPos = MidPos
        self.Hitbox = pyg.Rect(0,0,HitboxWidth,HitboxHeight)
        self.Hitbox.center = self.MidPos
        self.width, self.height = HitboxWidth, HitboxHeight
        self.velocity = pyg.Vector2(0,0)
    def MoveBody(self, ChangeVec: pyg.Vector2) -> None: # This moves the player to a relative new position
        self.MidPos += ChangeVec
        self.Hitbox.center = self.MidPos
    def SetMidPos(self,MovingintoSide: str, BorderPos: int) -> None: # This changes MidPos accordingly to tile size.
        if MovingintoSide == 'left':
            self.MidPos[0] = BorderPos+self.width/2
        elif MovingintoSide == 'right':
            self.MidPos[0] = BorderPos-self.width/2
        elif MovingintoSide == 'bottom':
            self.MidPos[1] = BorderPos-self.height/2
        elif MovingintoSide == 'top':
            self.MidPos[1] = BorderPos+self.height/2
        self.Hitbox.center = self.MidPos
class BaseCollisionTile:
    def __init__(self, TopLeftX: int,TopLeftY: int,width: int,height: int,TileType: str,IsSolid: bool,HasEvent: bool,ID) -> None:
        self.pos = pyg.Vector2(TopLeftX,TopLeftY)
        self.rect = pyg.Rect(TopLeftX,TopLeftY,width,height)
        self.IsSolid = IsSolid
        self.HasEvent = HasEvent
        self.TileType = TileType #'air' or 'solid' or 'ToLeftUpStairs' or 'ToRightUpStairs' or 'platform'
        self.ID = ID #Can be whatever you want to be able to find out which tile triggered an event.
def ExpandEventList(EventList: dict, Tiles: list) -> None:
    #This creates space for all the tile events
    for tile in Tiles:
        if tile.HasEvent:
            EventList[tile.ID] = False
def GetHitTiles(Rect: pyg.Rect, Tiles: list) -> list:
    #this checks which tiles are touched
    HitTiles = []
    for tile in Tiles:
        if tile.IsSolid or tile.HasEvent:
            if Rect.colliderect(tile.rect):
                HitTiles.append(tile)
    return HitTiles
def HandleCollisions(Player, Tiles: list,) -> dict:
    #This handles the collisions between the player and the tiles
    EventList = {'top': False, 'bottom': False, 'right': False, 'left': False, 'Stair': False}
    TileSize = Tiles[0].rect.width,Tiles[0].rect.height
    # X-collisions
    ExpandEventList(EventList, Tiles)
    Player.MoveBody(pyg.Vector2(Player.velocity[0], 0))
    HitTiles = GetHitTiles(Player.Hitbox, Tiles)
    for tile in HitTiles:
        if tile.HasEvent:
            EventList[tile.ID] = True
        if tile.TileType != 'ToLeftUpStairs' and tile.TileType!= 'ToRightUpStairs':
            if Player.velocity[0] >= 0:
                Player.SetMidPos('right',tile.rect.left)
                EventList['right'] = True
            elif Player.velocity[0] < 0:
                Player.SetMidPos('left', tile.rect.right)
                EventList['left'] = True
    # Y-collisions
    Player.MoveBody(pyg.Vector2(0, Player.velocity[1]))
    HitTiles = GetHitTiles(Player.Hitbox, Tiles)
    for tile in HitTiles:
        if tile.HasEvent:
            EventList[tile.ID] = True
        if tile.TileType != 'ToLeftUpStairs' and tile.TileType != 'ToRightUpStairs':
            if Player.velocity[1] >= 0:
                Player.SetMidPos('bottom', tile.rect.top)
                EventList['bottom'] = True
            elif Player.velocity[1] < 0:
                Player.SetMidPos('top', tile.rect.bottom)
                EventList['top'] = True
    #Stairs
    HitTiles = GetHitTiles(Player.Hitbox, Tiles)
    for tile in HitTiles:
        if tile.TileType == 'ToRightUpStairs':
            x = Player.Hitbox.right- TileSize[0] * tile.column
            x = min(max(x, 0), TileSize[0])
            if TileSize[1] * (tile.row+1) - x <= Player.Hitbox.bottom and Player.velocity[1] > 0:
                Player.SetMidPos('bottom', TileSize[1] * (tile.row+1) - x)
                EventList['bottom'] = True
                EventList['Stair'] = True

        elif tile.TileType == 'ToLeftUpStairs':
            x = TileSize[0]-(Player.Hitbox.x - TileSize[0] * tile.column)
            x = min(max(x,0),TileSize[0])
            if TileSize[1] * tile.row - x <= Player.Hitbox.bottom and Player.velocity[1] > 0:
                Player.SetMidPos('bottom', TileSize[1] * (tile.row + 1) - x)
                EventList['bottom'] = True
                EventList['Stair'] = True
    return EventList
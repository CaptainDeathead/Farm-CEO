import pygame as pg
import pygameGui as pgui
import math
import time
import json
from data import *
from copy import deepcopy
import os
import asyncio

pg.init()

PATH = os.path.abspath('.')
ASSETS_PATH: str = PATH + '/assets'
IMAGES_PATH: str = ASSETS_PATH + '/images'

def _mouseCollision(mx, my, x, y, w, h):
    if mx > x and mx < x + w and my > y and my < y + h: return True
    else: return False

def _createPopup(width, height, color, highlightColor, popupType, additional1=None):
    window.createPopup(width, height, color, highlightColor, popupType, additional1)

def _setPaddockState(paddock, state):
    window.setPaddockState(paddock, state)

def _fillSilo(ammount, fillType):
    window.farm.silo.storage[fillType] += ammount

def _addMoney(ammount):
    window.money += ammount

def _removeMoney(ammount):
    window.money -= ammount

def _addXP(ammount):
    window.xp += ammount

def _addCrop(cropType, ammount):
    window.farm.silo.storage[cropType] += ammount

def _addVehicle(parents):
    if parents[0] == 'Tractors': window.tractors.append(Tractor(window.farm.x+50/ZOOM, window.farm.y+150/ZOOM, window.vehiclesDict[parents[0]][parents[1]][parents[2]], parents[1], parents[2]))
    elif parents[0] == 'Harvesters': window.tractors.append(Header(window.farm.x+50/ZOOM, window.farm.y+150/ZOOM, window.vehiclesDict[parents[0]][parents[1]][parents[2]], parents[1], parents[2]))
    else: window.tools.append(Tool(window.farm.x+50/ZOOM, window.farm.y+150/ZOOM, parents[0][:len(parents[0])-1], window.toolsDict[parents[0]][parents[1]][parents[2]], parents[1], parents[2]))

class Shed:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, screen):
        pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Silo:
    def __init__(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.image = pg.image.load(f"{IMAGES_PATH}/silo.png").convert_alpha()
        self.image = pg.transform.rotate(pg.transform.scale(self.image, (self.image.get_width()*2/ZOOM, self.image.get_height()*2/ZOOM)), rotation)
        self.gridImage = pg.image.load(f"{IMAGES_PATH}/grid.png").convert_alpha()
        self.gridImage = pg.transform.rotate(pg.transform.scale(self.gridImage, (self.gridImage.get_width()*2/ZOOM, self.gridImage.get_height()*2/ZOOM)), rotation)
        self.storage = {
            "Wheat": 0,
            "Barley": 0,
            "Canola": 0,
            "Oat": 0
        }
        self.rotation = rotation
        if self.rotation == 180:
            self.gridX = self.x+self.image.get_width()*0.8
            self.gridY = self.y
        else:
            self.gridX = self.x-self.image.get_width()*0.15
            self.gridY = self.y

    def draw(self, screen, grid):
        if grid: 
            if self.rotation == 180: screen.blit(self.gridImage, (self.gridX, self.gridY))
            else: screen.blit(self.gridImage, (self.gridX, self.gridY))
        if not grid: screen.blit(self.image, (self.x, self.y))
        if DEBUG: pg.draw.circle(screen, (255, 0, 0), (self.gridX, self.gridY), 5)

class Farm:
    def __init__(self):
        self.x = 1460/ZOOM
        self.y = 368/ZOOM
        self.sheds = [Shed(self.x, self.y, 200/ZOOM, 75/ZOOM, (150, 150, 150))]
        self.silo = Silo(self.x+250/ZOOM, self.y+120/ZOOM)

    def draw(self, screen):
        for shed in self.sheds: shed.draw(screen)

class Tool:
    def __init__(self, x, y, toolType, attrs, brand, name):
        self.x = x
        self.y = y
        self.toolType = toolType
        self.size = attrs['size']
        self.sizePx =  attrs['sizePx']
        self.hp = attrs['hp']
        self.turningPoint = attrs['turningPoint']
        self.hitch = attrs['hitch']
        self.anims = attrs['anims']
        self.price = attrs['price']
        if self.toolType == "Seeder" or self.toolType == "Spreader" or self.toolType == "Sprayer" or self.toolType == "Trailer": self.storage = attrs['storage']
        if self.toolType == "Seeder": self.cart = attrs['cart']
        if self.toolType == "Trailer":
            self.fullImg = pg.image.load(f"{IMAGES_PATH}/{self.anims['full']}").convert_alpha()
            self.fullImg = pg.transform.scale(self.fullImg, (self.fullImg.get_width()*2/ZOOM, self.fullImg.get_height()*2/ZOOM))
        self.originalImage = pg.image.load(f"{IMAGES_PATH}/{self.anims[self.anims['default']]}").convert_alpha()
        self.originalImage = pg.transform.scale(self.originalImage, (self.originalImage.get_width()*2/ZOOM, self.originalImage.get_height()*2/ZOOM))
        self.image = self.originalImage
        self.rect = self.image.get_rect()
        self.desiredRotation = 0
        self.rotation = 180
        self.brand = brand
        self.name = name
        self.paddock = None
        self.inShed = True
        self.on = False
        self.lastPaint = (0, 0)
        self.fill = 0
        self.fillType = "Wheat"

    def draw(self, screen):
        if self.rotation < 0: self.rotation += 360
        elif self.rotation > 360: self.rotation -= 360

        rotateDistLeft = self.desiredRotation-self.rotation

        # rotatation cannot excede 30 degrees for trailer
        # 120 degrees max for outliers (random times it goes of 360 not 0)
        if rotateDistLeft < -30 and rotateDistLeft > -120: self.rotation = self.desiredRotation + 30
        elif rotateDistLeft > 30 and rotateDistLeft < 120: self.rotation = self.desiredRotation - 30

        rotateDistLeft = self.desiredRotation-self.rotation

        if rotateDistLeft < -180: rotateDistLeft = abs(rotateDistLeft+180)
        elif rotateDistLeft > 180: rotateDistLeft = 180 - rotateDistLeft

        if rotateDistLeft < 180 and rotateDistLeft > 0: self.rotation += min(1, abs(self.desiredRotation - self.rotation)/10)
        elif rotateDistLeft > -180 and rotateDistLeft < 0: self.rotation -= min(1, abs(self.desiredRotation - self.rotation)/10)

        screen.blit(pg.transform.rotate(self.image, self.rotation), (self.x, self.y))

class Tractor:
    def __init__(self, x, y, attrs, brand, name):
        self.x = x
        self.y = y
        self.hp = attrs['hp']
        self.hitch = attrs['hitch']
        self.anims = attrs['anims']
        self.price = attrs['price']
        self.defaultFuel = attrs['fuel']
        self.fuel = self.defaultFuel
        self.originalImage = pg.image.load(f"{IMAGES_PATH}/{self.anims['normal']}").convert_alpha()
        self.originalImage = pg.transform.scale(self.originalImage, (self.originalImage.get_width()/ZOOM, self.originalImage.get_height()/ZOOM))
        self.image = self.originalImage
        self.rect = self.image.get_rect(center = (x, y))
        self.desiredRotation = 180
        self.rotation = 180
        self.tool = None
        self.task = None
        self.stringTask = "No Task Assigned"
        self.brand = brand
        self.name = name
        self.paddock = None
        self.inShed = True
        self.speed = 10
        self.path = []
        self.headingToPdk = False
        self.headingToFarm = False
        self.watchIndex = None
        self.header = False
        self.fuelTicks = 0

    def draw(self, screen, sellPoionts, dt):
        screen.blit(pg.transform.rotate(self.image, self.rotation), (self.x, self.y))

        if len(self.path) > 0 and type(self.path[0][0]) == int:
            self.path[0][0]-=1
            if self.path[0][0]==0: self.path.pop(0)
            return
        elif len(self.path) > 0 and type(self.path[0][0]) == str:
            if len(self.path) > 0 and self.path[0][0] == "end":
                self.headingToFarm = True
                self.path.pop(0)
            if len(self.path) > 0 and self.path[0][0] == "sc":
                self.tool.image = self.tool.fullImg
                self.path.pop(0)
            if len(self.path) > 0 and self.path[0][0] == "rc":
                self.tool.image = self.tool.originalImage
                self.path.pop(0)
            if len(self.path) > 0 and type(self.path[1][0]) == str and self.path[0][0][:2] == "sf":
                sellPointIndex = list(SELL_POINT_LOCATIONS.keys()).index(self.task)
                _addMoney(sellPoionts[sellPointIndex].prices[self.tool.fillType]*self.tool.fill*4)
                sellPoionts[sellPointIndex].demand[self.tool.fillType] -= self.tool.fill / 2
                sellPoionts[sellPointIndex].prices[self.tool.fillType] = int(sellPoionts[sellPointIndex].prices[self.tool.fillType] * (sellPoionts[sellPointIndex].demand[self.tool.fillType] / 100))
                self.tool.fill = int(self.path[0][0][3:])
                self.path.pop(0)
            if len(self.path) > 0 and self.path[0][0] == "tf": self.path.pop(0)

        if len(self.path) > 0: self.desiredRotation = 270-math.atan2(self.path[0][1]-self.image.get_height()/2-self.y, self.path[0][0]-self.image.get_width()/2-self.x) * 57.2957795

        if self.rotation < 0: self.rotation += 360
        elif self.rotation > 360: self.rotation -= 360

        rotateDistLeft = self.desiredRotation-self.rotation
        if rotateDistLeft < -180: rotateDistLeft += 360
        elif rotateDistLeft > 180: rotateDistLeft -= 360

        if rotateDistLeft > 0: self.rotation += min(2, abs(self.desiredRotation - self.rotation)/30)
        elif rotateDistLeft < 0: self.rotation -= min(2, abs(self.desiredRotation - self.rotation)/30)

        self.direction = [math.cos(math.radians(self.rotation-90)), math.sin(math.radians(self.rotation-90))]
        self.x -= self.direction[0] * (self.speed*min(1, max(0.25, 1-abs(rotateDistLeft)/180))) / 10 * (dt/15)
        self.y += self.direction[1] * (self.speed*min(1, max(0.25, 1-abs(rotateDistLeft)/180))) / 10 * (dt/15)

        if len(self.path) > 0 and abs(self.path[0][1]-self.image.get_height()/2-self.y + self.path[0][0]-self.image.get_width()/2-self.x) < 2: self.path.pop(0)

        if DEBUG and len(self.path) > 1:
            for i in range(len(self.path)-1):
                if type(self.path[i]) == tuple and type(self.path[i+1]) == tuple: pg.draw.line(screen, (0, 255, 0), self.path[i], self.path[i+1])
        elif len(self.path) == 1 and self.headingToPdk: self.speed = min(3, 3*self.hp/self.tool.hp)
        elif len(self.path) == 0 and self.headingToPdk:
            self.headingToPdk = False
            self.paddock = self.task
            self.tool.paddock = self.paddock
            self.tool.on = True
            if self.tool.toolType == "Cultivator": self.task = "Cultervate"
            elif self.tool.toolType == "Seeder": self.task = "Sow"
            elif self.tool.toolType == "Spreader": self.task = "Spread"
            elif self.tool.toolType == "Sprayer": self.task = "Spray"
            self.stringTask = f"{self.task} paddock {self.paddock}"

            center = PADDOCK_CENTERS[self.paddock]
            currentDist = self.tool.sizePx-1
            currIter = 0

            for cp in PADDOCKS[self.paddock]:
                x = cp[0]
                y = cp[1]
                angle = 360-math.atan2((center[1]-y), (center[0]-x)) * 57.2957795
                direction = [math.cos(math.radians(angle)), math.sin(math.radians(angle))]
                #print(direction)
                x += direction[0] * currentDist
                y -= direction[1] * currentDist
                self.path.append((x, y))

            currentDist += self.tool.sizePx*2-2

            self.watchIndex = int(len(self.path)/2)

            while currIter < 10 and abs(math.sqrt((self.path[-1][1]-center[1])**2+(self.path[-1][0]-center[0])**2)) > self.tool.sizePx and abs(math.sqrt((self.path[self.watchIndex][1]-center[1])**2+(self.path[self.watchIndex][0]-center[0])**2)) > self.tool.sizePx:
                for cp in PADDOCKS[self.paddock]:
                    x = cp[0]
                    y = cp[1]
                    angle = 360-math.atan2((center[1]-y), (center[0]-x)) * 57.2957795
                    direction = [math.cos(math.radians(angle)), math.sin(math.radians(angle))]
                    #print(direction)
                    x += direction[0] * currentDist
                    y -= direction[1] * currentDist
                    self.path.append((x, y))
                currentDist += self.tool.sizePx*2-2
                currIter += 1
        elif len(self.path) == 0 and self.headingToFarm:
            self.headingToFarm = False
            self.tool.inShed = True
            self.tool = None
            self.inShed = True
            self.stringTask = "No Task Assigned"
        elif len(self.path) == 0 and self.headingToPdk != None and not self.headingToPdk:
            self.tool.on = False
            if self.tool.toolType == "Seeder": PADDOCK_CROPS[self.paddock] = CROP_TYPES.index(self.tool.fillType)
            _setPaddockState(self.paddock, TOOL_TYPES_STATES[self.tool.toolType])
            PADDOCK_LINES[self.paddock] = []
            self.path = ROADS[PADDOCK_ROUTES[self.paddock]].copy()
            self.path.append((1460/ZOOM+50/ZOOM, 368/ZOOM+150/ZOOM))
            self.paddock = None
            self.tool.paddock = None
            self.task = None
            self.stringTask = "Driving back to the farm"
            self.headingToFarm = True
            self.speed = 10
            _addXP(200)

        if self.tool != None: 
            self.tool.desiredRotation = self.rotation
            self.tool.x = self.x - (self.tool.rect.width - self.rect.width) / 2
            self.tool.y = self.y - (self.tool.rect.width - self.rect.width) / 2
            toolDirection = [math.cos(math.radians(self.tool.rotation-90)), math.sin(math.radians(self.tool.rotation-90))]
            self.tool.x += toolDirection[0] * (self.tool.rect.height + 5/ZOOM)
            self.tool.y -= toolDirection[1] * (self.tool.rect.height + 5/ZOOM)

        self.fuelTicks += 1
        if self.fuelTicks == 60*10:
            self.fuel -= 1
            self.fuelTicks = 0

            if self.fuel == 0:
                self.fuel = self.defaultFuel
                _removeMoney(self.fuel*2.5)

class Header:
    def __init__(self, x, y, attrs, brand, name):
        self.x = x
        self.y = y
        self.hp = attrs['hp']
        self.anims = attrs['anims']
        self.price = attrs['price']
        self.defaultFuel = attrs['fuel']
        self.fuel = self.defaultFuel
        self.originalImage = pg.image.load(f"{IMAGES_PATH}/{self.anims['pipeIn']}").convert_alpha()
        self.originalImage = pg.transform.scale(self.originalImage, (self.originalImage.get_width()*1.5/ZOOM, self.originalImage.get_height()*1.5/ZOOM))
        self.image = self.originalImage
        self.rect = self.image.get_rect(center = (x, y))
        self.desiredRotation = 180
        self.rotation = 180
        self.task = None
        self.stringTask = "No Task Assigned"
        self.brand = brand
        self.name = name
        self.paddock = None
        self.inShed = True
        self.speed = 10
        self.path = []
        self.headingToPdk = False
        self.headingToFarm = False
        self.watchIndex = None
        self.on = False
        self.lastPaint = (0, 0)
        self.header = True
        self.fill = 0
        self.fillType = "Wheat"
        self.fuelTicks = 0

    def draw(self, screen, sellPoints):
        screen.blit(pg.transform.rotate(self.image, self.rotation), (self.x, self.y))

        if len(self.path) > 0: self.desiredRotation = 270-math.atan2(self.path[0][1]-self.image.get_height()/2-self.y, self.path[0][0]-self.image.get_width()/2-self.x) * 57.2957795

        if self.rotation < 0: self.rotation += 360
        elif self.rotation > 360: self.rotation -= 360

        rotateDistLeft = self.desiredRotation-self.rotation
        if rotateDistLeft < -180: rotateDistLeft += 360
        elif rotateDistLeft > 180: rotateDistLeft -= 360

        if rotateDistLeft > 0: self.rotation += min(2, abs(self.desiredRotation - self.rotation)/30)
        elif rotateDistLeft < 0: self.rotation -= min(2, abs(self.desiredRotation - self.rotation)/30)

        self.direction = [math.cos(math.radians(self.rotation-90)), math.sin(math.radians(self.rotation-90))]
        self.x -= self.direction[0] * (self.speed*min(1, max(0.25, 1-abs(rotateDistLeft)/180))) / 10
        self.y += self.direction[1] * (self.speed*min(1, max(0.25, 1-abs(rotateDistLeft)/180))) / 10

        if len(self.path) > 0 and abs(self.path[0][1]-self.image.get_height()/2-self.y + self.path[0][0]-self.image.get_width()/2-self.x) < 2: self.path.pop(0)

        if DEBUG and len(self.path) > 1:
            for i in range(len(self.path)-1): pg.draw.line(screen, (0, 255, 0), self.path[i], self.path[i+1])
        elif len(self.path) == 1 and self.headingToPdk: self.speed = 3
        elif len(self.path) == 0 and self.headingToPdk:
            self.headingToPdk = False
            self.paddock = self.task
            self.fillType = CROP_TYPES[PADDOCK_CROPS[self.paddock]]
            self.on = True
            self.stringTask = f"Harvesting paddock {self.paddock}"

            center = PADDOCK_CENTERS[self.paddock]
            currentDist = self.rect.width/2-1
            currIter = 0

            for cp in PADDOCKS[self.paddock]:
                x = cp[0]
                y = cp[1]
                angle = 360-math.atan2((center[1]-y), (center[0]-x)) * 57.2957795
                direction = [math.cos(math.radians(angle)), math.sin(math.radians(angle))]
                #print(direction)
                x += direction[0] * currentDist
                y -= direction[1] * currentDist
                self.path.append((x, y))

            currentDist += self.rect.width-2

            self.watchIndex = int(len(self.path)/2)

            while currIter < 10 and abs(math.sqrt((self.path[-1][1]-center[1])**2+(self.path[-1][0]-center[0])**2)) > self.rect.width/2 and abs(math.sqrt((self.path[self.watchIndex][1]-center[1])**2+(self.path[self.watchIndex][0]-center[0])**2)) > self.rect.width/2:
                for cp in PADDOCKS[self.paddock]:
                    x = cp[0]
                    y = cp[1]
                    angle = 360-math.atan2((center[1]-y), (center[0]-x)) * 57.2957795
                    direction = [math.cos(math.radians(angle)), math.sin(math.radians(angle))]
                    #print(direction)
                    x += direction[0] * currentDist
                    y -= direction[1] * currentDist
                    self.path.append((x, y))
                currentDist += self.rect.width-2
                currIter += 1
        elif len(self.path) == 0 and self.headingToFarm:
            self.headingToFarm = False
            self.inShed = True
            _fillSilo(self.fill, self.fillType)
            self.fill = 0
            self.stringTask = "No Task Assigned"
        elif len(self.path) == 0 and not self.headingToPdk:
            self.on = False
            _setPaddockState(self.paddock, TOOL_TYPES_STATES["Harvester"])
            PADDOCK_LINES[self.paddock] = []
            self.path = ROADS[PADDOCK_ROUTES[self.paddock]].copy()
            self.path.append((1460/ZOOM+50/ZOOM, 368/ZOOM+150/ZOOM))
            self.paddock = None
            self.task = None
            self.stringTask = "Driving back to the farm"
            self.headingToFarm = True
            self.speed = 10
            _addXP(300)

        if self.on and math.sqrt(abs((self.y-self.lastPaint[1])**2+(self.x-self.lastPaint[0])**2)) > self.rect.width:
            self.lastPaint = (self.x, self.y)
            PADDOCK_LINES[self.paddock].append((STATE_COLORS[TOOL_TYPES_STATES["Harvester"]], self.x, self.y, self.rect.width, self.rect.width/2))
            self.fill += self.image.get_width() * 2 / 1000

        self.fuelTicks += 1
        if self.fuelTicks == 60*10:
            self.fuel -= 1
            self.fuelTicks = 0

            if self.fuel == 0:
                self.fuel = self.defaultFuel
                _removeMoney(self.fuel*2.5)

class Menu:
    def __init__(self, width, height, vehiclesDict, toolsDict):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.bg = (255, 255, 255)
        self.navBar = [pgui.Button(13/ZOOM, 6/ZOOM, 120/ZOOM, 100/ZOOM, (0, 200, 255), (0, 0, 200), (255, 255, 255), "Shop", int(20/ZOOM), (5, 5, 0, 0), 30/ZOOM, 40/ZOOM), pgui.Button(128/ZOOM, 6/ZOOM, 120/ZOOM, 100/ZOOM, (0, 200, 255), (0, 0, 200), (255, 255, 255), "Equipment", int(20/ZOOM), (0, 0, 0, 0), 10/ZOOM, 40/ZOOM), pgui.Button(248/ZOOM, 6/ZOOM, 120/ZOOM, 100/ZOOM, (0, 200, 255), (0, 0, 200), (255, 255, 255), "Paddocks", int(20/ZOOM), (0, 0, 0, 0), 15/ZOOM, 40/ZOOM), pgui.Button(368/ZOOM, 6/ZOOM, 120/ZOOM, 100/ZOOM, (0, 200, 255), (0, 0, 200), (255, 255, 255), "Grain", int(20/ZOOM), (0, 0, 0, 0), 30/ZOOM, 40/ZOOM), pgui.Button(488/ZOOM, 6/ZOOM, 120/ZOOM, 100/ZOOM, (0, 200, 255), (0, 0, 200), (255, 255, 255), "Finance", int(20/ZOOM), (0, 0, 5, 5), 25/ZOOM, 40/ZOOM)]
        self.selectedButton = 0
        self.scroll = 0
        self.font40 = pg.font.SysFont("Arial", int(40/ZOOM))
        self.font20 = pg.font.SysFont("Arial", int(30/ZOOM))
        self.font18 = pg.font.SysFont("Arial", int(25/ZOOM))
        self.equipmentButtons = []
        self.addedEquipment = False
        self.grainTable = pgui.Table(30/ZOOM, 140/ZOOM, self.width-(60/ZOOM), self.width-(60/ZOOM), 5, 5, (0, 200, 255), (0, 0, 255), int(45/ZOOM), ZOOM)
        self.shopBackBtn = pgui.Button(self.width/2-100/ZOOM, self.height-150/ZOOM, 200/ZOOM, 100/ZOOM, (0, 200, 255), (0, 0, 200), (255, 255, 255), "Back", int(40/ZOOM), (5, 5, 5, 5), 55/ZOOM, 27/ZOOM)
        self.shopButtons = []
        self.nonVolatileShopItems = {}
        self.shopItems = {}
        self.shopParents = []
        self.iter = 0
        self.vehiclesDict = vehiclesDict
        self.toolsDict = toolsDict
        self.__initShop()
        self.setShopButtons()
        self.shopImgs = []
        self.lastImg = 0
        self.shopImgIndex = 0
        self.shopTitle = None
        self.shopInfoLbls = []
        self.shopPriceLbl = None
        self.shopBuyBtn = pgui.Button(self.width/2-100/ZOOM, self.height-290/ZOOM, 200/ZOOM, 100/ZOOM, (0, 200, 255), (0, 0, 200), (255, 255, 255), "Buy", int(40/ZOOM), (5, 5, 5, 5), 65/ZOOM, 27/ZOOM)
        self.shopBuyLbls = (self.font20.render("Not enough XP!", True, (255, 0, 0)), self.font20.render("Not enough money!", True, (255, 0, 0)), self.font20.render("So sorry, not in the game yet :(", True, (255, 0, 0)))
        self.pdkBuyBtn = pgui.Button((self.width - 25/ZOOM*4)/3+25/ZOOM*2, 150/ZOOM+(self.width - 25/ZOOM*4)/3*2+25/ZOOM*2, (self.width - 25/ZOOM*4)/3, (self.width - 25/ZOOM*4)/3, (0, 200, 255), (0, 0, 200), (255, 255, 255), "Paddocks", min(int(30/ZOOM), int(250/len("Paddocks")/ZOOM)), (5, 5, 5, 5), 0, 0, True)
        self.cropBuyBtn = pgui.Button((self.width - 25/ZOOM*4)/3*2+25/ZOOM*3, 150/ZOOM+(self.width - 25/ZOOM*4)/3*2+25/ZOOM*2, (self.width - 25/ZOOM*4)/3, (self.width - 25/ZOOM*4)/3, (0, 200, 255), (0, 0, 200), (255, 255, 255), "Crops", min(int(30/ZOOM), int(250/len("Paddocks")/ZOOM)), (5, 5, 5, 5), 0, 0, True)
        self.drawingPdks = False
        self.drawingCrops = False
        self.shopDropdowns = []

    def __initShop(self):
        for vehicleType in list(self.vehiclesDict.keys()): self.shopItems[vehicleType] = self.vehiclesDict[vehicleType]
        for toolType in list(self.toolsDict.keys()): self.shopItems[toolType] = self.toolsDict[toolType]

        self.nonVolatileShopItems = deepcopy(self.shopItems)

    def setShopButtons(self):
        self.shopButtons = []
        x = 25/ZOOM
        y = 150/ZOOM
        
        size = (self.width - 25/ZOOM*4)/3
        step = size + 25/ZOOM

        for item in list(self.shopItems.keys()):
            self.shopButtons.append(pgui.Button(x, y, size, size, (0, 200, 255), (0, 0, 200), (255, 255, 255), item, min(int(30/ZOOM), int(250/len(item)/ZOOM)), (5, 5, 5, 5), 0, 0, True))
            x += step
            
            if x >= (step)*3+25/ZOOM-5/ZOOM:
                y += step
                x = 25/ZOOM

    def drawEquipment(self, screen, equipment, tools, clicked, pressed, rel):
        if len(equipment) != len(self.equipmentButtons):
            self.addedEquipment = False
            self.equipmentButtons = []
        
        x = 30/ZOOM
        y = 140/ZOOM
        yInc = 170/ZOOM
        if clicked:
            if len(self.equipmentButtons) > 0:
                for button in self.equipmentButtons:
                    if pg.Rect(button.x, button.y, button.width, button.height).collidepoint(pg.mouse.get_pos()):
                        toolTitles = []
                        toolClasses = []
                        for item in tools:
                            if item.inShed:
                                toolTitles.append(f"{item.brand} {item.name}")
                                toolClasses.append(item)
                        paddocks = []
                        for pdk in PADDOCKS:
                            if PADDOCK_OWNERS[pdk] == 1: paddocks.append(pdk)
                        sellPoints = SELL_POINTS.copy()
                        sellPoints.insert(0, None)
                        if equipment[self.equipmentButtons.index(button)].header: _createPopup(500/ZOOM, 250/ZOOM, (255, 255, 255), (63, 72, 204), "HeaderTask", [equipment[self.equipmentButtons.index(button)], paddocks])
                        else: _createPopup(500/ZOOM, 250/ZOOM, (255, 255, 255), (63, 72, 204), "Task", [equipment[self.equipmentButtons.index(button)], toolTitles, paddocks, sellPoints, toolClasses])
        if pressed:
            for item in equipment: y += yInc
            scrollScale = (y - yInc) / int(self.height-(140/ZOOM))
            scrollHeight = min(self.height-110/ZOOM, (self.height-110/ZOOM)/scrollScale)
            if pg.mouse.get_pos()[0] < self.width and ((110/ZOOM+self.scroll/ZOOM/scrollScale + scrollHeight/ZOOM)/self.height < 1 or rel[1] > 0) and ((110/ZOOM+self.scroll/ZOOM/scrollScale)/self.height > 0.10185 or rel[1] < 0):
                self.scroll = self.scroll-rel[1]
        y = 140/ZOOM
        for item in equipment:
            #pg.draw.rect(screen, (0, 200, 255), (x, y-self.scroll/ZOOM, self.width-x*3, 130/ZOOM), border_radius=20)
            if not self.addedEquipment: self.equipmentButtons.append(pgui.Button(x, y-self.scroll/ZOOM, self.width-x*3, 130/ZOOM, (0, 200, 255), (0, 0, 255), (255, 255, 255), "", 18, (20, 20, 20, 20), 0, 0))
            self.equipmentButtons[equipment.index(item)].y -= self.scroll / ZOOM
            self.equipmentButtons[equipment.index(item)].draw(screen)
            self.equipmentButtons[equipment.index(item)].y += self.scroll / ZOOM
            lbl = self.font20.render(f"{item.brand} {item.name}", True, (255, 255, 255))
            screen.blit(lbl, lbl.get_rect(center=((self.width-x*3-x)/1.7, y-self.scroll/ZOOM+30/ZOOM)))
            screen.blit(self.font18.render(f"Task: {item.stringTask}", True, (255, 255, 255)), (60/ZOOM, y-self.scroll/ZOOM+50/ZOOM))
            screen.blit(self.font18.render(f"Fuel: {item.fuel}L", True, (255, 255, 255)), (60/ZOOM, y-self.scroll/ZOOM+85/ZOOM))
            screen.blit(self.font18.render(f"Paddock: {item.paddock}", True, (255, 255, 255)), (self.width-(250/ZOOM), y-self.scroll/ZOOM+85/ZOOM))
            y += yInc

        self.addedEquipment = True

        scrollScale = (y - yInc) / int(self.height-(140/ZOOM))
        scrollHeight = min(self.height-110/ZOOM, (self.height-110/ZOOM)/scrollScale)
        pg.draw.rect(screen, (200, 200, 200), (self.width-30/ZOOM, 110/ZOOM, 30/ZOOM, self.height-110/ZOOM))
        pg.draw.rect(screen, (150, 150, 150), (self.width-30/ZOOM, 110/ZOOM+self.scroll/ZOOM/scrollScale, 30/ZOOM, scrollHeight/ZOOM))

    def drawGrain(self, screen, farmAmmount, greenSpringBakery, greenSpringMill, greenSpringTrades):
        self.grainTable.grid = [
            ["", "Wheat", "Barley", "Canola", "Oat"],
            ["Farm", farmAmmount[0], farmAmmount[1], farmAmmount[2], farmAmmount[3]],
            ["GSB", greenSpringBakery[0], greenSpringBakery[1], greenSpringBakery[2], greenSpringBakery[3]],
            ["GSM", greenSpringMill[0], greenSpringMill[1], greenSpringMill[2], greenSpringMill[3]],
            ["GST", greenSpringTrades[0], greenSpringTrades[1], greenSpringTrades[2], greenSpringTrades[3]]
            ]
        self.grainTable.draw(screen)

        screen.blit(self.font40.render("GSB = Green Spring Bakery", True, (0, 0, 0)), (30/ZOOM, 750/ZOOM))
        screen.blit(self.font40.render("GSM = Green Spring Mill", True, (0, 0, 0)), (30/ZOOM, 825/ZOOM))
        screen.blit(self.font40.render("GST = Green Spring Trades", True, (0, 0, 0)), (30/ZOOM, 900/ZOOM))

    def drawBuyMenu(self, screen, money, xp, clicked):
        if self.shopImgs == []:
            self.shopTitle = self.font40.render(self.shopParents[-1], True, (0, 0, 0))
            for img in list(self.shopItems["anims"].keys()):
                if img == "default" or self.shopItems["anims"][img] == None: continue
                self.shopImgs.append(pg.transform.scale_by(pg.image.load(f"{IMAGES_PATH}/{self.shopItems['anims'][img]}").convert_alpha(), 3/ZOOM))

            for attr in list(self.shopItems.keys()):
                if attr == "sizePx" or attr == "turningPoint" or attr == "hitch" or attr == "anims" or attr == "pipeOffset" or self.shopItems[attr] == None: continue
                elif attr == "price":
                    self.shopPriceLbl = self.font40.render(f"Price: ${self.shopItems[attr]:,}", True, (0, 0, 0)) # int(<an_integar>):, in an f string formats with commas
                    continue
                elif attr == "xp":
                    self.shopInfoLbls.append(self.font18.render(f"XP: {str(self.shopItems[attr])}", True, (0, 0, 0)))                    
                    continue

                additional = ""
                if attr == "fuel": additional = "L"
                elif attr == "storage": additional = "T"
                elif attr == "size": additional = "ft"

                self.shopInfoLbls.append(self.font18.render(f"{attr[0].upper()+attr[1:]}: {str(self.shopItems[attr])+additional}", True, (0, 0, 0)))

        if self.lastImg == 60:
            self.lastImg = 0
            self.shopImgIndex += 1

        if self.shopImgIndex == len(self.shopImgs): self.shopImgIndex = 0

        self.lastImg += 1

        if clicked:
            if pg.Rect(self.shopBackBtn.x, self.shopBackBtn.y, self.shopBackBtn.width, self.shopBackBtn.height).collidepoint(pg.mouse.get_pos()):
                self.lastImg = 0
                self.shopImgIndex = 0
                self.shopImgs = []
                self.shopInfoLbls = []
                self.iter -= 1
                self.shopItems = deepcopy(self.nonVolatileShopItems)
                
                self.shopParents.pop(-1)
                for parent in self.shopParents: self.shopItems = self.shopItems[parent]
                self.setShopButtons()
                return
            elif xp/1000 < float(self.shopItems['xp']) or money < self.shopItems['price']: pass # stops button selection if its not buyable
            elif pg.Rect(self.shopBuyBtn.x, self.shopBuyBtn.y, self.shopBuyBtn.width, self.shopBuyBtn.height).collidepoint(pg.mouse.get_pos()):
                _removeMoney(self.shopItems['price'])
                _addVehicle(self.shopParents)
                self.lastImg = 0
                self.shopImgIndex = 0
                self.shopImgs = []
                self.shopInfoLbls = []
                self.iter = 0
                self.shopItems = deepcopy(self.nonVolatileShopItems)
                
                self.shopParents = []
                self.setShopButtons()
                return

        screen.blit(self.shopImgs[self.shopImgIndex], (self.width/2-50/ZOOM, 200/ZOOM))

        screen.blit(self.shopTitle, (self.width/2-self.shopTitle.get_width()/2, 350/ZOOM))
        for lbl in self.shopInfoLbls: screen.blit(lbl, (100/ZOOM, 425/ZOOM+30*self.shopInfoLbls.index(lbl)))
        screen.blit(self.shopPriceLbl, (self.width/2-self.shopPriceLbl.get_width()/2, 700/ZOOM))

        if xp/1000 < float(self.shopItems['xp']): screen.blit(self.shopBuyLbls[0], (self.width/2-self.shopBuyLbls[0].get_width()/2, self.height-250/ZOOM))
        elif money < self.shopItems['price']: screen.blit(self.shopBuyLbls[1], (self.width/2-self.shopBuyLbls[1].get_width()/2, self.height-250/ZOOM))
        elif self.shopParents[0][:-1] not in TOOL_TYPES_STATES: screen.blit(self.shopBuyLbls[2], (self.width/2-self.shopBuyLbls[2].get_width()/2, self.height-250/ZOOM))
        else: self.shopBuyBtn.draw(screen)
        self.shopBackBtn.draw(screen)

    def drawPdkMenu(self, screen, money, clicked):
        if self.shopDropdowns == []:
            renderPdks = []
            for pdk in PADDOCK_OWNERS:
                if PADDOCK_OWNERS[pdk] == 0: renderPdks.append(pdk)

            self.shopDropdowns.append(DropDown(renderPdks, self.width/2-100/ZOOM, 400/ZOOM, 200/ZOOM, 40/ZOOM, (200, 200, 200)))
    
        self.shopDropdowns[0].draw(screen, clicked, pg.mouse.get_pos())
        price = PADDOCK_HECTARES[self.shopDropdowns[0].selectedButton.text]*12000
        priceLbl = self.font40.render(f"Price: ${price:,}", True, (0, 0, 0))
        screen.blit(priceLbl, (self.width/2-priceLbl.get_width()/2, 700/ZOOM))

        if clicked:
            if pg.Rect(self.shopBackBtn.x, self.shopBackBtn.y, self.shopBackBtn.width, self.shopBackBtn.height).collidepoint(pg.mouse.get_pos()):
                self.iter = 0
                self.shopDropdowns = []
                self.drawingPdks = False
                self.setShopButtons()
                return
            elif money < price: pass # stops button selection if its not buyable
            elif pg.Rect(self.shopBuyBtn.x, self.shopBuyBtn.y, self.shopBuyBtn.width, self.shopBuyBtn.height).collidepoint(pg.mouse.get_pos()):
                _removeMoney(price)
                PADDOCK_OWNERS[int(self.shopDropdowns[0].selectedButton.text)] = 1
                self.iter = 0
                self.shopDropdowns = []
                self.drawingPdks = False
                self.setShopButtons()
                return

        if money < price: screen.blit(self.shopBuyLbls[1], (self.width/2-self.shopBuyLbls[1].get_width()/2, self.height-250/ZOOM))
        else: self.shopBuyBtn.draw(screen)
        self.shopBackBtn.draw(screen)

    def drawCropMenu(self, screen, money, xp, clicked):
        if self.shopDropdowns == []:
            self.shopDropdowns.append(DropDown(["Wheat", "Barley", "Canola", "Oat"], self.width/2-220/ZOOM, 400/ZOOM, 200/ZOOM, 40/ZOOM, (200, 200, 200)))
            self.shopDropdowns.append(DropDown(["1T", "5T", "10T"], self.width/2+20/ZOOM, 400/ZOOM, 200/ZOOM, 40/ZOOM, (200, 200, 200)))

        cropTypeLbl = self.font20.render("Crop Type", True, (0, 0, 0))
        screen.blit(cropTypeLbl, (self.width/2-220/ZOOM/2-cropTypeLbl.get_width()/2, 350/ZOOM))
        cropAmountLbl = self.font20.render("Amount", True, (0, 0, 0))
        screen.blit(cropAmountLbl, (self.width/2+220/ZOOM/2-cropAmountLbl.get_width()/2, 350/ZOOM))

        for dropdown in self.shopDropdowns: dropdown.draw(screen, clicked, pg.mouse.get_pos())
        price = BASE_CROP_COSTS[self.shopDropdowns[0].selectedButton.text]*8*int(self.shopDropdowns[1].selectedButton.text[:-1])
        priceLbl = self.font40.render(f"Price: ${price:,}", True, (0, 0, 0))
        screen.blit(priceLbl, (self.width/2-priceLbl.get_width()/2, 650/ZOOM))

        xpCost = CROP_XP_COSTS[self.shopDropdowns[0].selectedButton.text]
        xpLbl = self.font40.render(f"XP: {xpCost}", True, (0, 0, 0))
        screen.blit(xpLbl, (self.width/2-xpLbl.get_width()/2, 710/ZOOM))

        if clicked:
            if pg.Rect(self.shopBackBtn.x, self.shopBackBtn.y, self.shopBackBtn.width, self.shopBackBtn.height).collidepoint(pg.mouse.get_pos()):
                self.iter = 0
                self.shopDropdowns = []
                self.drawingCrops = False
                self.setShopButtons()
                return
            elif money < price: pass # stops button selection if its not buyable
            elif pg.Rect(self.shopBuyBtn.x, self.shopBuyBtn.y, self.shopBuyBtn.width, self.shopBuyBtn.height).collidepoint(pg.mouse.get_pos()):
                _removeMoney(price)
                _addCrop(self.shopDropdowns[0].selectedButton.text, int(self.shopDropdowns[1].selectedButton.text[:-1]))
                self.iter = 0
                self.shopDropdowns = []
                self.drawingCrops = False
                self.setShopButtons()
                return
            
        if money < price: screen.blit(self.shopBuyLbls[1], (self.width/2-self.shopBuyLbls[1].get_width()/2, self.height-250/ZOOM))
        elif xp/1000 < xpCost: screen.blit(self.shopBuyLbls[0], (self.width/2-self.shopBuyLbls[0].get_width()/2, self.height-250/ZOOM))
        else: self.shopBuyBtn.draw(screen)
        self.shopBackBtn.draw(screen)

    def drawShop(self, screen, money, xp, clicked):
        if self.iter == 3:
            self.drawBuyMenu(screen, money, xp, clicked)
            return
        
        if self.drawingPdks:
            self.drawPdkMenu(screen, money, clicked)
            return
        elif self.drawingCrops:
            self.drawCropMenu(screen, money, xp, clicked)
            return
        
        for button in self.shopButtons:
            if clicked and pg.Rect(button.x, button.y, button.width, button.height).collidepoint(pg.mouse.get_pos()):
                self.iter += 1
                item = list(self.shopItems.keys())[self.shopButtons.index(button)]
                self.shopParents.append(item)
                self.shopItems = self.shopItems[item]
                self.setShopButtons()
                break

            button.draw(screen)

        if self.iter == 0:
            self.pdkBuyBtn.draw(screen)
            self.cropBuyBtn.draw(screen)

        if clicked:
            if pg.Rect(self.pdkBuyBtn.x, self.pdkBuyBtn.y, self.pdkBuyBtn.width, self.pdkBuyBtn.height).collidepoint(pg.mouse.get_pos()): self.drawingPdks = True
            elif pg.Rect(self.cropBuyBtn.x, self.cropBuyBtn.y, self.cropBuyBtn.width, self.cropBuyBtn.height).collidepoint(pg.mouse.get_pos()): self.drawingCrops = True

        if clicked and pg.Rect(self.shopBackBtn.x, self.shopBackBtn.y, self.shopBackBtn.width, self.shopBackBtn.height).collidepoint(pg.mouse.get_pos()):
            if self.iter > 0:
                self.iter -= 1
                self.shopItems = deepcopy(self.nonVolatileShopItems)
                
                self.shopParents.pop(-1)
                for parent in self.shopParents: self.shopItems = self.shopItems[parent]
                self.setShopButtons()

        if self.iter > 0: self.shopBackBtn.draw(screen)

    def draw(self, screen, equipment, tools, clicked, pressed, rel, grainGrid, money, xp):
        pg.draw.rect(screen, self.bg, (self.x, self.y, self.width, self.height))
        if self.selectedButton == 0: self.drawShop(screen, money, xp, clicked)

        elif self.selectedButton == 1: self.drawEquipment(screen, equipment, tools, clicked, pressed, rel)
        elif self.selectedButton == 3: self.drawGrain(screen, grainGrid[0], grainGrid[1], grainGrid[2], grainGrid[3])
        self.navBar[self.selectedButton].clicked = True
        for button in self.navBar:
            if self.navBar.index(button) != self.selectedButton: button.clicked = False
            pg.draw.rect(screen, (150, 150, 150), (button.x-5/ZOOM, button.y-5/ZOOM, button.width+10/ZOOM, button.height+10/ZOOM), border_radius=5)
            button.draw(screen)

        return None

class DropDown:
    def __init__(self, options, x, y, width, height, color):
        self.options = options
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.droppedHeight = height * len(self.options)
        self.color = color
        self.selected = 0
        self.font18 = pg.font.SysFont("Arial", 18)
        self.droppedDown = False
        self.selectedButton = pgui.Button(self.x, self.y, self.width, self.height, self.color, self.color, (0, 0, 0), self.options[self.selected], int(25/ZOOM), (5, 5, 5, 5), 10/ZOOM, 6/ZOOM)
        self.droppedButtons = [pgui.Button(self.x, self.y+self.height*dby, self.width, self.height, self.color, self.color, (0, 0, 0), self.options[dby], int(25/ZOOM), (5, 5, 5, 5), 10/ZOOM, 10/ZOOM) for dby in range(len(options))]

    def draw(self, screen, pressed, mousePos):
        if self.droppedDown:
            pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.droppedHeight), border_radius=10)
            for droppedButton in self.droppedButtons:
                droppedButton.draw(screen)
                if pressed and pg.Rect(droppedButton.x, droppedButton.y, droppedButton.width, droppedButton.height).collidepoint(mousePos):
                    self.droppedDown = False
                    self.selected = self.droppedButtons.index(droppedButton)
                    self.selectedButton.text = self.options[self.selected]
        else:
            self.selectedButton.draw(screen)
            if pressed and pg.Rect(self.selectedButton.x, self.selectedButton.y, self.selectedButton.width, self.selectedButton.height).collidepoint(mousePos): self.droppedDown = True

class Popup:
    def __init__(self, x, y, width, height, color, highlightColor, popupType, additionals):
        self.x = x-width/2
        self.y = y-height/2
        self.width = width
        self.height = height
        self.color = color
        self.highlightColor = highlightColor
        self.popupType = popupType
        self.additionals = additionals
        self.font20 = pg.font.SysFont("Arial", int(30/ZOOM))
        self.font18 = pg.font.SysFont("Arial", int(25/ZOOM))
        if self.popupType == "Task": self.dropDowns = [DropDown(self.additionals[1], self.x + 80/ZOOM, self.y + 75/ZOOM, 330/ZOOM, 40/ZOOM, (200, 200, 200)), DropDown(self.additionals[2], self.x + 125/ZOOM, self.y + 115/ZOOM, 34/ZOOM, 40/ZOOM, (200, 200, 200)), DropDown(self.additionals[3], self.x + 230/ZOOM, self.y + 150/ZOOM, 250/ZOOM, 40/ZOOM, (200, 200, 200))]
        elif self.popupType == "HeaderTask": self.dropDowns = [DropDown(self.additionals[1], self.x + 125/ZOOM, self.y + 70/ZOOM, 34/ZOOM, 40/ZOOM, (200, 200, 200))]
        elif self.popupType == "cropChoice": self.dropDowns = [DropDown(CROP_TYPES, self.x + 100/ZOOM, self.y + 75/ZOOM, 100/ZOOM, 40/ZOOM, (200, 200, 200))]
        else: self.dropDowns = []
        #self.decline = pgui.Button(self.x+self.width-50/ZOOM, self.y+self.height-25/ZOOM, 35/ZOOM, 35/ZOOM, (255, 0, 0), (200, 0, 0), (255, 255, 255), "", 10, (5, 5, 5, 5), 0, 0)
        #self.accept = pgui.Button(self.x+self.width-25/ZOOM, self.y+self.height-25/ZOOM, 35/ZOOM, 35/ZOOM, (0, 255, 0), (0, 200, 0), (255, 255, 255), "", 10, (5, 5, 5, 5), 0, 0)
        self.tick = pg.transform.scale(pg.image.load(f"{IMAGES_PATH}/tick.png").convert_alpha(), (35/ZOOM, 35/ZOOM))
        self.cross = pg.transform.scale(pg.image.load(f"{IMAGES_PATH}/cross.png").convert_alpha(), (35/ZOOM, 35/ZOOM))
        self.popup = None

    def draw(self, screen, pressed, mousePos):
        if self.popupType == "Task":
            pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=20)
            pg.draw.rect(screen, self.highlightColor, (self.x, self.y, self.width, 50/ZOOM), border_top_left_radius=20, border_top_right_radius=20)
            pg.draw.rect(screen, self.highlightColor, (self.x, self.y+self.height-50/ZOOM, self.width, 50/ZOOM), border_bottom_left_radius=20, border_bottom_right_radius=20)
            screen.blit(self.font20.render(f"{self.additionals[0].brand} {self.additionals[0].name} - New Task", True, (255, 255, 255)), (self.x + 10/ZOOM, self.y + 10/ZOOM))
            screen.blit(self.font18.render(f"Tool:", True, (0, 0, 0)), (self.x + 20/ZOOM, self.y + 80/ZOOM))
            screen.blit(self.font18.render(f"Paddock:", True, (0, 0, 0)), (self.x + 20/ZOOM, self.y + 120/ZOOM))
            screen.blit(self.font18.render(f"        or Destination:", True, (0, 0, 0)), (self.x + 20/ZOOM, self.y + 155/ZOOM))
            
            screen.blit(self.cross, (self.x+self.width-90/ZOOM, self.y+self.height-42/ZOOM))
            screen.blit(self.tick, (self.x+self.width-50/ZOOM, self.y+self.height-42/ZOOM))

            # draw dropdowns from bottom to top so when expaned they cover over each other
            self.dropDowns.reverse()
            for dropDown in self.dropDowns:
                if self.popup != None: dropDown.draw(screen, False, mousePos)
                else: dropDown.draw(screen, pressed, mousePos)
            self.dropDowns.reverse()

            if self.popup != None:
                cropType = self.popup.draw(screen, pressed, mousePos)
                if cropType != None: return "sellPoint", self.additionals[4][self.dropDowns[0].selected], self.dropDowns[2].selected, cropType

            if pressed and _mouseCollision(mousePos[0], mousePos[1], self.x+self.width-90/ZOOM, self.y+self.height-42/ZOOM, self.cross.get_rect().width, self.cross.get_rect().height):
                return "exit"
            elif pressed and _mouseCollision(mousePos[0], mousePos[1], self.x+self.width-50/ZOOM, self.y+self.height-42/ZOOM, self.tick.get_rect().width, self.tick.get_rect().height):
                if self.dropDowns[2].selected == 0:
                    if self.additionals[4][self.dropDowns[0].selected].toolType != "Trailer": return "pdk", self.additionals[4][self.dropDowns[0].selected], self.dropDowns[1].selected + 1
                    else: ...
                else:
                    if self.additionals[4][self.dropDowns[0].selected].toolType != "Trailer": ...
                    elif self.popup == None: self.popup = Popup(self.x, self.y, self.width, self.height, self.color, self.highlightColor, "cropChoice", []) 

            return None
        elif self.popupType == "HeaderTask":
            pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=20)
            pg.draw.rect(screen, self.highlightColor, (self.x, self.y, self.width, 50/ZOOM), border_top_left_radius=20, border_top_right_radius=20)
            pg.draw.rect(screen, self.highlightColor, (self.x, self.y+self.height-50/ZOOM, self.width, 50/ZOOM), border_bottom_left_radius=20, border_bottom_right_radius=20)
            screen.blit(self.font20.render(f"{self.additionals[0].brand} {self.additionals[0].name} - New Task", True, (255, 255, 255)), (self.x + 10/ZOOM, self.y + 10/ZOOM))
            screen.blit(self.font18.render(f"Paddock:", True, (0, 0, 0)), (self.x + 20/ZOOM, self.y + 75/ZOOM))
            
            self.dropDowns.reverse()
            for dropDown in self.dropDowns:
                dropDown.draw(screen, pressed, mousePos)
            self.dropDowns.reverse()

            #self.decline.draw(screen)
            screen.blit(self.cross, (self.x+self.width-90/ZOOM, self.y+self.height-42/ZOOM))
            #self.accept.draw(screen)
            screen.blit(self.tick, (self.x+self.width-50/ZOOM, self.y+self.height-42/ZOOM))

            if pressed and _mouseCollision(mousePos[0], mousePos[1], self.x+self.width-90/ZOOM, self.y+self.height-42/ZOOM, self.cross.get_rect().width, self.cross.get_rect().height):
                return "exit"
            elif pressed and _mouseCollision(mousePos[0], mousePos[1], self.x+self.width-50/ZOOM, self.y+self.height-42/ZOOM, self.tick.get_rect().width, self.tick.get_rect().height):
                return "hdr", self.dropDowns[0].selected

            return None
        elif self.popupType == "Warning":
            pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=20)
            pg.draw.rect(screen, self.highlightColor, (self.x, self.y, self.width, 50/ZOOM), border_top_left_radius=20, border_top_right_radius=20)
            pg.draw.rect(screen, self.highlightColor, (self.x, self.y+self.height-50/ZOOM, self.width, 50/ZOOM), border_bottom_left_radius=20, border_bottom_right_radius=20)
            screen.blit(self.font20.render(f"Warning", True, (255, 255, 255)), (self.x + 10/ZOOM, self.y + 10/ZOOM))
            screen.blit(self.font18.render(self.additionals[0], True, (0, 0, 0)), (self.x + 20/ZOOM, self.y + 80/ZOOM))
            screen.blit(self.font18.render(self.additionals[1], True, (0, 0, 0)), (self.x + 20/ZOOM, self.y + 120/ZOOM))
            screen.blit(self.tick, (self.x+self.width-50/ZOOM, self.y+self.height-42/ZOOM))
            if pressed and _mouseCollision(mousePos[0], mousePos[1], self.x+self.width-50/ZOOM, self.y+self.height-42/ZOOM, self.tick.get_rect().width, self.tick.get_rect().height):
                return "exit"
        elif self.popupType == "Sleep":
            pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=20)
            pg.draw.rect(screen, self.highlightColor, (self.x, self.y, self.width, 50/ZOOM), border_top_left_radius=20, border_top_right_radius=20)
            pg.draw.rect(screen, self.highlightColor, (self.x, self.y+self.height-50/ZOOM, self.width, 50/ZOOM), border_bottom_left_radius=20, border_bottom_right_radius=20)
            screen.blit(self.font20.render(f"Sleep", True, (255, 255, 255)), (self.x + 10/ZOOM, self.y + 10/ZOOM))
            screen.blit(self.font18.render(self.additionals[0], True, (0, 0, 0)), (self.x + 20/ZOOM, self.y + 80/ZOOM))
            screen.blit(self.font18.render(self.additionals[1], True, (0, 0, 0)), (self.x + 20/ZOOM, self.y + 120/ZOOM))
            screen.blit(self.cross, (self.x+self.width-90/ZOOM, self.y+self.height-42/ZOOM))
            screen.blit(self.tick, (self.x+self.width-50/ZOOM, self.y+self.height-42/ZOOM))
            if pressed and _mouseCollision(mousePos[0], mousePos[1], self.x+self.width-50/ZOOM, self.y+self.height-42/ZOOM, self.tick.get_rect().width, self.tick.get_rect().height):
                return "sleep"
            elif pressed and _mouseCollision(mousePos[0], mousePos[1], self.x+self.width-50/ZOOM, self.y+self.height-42/ZOOM, self.cross.get_rect().width, self.cross.get_rect().height):
                return "exit"
        elif self.popupType == "cropChoice":
            pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=20)
            pg.draw.rect(screen, self.highlightColor, (self.x, self.y, self.width, 50/ZOOM), border_top_left_radius=20, border_top_right_radius=20)
            pg.draw.rect(screen, self.highlightColor, (self.x, self.y+self.height-50/ZOOM, self.width, 50/ZOOM), border_bottom_left_radius=20, border_bottom_right_radius=20)
            screen.blit(self.font20.render(f"Crop Choice", True, (255, 255, 255)), (self.x + 10/ZOOM, self.y + 10/ZOOM))
            screen.blit(self.font18.render("Crop:", True, (0, 0, 0)), (self.x + 20/ZOOM, self.y + 80/ZOOM))
            screen.blit(self.tick, (self.x+self.width-50/ZOOM, self.y+self.height-42/ZOOM))
            self.dropDowns[0].draw(screen, pressed, mousePos)
            if pressed and _mouseCollision(mousePos[0], mousePos[1], self.x+self.width-50/ZOOM, self.y+self.height-42/ZOOM, self.tick.get_rect().width, self.tick.get_rect().height):
                return self.dropDowns[0].selected
            
class SellPoint:
    def __init__(self, pos, name, rotation):
        self.x = pos[0]
        self.y = pos[1]
        self.name = name
        self.ogPrices = {
            "Wheat": 300,
            "Barley": 400,
            "Canola": 800,
            "Oat": 600
        }
        self.prices = {
            "Wheat": 300,
            "Barley": 400,
            "Canola": 800,
            "Oat": 600
        }
        self.demand = {
            "Wheat": 100,
            "Barley": 100,
            "Canola": 100,
            "Oat": 100
        }
        self.silo = Silo(self.x, self.y, rotation)

class Window:
    def __init__(self):
        self.screen = pg.display.set_mode((int(2340/ZOOM), int(1080/ZOOM)))
        pg.display.set_caption("Farm CEO")
        self.mapScale = 1080/ZOOM/609
        self.map = pg.transform.scale(pg.image.load(f"{IMAGES_PATH}/map.png").convert_alpha(), (int(969*self.mapScale), int(609*self.mapScale)))
        self.vehiclesDict = json.loads(open(f'{ASSETS_PATH}/vehicles.json', 'r').read())
        self.toolsDict = json.loads(open(f'{ASSETS_PATH}/tools.json', 'r').read())
        self.save = json.loads(open(f'{ASSETS_PATH}/save.json', 'r').read())
        self.menu = Menu(2340/ZOOM-969*self.mapScale, 1080/ZOOM, self.vehiclesDict, self.toolsDict)
        self.farm = Farm()
        self.farm.silo.storage = self.save['siloFill']
        self.tractors = []
        self.tools = []
        self._initEquipment()
        #self.tractors = [Tractor(self.farm.x+50/ZOOM, self.farm.y+150/ZOOM, self.vehiclesDict['Tractors']['Case IH']['Puma 210'], "Case IH", "Puma 210") for i in range(2)]
        #self.tools = [Tool(self.farm.x+100/ZOOM, self.farm.y+100/ZOOM, "Cultivator", self.toolsDict['Cultivators']['Case IH']['490'], "Case IH", "490")]
        #self.tools.append(Tool(self.farm.x+100/ZOOM, self.farm.y+100/ZOOM, "Seeder", self.toolsDict['Seeders']['John Sheerer']['Combine 14ft'], "John Sheerer", "Combine 14ft"))
        #self.tools.append(Tool(self.farm.x+100/ZOOM, self.farm.y+100/ZOOM, "Cultivator", self.toolsDict['Cultivators']['Landoll']['Verticle Tillage'], "Landoll", "Verticle Tillage"))
        #self.tools.append(Tool(self.farm.x+100/ZOOM, self.farm.y+100/ZOOM, "Trailer", self.toolsDict['Trailers']['Marshall']['QM-12'], "Marshall", "QM-12"))
        #self.tractors.append(Header(self.farm.x+50/ZOOM, self.farm.y+150/ZOOM, self.vehiclesDict['Harvesters']['Case IH']['2388'], "Case IH", "2388"))
        #self.money = 20000*1000
        #self.xp = 1000*1000
        self.dt = 0
        self.money = self.save['money']
        self.xp = self.save['xp']
        self.popup = None
        self.paused = False
        self.font100 = pg.font.SysFont("Arial", int(100/ZOOM))
        self.font75 = pg.font.SysFont("Arial", int(75/ZOOM))
        loadingFont = self.font100.render("Farm CEO (Dev) Loading...", True, (0, 0, 255))
        loading = self.screen.blit(loadingFont, (self.screen.get_width()/2-loadingFont.get_width()/2, self.screen.get_height()/2-loadingFont.get_height()/2))
        pg.display.update(loading)
        for paddock in range(1, 10):
            PADDOCK_STATES[paddock] = self.save['paddockStates'][str(paddock)]
            PADDOCK_OWNERS[paddock] = self.save['paddockOwners'][str(paddock)]
            self.setPaddockState(paddock, PADDOCK_STATES[paddock])
            self.screen.fill((0,0,0))
            loadingFont = self.font100.render(f"Farm CEO (Dev) Loading... {int(round(paddock/9*100, 0))}%", True, (0, 0, 255))
            loading = self.screen.blit(loadingFont, (self.screen.get_width()/2-loadingFont.get_width()/2, self.screen.get_height()/2-loadingFont.get_height()/2))
            pg.display.update(loading)
        #self.sellPoints = [SellPoint(SELL_POINT_LOCATIONS["Green Spring Bakery"], "Green Spring Bakery", 0), SellPoint(SELL_POINT_LOCATIONS["Green Spring Mill"], "Green Spring Mill", 180), SellPoint(SELL_POINT_LOCATIONS["Green Spring Trades"], "Green Spring Trades", 180)]
        self.sellPoints = []
        for i in range(3):
            key = list(self.save['sellPoints'].keys())[i]
            newSellPoint = SellPoint(SELL_POINT_LOCATIONS[key], key, SELL_POINT_ROTATIONS[key])
            newSellPoint.prices = self.save['sellPoints'][key]['prices']
            newSellPoint.demand = self.save['sellPoints'][key]['demand']
            self.sellPoints.append(newSellPoint)
            
        self.focusedTractor = None
        self.xpIcon = pg.transform.scale(pg.image.load(f'{IMAGES_PATH}/xp.png').convert_alpha(), (52/ZOOM, 52/ZOOM))
        self.moneyIcon = pg.transform.scale(pg.image.load(f'{IMAGES_PATH}/currency.png').convert_alpha(), (52/ZOOM, 52/ZOOM))
        self.overlayFont = pg.font.SysFont("arial", int(45/ZOOM))

    def _initEquipment(self):
        for vehicle in list(self.save['tractors'].values()):
            if vehicle['header']: newVehicle = Header(self.farm.x+50/ZOOM, self.farm.y+150/ZOOM, self.vehiclesDict['Harvesters'][vehicle['brand']][vehicle['model']], vehicle['brand'], vehicle['model'])
            else: newVehicle = Tractor(self.farm.x+50/ZOOM, self.farm.y+150/ZOOM, self.vehiclesDict['Tractors'][vehicle['brand']][vehicle['model']], vehicle['brand'], vehicle['model'])
            newVehicle.fuel = vehicle['fuel']
            self.tractors.append(newVehicle)

        for tool in list(self.save['tools'].values()): self.tools.append(Tool(self.farm.x+100/ZOOM, self.farm.y+100/ZOOM, tool['toolType'][:-1], self.toolsDict[tool['toolType']][tool['brand']][tool['model']], tool['brand'], tool['model']))

    def setPaddockState(self, paddock, state):
        PADDOCK_STATES[paddock] = state
        newColor = STATE_COLORS[state]
        paddockRects = PADDOCK_RECTS[paddock]
        for rect in paddockRects:
            # THIS MUST BE CHANGED IN THE EVENT OF ADDING CROP TEXTURES
            # instead of rendering polygons with an opacity of 0 we render them with the texture
            for y in range(int(rect[1]), int(rect[1]+rect[3])):
                for x in range(int(rect[0]-self.menu.width), int(rect[0]+rect[2]-self.menu.width)):
                    if tuple((self.map.get_at((x, y))[0], self.map.get_at((x, y))[1], self.map.get_at((x, y))[2])) in STATE_COLORS_LIST:
                        self.map.set_at((x, y), newColor)
                    #else:
                    #    self.map.set_at((x, y), (255, 0, 0))
        #PADDOCK_POLYS[paddock] = pg.Surface(PADDOCK_SIZES[paddock], pg.SRCALPHA).convert_alpha()
        PADDOCK_POLYS_RENDERED[paddock] = pg.draw.polygon(self.screen, (0, 0, 0), PADDOCKS[paddock])

    def createPopup(self, width, height, color, highlightColor, popupType, additionals):
        self.popup = Popup(2340/ZOOM/2, 1080/ZOOM/2, width, height, color, highlightColor, popupType, additionals)

    def _saveGame(self):
        saveData = {
            "siloFill": self.farm.silo.storage,
            "sellPoints": {},
            "paddockStates": {},
            "paddockOwners": {},
            "tractors": {},
            "tools": {},
            "money": self.money,
            "xp": self.xp
        }

        for sellPoint in self.sellPoints:
            saveData["sellPoints"][sellPoint.name] = {'prices': sellPoint.prices, 'demand': sellPoint.demand}

        for pdk in PADDOCK_STATES:
            saveData["paddockStates"][str(pdk)] = PADDOCK_STATES[pdk]
            saveData["paddockOwners"][str(pdk)] = PADDOCK_OWNERS[pdk]

        for vehicle in self.tractors:
            saveData["tractors"][str(self.tractors.index(vehicle))] = {
                "header": vehicle.header,
                "brand": vehicle.brand,
                "model": vehicle.name,
                "fuel": vehicle.fuel
            }

        for tool in self.tools:
            saveData["tools"][str(self.tools.index(tool))] = {
                "toolType": tool.toolType + 's',
                "brand": tool.brand,
                "model": tool.name
            }

        open(f'{ASSETS_PATH}/save.json', 'w').write(json.dumps(saveData))

    def _sleep(self):
        for pdk in PADDOCK_STATES:
            if PADDOCK_STATES[pdk] in (2, 3, 4): self.setPaddockState(pdk, PADDOCK_STATES[pdk] + 1)

    async def main(self):
        pdkCount = 0
        clock = pg.time.Clock()
        pressed = False
        clicked = False
        while 1:
            self.screen.fill((0,0,0))
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._saveGame()
                    pg.quit()
                    exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for button in self.menu.navBar:
                            if not button.clicked and pg.Rect(button.x, button.y, button.width, button.height).collidepoint(event.pos):
                                self.menu.selectedButton = self.menu.navBar.index(button)
                        
                        if pg.Rect(self.farm.sheds[0].x, self.farm.sheds[0].y, self.farm.sheds[0].width, self.farm.sheds[0].height).collidepoint(pg.mouse.get_pos()) and self.popup == None:
                            for vehicle in self.tractors:
                                if vehicle.task != None:
                                    self.createPopup(500/ZOOM, 250/ZOOM, (255, 255, 255), (63, 72, 204), "Warning", [f"Vehicles cannot be working!", "Check the guide for more info."])
                                    break

                            if self.popup == None: self.createPopup(500/ZOOM, 250/ZOOM, (255, 255, 255), (63, 72, 204), "Sleep", [f"Do you want to sleep?", "This will advance all crop states."])

                        pressed = True
                        clicked = True
                elif event.type == pg.MOUSEBUTTONUP:
                    if event.button == 1:
                        pressed = False
                
            pg.display.set_caption(f"Farm CEO  -  Fps: {clock.get_fps()}")

            equipment = []
            equipment.extend(self.tractors)
            grainGrid = [[], [], [], []]
            for item in self.farm.silo.storage: grainGrid[0].append(str(round(self.farm.silo.storage[item], 1)) + "T")
            for sellPoint in self.sellPoints:
                for item in sellPoint.prices: grainGrid[self.sellPoints.index(sellPoint)+1].append('$' + str(round(sellPoint.prices[item], 1)) + '/T')
            self.menu.draw(self.screen, equipment, self.tools, clicked, pressed, pg.mouse.get_rel(), grainGrid, self.money, self.xp)
            self.screen.blit(self.map, (2340/ZOOM-969*self.mapScale, 0))

            if DEBUG:
                for road in ROADS:
                    for i in range(len(ROADS[road])-1):
                        pg.draw.line(self.screen, (255, 0, 0), ROADS[road][i], ROADS[road][i+1])

            if DEBUG:
                for pdk in PADDOCKS:
                    if len(PADDOCKS[pdk]) == 0: continue
                    for i in range(len(PADDOCKS[pdk])-1):
                        pg.draw.line(self.screen, (0, 0, 255), PADDOCKS[pdk][i], PADDOCKS  [pdk][i+1])
                    #PADDOCK_POLYS_RENDERED[pdk] = pg.draw.polygon(PADDOCK_POLYS[pdk], (STATE_COLORS[PADDOCK_STATES[pdk]][0], STATE_COLORS[PADDOCK_STATES[pdk]][1], STATE_COLORS[PADDOCK_STATES[pdk]][2], 0), PADDOCKS[pdk])
                    #self.screen.blit(PADDOCK_POLYS[pdk], (0, 0))

            for paddock in PADDOCK_LINES:
                for line in PADDOCK_LINES[paddock]:
                    pg.draw.rect(self.screen, line[0], (line[1], line[2], line[3], line[4]*2))

            for pdkCenter in PADDOCK_CENTERS:
                if PADDOCK_OWNERS[pdkCenter] == 0: self.screen.blit(self.font75.render(str(pdkCenter), True, (255, 255, 255)), PADDOCK_CENTERS[pdkCenter])
                else: self.screen.blit(self.font75.render(str(pdkCenter), True, (0, 0, 255)), PADDOCK_CENTERS[pdkCenter])

            # Machinary render in between the 2 silo parts (grid first)
            self.farm.silo.draw(self.screen, True)
            for sellPoint in self.sellPoints: sellPoint.silo.draw(self.screen, True)
            for tractor in self.tractors:
                if not tractor.inShed: tractor.draw(self.screen, self.sellPoints, self.dt)
            for tool in self.tools:
                if tool.on and math.sqrt(abs((tool.y-tool.lastPaint[1])**2+(tool.x-tool.lastPaint[0])**2)) > tool.rect.width:
                    tool.lastPaint = (tool.x, tool.y)
                    if tool.toolType == "Cultivator" or tool.toolType == "Seeder": PADDOCK_LINES[tool.paddock].append((STATE_COLORS[TOOL_TYPES_STATES[tool.toolType]], tool.x, tool.y, tool.rect.width, tool.rect.height))
                if not tool.inShed: tool.draw(self.screen)
            self.farm.silo.draw(self.screen, False)
            for sellPoint in self.sellPoints: sellPoint.silo.draw(self.screen, False)
            self.farm.draw(self.screen)

            self.screen.blit(self.xpIcon, (int(2340/ZOOM)-350, 25/ZOOM))
            self.screen.blit(self.overlayFont.render(str(int(round(self.xp/1000, 0))), True, (0, 0, 0)), (int(2340/ZOOM)-300, 25/ZOOM))
            self.screen.blit(self.moneyIcon, (int(2340/ZOOM)-250, 25/ZOOM))
            self.screen.blit(self.overlayFont.render(str(f"{self.money:,}"), True, (0, 0, 0)), (int(2340/ZOOM)-200, 25/ZOOM))

            if self.popup != None:
                status = self.popup.draw(self.screen, clicked, pg.mouse.get_pos())
                if type(status) == int:
                    if self.farm.silo.storage[CROP_TYPES[status]] == 0:
                        self.createPopup(500/ZOOM, 250/ZOOM, (255, 255, 255), (63, 72, 204), "Warning", [f"The silo does not contain any {CROP_TYPES[status]}!", "Check the guide for more info."])
                        self.focusedTractor = None
                    else:
                        self.focusedTractor.tool.fillType = CROP_TYPES[status]
                        self.focusedTractor.tool.fill = min(self.focusedTractor.tool.storage, self.farm.silo.storage[CROP_TYPES[status]])
                        self.farm.silo.storage[CROP_TYPES[status]] -= self.focusedTractor.tool.fill
                        self.focusedTractor.tool.inShed = False
                        self.focusedTractor.stringTask = f"Driving to paddock {self.focusedTractor.task}"
                        self.focusedTractor.inShed = False
                        self.focusedTractor.path = ROADS[PADDOCK_ROUTES[self.focusedTractor.task]].copy()
                        self.focusedTractor.path.reverse()
                        self.focusedTractor.path.append(PADDOCK_ENTRYS[self.focusedTractor.task])
                        self.focusedTractor.headingToPdk = True
                        self.focusedTractor = None
                        self.status = None
                        self.popup = None
                elif status == None: pass
                elif status == "exit": self.popup = None
                elif status == "sleep":
                    self.popup = None
                    self._sleep()
                elif status[0] == "hdr":
                    for tractor in self.tractors:
                        if self.popup == None: break
                        if tractor.inShed == False: continue
                        if not tractor.header: continue
                        if tractor.name == self.popup.additionals[0].name:
                            ownedPdks = []
                            for allPaddocks in PADDOCK_OWNERS:
                                if PADDOCK_OWNERS[allPaddocks] == 1: ownedPdks.append(allPaddocks)
                            if PADDOCK_STATES[ownedPdks[status[1]]] != 5:
                                self.createPopup(500/ZOOM, 250/ZOOM, (255, 255, 255), (63, 72, 204), "Warning", ["You cannot harvest this paddock yet!", "Check the guide for more info."])
                                break
                            tractor.inShed = False
                            tractor.task = ownedPdks[status[1]]
                            tractor.stringTask = f"Driving to paddock {tractor.task}"
                            tractor.path = ROADS[PADDOCK_ROUTES[tractor.task]].copy()
                            tractor.path.reverse()
                            tractor.path.append(PADDOCK_ENTRYS[tractor.task])
                            tractor.headingToPdk = True
                            self.popup = None
                elif status[0] == "pdk":
                    for tractor in self.tractors:
                        if self.popup == None: break
                        if tractor.inShed == False: continue
                        if tractor.name == self.popup.additionals[0].name:
                            tractor.tool = status[1]
                            ownedPdks = []
                            for allPaddocks in PADDOCK_OWNERS:
                                if PADDOCK_OWNERS[allPaddocks] == 1: ownedPdks.append(allPaddocks)
                            if tractor.tool.toolType == "Seeder" and PADDOCK_STATES[ownedPdks[status[2]-1]] != 1:
                                tractor.tool = None
                                self.createPopup(500/ZOOM, 250/ZOOM, (255, 255, 255), (63, 72, 204), "Warning", ["You cannot seed this paddock yet!", "Check the guide for more info."])
                                break
                            if STATE_COLORS[PADDOCK_STATES[status[2]]] == STATE_COLORS[TOOL_TYPES_STATES[tractor.tool.toolType]]:
                                tractor.tool = None
                                self.createPopup(620/ZOOM, 250/ZOOM, (255, 255, 255), (63, 72, 204), "Warning", [f"This paddock has already been covered by this tool!", "Check the guide for more info."])
                                break
                            if tractor.tool.toolType == "Seeder":
                                self.popup = None
                                self.focusedTractor = tractor
                                self.focusedTractor.task = ownedPdks[status[2]-1]
                                self.createPopup(500/ZOOM, 250/ZOOM, (255, 255, 255), (63, 72, 204), "cropChoice", [])
                                break
                            else:
                                tractor.task = ownedPdks[status[2]-1]
                                tractor.tool.inShed = False
                                tractor.stringTask = f"Driving to paddock {tractor.task}"
                                tractor.inShed = False
                                tractor.path = ROADS[PADDOCK_ROUTES[tractor.task]].copy()
                                tractor.path.reverse()
                                tractor.path.append(PADDOCK_ENTRYS[tractor.task])
                                tractor.headingToPdk = True
                                self.popup = None
                            #self.setPaddockState(9, 4)
                else:
                    for tractor in self.tractors:
                        if self.popup == None: break
                        if tractor.inShed == False: continue
                        if tractor.name == self.popup.additionals[0].name:
                            if self.farm.silo.storage[CROP_TYPES[status[3]]] == 0:
                                self.createPopup(500/ZOOM, 250/ZOOM, (255, 255, 255), (63, 72, 204), "Warning", [f"The silo does not contain any {CROP_TYPES[status[3]]}!", "Check the guide for more info."])
                                break
                            tractor.tool = status[1]
                            tractor.tool.fillType = CROP_TYPES[status[3]]
                            tractor.tool.fill = min(tractor.tool.storage, self.farm.silo.storage[CROP_TYPES[status[3]]])
                            self.farm.silo.storage[CROP_TYPES[status[3]]] -= tractor.tool.fill
                            tractor.tool.inShed = False
                            tractor.task = SELL_POINTS[status[2]-1]
                            tractor.stringTask = f"Driving to {tractor.task}"
                            tractor.inShed = False
                            tractor.path.append((self.farm.silo.gridX, self.farm.silo.gridY))
                            tractor.path.append([180])
                            tractor.path.append(['sc']) # set cover
                            roadPath = ROADS[SELL_POINT_ROADS[tractor.task]].copy()
                            roadPath.reverse()
                            tractor.path.extend(roadPath.copy())
                            tractor.path.append((self.sellPoints[SELL_POINTS.index(tractor.task)].silo.gridX, self.sellPoints[SELL_POINTS.index(tractor.task)].silo.gridY))
                            tractor.path.append([180])
                            tractor.path.append(['rc']) # remove cover
                            tractor.path.append(['sf|0']) # set fill = 0
                            tractor.path.append(["tf"]) # to farm
                            tractor.path.extend(ROADS[SELL_POINT_ROADS[tractor.task]].copy())
                            tractor.path.append((1460/ZOOM+50/ZOOM, 368/ZOOM+150/ZOOM))
                            tractor.path.append(["end"]) # end
                            tractor.headingToPdk = None
                            self.popup = None

            if clicked:
                mx, my = (int(pg.mouse.get_pos()[0]), int(pg.mouse.get_pos()[1]))
                self.screen.set_at((mx, my), (255, 0, 0))
                #if (mx, my) not in PADDOCKS[9]:
                #    PADDOCKS[9].append((mx, my))
                #    print(PADDOCKS[9])
                #if (mx, my) not in PADDOCK_RECTS[22] and pdkCount == 0:
                #    pdkCount += 1
                #    PADDOCK_RECTS[22][0].append(mx)
                #    PADDOCK_RECTS[22][0].append(my)
                #    #print(mx, my)
                #elif (mx, my) not in PADDOCK_RECTS[22] and pdkCount == 1:
                #    pdkCount += 1
                #    PADDOCK_RECTS[22][0].append(mx-PADDOCK_RECTS[22][0][0])
                #elif (mx, my) not in PADDOCK_RECTS[22] and pdkCount == 2:
                #    pdkCount += 1
                #    PADDOCK_RECTS[22][0].append(my-PADDOCK_RECTS[22][0][1])
                #    print(tuple(PADDOCK_RECTS[22][0]))
            clicked = False
            pg.display.flip()
            self.dt = clock.tick(60)
            await asyncio.sleep(0)

if __name__ == "__main__":
    window = Window()
    #window.main()
    asyncio.run(window.main())
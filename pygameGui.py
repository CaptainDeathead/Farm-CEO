import pygame as pg

pg.init()

class Button:
    def __init__(self, x, y, width, height, color, selectedColor, textColor, text, size, radius, offset_x, offset_y, center=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.selectedColor = selectedColor
        self.textColor = textColor
        self.text = text
        self.radius = radius
        self.clicked = False
        self.font = pg.font.SysFont("Arial", size)
        self.size = size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.center = center

    def draw(self, screen):
        if self.clicked: pg.draw.rect(screen, self.selectedColor, (self.x, self.y, self.width, self.height), border_top_left_radius = self.radius[0], border_bottom_left_radius = self.radius[1], border_top_right_radius = self.radius[2], border_bottom_right_radius = self.radius[3])
        else: pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_top_left_radius = self.radius[0], border_bottom_left_radius = self.radius[1], border_top_right_radius = self.radius[2], border_bottom_right_radius = self.radius[3])
        rendered = self.font.render(str(self.text), True, self.textColor)
        if self.center: screen.blit(rendered, (self.x+self.width/2-rendered.get_width()/2, self.y+self.height/2-rendered.get_height()/2))
        else: screen.blit(rendered, (self.x + self.offset_x, self.y + self.offset_y))

class Table:
    def __init__(self, x, y, width, height, rows, collumns, color, selectedColor, fontSize, zoom=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rows = rows
        self.collumns = collumns
        self.color = color
        self.selectedColor = selectedColor
        self.segWidth = self.width / self.rows
        self.segHeight = self.width / self.collumns
        self.grid = [["" for x in range(self.rows)] for y in range(self.collumns)]
        self.font = pg.font.SysFont("Arail", fontSize)
        if zoom != None: self.lineWidth = max(1, int(5/zoom))
        else: self.lineWidth = 5

    def draw(self, screen):
        pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pg.draw.rect(screen, self.selectedColor, (self.x, self.y, self.segWidth, self.height))
        pg.draw.rect(screen, self.selectedColor, (self.x, self.y, self.width, self.segHeight))
        
        for x in range(1, self.rows): pg.draw.line(screen, (0, 0, 0), (self.x+self.segWidth*x, self.y), (self.x+self.segHeight*x, self.y+self.height), self.lineWidth)
        for y in range(1, self.rows): pg.draw.line(screen, (0, 0, 0), (self.x, self.y+self.segHeight*y), (self.x+self.width, self.y+self.segHeight*y), self.lineWidth)

        for y in range(self.collumns):
            for x in range(self.rows):
                screen.blit(self.font.render(str(self.grid[y][x]), True, (255, 255, 255)), (self.x+self.segWidth*x+self.segWidth/16, self.y+self.segHeight*y+self.segHeight/2.5))
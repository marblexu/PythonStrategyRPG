__author__ = 'marble_xu'

import pygame as pg
from .. import tool
from .. import constants as c

class Map():
    def __init__(self, width, height, grid):
        self.width = width
        self.height = height
        self.bg_map = [[0 for x in range(self.width)] for y in range(self.height)]
        self.entity_map = [[None for x in range(self.width)] for y in range(self.height)]
        self.active_entity = None
        self.select = None
        self.setupMapImage(grid)
        self.setupMouseImage()

    def setupMapImage(self, grid):
        self.grid_map = [[0 for x in range(self.width)] for y in range(self.height)]
        if grid is not None:
            for data in grid:
                x, y, type = data['x'], data['y'], data['type']
                self.grid_map[y][x] = type
        
        self.map_image = pg.Surface((self.width * c.REC_SIZE, self.height * c.REC_SIZE)).convert()
        self.rect = self.map_image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        for y in range(self.height):
            for x in range(self.width):
                type = self.grid_map[y][x]
                if type != c.MAP_EMPTY:
                    if c.MAP_HEXAGON:
                        base_x, base_y = tool.getHexMapPos(x, y)
                        self.map_image.blit(tool.GRID[type], (base_x, base_y))
                    else:
                        self.map_image.blit(tool.GRID[type], (x * c.REC_SIZE, y * c.REC_SIZE))
        self.map_image.set_colorkey(c.BLACK)

    def setupMouseImage(self):
        self.mouse_frames = []
        frame_rect = (0, 0, 25, 27)
        self.mouse_image = tool.get_image(tool.GFX[c.MOUSE], *frame_rect, c.BLACK, 1)
        self.mouse_rect = self.mouse_image.get_rect()
        pg.mouse.set_visible(False)

    def isValid(self, map_x, map_y):
        if c.MAP_HEXAGON:
            if map_y % 2 == 0:
                max_x = self.width
            else:
                max_x = self.width - 1
        else:
            max_x = self.width
        if (map_x < 0 or map_x >= max_x or
            map_y < 0 or map_y >= self.height):
            return False
        return True
    
    def isMovable(self, map_x, map_y):
        return (self.entity_map[map_y][map_x] == None and 
                self.grid_map[map_y][map_x] != c.MAP_STONE)

    def getMapIndex(self, x, y):
        if c.MAP_HEXAGON:
            return tool.getHexMapIndex(x, y)
        else:
            return (x//c.REC_SIZE, y//c.REC_SIZE)

    def getDistance(self, x1, y1, map_x2, map_y2):
        if c.MAP_HEXAGON:
            x2, y2 = tool.getHexMapPos(map_x2, map_y2)
            x2 += c.HEX_X_SIZE // 2
            y2 += c.HEX_Y_SIZE // 2
            distance = (abs(x1 - x2) + abs(y1 - y2))
        else:
            map_x1, map_y1 = self.getMapIndex(x1, y1)
            x2 = map_x2 * c.REC_SIZE + c.REC_SIZE//2
            y2 = map_y2 * c.REC_SIZE + c.REC_SIZE//2
            distance = (abs(x1 - x2) + abs(y1 - y2))
            if map_x1 != map_x2 and map_y1 != map_y2:
               distance -= c.REC_SIZE//2
        return distance

    def checkMouseClick(self, x, y):
        if self.active_entity is None:
            return False
        
        map_x, map_y = self.getMapIndex(x, y)
        if not self.isValid(map_x, map_y):
            return False

        entity = self.entity_map[map_y][map_x]
        if ((entity is None or entity == self.active_entity) and 
            self.active_entity.inRange(self, map_x, map_y)):
            self.active_entity.setDestination(map_x, map_y)
            return True
        elif entity is not None:
            if self.active_entity.isRemote():
                self.active_entity.setTarget(entity)
                return True
            elif self.select is not None:
                self.active_entity.setDestination(self.select[0], self.select[1], entity)
                return True
        return False

    def checkMouseMove(self, x, y):
        if self.active_entity is None:
            return False

        map_x, map_y = self.getMapIndex(x, y)
        if not self.isValid(map_x, map_y):
            return False
        
        self.select = None
        entity = self.entity_map[map_y][map_x]
        if ((self.isMovable(map_x, map_y) or entity == self.active_entity) and 
            self.active_entity.inRange(self, map_x, map_y)):
                self.bg_map[map_y][map_x] = c.BG_SELECT
        elif entity is not None:
            if entity.group_id != self.active_entity.group_id:
                if self.active_entity.isRemote():
                    self.bg_map[map_y][map_x] = c.BG_ATTACK
                else:
                    dir_list = tool.getAttackPositions(map_x, map_y)
                    res_list = []
                    for offset_x, offset_y in dir_list:
                        if self.isValid(map_x + offset_x, map_y + offset_y):
                            type = self.bg_map[map_y + offset_y][map_x + offset_x]
                            if type == c.BG_RANGE or type == c.BG_ACTIVE:
                                res_list.append((map_x + offset_x, map_y + offset_y))
                    if len(res_list) > 0:
                        min_dis = c.MAP_WIDTH
                        for tmp_x, tmp_y in res_list:
                            distance = self.getDistance(x, y, tmp_x, tmp_y)
                            if distance < min_dis:
                                min_dis = distance
                                res = (tmp_x, tmp_y)
                        self.bg_map[res[1]][res[0]] = c.BG_SELECT
                        self.bg_map[map_y][map_x] = c.BG_ATTACK
                        self.select = res

    def setEntity(self, map_x, map_y, value):
        self.entity_map[map_y][map_x] = value

    def drawMouseShow(self, surface):
        x, y = pg.mouse.get_pos()
        map_x, map_y = self.getMapIndex(x, y)
        if self.isValid(map_x, map_y):
            self.mouse_rect.x = x
            self.mouse_rect.y = y
            surface.blit(self.mouse_image, self.mouse_rect)

    def updateMap(self):
        for y in range(self.height):
            for x in range(self.width):
                self.bg_map[y][x] = c.BG_EMPTY
                if self.entity_map[y][x] is not None and self.entity_map[y][x].isDead():
                    self.entity_map[y][x] = None

        if self.active_entity is None or self.active_entity.state != c.IDLE:
            return
        map_x, map_y = self.active_entity.map_x, self.active_entity.map_y
        self.bg_map[map_y][map_x] = c.BG_ACTIVE
        
        for y in range(self.height):
            for x in range(self.width):
                if not self.isMovable(x,y) or not self.isValid(x,y):
                    continue
                if self.active_entity.inRange(self, x, y):
                    self.bg_map[y][x] = c.BG_RANGE
        mouse_x, mouse_y = pg.mouse.get_pos()
        self.checkMouseMove(mouse_x, mouse_y)

    def drawBackground(self, surface):
        if c.MAP_HEXAGON:
            return self.drawBackgroundHex(surface)

        pg.draw.rect(surface, c.LIGHTYELLOW, pg.Rect(0, 0, c.MAP_WIDTH, c.MAP_HEIGHT))
        
        for y in range(self.height):
            for x in range(self.width):
                if self.bg_map[y][x] == c.BG_EMPTY:
                    color = c.LIGHTYELLOW
                elif self.bg_map[y][x] == c.BG_ACTIVE:
                    color = c.SKY_BLUE
                elif self.bg_map[y][x] == c.BG_RANGE:
                    color = c.NAVYBLUE
                elif self.bg_map[y][x] == c.BG_SELECT:
                    color = c.GREEN
                elif self.bg_map[y][x] == c.BG_ATTACK:
                    color = c.GOLD
                pg.draw.rect(surface, color, (x * c.REC_SIZE, y * c.REC_SIZE, 
                        c.REC_SIZE, c.REC_SIZE))
        
        surface.blit(self.map_image, self.rect)

        for y in range(self.height):
            # draw a horizontal line
            start_pos = (0, 0 + c.REC_SIZE * y)
            end_pos = (c.MAP_WIDTH, c.REC_SIZE * y)
            pg.draw.line(surface, c.BLACK, start_pos, end_pos, 1)

        for x in range(self.width):
            # draw a horizontal line
            start_pos = (c.REC_SIZE * x, 0) 
            end_pos = (c.REC_SIZE * x, c.MAP_HEIGHT)
            pg.draw.line(surface, c.BLACK, start_pos, end_pos, 1)

    def calHeuristicDistance(self, x1, y1, x2, y2):
        if c.MAP_HEXAGON:
            dis_y = abs(y1 - y2)
            dis_x = abs(x1 - x2)
            half_y = dis_y // 2
            if dis_y >= dis_x:
                dis_x = 0
            else:
                dis_x -= half_y
            return (dis_y + dis_x)
        else:
            return abs(x1 - x2) + abs(y1 - y2)

    def drawBackgroundHex(self, surface):
        Y_LEN = c.HEX_Y_SIZE // 2
        X_LEN = c.HEX_X_SIZE // 2

        pg.draw.rect(surface, c.LIGHTYELLOW, pg.Rect(0, 0, c.MAP_WIDTH, c.MAP_HEIGHT))

        for y in range(self.height):
            for x in range(self.width):
                if self.bg_map[y][x] == c.BG_EMPTY:
                    color = c.LIGHTYELLOW
                elif self.bg_map[y][x] == c.BG_ACTIVE:
                    color = c.SKY_BLUE
                elif self.bg_map[y][x] == c.BG_RANGE:
                    color = c.NAVYBLUE
                elif self.bg_map[y][x] == c.BG_SELECT:
                    color = c.GREEN
                elif self.bg_map[y][x] == c.BG_ATTACK:
                    color = c.GOLD

                base_x, base_y = tool.getHexMapPos(x, y)
                points = [(base_x, base_y + Y_LEN//2 + Y_LEN), (base_x, base_y + Y_LEN//2),
                          (base_x + X_LEN, base_y), (base_x + X_LEN * 2, base_y + Y_LEN//2),
                          (base_x + X_LEN * 2, base_y + Y_LEN//2 + Y_LEN), (base_x + X_LEN, base_y + Y_LEN*2)]
                pg.draw.polygon(surface, color, points)

        surface.blit(self.map_image, self.rect)

        for y in range(self.height):
            for x in range(self.width):
                if y % 2 == 1 and x == self.width - 1:
                    continue
                base_x, base_y = tool.getHexMapPos(x, y)
                points = [(base_x, base_y + Y_LEN//2 + Y_LEN), (base_x, base_y + Y_LEN//2),
                          (base_x + X_LEN, base_y), (base_x + X_LEN * 2, base_y + Y_LEN//2),
                          (base_x + X_LEN * 2, base_y + Y_LEN//2 + Y_LEN), (base_x + X_LEN, base_y + Y_LEN*2)]
                pg.draw.lines(surface, c.BLACK, True, points)
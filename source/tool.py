__author__ = 'marble_xu'

import os
import json
from abc import abstractmethod
import pygame as pg
from . import constants as c

class State():
    def __init__(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.next = None
        self.persist = {}
    
    @abstractmethod
    def startup(self, current_time, persist):
        '''abstract method'''

    def cleanup(self):
        self.done = False
        return self.persist
    
    @abstractmethod
    def update(sefl, surface, keys, current_time):
        '''abstract method'''

class Control():
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = 60
        self.keys = pg.key.get_pressed()
        self.mouse_pos = None
        self.current_time = 0.0
        self.state_dict = {}
        self.state_name = None
        self.state = None
        self.game_info = {c.CURRENT_TIME:0.0,
                          c.LEVEL_NUM:1}
 
    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, self.game_info)

    def update(self):
        self.current_time = pg.time.get_ticks()
        if self.state.done:
            self.flip_state()
        self.state.update(self.screen, self.current_time, self.mouse_pos)
        self.mouse_pos = None
    
    def flip_state(self):
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, persist)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_pos = pg.mouse.get_pos()

    def main(self):
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)
        print('game over')

def get_image(sheet, x, y, width, height, colorkey, scale):
        image = pg.Surface([width, height])
        rect = image.get_rect()

        image.blit(sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(colorkey)
        image = pg.transform.scale(image,
                                   (int(rect.width*scale),
                                    int(rect.height*scale)))
        return image

def load_all_gfx(directory, colorkey=c.WHITE, accept=('.png', '.jpg', '.bmp', '.gif')):
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name] = img
    return graphics

def load_map_grid_image():
    grid_images = {}
    image_rect_dict = {c.MAP_STONE:(80, 48, 16, 16), c.MAP_GRASS:(80, 32, 16, 16)}
    for type, rect in image_rect_dict.items():
        grid_images[type] = get_image(GFX['tile'], *rect, c.BLACK, 3)
    return grid_images

def load_entiry_attr(file_path):
    attrs = {}
    f = open(file_path)
    data = json.load(f)
    f.close()
    for name, attr in data.items():
        attrs[name] = attr
    return attrs

def getMovePositions(x, y):
    if c.MAP_HEXAGON:
        if y % 2 == 0:
            offsets = [(-1, 0), (-1, -1), (0, -1), (1, 0), (-1, 1), (0, 1)]
        else:
            offsets = [(-1, 0), (0, -1), (1, -1), (1, 0), (0, 1), (1, 1)]
    else:
        # use four ways or eight ways to move
        offsets = [(-1,0), (0, -1), (1, 0), (0, 1)]
        #offsets = [(-1,0), (0, -1), (1, 0), (0, 1), (-1,-1), (1, -1), (-1, 1), (1, 1)]
    return offsets

def getAttackPositions(x, y):
    if c.MAP_HEXAGON:
        return getMovePositions(x, y)
    else:
        return [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1),(1,0), (1,1)]

def isNextToEntity(entity1, entity2):
    if c.MAP_HEXAGON:
        dir_list = getMovePositions(entity1.map_x, entity1.map_y)
        for offset_x, offset_y in dir_list:
            x, y = entity1.map_x + offset_x, entity1.map_y + offset_y
            if x == entity2.map_x and y == entity2.map_y:
                return True
    else:
        if abs(entity1.map_x - entity2.map_x) <= 1 and abs(entity1.map_y - entity2.map_y) <= 1:
            return True
    return False

def getHexMapPos(x, y):
    X_LEN = c.HEX_X_SIZE // 2
    Y_LEN = c.HEX_Y_SIZE // 2
    if y % 2 == 0:
        base_x = X_LEN * 2 * x
        base_y = Y_LEN * 3 * (y//2)
    else:
        base_x = X_LEN * 2 * x + X_LEN
        base_y = Y_LEN * 3 * (y//2) + Y_LEN//2 + Y_LEN
    return (base_x, base_y)

class Vector2d():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def minus(self, vec):
        return Vector2d(self.x - vec.x, self.y - vec.y)

    def crossProduct(self, vec):
        return (self.x * vec.y - self.y * vec.x)

def isInTriangle(x1, y1, x2, y2, x3, y3, x, y):
    A = Vector2d(x1, y1)
    B = Vector2d(x2, y2)
    C = Vector2d(x3, y3)
    P = Vector2d(x, y)
    PA = A.minus(P)
    PB = B.minus(P)
    PC = C.minus(P)
    t1 = PA.crossProduct(PB)
    t2 = PB.crossProduct(PC)
    t3 = PC.crossProduct(PA)
    if (t1 * t2 >= 0) and (t1 * t3 >= 0):
        return True
    return False

def getHexMapIndex(x, y):
    X_LEN = c.HEX_X_SIZE // 2
    Y_LEN = c.HEX_Y_SIZE // 2
    tmp_x, offset_x = divmod(x, c.HEX_X_SIZE)
    tmp_y, offset_y = divmod(y, Y_LEN * 3)
    map_x, map_y = 0, 0
    if offset_y <= (Y_LEN + Y_LEN//2):
        if offset_y >= Y_LEN//2:
            map_x, map_y = tmp_x, tmp_y * 2
        else:
            triangle_list = [(0, 0, 0, Y_LEN//2, X_LEN, 0),
                             (0, Y_LEN//2, X_LEN, 0, c.HEX_X_SIZE, Y_LEN//2),
                             (X_LEN, 0, c.HEX_X_SIZE, 0, c.HEX_X_SIZE, Y_LEN//2)]
            map_list = [(tmp_x - 1, tmp_y * 2 -1), (tmp_x, tmp_y * 2), (tmp_x, tmp_y * 2 -1)]
            for i, data in enumerate(triangle_list):
                if isInTriangle(*data, offset_x, offset_y):
                    map_x, map_y = map_list[i]
                    break
    elif offset_y >= c.HEX_Y_SIZE:
        if offset_x <= X_LEN:
            map_x, map_y = tmp_x - 1, tmp_y * 2 + 1
        else:
            map_x, map_y = tmp_x, tmp_y *2 + 1
    else:
        triangle_list = [(0, Y_LEN + Y_LEN//2, 0, c.HEX_Y_SIZE, X_LEN, c.HEX_Y_SIZE),
                         (0, Y_LEN + Y_LEN//2, X_LEN, c.HEX_Y_SIZE, c.HEX_X_SIZE, Y_LEN + Y_LEN//2),
                         (X_LEN, c.HEX_Y_SIZE, c.HEX_X_SIZE, Y_LEN + Y_LEN//2, c.HEX_X_SIZE, c.HEX_Y_SIZE)]
        map_list = [(tmp_x - 1, tmp_y * 2 + 1), (tmp_x, tmp_y * 2), (tmp_x, tmp_y *2 + 1)]
        for i, data in enumerate(triangle_list):
            if isInTriangle(*data, offset_x, offset_y):
                map_x, map_y = map_list[i]
                break
    if map_x == 0 and map_y == 0:
        print('pos[%d, %d](%d, %d) base[%d, %d] off[%d, %d] ' % (map_x, map_y, x, y, tmp_x, tmp_y, offset_x, offset_y))
    return (map_x, map_y)

pg.init()
pg.display.set_caption(c.ORIGINAL_CAPTION)
SCREEN = pg.display.set_mode(c.SCREEN_SIZE)

GFX = load_all_gfx(os.path.join("resources","graphics"))
ATTR = load_entiry_attr(os.path.join('source', 'data', 'entity.json'))
GRID = load_map_grid_image()
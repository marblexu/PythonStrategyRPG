__author__ = 'marble_xu'

import os
import json
import pygame as pg
from .. import tool
from .. import constants as c
from .. import AStarSearch
from .. import gameAI
from ..component import map, entity


class Level(tool.State):
    def __init__(self):
        tool.State.__init__(self)
    
    def startup(self, current_time, persist):
        self.game_info = persist
        self.persist = self.game_info
        self.game_info[c.CURRENT_TIME] = current_time
        
        self.loadMap()
        grid = self.map_data[c.MAP_GRID] if c.MAP_GRID in self.map_data else None
        self.map = map.Map(c.GRID_X_LEN, c.GRID_Y_LEN, grid)
        self.setupGroup()
        self.state = c.IDLE
    
    def loadMap(self):
        map_file = 'level_' + str(self.game_info[c.LEVEL_NUM]) + '.json'
        file_path = os.path.join('source', 'data', 'map', map_file)
        f = open(file_path)
        self.map_data = json.load(f)
        f.close()
    
    def setupGroup(self):
        self.group1 = entity.EntityGroup(0)
        self.group1.createEntity(self.map_data[c.GROUP1], self.map)
        self.group2 = entity.EntityGroup(1)
        self.group2.createEntity(self.map_data[c.GROUP2], self.map)

    def getActiveEntity(self):
        entity1 = self.group1.getActiveEntity()
        entity2 = self.group2.getActiveEntity()
        if entity1 and entity2:
            if entity1.attr.speed >= entity2.attr.speed:
                entity, group = entity1, self.group1
            else:
                entity, group = entity2, self.group2
        elif entity1:
            entity, group = entity1, self.group1
        elif entity2:
            entity, group = entity2, self.group2
        else:
            return None
        return (entity, group)
        
    def update(self, surface, current_time, mouse_pos):
        self.current_time = self.game_info[c.CURRENT_TIME] = current_time
        if self.state == c.IDLE:
            if self.group1.isEmpty() or self.group2.isEmpty():
                self.done = True
                if self.group1.isEmpty():
                    self.game_info[c.LEVEL_NUM] += 1
                    self.next = c.LEVEL
                    print('Group 1 win!')
                else:
                    print('Group 0 win!')
            else:
                result = self.getActiveEntity()
                if result is not None:
                    entity, group = result
                    self.map.active_entity = entity
                    group.consumeEntity()
                    self.state = c.SELECT
                else:
                    self.group1.nextTurn()
                    self.group2.nextTurn()
        elif self.state == c.SELECT:
            if self.map.active_entity.group_id == 0:
                (map_x, map_y, enemy) = gameAI.getAction(self.map.active_entity, self.map, self.group2.group)
                print('pos(%d, %d)' % (map_x, map_y))
                self.map.active_entity.setDestination(map_x, map_y, enemy)
                self.state = c.ENTITY_ACT
            else:
                self.map.updateMap()
                if mouse_pos is not None:
                    self.mouseClick(mouse_pos[0], mouse_pos[1])
        elif self.state == c.ENTITY_ACT:
            self.map.updateMap()
            self.group1.update(self.game_info, self.map)
            self.group2.update(self.game_info, self.map)
            if self.map.active_entity.state == c.IDLE:
                self.state = c.IDLE
        self.draw(surface)

    def mouseClick(self, mouse_x, mouse_y):
        if self.state == c.SELECT:
            if self.map.checkMouseClick(mouse_x, mouse_y):
                self.state = c.ENTITY_ACT
        
    def draw(self, surface):
        self.map.drawBackground(surface)
        self.group1.draw(surface)
        self.group2.draw(surface)
        self.map.drawMouseShow(surface)
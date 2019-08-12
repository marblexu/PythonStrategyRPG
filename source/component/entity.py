__author__ = 'marble_xu'

import pygame as pg
from .. import tool
from .. import constants as c
from .. import AStarSearch
from . import map

class FireBall():
    def __init__(self, x, y, enemy, hurt):
        # first 3 Frames are flying, last 4 frams are exploding
        frame_rect = (0,0,14,14)
        self.image = tool.get_image(tool.GFX[c.FIREBALL], *frame_rect, c.BLACK, c.SIZE_MULTIPLIER)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.enemy = enemy
        self.hurt = hurt
        self.done = False
        self.calVelocity()
    
    def calVelocity(self):
        #print('calVelocity: x:', self.enemy.rect.centerx, self.rect.centerx, 'y:', self.enemy.rect.centery,self.rect.centery)
        dis_x = self.enemy.rect.centerx - self.rect.centerx
        dis_y = self.enemy.rect.centery - self.rect.centery
        distance = (dis_x ** 2 + dis_y ** 2) ** 0.5
        self.x_vel = (dis_x * 10)/distance
        self.y_vel = (dis_y * 10)/distance
        
    def update(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        if abs(self.rect.x - self.enemy.rect.x) + abs(self.rect.y - self.enemy.rect.y) < 25:
            self.enemy.setHurt(self.hurt)
            self.done = True
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class EntityAttr():
    def __init__(self, data):
        self.max_health = data[c.ATTR_HEALTH]
        self.range = data[c.ATTR_RANGE]
        self.damage = data[c.ATTR_DAMAGE]
        self.attack = data[c.ATTR_ATTACK]
        self.defense = data[c.ATTR_DEFENSE]
        self.speed = data[c.ATTR_SPEED]
        if data[c.ATTR_REMOTE] == 0:
            self.remote = False
        else:
            self.remote = True
    
    def getHurt(self, enemy_attr):
        offset = 0
        if self.attack > enemy_attr.defense:
            offset = (self.attack - enemy_attr.defense) * 0.05
        elif self.attack < enemy_attr.defense:
            offset = (self.attack - enemy_attr.defense) * 0.025
        hurt = int(self.damage * (1 + offset))
        return hurt

class Entity():
    def __init__(self, group, sheet, map_x, map_y, data):
        self.group = group
        self.group_id = group.group_id
        self.map_x = map_x
        self.map_y = map_y
        self.frames = []
        self.frame_index = 0
        self.loadFrames(sheet)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.getRectPos(map_x, map_y)
        
        self.attr = EntityAttr(data)
        self.health = self.attr.max_health
        self.weapon = None
        self.enemy = None
        self.state = c.IDLE
        self.animate_timer = 0.0
        self.current_time = 0.0
        self.move_speed = c.MOVE_SPEED
    
    def getRectPos(self, map_x, map_y):
        if c.MAP_HEXAGON:
            base_x, base_y = tool.getHexMapPos(map_x, map_y)
            return (base_x + 4, base_y + 6)
        else:
            return(map_x * c.REC_SIZE + 5, map_y * c.REC_SIZE + 8)

    def getRecIndex(self, x, y):
        if c.MAP_HEXAGON:
            x += c.HEX_X_SIZE // 2 - 4
            y += c.HEX_Y_SIZE // 2 - 6
            map_x, map_y = tool.getHexMapIndex(x, y)
        else:
            map_x, map_y = (x//c.REC_SIZE, y//c.REC_SIZE)
        return (map_x, map_y)

    def loadFrames(self, sheet):
        frame_rect_list = [(64, 0, 32, 32), (96, 0, 32, 32)]
        for frame_rect in frame_rect_list:
            self.frames.append(tool.get_image(sheet, *frame_rect, 
                            c.BLACK, c.SIZE_MULTIPLIER))
        
    def setDestination(self, map_x, map_y, enemy=None):
        self.dest_x, self.dest_y = self.getRectPos(map_x, map_y)
        self.next_x, self.next_y = self.rect.x, self.rect.y
        self.enemy = enemy
        self.state = c.WALK
    
    def setTarget(self, enemy):
        self.enemy = enemy
        self.state = c.ATTACK

    def getHealthRatio(self):
        if self.health > 0:
            return self.health / self.attr.max_health
        else:
            return 0
    
    def isDead(self):
        return self.health <= 0
    
    def isRemote(self):
        return self.attr.remote

    def inRange(self, map, map_x, map_y):
        location = AStarSearch.AStarSearch(map, (self.map_x, self.map_y), (map_x, map_y))
        if location is not None:
            _, _, distance = AStarSearch.getFirstStepAndDistance(location)
            if distance <= self.attr.range:
                return True
        return False
    
    def putHurt(self, enemy):
        hurt = self.attr.getHurt(enemy.attr)
        enemy.setHurt(hurt)

    def setHurt(self, damage):
        self.health -= damage
        if self.isDead():
            self.group.removeEntity(self)
    
    def shoot(self, enemy):
        hurt = self.attr.getHurt(enemy.attr)
        self.weapon = FireBall(*self.rect.center, self.enemy, hurt)
     
    def walkToDestination(self, map):
        if self.rect.x == self.next_x and self.rect.y == self.next_y:
            source = self.getMapIndex(self.rect.x, self.rect.y)
            dest = self.getMapIndex(self.dest_x, self.dest_y)
            location = AStarSearch.AStarSearch(map, source, dest)
            if location is not None:
                map_x, map_y, _ = AStarSearch.getFirstStepAndDistance(location)
                self.next_x, self.next_y = self.getRectPos(map_x, map_y)
            else:
                self.state = c.IDLE

        if c.MAP_HEXAGON and self.rect.x != self.next_x and self.rect.y != self.next_y:
            self.rect.x += self.move_speed if self.rect.x < self.next_x else -self.move_speed
            self.rect.y += self.move_speed if self.rect.y < self.next_y else -self.move_speed
        elif self.rect.x != self.next_x:
            self.rect.x += self.move_speed if self.rect.x < self.next_x else -self.move_speed
        elif self.rect.y != self.next_y:
            self.rect.y += self.move_speed if self.rect.y < self.next_y else -self.move_speed

    def update(self, game_info, map):
        self.current_time = game_info[c.CURRENT_TIME]
        if self.state == c.WALK:
            if (self.current_time - self.animate_timer) > 250:
                if self.frame_index == 0:
                    self.frame_index = 1
                else:
                    self.frame_index = 0
                self.animate_timer = self.current_time

            if self.rect.x != self.dest_x or self.rect.y != self.dest_y:
                self.walkToDestination(map)
            else:
                map.setEntity(self.map_x, self.map_y, None)
                self.map_x, self.map_y = self.getRecIndex(self.dest_x, self.dest_y)
                map.setEntity(self.map_x, self.map_y, self)
                if self.enemy is None:
                    self.state = c.IDLE
                else:
                    self.state = c.ATTACK
        elif self.state == c.ATTACK:
            if self.attr.remote:
                if self.weapon is None:
                    self.shoot(self.enemy)
                else:
                    self.weapon.update()
                    if self.weapon.done:
                        self.weapon = None
                        self.enemy = None
                        self.state = c.IDLE
            else:
                self.putHurt(self.enemy)
                self.enemy = None
                self.state = c.IDLE
        
        if self.state == c.IDLE:
            self.frame_index = 0

    def draw(self, surface):
        self.image = self.frames[self.frame_index]
        surface.blit(self.image, self.rect)
        width = self.rect.width * self.getHealthRatio()
        height = 5
        pg.draw.rect(surface, c.RED, pg.Rect(self.rect.left, self.rect.top - height - 1, width, height))
        
        if self.weapon is not None:
            self.weapon.draw(surface)

class EntityGroup():
    def __init__(self, group_id):
        self.group = []
        self.group_id =  group_id
        self.entity_index = 0

    def createEntity(self, entity_list, map):
        for data in entity_list:
            entity_name, map_x, map_y = data['name'], data['x'], data['y']
            if map_x < 0:
                map_x = c.GRID_X_LEN + map_x
            if map_y < 0:
                map_y = c.GRID_Y_LEN + map_y
            
            entity = Entity(self, tool.GFX[entity_name], map_x, map_y, tool.ATTR[entity_name])
            self.group.append(entity)
            map.setEntity(map_x, map_y, entity)
        
        #self.group = sorted(self.group, key=lambda x:x.attr.speed, reverse=True)
    
    def removeEntity(self, entity):
        for i in range(len(self.group)):
            if self.group[i] == entity:
                if (self.entity_index > i or
                    (self.entity_index >= len(self.group) - 1)):
                    self.entity_index -= 1
        self.group.remove(entity)
    
    def isEmpty(self):
        if len(self.group) == 0:
            return True
        return False

    def nextTurn(self):
        self.entity_index = 0

    def getActiveEntity(self):
        if self.entity_index >= len(self.group):
            entity = None
        else:
            entity = self.group[self.entity_index]
        return entity

    def consumeEntity(self):
        self.entity_index += 1

    def update(self, game_info, map):
        for entity in self.group:
            entity.update(game_info, map)

    def draw(self, surface):
        for entity in self.group:
            entity.draw(surface)
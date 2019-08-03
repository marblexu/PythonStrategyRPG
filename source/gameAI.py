__author__ = 'marble_xu'

from .component import map
from . import AStarSearch

class EnemyInfo():
    def __init__(self, enemy):
        self.enemy = enemy
        self.range_num = 100
        self.kill_time = 1000
        self.remote = False
         
def getAction(entity, map, enemy_group):
    def getDestination(entity, map, enemy):
        dir_list = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1),(1,0), (1,1)]
        best_pos = None
        min_dis = 0
        for offset_x, offset_y in dir_list:
            x, y = enemy.map_x + offset_x, enemy.map_y + offset_y
            if map.isValid(x, y) and map.isMovable(x, y):
                distance = AStarSearch.getAStarDistance(map, (entity.map_x, entity.map_y), (x, y))
                if distance is None:
                    continue
                if best_pos is None:
                    best_pos = (x, y)
                    min_dis =  distance
                elif distance < min_dis:
                    best_pos = (x, y)
                    min_dis =  distance
        return best_pos

    def getEnemyInfo(info_list, entity, enemy, destination):
        enemyinfo = EnemyInfo(enemy)
        location = AStarSearch.AStarSearch(map, (entity.map_x, entity.map_y), destination)
        _, _, distance = AStarSearch.getFirstStepAndDistance(location)
        
        print('entity(%d, %d), dest(%d, %d) location(%d, %d) distance:%d' % 
            (entity.map_x, entity.map_y, destination[0], destination[1], location.x, location.y, distance))
        
        if distance == 0:
            enemyinfo.range_num = 0
        else:
            enemyinfo.range_num = (distance - 1) // entity.attr.range
        enemyinfo.location = location
        enemyinfo.distance = distance
        
        hurt = entity.attr.getHurt(enemy.attr)
        enemyinfo.kill_time = (enemy.health-1) // hurt
        
        enemyinfo.remote = enemy.attr.remote
        info_list.append(enemyinfo)
    
    info_list = []
    best_info = None
    for enemy in enemy_group:
        if abs(entity.map_x - enemy.map_x) <= 1 and abs(entity.map_y - enemy.map_y) <= 1:
            print('entity(%d,%d) next to enemy(%d, %d)' % (entity.map_x, entity.map_y, enemy.map_x, enemy.map_y))
            destination = (entity.map_x, entity.map_y)
        else:
            destination = getDestination(entity, map, enemy)
        if destination is not None:
            getEnemyInfo(info_list, entity, enemy, destination)

    for info in info_list:
        if best_info == None:
            best_info = info
        else:
            if info.range_num < best_info.range_num:
                best_info = info
            elif info.range_num == best_info.range_num:
                if info.range_num == 0:
                    if info.kill_time < best_info.kill_time:
                        best_info = info
                    elif info.kill_time == best_info.kill_time:
                        if info.remote == True and best_info.remote == False:
                            best_info = info
                        elif info.distance < best_info.distance:
                            best_info = info
                else:
                    if info.distance < best_info.distance:
                        best_info = info
    
    if best_info.range_num == 0:
        return (best_info.location.x, best_info.location.y, best_info.enemy)
    elif best_info.range_num == 1:
        range = entity.attr.range
        x, y = AStarSearch.getPosInRange(best_info.location, range)
        return (x, y, None)
    else:
        range = best_info.distance - entity.attr.range
        x, y = AStarSearch.getPosInRange(best_info.location, range)
        return (x, y, None)
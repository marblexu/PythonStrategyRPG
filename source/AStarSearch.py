__author__ = 'marble_xu'

from .component import map

class SearchEntry():
    def __init__(self, x, y, g_cost, f_cost=0, pre_entry=None):
        self.x = x
        self.y = y
        # cost move form start entry to this entry
        self.g_cost = g_cost
        self.f_cost = f_cost
        self.pre_entry = pre_entry
    
    def getPos(self):
        return (self.x, self.y)


def AStarSearch(map, source, dest):
    def getNewPosition(map, locatioin, offset):
        x,y = (location.x + offset[0], location.y + offset[1])
        if not map.isValid(x, y) or not map.isMovable(x, y):
            return None
        return (x, y)
        
    def getPositions(map, location):
        offsets = map.getMovePositions(location.x, location.y)
        poslist = []
        for offset in offsets:
            pos = getNewPosition(map, location, offset)
            if pos is not None:
                poslist.append(pos)
        return poslist
    
    # imporve the heuristic distance more precisely in future
    def calHeuristic(pos, dest):
        return abs(dest.x - pos[0]) + abs(dest.y - pos[1])
        
    def getMoveCost(location, pos):
        if location.x != pos[0] and location.y != pos[1]:
            return 1.4
        else:
            return 1

    # check if the position is in list
    def isInList(list, pos):
        if pos in list:
            return list[pos]
        return None
    
    # add available adjacent positions
    def addAdjacentPositions(map, location, dest, openlist, closedlist):
        poslist = getPositions(map, location)
        for pos in poslist:
            # if position is already in closedlist, do nothing
            if isInList(closedlist, pos) is None:
                findEntry = isInList(openlist, pos)
                h_cost = calHeuristic(pos, dest)
                g_cost = location.g_cost + getMoveCost(location, pos)
                if findEntry is None :
                    # if position is not in openlist, add it to openlist
                    openlist[pos] = SearchEntry(pos[0], pos[1], g_cost, g_cost+h_cost, location)
                elif findEntry.g_cost > g_cost:
                    # if position is in openlist and cost is larger than current one,
                    # then update cost and previous position
                    findEntry.g_cost = g_cost
                    findEntry.f_cost = g_cost + h_cost
                    findEntry.pre_entry = location
    
    # find a least cost position in openlist, return None if openlist is empty
    def getFastPosition(openlist):
        fast = None
        for entry in openlist.values():
            if fast is None:
                fast = entry
            elif fast.f_cost > entry.f_cost:
                fast = entry
        return fast

    openlist = {}
    closedlist = {}
    location = SearchEntry(source[0], source[1], 0.0)
    dest = SearchEntry(dest[0], dest[1], 0.0)
    openlist[source] = location

    while True:
        location = getFastPosition(openlist)
        if location is None:
            # not found valid path
            print("can't find valid path")
            break;
        
        if location.x == dest.x and location.y == dest.y:
            break
        
        closedlist[location.getPos()] = location
        openlist.pop(location.getPos())
        addAdjacentPositions(map, location, dest, openlist, closedlist)

    return location

def getFirstStepAndDistance(location):
    distance = 0
    tmp = location
    while location.pre_entry is not None:
        distance += 1
        tmp = location
        location = location.pre_entry
    return (tmp.x, tmp.y, distance)

def getPosInRange(location, range):
    '''get the position which distance from it to destination is range '''
    tmp = location
    while location.pre_entry is not None:
        if range == 0:
            break
        location = location.pre_entry
        tmp = location
        range -= 1
        
    return (tmp.x, tmp.y)

def getAStarDistance(map, source, dest):
    location = AStarSearch(map, source, dest)
    if location is not None:
        _, _, distance = getFirstStepAndDistance(location)
    else:
        distance = None
    return distance

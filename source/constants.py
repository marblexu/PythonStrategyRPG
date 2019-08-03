
ORIGINAL_CAPTION = 'RPG Game'

REC_SIZE = 50
GRID_X_LEN = 10
GRID_Y_LEN = 11
MAP_WIDTH = GRID_X_LEN * REC_SIZE
MAP_HEIGHT = GRID_Y_LEN * REC_SIZE

SCREEN_WIDTH = MAP_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)


WHITE        = (255, 255, 255)
NAVYBLUE     = ( 60,  60, 100)
SKY_BLUE     = ( 39, 145, 251)
BLACK        = (  0,   0,   0)
LIGHTYELLOW  = (247, 238, 214)
RED          = (255,   0,   0)
PURPLE       = (255,   0, 255)
GOLD         = (255, 215,   0)
GREEN        = (  0, 255,   0)

SIZE_MULTIPLIER = 1.3

#GAME INFO DICTIONARY KEYS
CURRENT_TIME = 'current time'
LEVEL_NUM = 'level num'

#STATES FOR ENTIRE GAME
MAIN_MENU = 'main menu'
LOAD_SCREEN = 'load screen'
GAME_OVER = 'game over'
LEVEL = 'level'

#MAP BACKGROUND STATE
BG_EMPTY = 0
BG_ACTIVE = 1
BG_RANGE = 2
BG_SELECT = 3
BG_ATTACK = 4

#MAP GRID TYPE
MAP_EMPTY = 0
MAP_STONE = 1
MAP_GRASS = 2
MAP_DESERT = 3
MAP_LAKE = 4

GROUP1 = 'group1'
GROUP2 = 'group2'
MAP_GRID = 'mapgrid'

#Entity State
IDLE = 'idle'
WALK = 'walk'
ATTACK = 'attack'

#Entity Attribute
ATTR_HEALTH = 'health'
ATTR_RANGE = 'range'
ATTR_DAMAGE = 'damage'
ATTR_ATTACK = 'attack'
ATTR_DEFENSE = 'defense'
ATTR_REMOTE = 'remote' # remote army or melee army
ATTR_SPEED = 'speed' # higher speed army can act prior to lower speed army in a game turn 

#Entity Name
DEVIL = 'devil'
SOLDIER = 'footman'
MAGICIAN = 'magician'
FIREBALL = 'fireball'

#Game State
INIT = 'init'
SELECT = 'select'
ENTITY_ACT = 'entity act'

#Game Setting
MOVE_SPEED = 2



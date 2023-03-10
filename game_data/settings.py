
# Player and monster state constants
IDLE = 0
WALKING = 1
JUMPING = 2
STOMPING = 3
ATTACKING = 4
CASTING = 5
STUNNED = 6
DYING = 7
DEAD = 8

# Game state constants
GS_WELCOME = 0
GS_PLAYING = 1
GS_GAME_OVER = 2
GS_LEVEL_COMPLETE = 3
GS_QUIT = 4
GS_MAP_SCREEN = 5

# Frequently used color contants
WHITE    = (255, 255, 255)
BLACK    = (  0,   0,   0)
RED      = (255,   0,   0)
DARKGRAY = ( 20,  20,  20)

# General constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 960

# Pixels available is a quarter of that: 480x240, which is the native resolution

# Derived values for scaling
TILE_SIZE = 32  # x and y native resolution of standard tiles - this MUST match the actual resolution in the image file!
TILE_SIZE_SCREEN = SCREEN_WIDTH // TILE_SIZE

GRAVITY = 1
MAX_PLATFORMS = 10
JUMP_HEIGHT = 20
H_SCROLL_THRESHOLD = 400
V_SCROLL_THRESHOLD = 200 

TILE_TYPES = 18
ANIMATION_TYPES = 3
OBJECT_TYPES = 9
WALKING_SPEED = 10
ATTACK_SPEED = 1  # UNUSED
PLAYER_HEALTH = 1000
PLAYER_STOMP = 5  # monsters to kill before stop recharges
STOMP_SPEED = 50
MUSIC_ON = False
SOUNDS_ON = True
FIRST_LEVEL = 1  # where to start
LAST_LEVEL = 2  # where to end

# Debug settings
DEBUG_HITBOXES = False
SHOW_FPS = True
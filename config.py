"""Game constants and Q-learning hyperparameters."""

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Decision tick (0.25 seconds = 15 frames at 60 FPS)
DECISION_TICK_FRAMES = 15

# Q-Learning defaults
BASE_ALPHA = 0.1      # Learning rate
GAMMA = 0.95          # Discount factor
EPSILON_START = 1.0   # Initial exploration
EPSILON_MIN = 0.05
EPSILON_DECAY = 0.995

# Physics
GRAVITY = 0.5
GROUND_Y = 500  # Ground level (y position of floor)
FRICTION = 0.85
KNOCKBACK_FORCE = 8

# Combat
ATTACK_RANGE = 50
ATTACK_COOLDOWN_FRAMES = 30  # 0.5 seconds at 60 FPS
MELEE_DAMAGE = 10
RANGED_DAMAGE = 8
PROJECTILE_SPEED = 6

# Movement speeds
AGENT_SPEED = 3
ENEMY_MELEE_SPEED = 2
ENEMY_RANGED_SPEED = 1.5

# Agent defaults
AGENT_MAX_HP = 100
AGENT_BASE_STRENGTH = 10
AGENT_BASE_INTELLIGENCE = 1

# Enemy defaults
ENEMY_MELEE_HP = 30
ENEMY_RANGED_HP = 20
ENEMY_RANGED_PREFERRED_DISTANCE = 150

# Rewards for Q-learning
REWARD_DAMAGE_DEALT = 5
REWARD_ENEMY_DEFEATED = 50
REWARD_FLOOR_CLEARED = 100
REWARD_DAMAGE_TAKEN = -3
REWARD_DEATH = -100

# Actions
ACTION_ATTACK = 0
ACTION_RUN = 1
ACTIONS = [ACTION_ATTACK, ACTION_RUN]

# State discretization thresholds
HP_THRESHOLDS = {
    'critical': 0.25,  # Below 25%
    'low': 0.50,       # 25-50%
    'medium': 0.75,    # 50-75%
    'high': 1.0        # Above 75%
}

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (200, 50, 50)
COLOR_BLUE = (50, 100, 200)
COLOR_GREEN = (50, 200, 50)
COLOR_YELLOW = (255, 255, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_DARK_GRAY = (64, 64, 64)

# Game states
STATE_BASE = 'base'
STATE_COMBAT = 'combat'
STATE_POST_FLOOR = 'post_floor'
STATE_GAME_OVER = 'game_over'

# Save file
SAVE_FILE = 'tower_climber_save.json'

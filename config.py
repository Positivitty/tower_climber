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
GROUND_Y = 450  # Ground level (moved up to give more room)
FRICTION = 0.85
KNOCKBACK_FORCE = 8

# Combat
ATTACK_RANGE = 50
ATTACK_COOLDOWN_FRAMES = 30  # 0.5 seconds at 60 FPS
MELEE_DAMAGE = 10
RANGED_DAMAGE = 6  # Reduced from 8
PROJECTILE_SPEED = 4  # Reduced from 6 to make dodging easier

# Movement speeds
AGENT_SPEED = 3
AGENT_CHARGE_SPEED = 6  # Speed when charging
ENEMY_MELEE_SPEED = 2
ENEMY_RANGED_SPEED = 1.5
ENEMY_RANGED_RETREAT_SPEED = 0.8  # Slower when backing up

# Agent defaults
AGENT_MAX_HP = 100
AGENT_BASE_STRENGTH = 10
AGENT_BASE_INTELLIGENCE = 1
AGENT_BASE_AGILITY = 5
AGENT_BASE_DEFENSE = 5
AGENT_BASE_LUCK = 5

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
REWARD_TRAINING_SUCCESS = 10
REWARD_TRAINING_FAIL = -2
REWARD_MINIGAME_PERFECT = 20

# Combat Actions
ACTION_ATTACK = 0
ACTION_RUN = 1
ACTION_CHARGE = 2  # Rush toward enemy, closing distance quickly
COMBAT_ACTIONS = [ACTION_ATTACK, ACTION_RUN, ACTION_CHARGE]

# Base Actions (what to do at base)
ACTION_TRAIN_STRENGTH = 0
ACTION_TRAIN_INTELLIGENCE = 1
ACTION_TRAIN_AGILITY = 2
ACTION_TRAIN_DEFENSE = 3
ACTION_TRAIN_LUCK = 4
ACTION_START_CLIMB = 5
BASE_ACTIONS = [
    ACTION_TRAIN_STRENGTH,
    ACTION_TRAIN_INTELLIGENCE,
    ACTION_TRAIN_AGILITY,
    ACTION_TRAIN_DEFENSE,
    ACTION_TRAIN_LUCK,
    ACTION_START_CLIMB
]

# Mini-game actions (timing-based)
ACTION_MINIGAME_PRESS = 0
ACTION_MINIGAME_WAIT = 1
MINIGAME_ACTIONS = [ACTION_MINIGAME_PRESS, ACTION_MINIGAME_WAIT]

# Stats list
TRAINABLE_STATS = ['strength', 'intelligence', 'agility', 'defense', 'luck']

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
COLOR_ORANGE = (255, 165, 0)
COLOR_PURPLE = (150, 50, 200)
COLOR_CYAN = (50, 200, 200)
COLOR_GRAY = (128, 128, 128)
COLOR_DARK_GRAY = (64, 64, 64)
COLOR_LIGHT_GRAY = (180, 180, 180)

# Sprite colors
SPRITE_AGENT_PRIMARY = (70, 130, 200)
SPRITE_AGENT_SECONDARY = (50, 100, 160)
SPRITE_ENEMY_PRIMARY = (200, 70, 70)
SPRITE_ENEMY_SECONDARY = (160, 50, 50)

# Game states
STATE_BASE = 'base'
STATE_COMBAT = 'combat'
STATE_POST_FLOOR = 'post_floor'
STATE_GAME_OVER = 'game_over'
STATE_TRAINING = 'training'

# Mini-game settings
MINIGAME_DURATION_FRAMES = 300  # 5 seconds at 60 FPS (longer to watch)
MINIGAME_TARGET_WIDTH = 40  # Width of target zone in timing bar
MINIGAME_RESULT_DISPLAY_FRAMES = 120  # 2 seconds to show result
MINIGAME_AI_DECISION_DELAY = 15  # Frames between AI decisions in minigames

# AI Dialogue
AI_THINK_DELAY_FRAMES = 30  # Pause between AI thoughts

# Save file
SAVE_FILE = 'tower_climber_save.json'

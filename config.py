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

# Tank enemy stats (multipliers of base melee)
ENEMY_TANK_HP_MULT = 2.5
ENEMY_TANK_DAMAGE_MULT = 0.6
ENEMY_TANK_SPEED_MULT = 0.5
ENEMY_TANK_ARMOR_HITS = 3  # First N hits reduced by 50%

# Assassin enemy stats (multipliers of base melee)
ENEMY_ASSASSIN_HP_MULT = 0.5
ENEMY_ASSASSIN_DAMAGE_MULT = 2.0
ENEMY_ASSASSIN_SPEED_MULT = 2.0
ENEMY_ASSASSIN_FIRST_STRIKE_BONUS = 0.5  # +50% on first hit

# Elements
ELEMENT_FIRE = 'fire'
ELEMENT_ICE = 'ice'
ELEMENT_POISON = 'poison'

# Status effect durations (frames at 60 FPS)
BURN_DURATION = 180  # 3 seconds
BURN_TICK_DAMAGE = 2
BURN_TICK_INTERVAL = 30  # Every 0.5 seconds

FREEZE_DURATION = 120  # 2 seconds
FREEZE_SPEED_MULT = 0.3  # 70% slow

POISON_DURATION = 300  # 5 seconds
POISON_TICK_DAMAGE = 1
POISON_TICK_INTERVAL = 60  # Every 1 second

# Boss settings
BOSS_FLOOR_INTERVAL = 5  # Boss every 5 floors
BOSS_HP_MULT = 5.0
BOSS_DAMAGE_MULT = 1.5
BOSS_SPECIAL_COOLDOWN = 300  # 5 seconds
BOSS_ENRAGE_THRESHOLD = 0.3  # Enrage at 30% HP

# Enemy type colors
COLOR_TANK = (100, 100, 150)  # Steel blue
COLOR_ASSASSIN = (80, 0, 80)  # Dark purple
COLOR_FIRE_ENEMY = (255, 100, 0)  # Orange-red
COLOR_ICE_ENEMY = (100, 200, 255)  # Light blue
COLOR_POISON_ENEMY = (100, 200, 50)  # Sickly green
COLOR_BOSS = (200, 50, 200)  # Magenta

# Rewards for Q-learning
REWARD_DAMAGE_DEALT = 5
REWARD_ENEMY_DEFEATED = 50
REWARD_FLOOR_CLEARED = 100
REWARD_DAMAGE_TAKEN = -3
REWARD_DEATH = -100
REWARD_TRAINING_SUCCESS = 10
REWARD_TRAINING_FAIL = -2
REWARD_MINIGAME_PERFECT = 20
REWARD_SUCCESSFUL_DODGE = 8     # Dodged attack that would hit
REWARD_SUCCESSFUL_PARRY = 12    # Parried incoming attack
REWARD_PARRY_COUNTER = 15       # Counter-attack after parry
REWARD_HAZARD_DAMAGE = -5       # Took hazard damage
REWARD_HIGH_GROUND_KILL = 10    # Kill from elevated position
REWARD_USELESS_JUMP = -1        # Jumped without purpose (no platform, already airborne)
REWARD_PLATFORM_REACHED = 3     # Successfully landed on a platform

# Combat Actions
ACTION_ATTACK_HIGH = 0   # Aim for head - critical damage, can stun
ACTION_ATTACK_MID = 1    # Aim for body/arms - can disable attacks
ACTION_ATTACK_LOW = 2    # Aim for legs - can slow enemy
ACTION_RUN = 3
ACTION_CHARGE = 4        # Rush toward enemy, closing distance quickly
ACTION_DODGE = 5         # Dodge roll with i-frames
ACTION_PARRY = 6         # Parry incoming attack
ACTION_JUMP = 7          # Jump to platforms
COMBAT_ACTIONS = [ACTION_ATTACK_HIGH, ACTION_ATTACK_MID, ACTION_ATTACK_LOW,
                  ACTION_RUN, ACTION_CHARGE, ACTION_DODGE, ACTION_PARRY, ACTION_JUMP]

# Legacy alias for compatibility
ACTION_ATTACK = ACTION_ATTACK_MID

# Dodge mechanics
DODGE_DURATION_FRAMES = 12      # i-frames duration (0.2 seconds)
DODGE_COOLDOWN_FRAMES = 45      # 0.75 seconds between dodges
DODGE_STAMINA_COST = 25
DODGE_DISTANCE = 60             # Pixels moved during dodge

# Parry mechanics
PARRY_WINDOW_FRAMES = 10        # Timing window (0.167 seconds)
PARRY_COOLDOWN_FRAMES = 60      # 1 second between parries
PARRY_STAMINA_COST = 15
PARRY_DAMAGE_REDUCTION = 0.8    # 80% damage reduction on success
PARRY_COUNTER_WINDOW_FRAMES = 20  # Frames to counter-attack after parry
PARRY_COUNTER_DAMAGE_MULT = 1.5   # 50% bonus damage on counter

# Stamina system
MAX_STAMINA = 100
STAMINA_REGEN_RATE = 1.0        # Per frame when not acting
STAMINA_REGEN_DELAY_FRAMES = 30 # Delay after action before regen

# Jump mechanics
JUMP_FORCE = -12                # Initial vertical velocity
JUMP_STAMINA_COST = 10

# Jump spam prevention
ENEMY_JUMP_COOLDOWN = 90        # Frames between enemy jumps (1.5 seconds)
ENEMY_JUMP_HEIGHT_THRESHOLD = 50  # Only jump if agent is this many pixels higher
ENEMY_JUMP_PROBABILITY = 0.4    # 40% chance to jump when conditions met

# Enemy type jump probabilities (overrides default)
ENEMY_TANK_JUMP_PROBABILITY = 0.15      # Tanks rarely jump
ENEMY_ASSASSIN_JUMP_PROBABILITY = 0.6   # Assassins jump more often
ENEMY_RANGED_JUMP_PROBABILITY = 0.25    # Ranged prefers distance over height

# Height advantage
HIGH_GROUND_DAMAGE_BONUS = 0.15   # +15% damage when above enemy
LOW_GROUND_DAMAGE_PENALTY = 0.10  # -10% damage when below enemy

# Height levels for state discretization
HEIGHT_LEVEL_GROUND = 0
HEIGHT_LEVEL_LOW = 1              # 0-100 pixels above ground
HEIGHT_LEVEL_MID = 2              # 100-200 pixels above ground
HEIGHT_LEVEL_HIGH = 3             # 200+ pixels above ground

# Platform types
PLATFORM_WOODEN = 'wooden'
PLATFORM_STONE = 'stone'
PLATFORM_CRUMBLING = 'crumbling'

# Platform dimensions
PLATFORM_MIN_WIDTH = 80
PLATFORM_MAX_WIDTH = 200
PLATFORM_HEIGHT = 15
PLATFORM_CRUMBLE_TIME = 60  # Frames before crumbling platform breaks

# Platform heights (y positions)
PLATFORM_HEIGHTS = [350, 280, 200, 130]

# Hazard types
HAZARD_LAVA = 'lava'
HAZARD_SPIKES = 'spikes'
HAZARD_POISON_POOL = 'poison_pool'
HAZARD_FIRE_GEYSER = 'fire_geyser'
HAZARD_ICE_PATCH = 'ice_patch'

# Hazard damage/effects
LAVA_DAMAGE_PER_FRAME = 3
SPIKE_DAMAGE = 25
SPIKE_COOLDOWN = 60             # Immunity after hitting spikes
POISON_POOL_TICK_FRAMES = 30
FIRE_GEYSER_DAMAGE = 35
FIRE_GEYSER_INTERVAL = 180      # 3 seconds between eruptions
FIRE_GEYSER_DURATION = 30       # How long geyser stays active
ICE_PATCH_FRICTION = 0.5        # Reduced friction (slippery)

# Hazard dimensions
HAZARD_MIN_WIDTH = 40
HAZARD_MAX_WIDTH = 120

# Hazard colors
COLOR_LAVA = (255, 100, 0)
COLOR_SPIKES = (150, 150, 150)
COLOR_POISON_POOL = (100, 200, 50)
COLOR_FIRE_GEYSER = (255, 150, 50)
COLOR_ICE_PATCH = (180, 220, 255)

# Body parts
BODY_PART_HEAD = 'head'
BODY_PART_BODY = 'body'
BODY_PART_LEGS = 'legs'

# Body part damage multipliers
HEAD_DAMAGE_MULT = 1.5      # Crits to head
BODY_DAMAGE_MULT = 1.0      # Normal damage
LEGS_DAMAGE_MULT = 0.8      # Less damage but slows

# Body part wound thresholds (% of max HP damage to wound)
WOUND_THRESHOLD = 0.25      # 25% of max HP in one hit wounds the part

# Wound effects
HEAD_WOUND_STUN_CHANCE = 0.3    # 30% chance to stun on head wound
BODY_WOUND_DAMAGE_REDUCTION = 0.5  # 50% less damage when arms wounded
LEGS_WOUND_SPEED_REDUCTION = 0.5   # 50% slower when legs wounded

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
STATE_DEATH_ROLL = 'death_roll'
STATE_SKILLS = 'skills'

# Mini-game settings
MINIGAME_DURATION_FRAMES = 300  # 5 seconds at 60 FPS (longer to watch)
MINIGAME_TARGET_WIDTH = 40  # Width of target zone in timing bar
MINIGAME_RESULT_DISPLAY_FRAMES = 120  # 2 seconds to show result
MINIGAME_AI_DECISION_DELAY = 15  # Frames between AI decisions in minigames

# AI Dialogue
AI_THINK_DELAY_FRAMES = 30  # Pause between AI thoughts

# Save file
SAVE_FILE = 'tower_climber_save.json'

# Skill system
SKILL_DROP_BASE_CHANCE = 0.01  # 1% base drop chance
SKILL_DROP_MAX_CHANCE = 0.05   # 5% max
SKILL_DROP_LUCK_SCALING = 0.002  # +0.2% per luck point above 5
MAX_ACTIVE_SKILLS = 3
MAX_PASSIVE_SKILLS = 5

# Training unlock items
TRAINING_UNLOCK_DROP_CHANCE = 0.15  # 15% per enemy

# Death penalty
DEATH_ROLL_PENALTY_THRESHOLD = 4  # Roll 1-4 = penalty
DICE_ROLL_FRAMES = 120  # 2 seconds of rolling animation
DICE_RESULT_DISPLAY_FRAMES = 90  # 1.5 seconds to show result

# Conversation system states
STATE_CONVERSATION = 'conversation'

# Portrait emotions
EMOTION_NEUTRAL = 'neutral'
EMOTION_WORRIED = 'worried'
EMOTION_EXCITED = 'excited'
EMOTION_HURT = 'hurt'
EMOTION_QUESTIONING = 'questioning'
EMOTION_DETERMINED = 'determined'

# Emotion colors (tints for portrait)
EMOTION_COLORS = {
    EMOTION_NEUTRAL: (0, 255, 255),      # Cyan
    EMOTION_WORRIED: (255, 255, 0),       # Yellow
    EMOTION_EXCITED: (100, 255, 255),     # Bright cyan
    EMOTION_HURT: (255, 100, 100),        # Red tint
    EMOTION_QUESTIONING: (200, 100, 255), # Purple
    EMOTION_DETERMINED: (255, 255, 255),  # Bright white
}

# Dialogue spam reduction
DIALOGUE_GLOBAL_COOLDOWN = 15           # Frames between any messages
DIALOGUE_COMBAT_COOLDOWN = 60           # Frames for combat category
DIALOGUE_HP_WARNING_COOLDOWN = 300      # Frames for HP warnings (5 seconds)
DIALOGUE_EXPLORATION_COOLDOWN = 120     # Frames for exploration messages
DIALOGUE_MAX_COMBAT_MESSAGES = 15       # Max messages per combat

# Critical moment triggers
TRIGGER_LOW_HP = 'low_hp'               # HP drops below 25%
TRIGGER_NEAR_DEATH = 'near_death'       # Survived with <10% HP
TRIGGER_BOSS_ENCOUNTER = 'boss_encounter'  # First time seeing a boss type
TRIGGER_FIRST_ENEMY_TYPE = 'first_enemy_type'  # First time seeing enemy type
TRIGGER_VICTORY = 'victory'             # Floor cleared
TRIGGER_DEATH = 'death'                 # Agent dies
TRIGGER_CLOSE_CALL = 'close_call'       # Dodged lethal attack
TRIGGER_STRATEGY_QUESTION = 'strategy_question'  # Random or 3+ floors since last

# Critical moment cooldowns (in floors or frames)
CLOSE_CALL_COOLDOWN_FRAMES = 1800       # 30 seconds at 60 FPS
STRATEGY_QUESTION_MIN_FLOORS = 3        # Minimum floors between strategy questions

# Conversation timing
TYPEWRITER_SPEED = 2                    # Characters per frame
CONVERSATION_CHOICE_TIMEOUT = 600       # 10 seconds to choose (0 = no timeout)

# Player choice effects
CHOICE_EFFECT_STRATEGY = 'strategy'
CHOICE_EFFECT_LEARNING_BOOST = 'learning_boost'
CHOICE_EFFECT_ENCOURAGEMENT = 'encouragement'

# Effect durations (in frames)
STRATEGY_BIAS_DURATION = 300            # 5 seconds
LEARNING_BOOST_DURATION = 600           # 10 seconds
LEARNING_BOOST_MULTIPLIER = 1.5         # 1.5x learning rate

# Portrait dimensions
PORTRAIT_SIZE = 128                     # Base size (pixels)
PORTRAIT_DISPLAY_SIZE = 192             # Display size (scaled)

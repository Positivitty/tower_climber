"""Player's AI agent entity."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systems.physics import PhysicsBody
from config import (
    SCREEN_WIDTH, GROUND_Y, AGENT_SPEED, AGENT_MAX_HP,
    AGENT_BASE_STRENGTH, AGENT_BASE_INTELLIGENCE,
    AGENT_BASE_AGILITY, AGENT_BASE_DEFENSE, AGENT_BASE_LUCK,
    ATTACK_COOLDOWN_FRAMES, ATTACK_RANGE,
    SPRITE_AGENT_PRIMARY
)


class Agent(PhysicsBody):
    """The player's AI-controlled agent (the tower climber)."""

    def __init__(self, x: float = None, y: float = None):
        if x is None:
            x = SCREEN_WIDTH // 4  # Start on the left side
        if y is None:
            y = GROUND_Y

        super().__init__(x, y)

        # Core stats
        self.max_hp = AGENT_MAX_HP
        self.hp = self.max_hp

        # Trainable stats
        self.strength = AGENT_BASE_STRENGTH      # Attack damage
        self.intelligence = AGENT_BASE_INTELLIGENCE  # Learning rate modifier
        self.agility = AGENT_BASE_AGILITY        # Movement speed + dodge chance
        self.defense = AGENT_BASE_DEFENSE        # Damage reduction
        self.luck = AGENT_BASE_LUCK              # Crit chance + mini-game bonus

        # Combat state
        self.speed = AGENT_SPEED
        self.attack_cooldown = 0
        self.facing = 1  # 1 = right, -1 = left
        self.is_attacking = False
        self.attack_timer = 0  # Frames remaining in attack animation

        # Visual
        self.color = SPRITE_AGENT_PRIMARY

    def get_damage(self) -> int:
        """Calculate attack damage based on strength."""
        return self.strength

    def get_damage_reduction(self) -> float:
        """Calculate damage reduction from defense (0.0 to 0.5 max)."""
        return min(0.5, self.defense * 0.02)

    def get_speed(self) -> float:
        """Calculate movement speed based on agility."""
        return AGENT_SPEED + (self.agility - 5) * 0.1

    def get_dodge_chance(self) -> float:
        """Calculate dodge chance from agility (0.0 to 0.3 max)."""
        return min(0.3, (self.agility - 5) * 0.02)

    def get_crit_chance(self) -> float:
        """Calculate crit chance from luck (0.0 to 0.25 max)."""
        return min(0.25, (self.luck - 5) * 0.02)

    def can_attack(self) -> bool:
        """Check if agent can attack (cooldown is ready)."""
        return self.attack_cooldown <= 0

    def start_attack(self):
        """Start an attack action."""
        if self.can_attack():
            self.is_attacking = True
            self.attack_timer = 10  # Attack animation frames
            self.attack_cooldown = ATTACK_COOLDOWN_FRAMES

    def move_toward(self, target_x: float):
        """Move horizontally toward a target x position."""
        speed = self.get_speed()
        if target_x > self.x:
            self.vx = speed
            self.facing = 1
        elif target_x < self.x:
            self.vx = -speed
            self.facing = -1

    def move_away_from(self, target_x: float):
        """Move horizontally away from a target x position."""
        speed = self.get_speed()
        if target_x > self.x:
            self.vx = -speed
            self.facing = -1
        elif target_x < self.x:
            self.vx = speed
            self.facing = 1
        else:
            self.vx = speed
            self.facing = 1

    def update(self):
        """Update agent state each frame."""
        # Update physics
        self.update_physics()

        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Update attack animation
        if self.attack_timer > 0:
            self.attack_timer -= 1
        else:
            self.is_attacking = False

    def take_damage(self, amount: int) -> int:
        """Take damage and return actual damage taken."""
        import random

        # Check for dodge
        if random.random() < self.get_dodge_chance():
            return 0  # Dodged!

        # Apply damage reduction
        reduction = self.get_damage_reduction()
        actual_damage = int(amount * (1 - reduction))
        actual_damage = min(actual_damage, self.hp)

        self.hp -= actual_damage
        return actual_damage

    def heal(self, amount: int):
        """Heal the agent."""
        self.hp = min(self.hp + amount, self.max_hp)

    def is_alive(self) -> bool:
        """Check if agent is still alive."""
        return self.hp > 0

    def reset_for_floor(self):
        """Reset combat state for a new floor (keep stats)."""
        self.hp = self.max_hp
        self.attack_cooldown = 0
        self.is_attacking = False
        self.attack_timer = 0
        self.x = SCREEN_WIDTH // 4
        self.y = GROUND_Y
        self.vx = 0
        self.vy = 0
        self.grounded = True

    def train_stat(self, stat: str):
        """Increase a stat by 1."""
        if stat == 'strength':
            self.strength += 1
        elif stat == 'intelligence':
            self.intelligence += 1
        elif stat == 'agility':
            self.agility += 1
        elif stat == 'defense':
            self.defense += 1
        elif stat == 'luck':
            self.luck += 1

    def get_stat(self, stat: str) -> int:
        """Get a stat value by name."""
        stats = {
            'strength': self.strength,
            'intelligence': self.intelligence,
            'agility': self.agility,
            'defense': self.defense,
            'luck': self.luck
        }
        return stats.get(stat, 0)

    def get_stats_dict(self) -> dict:
        """Get agent stats as a dictionary for saving."""
        return {
            'max_hp': self.max_hp,
            'strength': self.strength,
            'intelligence': self.intelligence,
            'agility': self.agility,
            'defense': self.defense,
            'luck': self.luck
        }

    def load_stats_dict(self, data: dict):
        """Load agent stats from a dictionary."""
        self.max_hp = data.get('max_hp', AGENT_MAX_HP)
        self.hp = self.max_hp
        self.strength = data.get('strength', AGENT_BASE_STRENGTH)
        self.intelligence = data.get('intelligence', AGENT_BASE_INTELLIGENCE)
        self.agility = data.get('agility', AGENT_BASE_AGILITY)
        self.defense = data.get('defense', AGENT_BASE_DEFENSE)
        self.luck = data.get('luck', AGENT_BASE_LUCK)

"""Player's AI agent entity."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systems.physics import PhysicsBody
from config import (
    SCREEN_WIDTH, GROUND_Y, AGENT_SPEED, AGENT_MAX_HP,
    AGENT_BASE_STRENGTH, AGENT_BASE_INTELLIGENCE,
    ATTACK_COOLDOWN_FRAMES, ATTACK_RANGE, COLOR_BLUE
)


class Agent(PhysicsBody):
    """The player's AI-controlled agent (the tower climber)."""

    def __init__(self, x: float = None, y: float = None):
        if x is None:
            x = SCREEN_WIDTH // 4  # Start on the left side
        if y is None:
            y = GROUND_Y

        super().__init__(x, y)

        # Stats
        self.max_hp = AGENT_MAX_HP
        self.hp = self.max_hp
        self.strength = AGENT_BASE_STRENGTH
        self.intelligence = AGENT_BASE_INTELLIGENCE
        self.speed = AGENT_SPEED

        # Combat state
        self.attack_cooldown = 0
        self.facing = 1  # 1 = right, -1 = left
        self.is_attacking = False
        self.attack_timer = 0  # Frames remaining in attack animation

        # Visual
        self.color = COLOR_BLUE
        self.head_radius = 10
        self.body_length = 30
        self.limb_length = 20

    def get_damage(self) -> int:
        """Calculate attack damage based on strength."""
        return self.strength

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
        if target_x > self.x:
            self.vx = self.speed
            self.facing = 1
        elif target_x < self.x:
            self.vx = -self.speed
            self.facing = -1

    def move_away_from(self, target_x: float):
        """Move horizontally away from a target x position."""
        if target_x > self.x:
            self.vx = -self.speed
            self.facing = -1
        elif target_x < self.x:
            self.vx = self.speed
            self.facing = 1
        else:
            # Target is at same position, pick a random direction
            self.vx = self.speed
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
        actual_damage = min(amount, self.hp)
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

    def get_stats_dict(self) -> dict:
        """Get agent stats as a dictionary for saving."""
        return {
            'max_hp': self.max_hp,
            'strength': self.strength,
            'intelligence': self.intelligence
        }

    def load_stats_dict(self, data: dict):
        """Load agent stats from a dictionary."""
        self.max_hp = data.get('max_hp', AGENT_MAX_HP)
        self.hp = self.max_hp
        self.strength = data.get('strength', AGENT_BASE_STRENGTH)
        self.intelligence = data.get('intelligence', AGENT_BASE_INTELLIGENCE)

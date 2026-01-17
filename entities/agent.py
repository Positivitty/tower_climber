"""Player's AI agent entity."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systems.physics import PhysicsBody
from config import (
    SCREEN_WIDTH, GROUND_Y, AGENT_SPEED, AGENT_MAX_HP,
    AGENT_BASE_STRENGTH, AGENT_BASE_INTELLIGENCE,
    AGENT_BASE_AGILITY, AGENT_BASE_DEFENSE, AGENT_BASE_LUCK,
    ATTACK_COOLDOWN_FRAMES, SPRITE_AGENT_PRIMARY
)


class Agent(PhysicsBody):
    """The player's AI-controlled agent (the tower climber)."""

    def __init__(self, x: float = None, y: float = None):
        if x is None:
            x = SCREEN_WIDTH // 4
        if y is None:
            y = GROUND_Y

        super().__init__(x, y)

        # Character identity
        self.race = 'human'
        self.char_class = 'knight'
        self.name = "Climber"

        # Core stats
        self.max_hp = AGENT_MAX_HP
        self.hp = self.max_hp

        # Trainable stats
        self.strength = AGENT_BASE_STRENGTH
        self.intelligence = AGENT_BASE_INTELLIGENCE
        self.agility = AGENT_BASE_AGILITY
        self.defense = AGENT_BASE_DEFENSE
        self.luck = AGENT_BASE_LUCK

        # Equipment
        self.equipment = None  # Set by game

        # Special abilities (from race/class)
        self.undying_available = False  # Undead special
        self.divine_heal_pending = False  # Angel special

        # Combat state
        self.speed = AGENT_SPEED
        self.attack_cooldown = 0
        self.facing = 1
        self.is_attacking = False
        self.attack_timer = 0

        # Visual
        self.color = SPRITE_AGENT_PRIMARY

    def get_total_stat(self, stat: str) -> int:
        """Get stat including equipment bonuses."""
        base = self.get_stat(stat)
        if self.equipment:
            equip_bonus = self.equipment.get_total_stats().get(stat, 0)
            return base + equip_bonus
        return base

    def get_damage(self) -> int:
        """Calculate attack damage."""
        import random
        base_damage = self.get_total_stat('strength')

        # Crit check
        crit_chance = self.get_crit_chance()
        if random.random() < crit_chance:
            base_damage = int(base_damage * 2)

        # Demon bloodlust
        if self.race == 'demon' and self.hp / self.max_hp < 0.3:
            base_damage = int(base_damage * 1.5)

        return base_damage

    def get_damage_reduction(self) -> float:
        """Calculate damage reduction from defense."""
        defense = self.get_total_stat('defense')
        return min(0.5, defense * 0.02)

    def get_speed(self) -> float:
        """Calculate movement speed."""
        agility = self.get_total_stat('agility')
        return AGENT_SPEED + (agility - 5) * 0.1

    def get_dodge_chance(self) -> float:
        """Calculate dodge chance from agility."""
        agility = self.get_total_stat('agility')
        base_dodge = min(0.3, (agility - 5) * 0.02)

        # Assassin bonus
        if self.char_class == 'assassin':
            base_dodge += 0.05

        return min(0.4, base_dodge)

    def get_crit_chance(self) -> float:
        """Calculate crit chance from luck."""
        luck = self.get_total_stat('luck')
        base_crit = min(0.25, (luck - 5) * 0.02)

        # Assassin bonus
        if self.char_class == 'assassin':
            base_crit += 0.1

        return min(0.4, base_crit)

    def get_learning_modifier(self) -> float:
        """Get modifier for Q-learning rate."""
        intelligence = self.get_total_stat('intelligence')
        modifier = 1.0 + (intelligence - 1) * 0.1

        # Wizard bonus
        if self.char_class == 'wizard':
            modifier *= 2.0

        return modifier

    def can_attack(self) -> bool:
        return self.attack_cooldown <= 0

    def start_attack(self):
        if self.can_attack():
            self.is_attacking = True
            self.attack_timer = 10
            self.attack_cooldown = ATTACK_COOLDOWN_FRAMES

    def move_toward(self, target_x: float):
        speed = self.get_speed()
        if target_x > self.x:
            self.vx = speed
            self.facing = 1
        elif target_x < self.x:
            self.vx = -speed
            self.facing = -1

    def move_away_from(self, target_x: float):
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
        self.update_physics()
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
        else:
            self.is_attacking = False

    def take_damage(self, amount: int) -> int:
        import random

        # Dodge check
        if random.random() < self.get_dodge_chance():
            return 0

        # Damage reduction
        reduction = self.get_damage_reduction()
        actual_damage = int(amount * (1 - reduction))
        actual_damage = min(actual_damage, self.hp)

        self.hp -= actual_damage

        # Undead special - survive fatal hit once
        if self.hp <= 0 and self.race == 'undead' and self.undying_available:
            self.hp = 1
            self.undying_available = False

        return actual_damage

    def heal(self, amount: int):
        self.hp = min(self.hp + amount, self.max_hp)

    def is_alive(self) -> bool:
        return self.hp > 0

    def reset_for_floor(self):
        """Reset for a new floor."""
        self.attack_cooldown = 0
        self.is_attacking = False
        self.attack_timer = 0
        self.x = SCREEN_WIDTH // 4
        self.y = GROUND_Y
        self.vx = 0
        self.vy = 0
        self.grounded = True

        # Angel divine heal
        if self.race == 'angel' and self.divine_heal_pending:
            self.heal(int(self.max_hp * 0.1))
            self.divine_heal_pending = False

    def start_new_climb(self):
        """Start a new climb - full reset."""
        self.hp = self.max_hp
        self.undying_available = (self.race == 'undead')
        self.divine_heal_pending = False
        self.reset_for_floor()

    def end_floor(self, cleared: bool):
        """Called when a floor ends."""
        if cleared and self.race == 'angel':
            self.divine_heal_pending = True

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
        """Get base stat value."""
        stats = {
            'strength': self.strength,
            'intelligence': self.intelligence,
            'agility': self.agility,
            'defense': self.defense,
            'luck': self.luck
        }
        return stats.get(stat, 0)

    def get_stats_dict(self) -> dict:
        """Get agent stats for saving."""
        return {
            'race': self.race,
            'char_class': self.char_class,
            'name': self.name,
            'max_hp': self.max_hp,
            'strength': self.strength,
            'intelligence': self.intelligence,
            'agility': self.agility,
            'defense': self.defense,
            'luck': self.luck
        }

    def load_stats_dict(self, data: dict):
        """Load agent stats."""
        self.race = data.get('race', 'human')
        self.char_class = data.get('char_class', 'knight')
        self.name = data.get('name', 'Climber')
        self.max_hp = data.get('max_hp', AGENT_MAX_HP)
        self.hp = self.max_hp
        self.strength = data.get('strength', AGENT_BASE_STRENGTH)
        self.intelligence = data.get('intelligence', AGENT_BASE_INTELLIGENCE)
        self.agility = data.get('agility', AGENT_BASE_AGILITY)
        self.defense = data.get('defense', AGENT_BASE_DEFENSE)
        self.luck = data.get('luck', AGENT_BASE_LUCK)

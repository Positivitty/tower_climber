"""Enemy entities - melee and ranged enemies."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systems.physics import PhysicsBody
from config import (
    GROUND_Y, ENEMY_MELEE_HP, ENEMY_RANGED_HP,
    MELEE_DAMAGE, RANGED_DAMAGE, ENEMY_MELEE_SPEED, ENEMY_RANGED_SPEED,
    ENEMY_RANGED_PREFERRED_DISTANCE, ENEMY_RANGED_RETREAT_SPEED,
    ATTACK_COOLDOWN_FRAMES, ATTACK_RANGE, COLOR_RED,
    BODY_PART_HEAD, BODY_PART_BODY, BODY_PART_LEGS,
    HEAD_WOUND_STUN_CHANCE, BODY_WOUND_DAMAGE_REDUCTION, LEGS_WOUND_SPEED_REDUCTION
)


class Enemy(PhysicsBody):
    """Base enemy class with common functionality."""

    def __init__(self, x: float, y: float, enemy_type: str):
        super().__init__(x, y)

        self.enemy_type = enemy_type  # 'melee' or 'ranged'
        self.hp = ENEMY_MELEE_HP if enemy_type == 'melee' else ENEMY_RANGED_HP
        self.max_hp = self.hp
        self.damage = MELEE_DAMAGE if enemy_type == 'melee' else RANGED_DAMAGE
        self.speed = ENEMY_MELEE_SPEED if enemy_type == 'melee' else ENEMY_RANGED_SPEED
        self.preferred_distance = 0 if enemy_type == 'melee' else ENEMY_RANGED_PREFERRED_DISTANCE

        # Combat state
        self.attack_cooldown = 0
        self.facing = -1  # Default face left (toward player spawn)
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_height = 'mid'  # 'high', 'mid', 'low'

        # Body part wounds
        self.wounds = {
            BODY_PART_HEAD: False,
            BODY_PART_BODY: False,
            BODY_PART_LEGS: False
        }
        self.stunned = 0  # Frames remaining stunned

        # Visual (enemies are red-tinted)
        self.color = COLOR_RED

    def can_attack(self) -> bool:
        """Check if enemy can attack."""
        return self.attack_cooldown <= 0 and not self.is_stunned()

    def is_stunned(self) -> bool:
        """Check if enemy is currently stunned."""
        return self.stunned > 0

    def apply_stun(self, frames: int):
        """Apply stun for given frames."""
        self.stunned = max(self.stunned, frames)

    def apply_wound(self, body_part: str):
        """Apply a wound to a body part."""
        import random

        self.wounds[body_part] = True

        # Head wound can cause stun
        if body_part == BODY_PART_HEAD:
            if random.random() < HEAD_WOUND_STUN_CHANCE:
                self.apply_stun(60)  # 1 second stun

    def get_damage(self) -> int:
        """Get attack damage, accounting for wounds."""
        base_damage = self.damage

        # Body wound reduces damage output
        if self.wounds[BODY_PART_BODY]:
            base_damage = int(base_damage * BODY_WOUND_DAMAGE_REDUCTION)

        return base_damage

    def get_speed(self) -> float:
        """Get movement speed, accounting for wounds."""
        speed = self.speed

        # Leg wound reduces speed
        if self.wounds[BODY_PART_LEGS]:
            speed *= LEGS_WOUND_SPEED_REDUCTION

        return speed

    def start_attack(self):
        """Start an attack action."""
        if self.can_attack():
            self.is_attacking = True
            self.attack_timer = 10
            self.attack_cooldown = ATTACK_COOLDOWN_FRAMES

    def update_ai(self, agent):
        """Update enemy AI behavior based on agent position."""
        raise NotImplementedError("Subclasses must implement update_ai")

    def update(self, agent):
        """Update enemy state each frame."""
        # Update stun timer
        if self.stunned > 0:
            self.stunned -= 1

        # Update AI behavior (only if not stunned)
        if not self.is_stunned():
            self.update_ai(agent)
        else:
            self.vx = 0  # Can't move while stunned

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

        # Update facing based on agent position
        if agent.x > self.x:
            self.facing = 1
        elif agent.x < self.x:
            self.facing = -1

    def take_damage(self, amount: int) -> int:
        """Take damage and return actual damage taken."""
        actual_damage = min(amount, self.hp)
        self.hp -= actual_damage
        return actual_damage

    def is_alive(self) -> bool:
        """Check if enemy is still alive."""
        return self.hp > 0


class MeleeEnemy(Enemy):
    """Melee enemy that chases the player and attacks up close."""

    def __init__(self, x: float, y: float = None):
        if y is None:
            y = GROUND_Y
        super().__init__(x, y, 'melee')

    def update_ai(self, agent):
        """Chase the player and attack when in range."""
        distance = self.distance_to(agent)
        direction = self.direction_to(agent)

        if distance <= ATTACK_RANGE:
            # In range - attack
            self.vx = 0
            if self.can_attack():
                self.start_attack()
        else:
            # Chase the player
            self.vx = direction * self.get_speed()


class RangedEnemy(Enemy):
    """Ranged enemy that maintains distance and shoots projectiles."""

    def __init__(self, x: float, y: float = None):
        if y is None:
            y = GROUND_Y
        super().__init__(x, y, 'ranged')
        self.projectile_ready = True  # Tracks if we can spawn a projectile

    def update_ai(self, agent):
        """Maintain preferred distance and shoot when possible."""
        distance = self.distance_to(agent)
        direction = self.direction_to(agent)

        # Get current speed (accounts for wounds)
        current_speed = self.get_speed()
        retreat_speed = ENEMY_RANGED_RETREAT_SPEED
        if self.wounds[BODY_PART_LEGS]:
            retreat_speed *= LEGS_WOUND_SPEED_REDUCTION

        # Try to maintain preferred distance
        if distance < self.preferred_distance - 20:
            # Too close - back away (but slowly!)
            self.vx = -direction * retreat_speed
        elif distance > self.preferred_distance + 20:
            # Too far - move closer
            self.vx = direction * current_speed
        else:
            # At preferred distance - stop and shoot
            self.vx = 0
            if self.can_attack():
                self.start_attack()
                self.projectile_ready = True

    def should_spawn_projectile(self) -> bool:
        """Check if a projectile should be spawned this frame."""
        # Spawn projectile at the start of attack animation
        if self.is_attacking and self.attack_timer == 9 and self.projectile_ready:
            self.projectile_ready = False
            return True
        return False

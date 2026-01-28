"""Enemy entities - melee and ranged enemies."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systems.physics import PhysicsBody
from systems.status_effects import StatusEffectManager
import random
from config import (
    GROUND_Y, ENEMY_MELEE_HP, ENEMY_RANGED_HP,
    MELEE_DAMAGE, RANGED_DAMAGE, ENEMY_MELEE_SPEED, ENEMY_RANGED_SPEED,
    ENEMY_RANGED_PREFERRED_DISTANCE, ENEMY_RANGED_RETREAT_SPEED,
    ATTACK_COOLDOWN_FRAMES, ATTACK_RANGE, COLOR_RED,
    BODY_PART_HEAD, BODY_PART_BODY, BODY_PART_LEGS,
    HEAD_WOUND_STUN_CHANCE, BODY_WOUND_DAMAGE_REDUCTION, LEGS_WOUND_SPEED_REDUCTION,
    ENEMY_TANK_HP_MULT, ENEMY_TANK_DAMAGE_MULT, ENEMY_TANK_SPEED_MULT, ENEMY_TANK_ARMOR_HITS,
    ENEMY_ASSASSIN_HP_MULT, ENEMY_ASSASSIN_DAMAGE_MULT, ENEMY_ASSASSIN_SPEED_MULT,
    ENEMY_ASSASSIN_FIRST_STRIKE_BONUS,
    COLOR_TANK, COLOR_ASSASSIN, COLOR_BOSS,
    BOSS_HP_MULT, BOSS_DAMAGE_MULT, BOSS_SPECIAL_COOLDOWN, BOSS_ENRAGE_THRESHOLD,
    ELEMENT_FIRE, ELEMENT_ICE, ELEMENT_POISON,
    COLOR_FIRE_ENEMY, COLOR_ICE_ENEMY, COLOR_POISON_ENEMY,
    ENEMY_JUMP_COOLDOWN, ENEMY_JUMP_HEIGHT_THRESHOLD, ENEMY_JUMP_PROBABILITY,
    ENEMY_TANK_JUMP_PROBABILITY, ENEMY_ASSASSIN_JUMP_PROBABILITY, ENEMY_RANGED_JUMP_PROBABILITY
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

        # Elemental type (None for normal enemies)
        self.element = None

        # Status effects
        self.status_effects = StatusEffectManager()

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

    def update(self, agent, terrain_manager=None):
        """Update enemy state each frame."""
        # Update status effects
        self.status_effects.update(self)

        # Update stun timer
        if self.stunned > 0:
            self.stunned -= 1

        # Update AI behavior (only if not stunned)
        if not self.is_stunned():
            self.update_ai(agent)
        else:
            self.vx = 0  # Can't move while stunned

        # Update physics
        self.update_physics(terrain_manager)

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
        self.jump_cooldown = 0  # Frames until enemy can jump again

    def update_ai(self, agent):
        """Chase the player and attack when in range. Jump if player is above."""
        distance = self.distance_to(agent)
        direction = self.direction_to(agent)

        # Check if player is significantly above us (with height threshold and probability)
        height_diff = self.y - agent.y
        should_jump = (
            height_diff > ENEMY_JUMP_HEIGHT_THRESHOLD and
            self.grounded and
            self.jump_cooldown <= 0 and
            random.random() < ENEMY_JUMP_PROBABILITY
        )

        if distance <= ATTACK_RANGE:
            # In range - attack
            self.vx = 0
            if self.can_attack():
                self.start_attack()
        else:
            # Chase the player
            self.vx = direction * self.get_speed()

            # Jump if player is on higher platform
            if should_jump:
                self.vy = -12  # Jump force
                self.grounded = False
                self.jump_cooldown = ENEMY_JUMP_COOLDOWN

        # Decrement jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1


class RangedEnemy(Enemy):
    """Ranged enemy that maintains distance and shoots projectiles."""

    def __init__(self, x: float, y: float = None):
        if y is None:
            y = GROUND_Y
        super().__init__(x, y, 'ranged')
        self.projectile_ready = True  # Tracks if we can spawn a projectile
        self.jump_cooldown = 0  # Frames until enemy can jump again

    def update_ai(self, agent):
        """Maintain preferred distance and shoot when possible. Jump if player is above."""
        distance = self.distance_to(agent)
        direction = self.direction_to(agent)

        # Get current speed (accounts for wounds)
        current_speed = self.get_speed()
        retreat_speed = ENEMY_RANGED_RETREAT_SPEED
        if self.wounds[BODY_PART_LEGS]:
            retreat_speed *= LEGS_WOUND_SPEED_REDUCTION

        # Check if player is significantly above us (ranged prefers distance over height)
        height_diff = self.y - agent.y
        should_jump = (
            height_diff > ENEMY_JUMP_HEIGHT_THRESHOLD and
            self.grounded and
            self.jump_cooldown <= 0 and
            random.random() < ENEMY_RANGED_JUMP_PROBABILITY
        )

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

        # Jump if player is on higher platform
        if should_jump:
            self.vy = -12  # Jump force
            self.grounded = False
            self.jump_cooldown = ENEMY_JUMP_COOLDOWN

        # Decrement jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1

    def should_spawn_projectile(self) -> bool:
        """Check if a projectile should be spawned this frame."""
        # Spawn projectile at the start of attack animation
        if self.is_attacking and self.attack_timer == 9 and self.projectile_ready:
            self.projectile_ready = False
            return True
        return False


class TankEnemy(Enemy):
    """Tank enemy - high HP, slow, has armor that reduces first few hits."""

    def __init__(self, x: float, y: float = None):
        if y is None:
            y = GROUND_Y
        super().__init__(x, y, 'tank')

        # Tank stats - high HP, low damage, slow
        self.hp = int(ENEMY_MELEE_HP * ENEMY_TANK_HP_MULT)
        self.max_hp = self.hp
        self.damage = int(MELEE_DAMAGE * ENEMY_TANK_DAMAGE_MULT)
        self.speed = ENEMY_MELEE_SPEED * ENEMY_TANK_SPEED_MULT

        # Armor mechanic - first N hits are reduced by 50%
        self.armor_hits_remaining = ENEMY_TANK_ARMOR_HITS
        self.jump_cooldown = 0  # Frames until enemy can jump again

        # Visual
        self.color = COLOR_TANK

    def take_damage(self, amount: int) -> int:
        """Take damage with armor reduction for first few hits."""
        # Armor reduces damage by 50% for first N hits
        if self.armor_hits_remaining > 0:
            amount = amount // 2
            self.armor_hits_remaining -= 1

        actual_damage = min(amount, self.hp)
        self.hp -= actual_damage
        return actual_damage

    def update_ai(self, agent):
        """Slowly advance and attack when in range. Jump if player is above."""
        distance = self.distance_to(agent)
        direction = self.direction_to(agent)

        # Check if player is significantly above us (tanks rarely jump)
        height_diff = self.y - agent.y
        should_jump = (
            height_diff > ENEMY_JUMP_HEIGHT_THRESHOLD and
            self.grounded and
            self.jump_cooldown <= 0 and
            random.random() < ENEMY_TANK_JUMP_PROBABILITY
        )

        if distance <= ATTACK_RANGE:
            # In range - attack
            self.vx = 0
            if self.can_attack():
                self.start_attack()
        else:
            # Slowly advance
            self.vx = direction * self.get_speed()

        # Jump if player is on higher platform (rarely for tanks)
        if should_jump:
            self.vy = -10  # Weaker jump for heavy tank
            self.grounded = False
            self.jump_cooldown = ENEMY_JUMP_COOLDOWN * 2  # Even longer cooldown for tanks

        # Decrement jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1


class AssassinEnemy(Enemy):
    """Assassin enemy - low HP, fast, high damage, first strike bonus."""

    def __init__(self, x: float, y: float = None):
        if y is None:
            y = GROUND_Y
        super().__init__(x, y, 'assassin')

        # Assassin stats - low HP, high damage, fast
        self.hp = int(ENEMY_MELEE_HP * ENEMY_ASSASSIN_HP_MULT)
        self.max_hp = self.hp
        self.damage = int(MELEE_DAMAGE * ENEMY_ASSASSIN_DAMAGE_MULT)
        self.speed = ENEMY_MELEE_SPEED * ENEMY_ASSASSIN_SPEED_MULT

        # First strike bonus
        self.first_strike_used = False

        # Behavior state
        self.retreating = False
        self.retreat_timer = 0
        self.jump_cooldown = 0  # Frames until enemy can jump again

        # Visual
        self.color = COLOR_ASSASSIN

    def get_damage(self) -> int:
        """Get damage with first strike bonus."""
        base_damage = super().get_damage()

        # First strike deals bonus damage
        if not self.first_strike_used:
            self.first_strike_used = True
            return int(base_damage * (1 + ENEMY_ASSASSIN_FIRST_STRIKE_BONUS))

        return base_damage

    def update_ai(self, agent):
        """Rush in, attack, then retreat briefly. Jump if player is above."""
        distance = self.distance_to(agent)
        direction = self.direction_to(agent)

        # Check if player is significantly above us (assassins jump more often)
        height_diff = self.y - agent.y
        should_jump = (
            height_diff > ENEMY_JUMP_HEIGHT_THRESHOLD and
            self.grounded and
            self.jump_cooldown <= 0 and
            random.random() < ENEMY_ASSASSIN_JUMP_PROBABILITY
        )

        # Handle retreat behavior
        if self.retreating:
            self.retreat_timer -= 1
            if self.retreat_timer <= 0:
                self.retreating = False
            else:
                # Move away from agent
                self.vx = -direction * self.get_speed() * 0.8
                # Decrement jump cooldown
                if self.jump_cooldown > 0:
                    self.jump_cooldown -= 1
                return

        if distance <= ATTACK_RANGE:
            # In range - attack
            self.vx = 0
            if self.can_attack():
                self.start_attack()
                # After attacking, retreat briefly
                self.retreating = True
                self.retreat_timer = 30  # 0.5 seconds retreat
        else:
            # Rush toward player
            self.vx = direction * self.get_speed()

        # Jump if player is on higher platform
        if should_jump:
            self.vy = -14  # Stronger jump for agile assassin
            self.grounded = False
            self.jump_cooldown = ENEMY_JUMP_COOLDOWN // 2  # Shorter cooldown for assassins

        # Decrement jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1


class BossEnemy(Enemy):
    """Base class for floor bosses."""

    def __init__(self, x: float, y: float, floor_level: int, boss_name: str):
        if y is None:
            y = GROUND_Y
        super().__init__(x, y, 'boss')

        self.name = boss_name
        self.floor_level = floor_level

        # Boss stats - scaled by floor
        floor_scale = 1 + (floor_level - 1) * 0.2
        self.hp = int(ENEMY_MELEE_HP * BOSS_HP_MULT * floor_scale)
        self.max_hp = self.hp
        self.damage = int(MELEE_DAMAGE * BOSS_DAMAGE_MULT)
        self.speed = ENEMY_MELEE_SPEED * 1.2

        # Phase system
        self.phase = 1
        self.max_phases = 3

        # Special attack cooldown
        self.special_cooldown = BOSS_SPECIAL_COOLDOWN
        self.special_timer = self.special_cooldown
        self.special_active = False
        self.special_type = None

        # Enrage state
        self.enraged = False

        # Visual
        self.color = COLOR_BOSS

    def update_phase(self):
        """Update boss phase based on HP."""
        hp_ratio = self.hp / self.max_hp

        if hp_ratio <= BOSS_ENRAGE_THRESHOLD and self.phase < 3:
            self.phase = 3
            if not self.enraged:
                self.enraged = True
                self.speed *= 1.5
                self.damage = int(self.damage * 1.25)
        elif hp_ratio <= 0.6 and self.phase < 2:
            self.phase = 2

    def can_use_special(self) -> bool:
        """Check if special attack is ready."""
        return self.special_timer <= 0 and not self.is_stunned() and not self.special_active

    def start_special_attack(self, special_type: str):
        """Start a special attack."""
        self.special_active = True
        self.special_type = special_type
        self.special_timer = self.special_cooldown

    def end_special_attack(self):
        """End the special attack."""
        self.special_active = False
        self.special_type = None

    def update_ai(self, agent):
        """Boss AI - override in subclasses for specific behavior."""
        self.update_phase()

        # Decrement special timer
        if self.special_timer > 0:
            self.special_timer -= 1

        # Default melee behavior
        self._melee_ai(agent)

    def _melee_ai(self, agent):
        """Standard melee chase and attack behavior."""
        distance = self.distance_to(agent)
        direction = self.direction_to(agent)

        if distance <= ATTACK_RANGE:
            self.vx = 0
            if self.can_attack():
                self.start_attack()
        else:
            self.vx = direction * self.get_speed()


class InfernoGuardian(BossEnemy):
    """Fire boss - Floor 5. Uses flame breath and fire trails."""

    def __init__(self, x: float, y: float = None, floor_level: int = 5):
        super().__init__(x, y, floor_level, "Inferno Guardian")
        self.element = ELEMENT_FIRE
        self.color = COLOR_FIRE_ENEMY

        # Flame breath state
        self.flame_breath_active = False
        self.flame_breath_timer = 0

    def update_ai(self, agent):
        """Fire boss AI with flame breath special."""
        self.update_phase()

        if self.special_timer > 0:
            self.special_timer -= 1

        # Handle active flame breath
        if self.flame_breath_active:
            self.flame_breath_timer -= 1
            if self.flame_breath_timer <= 0:
                self.flame_breath_active = False
                self.end_special_attack()
            self.vx = 0  # Stand still during flame breath
            return

        # Use flame breath special when ready and in range
        distance = self.distance_to(agent)
        if distance <= 150 and self.can_use_special():
            self.start_special_attack('flame_breath')
            self.flame_breath_active = True
            self.flame_breath_timer = 60  # 1 second attack
            return

        # Default melee behavior
        self._melee_ai(agent)


class FrostWarden(BossEnemy):
    """Ice boss - Floor 10. Uses frost nova and ice shield."""

    def __init__(self, x: float, y: float = None, floor_level: int = 10):
        super().__init__(x, y, floor_level, "Frost Warden")
        self.element = ELEMENT_ICE
        self.color = COLOR_ICE_ENEMY

        # Ice shield state
        self.ice_shield_active = False
        self.ice_shield_hits = 0

    def take_damage(self, amount: int) -> int:
        """Take damage with ice shield protection."""
        if self.ice_shield_active:
            self.ice_shield_hits -= 1
            if self.ice_shield_hits <= 0:
                self.ice_shield_active = False
            return 0  # Shield absorbs hit

        return super().take_damage(amount)

    def update_ai(self, agent):
        """Ice boss AI with frost nova and ice shield."""
        self.update_phase()

        if self.special_timer > 0:
            self.special_timer -= 1

        # Activate ice shield in phase 2+
        if self.phase >= 2 and not self.ice_shield_active and self.can_use_special():
            self.ice_shield_active = True
            self.ice_shield_hits = 2
            self.start_special_attack('ice_shield')
            self.special_timer = self.special_cooldown * 2  # Longer cooldown for shield

        # Use frost nova when close
        distance = self.distance_to(agent)
        if distance <= 100 and self.can_use_special():
            self.start_special_attack('frost_nova')

        self._melee_ai(agent)


class PlagueLord(BossEnemy):
    """Poison boss - Floor 15. Uses poison cloud and heals from poison damage."""

    def __init__(self, x: float, y: float = None, floor_level: int = 15):
        super().__init__(x, y, floor_level, "Plague Lord")
        self.element = ELEMENT_POISON
        self.color = COLOR_POISON_ENEMY

        # Poison cloud state
        self.poison_cloud_active = False
        self.poison_cloud_timer = 0

    def update_ai(self, agent):
        """Poison boss AI with poison cloud."""
        self.update_phase()

        if self.special_timer > 0:
            self.special_timer -= 1

        # Handle active poison cloud
        if self.poison_cloud_active:
            self.poison_cloud_timer -= 1
            if self.poison_cloud_timer <= 0:
                self.poison_cloud_active = False
                self.end_special_attack()

        # Use poison cloud special
        distance = self.distance_to(agent)
        if distance <= 120 and self.can_use_special():
            self.start_special_attack('poison_cloud')
            self.poison_cloud_active = True
            self.poison_cloud_timer = 120  # 2 seconds

        self._melee_ai(agent)

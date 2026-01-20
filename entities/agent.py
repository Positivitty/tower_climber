"""Player's AI agent entity."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systems.physics import PhysicsBody
from config import (
    SCREEN_WIDTH, GROUND_Y, AGENT_SPEED, AGENT_MAX_HP,
    AGENT_BASE_STRENGTH, AGENT_BASE_INTELLIGENCE,
    AGENT_BASE_AGILITY, AGENT_BASE_DEFENSE, AGENT_BASE_LUCK,
    ATTACK_COOLDOWN_FRAMES, SPRITE_AGENT_PRIMARY,
    BODY_PART_HEAD, BODY_PART_BODY, BODY_PART_LEGS,
    BODY_WOUND_DAMAGE_REDUCTION, LEGS_WOUND_SPEED_REDUCTION,
    MAX_ACTIVE_SKILLS, MAX_PASSIVE_SKILLS
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
        self.attack_height = 'mid'  # 'high', 'mid', 'low'

        # Body part wounds
        self.wounds = {
            BODY_PART_HEAD: False,
            BODY_PART_BODY: False,
            BODY_PART_LEGS: False
        }
        self.stunned = 0  # Frames remaining stunned

        # Visual
        self.color = SPRITE_AGENT_PRIMARY

        # Skills
        self.active_skills = []  # List of Skill objects (max 3)
        self.passive_skills = []  # List of Skill objects (max 5)
        self.active_buffs = []  # Active buff effects [{name, frames_remaining, effects}]
        self.regen_counter = 0  # For HP regen passive
        self.second_wind_available = False  # Per-floor death save

        # Training unlocks
        self.unlocked_training = set()  # Set of stat names that can be trained

    def get_total_stat(self, stat: str) -> int:
        """Get stat including equipment bonuses."""
        base = self.get_stat(stat)
        if self.equipment:
            equip_bonus = self.equipment.get_total_stats().get(stat, 0)
            return base + equip_bonus
        return base

    def get_damage(self, target_hp_ratio: float = 1.0) -> int:
        """Calculate attack damage."""
        import random
        base_damage = self.get_total_stat('strength')

        # Body wound reduces damage output
        if self.wounds[BODY_PART_BODY]:
            base_damage = int(base_damage * BODY_WOUND_DAMAGE_REDUCTION)

        # Passive damage boost
        damage_mult = 1.0 + self.get_passive_bonus('damage_mult')
        base_damage = int(base_damage * damage_mult)

        # Execute passive (bonus damage to low HP enemies)
        execute_threshold = self.get_passive_bonus('execute_threshold')
        if execute_threshold > 0 and target_hp_ratio < execute_threshold:
            execute_mult = self.get_passive_bonus('execute_mult')
            base_damage = int(base_damage * execute_mult)

        # Active buff damage bonuses
        for buff in self.active_buffs:
            if 'damage_mult_bonus' in buff.get('effects', {}):
                base_damage = int(base_damage * (1 + buff['effects']['damage_mult_bonus']))

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
        speed = AGENT_SPEED + (agility - 5) * 0.1

        # Leg wound reduces speed
        if self.wounds[BODY_PART_LEGS]:
            speed *= LEGS_WOUND_SPEED_REDUCTION

        return speed

    def get_dodge_chance(self) -> float:
        """Calculate dodge chance from agility."""
        agility = self.get_total_stat('agility')
        base_dodge = min(0.3, (agility - 5) * 0.02)

        # Assassin bonus
        if self.char_class == 'assassin':
            base_dodge += 0.05

        # Passive skill bonus
        base_dodge += self.get_passive_bonus('dodge_chance')

        return min(0.5, base_dodge)

    def get_crit_chance(self) -> float:
        """Calculate crit chance from luck."""
        luck = self.get_total_stat('luck')
        base_crit = min(0.25, (luck - 5) * 0.02)

        # Assassin bonus
        if self.char_class == 'assassin':
            base_crit += 0.1

        # Passive skill bonus
        base_crit += self.get_passive_bonus('crit_chance')

        return min(0.5, base_crit)

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

    def has_ranged_weapon(self) -> bool:
        """Check if agent has a bow or ranged weapon equipped."""
        if not self.equipment:
            return False
        weapon = self.equipment.get_equipped_item('weapon')
        if not weapon:
            return False
        # Check if weapon name suggests ranged
        ranged_keywords = ['bow', 'crossbow', 'staff', 'wand']
        return any(kw in weapon.name.lower() for kw in ranged_keywords)

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

        # Update stun timer
        if self.stunned > 0:
            self.stunned -= 1

    def is_stunned(self) -> bool:
        """Check if agent is currently stunned."""
        return self.stunned > 0

    def apply_stun(self, frames: int):
        """Apply stun for given frames."""
        self.stunned = max(self.stunned, frames)

    def apply_wound(self, body_part: str):
        """Apply a wound to a body part."""
        import random
        from config import HEAD_WOUND_STUN_CHANCE

        self.wounds[body_part] = True

        # Head wound can cause stun
        if body_part == BODY_PART_HEAD:
            if random.random() < HEAD_WOUND_STUN_CHANCE:
                self.apply_stun(60)  # 1 second stun

    def clear_wounds(self):
        """Clear all wounds (for new floor/climb)."""
        self.wounds = {
            BODY_PART_HEAD: False,
            BODY_PART_BODY: False,
            BODY_PART_LEGS: False
        }
        self.stunned = 0

    def take_damage(self, amount: int) -> int:
        import random

        # Dodge check
        if random.random() < self.get_dodge_chance():
            return 0

        # Damage reduction (base + passive)
        reduction = self.get_damage_reduction()
        reduction += self.get_passive_bonus('damage_reduction')
        reduction = min(0.75, reduction)  # Cap at 75%

        # Active buff damage taken multipliers
        damage_taken_mult = 1.0
        for buff in self.active_buffs:
            if 'damage_taken_mult' in buff.get('effects', {}):
                damage_taken_mult *= buff['effects']['damage_taken_mult']

        actual_damage = int(amount * (1 - reduction) * damage_taken_mult)
        actual_damage = min(actual_damage, self.hp)

        self.hp -= actual_damage

        # Undead special - survive fatal hit once
        if self.hp <= 0 and self.race == 'undead' and self.undying_available:
            self.hp = 1
            self.undying_available = False

        # Second Wind passive - survive fatal hit once per floor
        if self.hp <= 0 and self.second_wind_available:
            self.hp = 1
            self.second_wind_available = False

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
        self.attack_height = 'mid'
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
        self.clear_wounds()

        # Reset skill state
        self.active_buffs = []
        self.regen_counter = 0
        self.second_wind_available = any(
            s.skill_id == 'second_wind' for s in self.passive_skills
        )
        for skill in self.active_skills:
            skill.cooldown_remaining = 0
        for skill in self.passive_skills:
            skill.reset_for_floor()

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
            'luck': self.luck,
            'active_skills': [s.to_dict() for s in self.active_skills],
            'passive_skills': [s.to_dict() for s in self.passive_skills],
            'unlocked_training': list(self.unlocked_training)
        }

    def load_stats_dict(self, data: dict):
        """Load agent stats."""
        from systems.skills import Skill

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

        # Load skills
        self.active_skills = []
        for skill_data in data.get('active_skills', []):
            try:
                self.active_skills.append(Skill.from_dict(skill_data))
            except KeyError:
                pass  # Skip invalid skills

        self.passive_skills = []
        for skill_data in data.get('passive_skills', []):
            try:
                self.passive_skills.append(Skill.from_dict(skill_data))
            except KeyError:
                pass  # Skip invalid skills

        # Load training unlocks
        self.unlocked_training = set(data.get('unlocked_training', []))

    def get_passive_bonus(self, stat: str) -> float:
        """Get total bonus from passive skills for a given stat."""
        total = 0.0
        for skill in self.passive_skills:
            if skill.data.get('effect') == 'stat_bonus':
                if skill.data.get('stat') == stat:
                    total += skill.data.get('value', 0)
            elif skill.data.get('effect') == 'conditional_damage':
                # Execute passive
                if stat == 'execute_threshold':
                    total = max(total, skill.data.get('hp_threshold', 0))
                elif stat == 'execute_mult':
                    total = max(total, skill.data.get('damage_mult', 1.0))
        return total

    def add_skill(self, skill) -> bool:
        """Add a skill to the agent. Returns True if successful."""
        from systems.skills import SKILL_TYPE_ACTIVE

        if skill.skill_type == SKILL_TYPE_ACTIVE:
            if len(self.active_skills) >= MAX_ACTIVE_SKILLS:
                return False
            # Check for duplicates
            if any(s.skill_id == skill.skill_id for s in self.active_skills):
                return False
            self.active_skills.append(skill)
        else:
            if len(self.passive_skills) >= MAX_PASSIVE_SKILLS:
                return False
            # Check for duplicates
            if any(s.skill_id == skill.skill_id for s in self.passive_skills):
                return False
            self.passive_skills.append(skill)
            # Check for second wind
            if skill.skill_id == 'second_wind':
                self.second_wind_available = True
        return True

    def remove_skill(self, skill_id: str, skill_type: str) -> bool:
        """Remove a skill by ID. Returns True if removed."""
        from systems.skills import SKILL_TYPE_ACTIVE

        if skill_type == SKILL_TYPE_ACTIVE:
            for i, skill in enumerate(self.active_skills):
                if skill.skill_id == skill_id:
                    self.active_skills.pop(i)
                    return True
        else:
            for i, skill in enumerate(self.passive_skills):
                if skill.skill_id == skill_id:
                    self.passive_skills.pop(i)
                    return True
        return False

    def remove_random_passive(self) -> str:
        """Remove a random passive skill. Returns the skill name or None."""
        import random
        if not self.passive_skills:
            return None
        skill = random.choice(self.passive_skills)
        self.passive_skills.remove(skill)
        return skill.name

    def reduce_random_stat(self) -> str:
        """Reduce a random stat by 1. Returns the stat name or None."""
        import random

        # Find stats above their base that can be reduced
        reducible = []
        if self.strength > AGENT_BASE_STRENGTH:
            reducible.append('strength')
        if self.intelligence > AGENT_BASE_INTELLIGENCE:
            reducible.append('intelligence')
        if self.agility > AGENT_BASE_AGILITY:
            reducible.append('agility')
        if self.defense > AGENT_BASE_DEFENSE:
            reducible.append('defense')
        if self.luck > AGENT_BASE_LUCK:
            reducible.append('luck')

        if not reducible:
            return None

        stat = random.choice(reducible)
        if stat == 'strength':
            self.strength -= 1
        elif stat == 'intelligence':
            self.intelligence -= 1
        elif stat == 'agility':
            self.agility -= 1
        elif stat == 'defense':
            self.defense -= 1
        elif stat == 'luck':
            self.luck -= 1

        return stat

    def unlock_training(self, stat: str):
        """Unlock training for a stat."""
        self.unlocked_training.add(stat)

    def is_training_unlocked(self, stat: str) -> bool:
        """Check if training is unlocked for a stat."""
        return stat in self.unlocked_training

    def update_skill_cooldowns(self):
        """Update cooldowns for all active skills."""
        for skill in self.active_skills:
            skill.update_cooldown()

    def update_buffs(self):
        """Update active buff durations."""
        for buff in self.active_buffs[:]:  # Copy list to allow removal
            buff['frames_remaining'] -= 1
            if buff['frames_remaining'] <= 0:
                self.active_buffs.remove(buff)

    def update_regen(self):
        """Update HP regeneration from passive skills."""
        for skill in self.passive_skills:
            if skill.data.get('effect') == 'regen':
                self.regen_counter += 1
                tick_frames = skill.data.get('tick_frames', 120)
                if self.regen_counter >= tick_frames:
                    self.regen_counter = 0
                    hp_heal = skill.data.get('hp_per_tick', 1)
                    self.heal(hp_heal)
                break  # Only one regen at a time

    def get_lifesteal_percent(self) -> float:
        """Get lifesteal percentage from passive skills."""
        for skill in self.passive_skills:
            if skill.data.get('effect') == 'on_hit':
                return skill.data.get('heal_percent', 0)
        return 0

    def get_thorns_percent(self) -> float:
        """Get thorns reflection percentage from passive skills."""
        for skill in self.passive_skills:
            if skill.data.get('effect') == 'on_hit_taken':
                return skill.data.get('reflect_percent', 0)
        return 0

    def get_drop_rate_bonus(self) -> float:
        """Get drop rate bonus from passive skills."""
        return self.get_passive_bonus('drop_rate_bonus')

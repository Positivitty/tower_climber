"""Skill system for active and passive abilities."""

import random

# Skill types
SKILL_TYPE_ACTIVE = 'active'
SKILL_TYPE_PASSIVE = 'passive'

# Active skill definitions
ACTIVE_SKILLS = {
    'fireball': {
        'name': 'Fireball',
        'description': 'Hurl a fireball dealing 150% STR damage',
        'cooldown_frames': 300,  # 5 seconds
        'effect': 'damage',
        'damage_mult': 1.5,
        'range': 200,
        'rarity': 'rare'
    },
    'heal': {
        'name': 'Healing Light',
        'description': 'Restore 25% of max HP',
        'cooldown_frames': 600,  # 10 seconds
        'effect': 'heal',
        'heal_percent': 0.25,
        'rarity': 'epic'
    },
    'dash_attack': {
        'name': 'Shadow Dash',
        'description': 'Dash forward dealing 80% damage',
        'cooldown_frames': 240,  # 4 seconds
        'effect': 'dash_damage',
        'damage_mult': 0.8,
        'dash_distance': 150,
        'rarity': 'rare'
    },
    'lightning_strike': {
        'name': 'Lightning Strike',
        'description': 'Strike all enemies for 60% damage',
        'cooldown_frames': 360,  # 6 seconds
        'effect': 'aoe_damage',
        'damage_mult': 0.6,
        'rarity': 'epic'
    },
    'shield_bash': {
        'name': 'Shield Bash',
        'description': 'Stun nearest enemy for 2 seconds',
        'cooldown_frames': 480,  # 8 seconds
        'effect': 'stun',
        'stun_frames': 120,
        'rarity': 'uncommon'
    },
    'berserker_rage': {
        'name': 'Berserker Rage',
        'description': '+50% damage for 5s, +25% damage taken',
        'cooldown_frames': 720,  # 12 seconds
        'effect': 'buff',
        'duration_frames': 300,
        'damage_mult_bonus': 0.5,
        'damage_taken_mult': 1.25,
        'rarity': 'legendary'
    },
    'vampiric_strike': {
        'name': 'Vampiric Strike',
        'description': 'Attack, heal for 50% of damage dealt',
        'cooldown_frames': 420,  # 7 seconds
        'effect': 'lifesteal_attack',
        'damage_mult': 1.0,
        'lifesteal_percent': 0.5,
        'rarity': 'epic'
    }
}

# Passive skill definitions
PASSIVE_SKILLS = {
    'crit_boost': {
        'name': 'Critical Eye',
        'description': '+10% critical hit chance',
        'effect': 'stat_bonus',
        'stat': 'crit_chance',
        'value': 0.10,
        'rarity': 'uncommon'
    },
    'lifesteal': {
        'name': 'Vampirism',
        'description': 'Heal for 5% of damage dealt',
        'effect': 'on_hit',
        'heal_percent': 0.05,
        'rarity': 'rare'
    },
    'thorns': {
        'name': 'Thorns Aura',
        'description': 'Reflect 20% of melee damage taken',
        'effect': 'on_hit_taken',
        'reflect_percent': 0.20,
        'rarity': 'rare'
    },
    'dodge_boost': {
        'name': 'Evasion',
        'description': '+8% dodge chance',
        'effect': 'stat_bonus',
        'stat': 'dodge_chance',
        'value': 0.08,
        'rarity': 'uncommon'
    },
    'hp_regen': {
        'name': 'Regeneration',
        'description': 'Regenerate 1 HP every 2 seconds',
        'effect': 'regen',
        'hp_per_tick': 1,
        'tick_frames': 120,
        'rarity': 'uncommon'
    },
    'damage_boost': {
        'name': 'Power Surge',
        'description': '+15% base damage',
        'effect': 'stat_bonus',
        'stat': 'damage_mult',
        'value': 0.15,
        'rarity': 'rare'
    },
    'defense_boost': {
        'name': 'Iron Skin',
        'description': '+10% damage reduction',
        'effect': 'stat_bonus',
        'stat': 'damage_reduction',
        'value': 0.10,
        'rarity': 'uncommon'
    },
    'lucky_drops': {
        'name': 'Fortune',
        'description': '+25% item drop rate',
        'effect': 'stat_bonus',
        'stat': 'drop_rate_bonus',
        'value': 0.25,
        'rarity': 'rare'
    },
    'execute': {
        'name': 'Executioner',
        'description': '+50% damage to enemies below 25% HP',
        'effect': 'conditional_damage',
        'hp_threshold': 0.25,
        'damage_mult': 1.5,
        'rarity': 'epic'
    },
    'second_wind': {
        'name': 'Second Wind',
        'description': 'Survive fatal hit once per floor with 1 HP',
        'effect': 'death_save',
        'rarity': 'legendary'
    }
}

# Rarity colors for display
SKILL_RARITY_COLORS = {
    'common': (200, 200, 200),
    'uncommon': (50, 200, 50),
    'rare': (50, 100, 200),
    'epic': (150, 50, 200),
    'legendary': (255, 200, 50)
}


class Skill:
    """Represents a skill (active or passive)."""

    def __init__(self, skill_id: str, skill_type: str):
        self.skill_id = skill_id
        self.skill_type = skill_type

        # Get definition
        if skill_type == SKILL_TYPE_ACTIVE:
            self.data = ACTIVE_SKILLS[skill_id]
        else:
            self.data = PASSIVE_SKILLS[skill_id]

        self.name = self.data['name']
        self.description = self.data['description']
        self.rarity = self.data['rarity']

        # Active skill state
        self.cooldown_remaining = 0

        # Passive skill state (for per-floor effects)
        self.used_this_floor = False

    def is_ready(self) -> bool:
        """Check if active skill is ready to use."""
        return self.skill_type == SKILL_TYPE_ACTIVE and self.cooldown_remaining <= 0

    def start_cooldown(self):
        """Start the cooldown for an active skill."""
        if self.skill_type == SKILL_TYPE_ACTIVE:
            self.cooldown_remaining = self.data.get('cooldown_frames', 300)

    def update_cooldown(self):
        """Decrement cooldown by 1 frame."""
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1

    def reset_for_floor(self):
        """Reset per-floor state."""
        self.used_this_floor = False

    def get_color(self) -> tuple:
        """Get display color based on rarity."""
        return SKILL_RARITY_COLORS.get(self.rarity, (200, 200, 200))

    def to_dict(self) -> dict:
        """Serialize skill to dictionary."""
        return {
            'skill_id': self.skill_id,
            'skill_type': self.skill_type,
            'cooldown_remaining': self.cooldown_remaining,
            'used_this_floor': self.used_this_floor
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Skill':
        """Deserialize skill from dictionary."""
        skill = cls(data['skill_id'], data['skill_type'])
        skill.cooldown_remaining = data.get('cooldown_remaining', 0)
        skill.used_this_floor = data.get('used_this_floor', False)
        return skill


def generate_random_skill(floor_level: int) -> Skill:
    """Generate a random skill based on floor level."""
    # 50/50 active vs passive
    if random.random() < 0.5:
        skill_type = SKILL_TYPE_ACTIVE
        skills = ACTIVE_SKILLS
    else:
        skill_type = SKILL_TYPE_PASSIVE
        skills = PASSIVE_SKILLS

    # Filter by rarity based on floor
    eligible_skills = []
    for skill_id, skill_data in skills.items():
        rarity = skill_data['rarity']
        # Legendary requires floor 5+
        if rarity == 'legendary' and floor_level < 5:
            continue
        # Epic requires floor 3+
        if rarity == 'epic' and floor_level < 3:
            continue
        # Rare requires floor 2+
        if rarity == 'rare' and floor_level < 2:
            continue
        eligible_skills.append(skill_id)

    if not eligible_skills:
        # Fallback to any uncommon/common skill
        eligible_skills = [
            sid for sid, sd in skills.items()
            if sd['rarity'] in ['common', 'uncommon']
        ]

    if eligible_skills:
        chosen_id = random.choice(eligible_skills)
        return Skill(chosen_id, skill_type)

    return None

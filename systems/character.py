"""Character system - races, classes, and items."""

import random


# Race definitions
RACES = {
    'human': {
        'name': 'Human',
        'description': 'Balanced stats, fast learner',
        'stat_bonuses': {'strength': 1, 'intelligence': 1, 'agility': 1, 'defense': 1, 'luck': 1},
        'special': 'Adaptable: +20% experience gain',
        'color': (200, 180, 160)
    },
    'undead': {
        'name': 'Undead',
        'description': 'High defense, slow but relentless',
        'stat_bonuses': {'strength': 2, 'intelligence': 0, 'agility': -1, 'defense': 3, 'luck': 0},
        'special': 'Undying: Survive one fatal hit per floor',
        'color': (100, 120, 100)
    },
    'demon': {
        'name': 'Demon',
        'description': 'High damage, risky playstyle',
        'stat_bonuses': {'strength': 4, 'intelligence': 1, 'agility': 1, 'defense': -2, 'luck': 0},
        'special': 'Bloodlust: Deal +50% damage below 30% HP',
        'color': (180, 60, 60)
    },
    'angel': {
        'name': 'Angel',
        'description': 'High luck and intelligence',
        'stat_bonuses': {'strength': 0, 'intelligence': 3, 'agility': 1, 'defense': 0, 'luck': 3},
        'special': 'Divine: Heal 10% HP after each floor',
        'color': (220, 220, 180)
    }
}

# Class definitions
CLASSES = {
    'knight': {
        'name': 'Knight',
        'description': 'Tank with high defense',
        'stat_bonuses': {'strength': 2, 'intelligence': 0, 'agility': 0, 'defense': 3, 'luck': 0},
        'hp_bonus': 30,
        'special': 'Shield Wall: Block attacks more easily',
        'color_modifier': (0, -20, 40)
    },
    'wizard': {
        'name': 'Wizard',
        'description': 'High intelligence, learns fast',
        'stat_bonuses': {'strength': 0, 'intelligence': 4, 'agility': 1, 'defense': 0, 'luck': 0},
        'hp_bonus': -10,
        'special': 'Arcane Mind: Double learning rate',
        'color_modifier': (40, 0, 60)
    },
    'assassin': {
        'name': 'Assassin',
        'description': 'Fast and deadly criticals',
        'stat_bonuses': {'strength': 1, 'intelligence': 0, 'agility': 4, 'defense': -1, 'luck': 2},
        'hp_bonus': 0,
        'special': 'Shadow Strike: Higher crit chance',
        'color_modifier': (-30, -30, -30)
    },
    'monk': {
        'name': 'Monk',
        'description': 'Balanced fighter with dodge',
        'stat_bonuses': {'strength': 1, 'intelligence': 1, 'agility': 2, 'defense': 1, 'luck': 1},
        'hp_bonus': 10,
        'special': 'Inner Peace: Better at training mini-games',
        'color_modifier': (30, 20, 0)
    }
}

# Item definitions
ITEM_RARITIES = {
    'common': {'color': (200, 200, 200), 'stat_mult': 1.0},
    'uncommon': {'color': (50, 200, 50), 'stat_mult': 1.5},
    'rare': {'color': (50, 100, 200), 'stat_mult': 2.0},
    'epic': {'color': (150, 50, 200), 'stat_mult': 3.0},
    'legendary': {'color': (255, 200, 50), 'stat_mult': 5.0}
}

ITEM_TYPES = {
    'weapon': {
        'slot': 'weapon',
        'primary_stat': 'strength',
        'secondary_stats': ['agility', 'luck']
    },
    'armor': {
        'slot': 'armor',
        'primary_stat': 'defense',
        'secondary_stats': ['strength', 'agility']
    },
    'accessory': {
        'slot': 'accessory',
        'primary_stat': 'luck',
        'secondary_stats': ['intelligence', 'agility']
    }
}

WEAPON_NAMES = ['Sword', 'Axe', 'Dagger', 'Staff', 'Mace', 'Spear', 'Bow', 'Claws']
ARMOR_NAMES = ['Plate', 'Mail', 'Leather', 'Robe', 'Scale', 'Hide']
ACCESSORY_NAMES = ['Ring', 'Amulet', 'Bracelet', 'Belt', 'Cloak', 'Charm']
PREFIXES = ['Mighty', 'Swift', 'Wise', 'Lucky', 'Ancient', 'Cursed', 'Blessed', 'Dark', 'Light', 'Burning', 'Frozen']


class Item:
    """An equipment item."""

    def __init__(self, item_type: str, floor_level: int = 1):
        self.item_type = item_type
        self.slot = ITEM_TYPES[item_type]['slot']

        # Determine rarity based on floor
        self.rarity = self._roll_rarity(floor_level)

        # Generate name
        self.name = self._generate_name()

        # Generate stats
        self.stats = self._generate_stats(floor_level)

    def _roll_rarity(self, floor_level: int) -> str:
        roll = random.random()
        legendary_chance = 0.01 + floor_level * 0.002
        epic_chance = 0.05 + floor_level * 0.005
        rare_chance = 0.15 + floor_level * 0.01
        uncommon_chance = 0.35

        if roll < legendary_chance:
            return 'legendary'
        elif roll < legendary_chance + epic_chance:
            return 'epic'
        elif roll < legendary_chance + epic_chance + rare_chance:
            return 'rare'
        elif roll < legendary_chance + epic_chance + rare_chance + uncommon_chance:
            return 'uncommon'
        return 'common'

    def _generate_name(self) -> str:
        if self.item_type == 'weapon':
            base = random.choice(WEAPON_NAMES)
        elif self.item_type == 'armor':
            base = random.choice(ARMOR_NAMES)
        else:
            base = random.choice(ACCESSORY_NAMES)

        if self.rarity in ['rare', 'epic', 'legendary']:
            prefix = random.choice(PREFIXES)
            return f"{prefix} {base}"
        return base

    def _generate_stats(self, floor_level: int) -> dict:
        stats = {}
        type_info = ITEM_TYPES[self.item_type]
        mult = ITEM_RARITIES[self.rarity]['stat_mult']

        # Primary stat
        base_value = 1 + floor_level // 2
        stats[type_info['primary_stat']] = int(base_value * mult)

        # Secondary stats for rare+
        if self.rarity in ['rare', 'epic', 'legendary']:
            secondary = random.choice(type_info['secondary_stats'])
            stats[secondary] = int(base_value * mult * 0.5)

        return stats

    def get_color(self) -> tuple:
        return ITEM_RARITIES[self.rarity]['color']

    def get_description(self) -> str:
        stat_str = ', '.join(f"+{v} {k[:3].upper()}" for k, v in self.stats.items())
        return f"{self.name} ({self.rarity.title()}) - {stat_str}"

    def to_dict(self) -> dict:
        return {
            'item_type': self.item_type,
            'slot': self.slot,
            'name': self.name,
            'rarity': self.rarity,
            'stats': self.stats
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        item = cls.__new__(cls)
        item.item_type = data['item_type']
        item.slot = data['slot']
        item.name = data['name']
        item.rarity = data['rarity']
        item.stats = data['stats']
        return item


class Equipment:
    """Manages equipped items."""

    def __init__(self):
        self.slots = {
            'weapon': None,
            'armor': None,
            'accessory': None
        }
        self.inventory = []  # Unequipped items

    def equip(self, item: Item) -> Item:
        """Equip an item, returns the previously equipped item (if any)."""
        old_item = self.slots[item.slot]
        self.slots[item.slot] = item

        # Remove from inventory if it was there
        if item in self.inventory:
            self.inventory.remove(item)

        # Add old item to inventory
        if old_item:
            self.inventory.append(old_item)

        return old_item

    def unequip(self, slot: str) -> Item:
        """Unequip an item from a slot."""
        item = self.slots[slot]
        if item:
            self.slots[slot] = None
            self.inventory.append(item)
        return item

    def add_to_inventory(self, item: Item):
        """Add item to inventory without equipping."""
        self.inventory.append(item)

    def get_total_stats(self) -> dict:
        """Get combined stats from all equipped items."""
        total = {}
        for item in self.slots.values():
            if item:
                for stat, value in item.stats.items():
                    total[stat] = total.get(stat, 0) + value
        return total

    def get_equipped_item(self, slot: str) -> Item:
        return self.slots.get(slot)

    def to_dict(self) -> dict:
        return {
            'slots': {k: v.to_dict() if v else None for k, v in self.slots.items()},
            'inventory': [i.to_dict() for i in self.inventory]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Equipment':
        eq = cls()
        for slot, item_data in data.get('slots', {}).items():
            if item_data:
                eq.slots[slot] = Item.from_dict(item_data)
        eq.inventory = [Item.from_dict(i) for i in data.get('inventory', [])]
        return eq


def generate_loot(floor_level: int, enemy_type: str = 'melee') -> list:
    """Generate random loot drops."""
    drops = []

    # Drop chance based on floor
    drop_chance = 0.3 + floor_level * 0.02

    if random.random() < drop_chance:
        # Choose item type
        if enemy_type == 'melee':
            item_type = random.choice(['weapon', 'armor'])
        else:
            item_type = random.choice(['weapon', 'accessory'])

        drops.append(Item(item_type, floor_level))

    return drops


def apply_race_class_bonuses(agent, race: str, char_class: str):
    """Apply race and class stat bonuses to agent."""
    race_data = RACES.get(race, RACES['human'])
    class_data = CLASSES.get(char_class, CLASSES['knight'])

    # Apply race bonuses
    for stat, bonus in race_data['stat_bonuses'].items():
        current = agent.get_stat(stat)
        setattr(agent, stat, current + bonus)

    # Apply class bonuses
    for stat, bonus in class_data['stat_bonuses'].items():
        current = agent.get_stat(stat)
        setattr(agent, stat, current + bonus)

    # Apply HP bonus
    agent.max_hp += class_data.get('hp_bonus', 0)
    agent.hp = agent.max_hp


def get_character_color(race: str, char_class: str) -> tuple:
    """Get character color based on race and class."""
    race_color = RACES.get(race, RACES['human'])['color']
    class_mod = CLASSES.get(char_class, CLASSES['knight'])['color_modifier']

    return (
        max(0, min(255, race_color[0] + class_mod[0])),
        max(0, min(255, race_color[1] + class_mod[1])),
        max(0, min(255, race_color[2] + class_mod[2]))
    )

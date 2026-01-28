"""Critical moment detection for triggering conversations."""

from config import (
    TRIGGER_LOW_HP, TRIGGER_NEAR_DEATH, TRIGGER_BOSS_ENCOUNTER,
    TRIGGER_FIRST_ENEMY_TYPE, TRIGGER_VICTORY, TRIGGER_DEATH,
    TRIGGER_CLOSE_CALL, TRIGGER_STRATEGY_QUESTION,
    CLOSE_CALL_COOLDOWN_FRAMES, STRATEGY_QUESTION_MIN_FLOORS
)


class CriticalMomentDetector:
    """Detects critical moments that should trigger conversations."""

    def __init__(self):
        # Track what we've seen (persists across floors)
        self.seen_enemy_types = set()
        self.seen_boss_types = set()

        # Per-floor tracking
        self.low_hp_triggered_this_floor = False
        self.near_death_triggered_this_combat = False

        # Cooldown tracking
        self.close_call_cooldown = 0
        self.floors_since_strategy_question = 0

        # Track last HP for near-death detection
        self.last_hp_ratio = 1.0

        # Track pending triggers (to be processed by game)
        self.pending_trigger = None
        self.pending_trigger_data = {}

    def reset_for_floor(self):
        """Reset per-floor state."""
        self.low_hp_triggered_this_floor = False
        self.floors_since_strategy_question += 1

    def reset_for_combat(self):
        """Reset per-combat state."""
        self.near_death_triggered_this_combat = False
        self.last_hp_ratio = 1.0

    def update(self, dt: int = 1):
        """Update cooldowns."""
        if self.close_call_cooldown > 0:
            self.close_call_cooldown -= dt

    def check_low_hp(self, agent) -> bool:
        """Check if HP dropped below 25% (once per floor)."""
        if self.low_hp_triggered_this_floor:
            return False

        hp_ratio = agent.hp / agent.max_hp if agent.max_hp > 0 else 0

        if hp_ratio < 0.25:
            self.low_hp_triggered_this_floor = True
            self.pending_trigger = TRIGGER_LOW_HP
            self.pending_trigger_data = {
                'hp': agent.hp,
                'max_hp': agent.max_hp,
                'hp_ratio': hp_ratio
            }
            return True

        return False

    def check_near_death(self, agent, damage_taken: int) -> bool:
        """Check if survived with <10% HP (once per combat)."""
        if self.near_death_triggered_this_combat:
            return False

        hp_ratio = agent.hp / agent.max_hp if agent.max_hp > 0 else 0
        prev_ratio = self.last_hp_ratio
        self.last_hp_ratio = hp_ratio

        # Survived a hit that brought us below 10%
        if hp_ratio < 0.1 and hp_ratio > 0 and prev_ratio >= 0.1:
            self.near_death_triggered_this_combat = True
            self.pending_trigger = TRIGGER_NEAR_DEATH
            self.pending_trigger_data = {
                'hp': agent.hp,
                'max_hp': agent.max_hp,
                'damage_taken': damage_taken
            }
            return True

        return False

    def check_boss_encounter(self, enemy) -> bool:
        """Check if this is first time seeing this boss type."""
        if enemy.enemy_type != 'boss':
            return False

        boss_name = getattr(enemy, 'name', 'Unknown Boss')
        if boss_name in self.seen_boss_types:
            return False

        self.seen_boss_types.add(boss_name)
        self.pending_trigger = TRIGGER_BOSS_ENCOUNTER
        self.pending_trigger_data = {
            'boss_name': boss_name,
            'boss_element': enemy.element
        }
        return True

    def check_first_enemy_type(self, enemy) -> bool:
        """Check if this is first time seeing this enemy type."""
        enemy_key = f"{enemy.enemy_type}_{enemy.element or 'none'}"

        if enemy_key in self.seen_enemy_types:
            return False

        self.seen_enemy_types.add(enemy_key)
        self.pending_trigger = TRIGGER_FIRST_ENEMY_TYPE
        self.pending_trigger_data = {
            'enemy_type': enemy.enemy_type,
            'enemy_element': enemy.element
        }
        return True

    def trigger_victory(self, floor: int, enemies_defeated: int):
        """Trigger victory conversation."""
        self.pending_trigger = TRIGGER_VICTORY
        self.pending_trigger_data = {
            'floor': floor,
            'enemies_defeated': enemies_defeated
        }
        self.reset_for_floor()

    def trigger_death(self, floor: int, killer_type: str = None):
        """Trigger death conversation."""
        self.pending_trigger = TRIGGER_DEATH
        self.pending_trigger_data = {
            'floor': floor,
            'killer_type': killer_type
        }

    def check_close_call(self, agent, attack_damage: int) -> bool:
        """Check if dodged a lethal attack."""
        if self.close_call_cooldown > 0:
            return False

        # Would the attack have killed us?
        if attack_damage >= agent.hp:
            self.close_call_cooldown = CLOSE_CALL_COOLDOWN_FRAMES
            self.pending_trigger = TRIGGER_CLOSE_CALL
            self.pending_trigger_data = {
                'damage_avoided': attack_damage,
                'current_hp': agent.hp
            }
            return True

        return False

    def check_strategy_question(self, force: bool = False) -> bool:
        """Check if it's time for a strategy question."""
        import random

        if force:
            should_trigger = True
        elif self.floors_since_strategy_question >= STRATEGY_QUESTION_MIN_FLOORS:
            # Random chance after minimum floors
            should_trigger = random.random() < 0.3
        else:
            should_trigger = False

        if should_trigger:
            self.floors_since_strategy_question = 0
            self.pending_trigger = TRIGGER_STRATEGY_QUESTION
            self.pending_trigger_data = {}
            return True

        return False

    def get_pending_trigger(self):
        """Get and clear the pending trigger."""
        trigger = self.pending_trigger
        data = self.pending_trigger_data

        self.pending_trigger = None
        self.pending_trigger_data = {}

        return trigger, data

    def has_pending_trigger(self) -> bool:
        """Check if there's a pending trigger."""
        return self.pending_trigger is not None

    def check_enemies_for_firsts(self, enemies: list) -> bool:
        """Check all enemies for first-time encounters."""
        for enemy in enemies:
            if not enemy.is_alive():
                continue

            # Check boss first (higher priority)
            if enemy.enemy_type == 'boss':
                if self.check_boss_encounter(enemy):
                    return True
            else:
                if self.check_first_enemy_type(enemy):
                    return True

        return False

    def get_state_dict(self) -> dict:
        """Get state for serialization."""
        return {
            'seen_enemy_types': list(self.seen_enemy_types),
            'seen_boss_types': list(self.seen_boss_types),
            'floors_since_strategy': self.floors_since_strategy_question
        }

    def load_state_dict(self, data: dict):
        """Load state from serialized data."""
        self.seen_enemy_types = set(data.get('seen_enemy_types', []))
        self.seen_boss_types = set(data.get('seen_boss_types', []))
        self.floors_since_strategy_question = data.get('floors_since_strategy', 0)

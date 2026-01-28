"""AI dialogue system - the AI thinks out loud and asks for suggestions."""

import random
from config import (
    TRAINABLE_STATS,
    DIALOGUE_GLOBAL_COOLDOWN,
    DIALOGUE_COMBAT_COOLDOWN,
    DIALOGUE_HP_WARNING_COOLDOWN,
    DIALOGUE_EXPLORATION_COOLDOWN,
    DIALOGUE_MAX_COMBAT_MESSAGES
)


# Message categories for cooldown tracking
CATEGORY_COMBAT = 'combat'
CATEGORY_HP_WARNING = 'hp_warning'
CATEGORY_EXPLORATION = 'exploration'
CATEGORY_SYSTEM = 'system'  # Always shows (no cooldown)


class AIDialogue:
    """Manages AI thoughts and dialogue with the player."""

    def __init__(self):
        self.messages = []
        self.max_messages = 20
        self.waiting_for_suggestion = False
        self.suggestion_options = []

        # Spam reduction
        self.global_cooldown = 0
        self.category_cooldowns = {
            CATEGORY_COMBAT: 0,
            CATEGORY_HP_WARNING: 0,
            CATEGORY_EXPLORATION: 0,
        }
        self.combat_message_count = 0

    def update(self, dt: int = 1):
        """Update cooldowns."""
        if self.global_cooldown > 0:
            self.global_cooldown -= dt

        for category in self.category_cooldowns:
            if self.category_cooldowns[category] > 0:
                self.category_cooldowns[category] -= dt

    def reset_for_combat(self):
        """Reset combat-specific counters."""
        self.combat_message_count = 0

    def can_add_message(self, category: str = CATEGORY_SYSTEM, is_critical: bool = False) -> bool:
        """Check if a message can be added based on cooldowns."""
        # Critical messages always show
        if is_critical or category == CATEGORY_SYSTEM:
            return True

        # Check global cooldown
        if self.global_cooldown > 0:
            return False

        # Check category cooldown
        if category in self.category_cooldowns:
            if self.category_cooldowns[category] > 0:
                return False

        # Check combat message limit
        if category == CATEGORY_COMBAT:
            if self.combat_message_count >= DIALOGUE_MAX_COMBAT_MESSAGES:
                return False

        return True

    def _apply_cooldowns(self, category: str):
        """Apply cooldowns after adding a message."""
        self.global_cooldown = DIALOGUE_GLOBAL_COOLDOWN

        if category == CATEGORY_COMBAT:
            self.category_cooldowns[CATEGORY_COMBAT] = DIALOGUE_COMBAT_COOLDOWN
            self.combat_message_count += 1
        elif category == CATEGORY_HP_WARNING:
            self.category_cooldowns[CATEGORY_HP_WARNING] = DIALOGUE_HP_WARNING_COOLDOWN
        elif category == CATEGORY_EXPLORATION:
            self.category_cooldowns[CATEGORY_EXPLORATION] = DIALOGUE_EXPLORATION_COOLDOWN

    def add_thought(self, message: str, category: str = CATEGORY_SYSTEM, is_critical: bool = False):
        """Add a thought message with spam reduction."""
        if not self.can_add_message(category, is_critical):
            return False

        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

        self._apply_cooldowns(category)
        return True

    def add_critical_thought(self, message: str):
        """Add a critical thought that bypasses cooldowns."""
        return self.add_thought(message, CATEGORY_SYSTEM, is_critical=True)

    def get_recent_messages(self, count: int = 4) -> list:
        """Get the most recent messages."""
        return self.messages[-count:]

    def clear(self):
        """Clear all messages."""
        self.messages = []

    def think_about_combat(self, state: tuple, action: str, q_values: dict):
        """Generate thoughts about combat decisions with spam reduction."""
        hp_names = ['high', 'medium', 'low', 'critical']
        enemy_names = ['melee', 'ranged', 'none']
        threat_names = ['low', 'medium', 'high']

        hp = hp_names[state[0]] if state[0] < len(hp_names) else 'unknown'
        enemy = enemy_names[state[1]] if state[1] < len(enemy_names) else 'unknown'
        threat = threat_names[state[2]] if state[2] < len(threat_names) else 'unknown'
        in_range = state[3] == 1 if len(state) > 3 else False

        # HP warnings use HP_WARNING category (longer cooldown)
        if hp == 'critical':
            self.add_thought("My HP is critical! Need to be careful...", CATEGORY_HP_WARNING)
        elif hp == 'low':
            self.add_thought("HP getting low. Should I retreat?", CATEGORY_HP_WARNING)

        # Combat observations use COMBAT category
        if enemy == 'ranged' and not in_range:
            self.add_thought("Ranged enemy - need to close distance.", CATEGORY_COMBAT)
        elif enemy == 'melee' and in_range:
            self.add_thought("Melee enemy in range.", CATEGORY_COMBAT)

        if threat == 'high':
            self.add_thought("High threat detected!", CATEGORY_COMBAT)

        # Only occasionally explain the decision (reduce spam)
        if random.random() < 0.2:  # 20% chance to explain
            attack_q = q_values.get(0, 0)
            run_q = q_values.get(1, 0)

            if 'ATTACK' in action or 'ATK' in action:
                if attack_q > run_q:
                    self.add_thought(f"Attacking (Q:{attack_q:.1f}).", CATEGORY_COMBAT)
            elif action == 'RUN':
                if run_q > attack_q:
                    self.add_thought(f"Retreating (Q:{run_q:.1f}).", CATEGORY_COMBAT)
            elif action == 'DODGE':
                self.add_thought("Dodging!", CATEGORY_COMBAT)
            elif action == 'PARRY':
                self.add_thought("Parrying!", CATEGORY_COMBAT)

    def think_about_base(self, agent, epsilon: float):
        """Generate thoughts about base decisions."""
        # Analyze stats
        stats = {
            'strength': agent.strength,
            'intelligence': agent.intelligence,
            'agility': agent.agility,
            'defense': agent.defense,
            'luck': agent.luck
        }

        min_stat = min(stats, key=stats.get)
        max_stat = max(stats, key=stats.get)

        self.add_critical_thought("At base camp.")

        if stats[min_stat] < stats[max_stat] - 3:
            self.add_thought(f"My {min_stat} ({stats[min_stat]}) is lower than {max_stat} ({stats[max_stat]}).", CATEGORY_EXPLORATION)

        if epsilon > 0.5:
            self.add_thought("Still exploring strategies.", CATEGORY_EXPLORATION)
        elif epsilon > 0.2:
            self.add_thought("Getting better at this.", CATEGORY_EXPLORATION)
        else:
            self.add_thought("Making informed decisions now.", CATEGORY_EXPLORATION)

    def think_about_training(self, stat: str, difficulty: int):
        """Generate thoughts about starting training."""
        stat_descriptions = {
            'strength': "Time to lift some weights!",
            'intelligence': "Pattern memory training.",
            'agility': "Reaction training!",
            'defense': "Block training.",
            'luck': "Dice game!"
        }

        self.add_critical_thought(f"Training {stat.upper()} (difficulty {difficulty})...")
        self.add_thought(stat_descriptions.get(stat, "Here we go..."), CATEGORY_EXPLORATION)

    def think_about_minigame(self, game_state: tuple, action: str, stat: str):
        """Generate thoughts during a mini-game (reduced frequency)."""
        # Only generate thoughts occasionally to reduce spam
        if random.random() > 0.15:  # 15% chance
            return

        if stat == 'strength':
            if len(game_state) > 2 and game_state[2] == 1:  # In perfect zone
                self.add_thought("Perfect zone! NOW!", CATEGORY_COMBAT)
            elif len(game_state) > 1 and game_state[1] == 1:  # In target
                self.add_thought("In the zone...", CATEGORY_COMBAT)

        elif stat == 'agility':
            if len(game_state) > 0 and game_state[0] == 1:  # Signal active
                self.add_thought("SIGNAL!", CATEGORY_COMBAT)

        elif stat == 'defense':
            if len(game_state) > 2 and game_state[2] == 1:  # In block window
                self.add_thought("Block NOW!", CATEGORY_COMBAT)

    def think_about_result(self, success: bool, perfect: bool, message: str):
        """Generate thoughts about a training result."""
        if perfect:
            self.add_critical_thought("PERFECT!")
        elif success:
            self.add_critical_thought("Success!")
        else:
            self.add_critical_thought("Failed...")

        self.add_critical_thought(message)

    def ask_for_suggestion(self, context: str, options: list):
        """Ask the player for a suggestion."""
        self.waiting_for_suggestion = True
        self.suggestion_options = options

        self.add_thought(f"Hmm, {context}")
        self.add_thought("What do you think I should do? (Press 1-" + str(len(options)) + ")")

        for i, opt in enumerate(options):
            self.add_thought(f"  {i+1}. {opt}")

    def receive_suggestion(self, choice: int) -> str:
        """Receive a suggestion from the player."""
        if not self.waiting_for_suggestion or choice < 0 or choice >= len(self.suggestion_options):
            return None

        suggestion = self.suggestion_options[choice]
        self.waiting_for_suggestion = False
        self.suggestion_options = []

        self.add_thought(f"Good idea! I'll {suggestion.lower()}.")
        return suggestion

    def cancel_suggestion(self):
        """Cancel waiting for suggestion (AI decides on its own)."""
        if self.waiting_for_suggestion:
            self.add_thought("No input? I'll decide on my own then.")
            self.waiting_for_suggestion = False
            self.suggestion_options = []

"""AI dialogue system - the AI thinks out loud and asks for suggestions."""

import random
from config import TRAINABLE_STATS


class AIDialogue:
    """Manages AI thoughts and dialogue with the player."""

    def __init__(self):
        self.messages = []
        self.max_messages = 20
        self.waiting_for_suggestion = False
        self.suggestion_options = []

    def add_thought(self, message: str):
        """Add a thought message."""
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def get_recent_messages(self, count: int = 4) -> list:
        """Get the most recent messages."""
        return self.messages[-count:]

    def clear(self):
        """Clear all messages."""
        self.messages = []

    def think_about_combat(self, state: tuple, action: str, q_values: dict):
        """Generate thoughts about combat decisions."""
        hp_names = ['high', 'medium', 'low', 'critical']
        enemy_names = ['melee', 'ranged', 'none']
        threat_names = ['low', 'medium', 'high']

        hp = hp_names[state[0]]
        enemy = enemy_names[state[1]]
        threat = threat_names[state[2]]
        in_range = state[3] == 1

        thoughts = []

        # Analyze situation
        if hp == 'critical':
            thoughts.append(f"My HP is critical! Need to be careful...")
        elif hp == 'low':
            thoughts.append(f"HP getting low. Should I retreat?")

        if enemy == 'ranged' and not in_range:
            thoughts.append("Ranged enemy - need to close the distance or dodge.")
        elif enemy == 'melee' and in_range:
            thoughts.append("Melee enemy in range - fight or flight?")

        if threat == 'high':
            thoughts.append("High threat level detected!")

        # Explain decision
        attack_q = q_values.get(0, 0)
        run_q = q_values.get(1, 0)

        if action == 'ATTACK':
            if attack_q > run_q:
                thoughts.append(f"ATTACK looks best (Q:{attack_q:.1f} vs {run_q:.1f}). Engaging!")
            else:
                thoughts.append("Exploring: trying ATTACK to learn more.")
        else:
            if run_q > attack_q:
                thoughts.append(f"RUN is safer (Q:{run_q:.1f} vs {attack_q:.1f}). Retreating!")
            else:
                thoughts.append("Exploring: trying RUN to see what happens.")

        for thought in thoughts[-2:]:  # Last 2 thoughts
            self.add_thought(thought)

    def think_about_base(self, agent, epsilon: float):
        """Generate thoughts about base decisions."""
        thoughts = []

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

        thoughts.append(f"At base camp. Time to decide what to do...")

        if stats[min_stat] < stats[max_stat] - 3:
            thoughts.append(f"My {min_stat} ({stats[min_stat]}) is much lower than {max_stat} ({stats[max_stat]}).")

        if epsilon > 0.5:
            thoughts.append("Still learning a lot - exploring different strategies.")
        elif epsilon > 0.2:
            thoughts.append("Getting better at this. Starting to know what works.")
        else:
            thoughts.append("I've learned a lot! Making informed decisions now.")

        for thought in thoughts:
            self.add_thought(thought)

    def think_about_training(self, stat: str, difficulty: int):
        """Generate thoughts about starting training."""
        stat_descriptions = {
            'strength': "Time to lift some weights! Need to time this right...",
            'intelligence': "Pattern memory training. Let me focus...",
            'agility': "Reaction training! Gotta be fast...",
            'defense': "Block training. Need to time my blocks perfectly...",
            'luck': "Dice game! Let's see if luck is on my side..."
        }

        self.add_thought(f"Training {stat.upper()} (difficulty {difficulty})...")
        self.add_thought(stat_descriptions.get(stat, "Here we go..."))

    def think_about_minigame(self, game_state: tuple, action: str, stat: str):
        """Generate thoughts during a mini-game."""
        if stat == 'strength':
            if game_state[1] == 1:  # In target
                if game_state[2] == 1:  # In perfect zone
                    self.add_thought("Perfect zone! NOW!")
                else:
                    self.add_thought("In the target zone...")
            elif game_state[3] == 1:  # Approaching
                self.add_thought("Getting closer to target...")

        elif stat == 'agility':
            if game_state[0] == 1:  # Signal active
                self.add_thought("SIGNAL! React!")
            else:
                self.add_thought("Waiting for signal...")

        elif stat == 'defense':
            if game_state[2] == 1:  # In block window
                self.add_thought("Block window! NOW!")
            elif game_state[0] == 1:  # Attack active
                self.add_thought("Attack incoming...")

    def think_about_result(self, success: bool, perfect: bool, message: str):
        """Generate thoughts about a training result."""
        if perfect:
            self.add_thought("PERFECT! I'm getting good at this!")
        elif success:
            self.add_thought("Success! That worked out.")
        else:
            self.add_thought("Failed... Need more practice.")

        self.add_thought(message)

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

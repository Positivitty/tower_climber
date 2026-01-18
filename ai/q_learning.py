"""Q-learning agent for the tower climber AI."""

import random
from config import (
    BASE_ALPHA, GAMMA, EPSILON_START, EPSILON_MIN, EPSILON_DECAY,
    COMBAT_ACTIONS, BASE_ACTIONS, MINIGAME_ACTIONS,
    ACTION_ATTACK, ACTION_RUN, ACTION_CHARGE, ACTION_START_CLIMB,
    ACTION_TRAIN_STRENGTH, ACTION_TRAIN_INTELLIGENCE,
    ACTION_TRAIN_AGILITY, ACTION_TRAIN_DEFENSE, ACTION_TRAIN_LUCK,
    ACTION_MINIGAME_PRESS, ACTION_MINIGAME_WAIT,
    TRAINABLE_STATS
)


class QLearningAgent:
    """Tabular Q-learning agent with multiple action contexts."""

    def __init__(self, alpha: float = BASE_ALPHA, gamma: float = GAMMA,
                 epsilon: float = EPSILON_START):
        # Separate Q-tables for different contexts
        self.combat_q = {}      # Combat decisions
        self.base_q = {}        # Base decisions (train vs climb)
        self.minigame_q = {}    # Mini-game decisions

        self.base_alpha = alpha
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

        # Tracking for debug/explainability
        self.last_state = None
        self.last_action = None
        self.last_reward = 0.0
        self.cumulative_reward = 0.0
        self.last_context = None  # 'combat', 'base', 'minigame'

        # Intelligence tracking
        self.total_battles = 0
        self.battles_won = 0
        self.floors_cleared = 0
        self.highest_floor = 0
        self.total_learning_updates = 0
        self.lessons_learned = []  # List of key insights AI has learned
        self.player_taught_actions = 0  # Actions taught by player

    def _get_q_table(self, context: str) -> dict:
        """Get the Q-table for a context."""
        if context == 'combat':
            return self.combat_q
        elif context == 'base':
            return self.base_q
        elif context == 'minigame':
            return self.minigame_q
        return self.combat_q

    def _get_actions(self, context: str) -> list:
        """Get available actions for a context."""
        if context == 'combat':
            return COMBAT_ACTIONS
        elif context == 'base':
            return BASE_ACTIONS
        elif context == 'minigame':
            return MINIGAME_ACTIONS
        return COMBAT_ACTIONS

    def get_q(self, state: tuple, action: int, context: str = 'combat') -> float:
        """Get Q-value for a state-action pair."""
        q_table = self._get_q_table(context)
        return q_table.get((state, action), 0.0)

    def set_q(self, state: tuple, action: int, value: float, context: str = 'combat'):
        """Set Q-value for a state-action pair."""
        q_table = self._get_q_table(context)
        q_table[(state, action)] = value

    def get_all_q_values(self, state: tuple, context: str = 'combat') -> dict:
        """Get Q-values for all actions in a state."""
        actions = self._get_actions(context)
        return {action: self.get_q(state, action, context) for action in actions}

    def choose_action(self, state: tuple, context: str = 'combat') -> int:
        """Choose an action using epsilon-greedy policy."""
        actions = self._get_actions(context)

        # Exploration: random action
        if random.random() < self.epsilon:
            action = random.choice(actions)
        else:
            # Exploitation: choose best action
            q_values = [self.get_q(state, a, context) for a in actions]
            max_q = max(q_values)

            # If multiple actions have the same Q-value, choose randomly
            best_actions = [a for a, q in zip(actions, q_values) if q == max_q]
            action = random.choice(best_actions)

        self.last_state = state
        self.last_action = action
        self.last_context = context
        return action

    def learn(self, state: tuple, action: int, reward: float, next_state: tuple,
              context: str = 'combat', done: bool = False):
        """Update Q-value using the Q-learning update rule."""
        actions = self._get_actions(context)
        current_q = self.get_q(state, action, context)

        if done:
            target = reward
        else:
            max_next_q = max(self.get_q(next_state, a, context) for a in actions)
            target = reward + self.gamma * max_next_q

        new_q = current_q + self.alpha * (target - current_q)
        self.set_q(state, action, new_q, context)

        self.last_reward = reward
        self.cumulative_reward += reward
        self.total_learning_updates += 1

        # Track significant lessons learned
        if context == 'combat' and abs(new_q - current_q) > 5:
            self._maybe_add_lesson(state, action, new_q, reward)

    def _maybe_add_lesson(self, state, action, q_value, reward):
        """Track when AI learns something significant."""
        action_name = self.get_action_name(action, 'combat')
        hp_names = ['High HP', 'Medium HP', 'Low HP', 'Critical HP']
        hp_state = hp_names[state[0]] if state[0] < 4 else 'Unknown'

        if reward > 20:
            lesson = f"Learned: {action_name} is great when {hp_state}!"
        elif reward < -20:
            lesson = f"Learned: {action_name} is bad when {hp_state}"
        elif q_value > 30:
            lesson = f"Mastered: {action_name} at {hp_state}"
        else:
            return

        if lesson not in self.lessons_learned:
            self.lessons_learned.append(lesson)
            if len(self.lessons_learned) > 20:  # Keep last 20
                self.lessons_learned.pop(0)

    def record_battle_result(self, won: bool, floor: int):
        """Record the result of a battle."""
        self.total_battles += 1
        if won:
            self.battles_won += 1
            self.floors_cleared += 1
            if floor > self.highest_floor:
                self.highest_floor = floor

    def get_intelligence_level(self) -> tuple:
        """Calculate AI intelligence level (0-100) and title."""
        # Factors that contribute to intelligence:
        # 1. Knowledge (Q-table size)
        knowledge = len(self.combat_q) + len(self.minigame_q)
        knowledge_score = min(25, knowledge / 4)  # Max 25 points for 100+ entries

        # 2. Win rate
        if self.total_battles > 0:
            win_rate = self.battles_won / self.total_battles
            win_score = win_rate * 25  # Max 25 points
        else:
            win_score = 0

        # 3. Experience (learning updates)
        exp_score = min(25, self.total_learning_updates / 100)  # Max 25 for 2500+ updates

        # 4. Exploration done (low epsilon = more exploitation)
        exploit_score = (1 - self.epsilon) * 15  # Max 15 points

        # 5. Player teaching bonus
        teach_score = min(10, self.player_taught_actions / 5)  # Max 10 points

        total = knowledge_score + win_score + exp_score + exploit_score + teach_score
        total = min(100, max(0, total))

        # Determine title based on score
        if total < 10:
            title = "Newborn"
            desc = "Doesn't know anything yet"
        elif total < 20:
            title = "Infant"
            desc = "Learning basic concepts"
        elif total < 35:
            title = "Toddler"
            desc = "Starting to understand"
        elif total < 50:
            title = "Child"
            desc = "Grasping combat basics"
        elif total < 65:
            title = "Teenager"
            desc = "Developing strategies"
        elif total < 80:
            title = "Adult"
            desc = "Competent fighter"
        elif total < 90:
            title = "Expert"
            desc = "Skilled tactician"
        elif total < 98:
            title = "Master"
            desc = "Near-perfect decisions"
        else:
            title = "Superhuman"
            desc = "Beyond human capability"

        return (total, title, desc)

    def get_stats_summary(self) -> dict:
        """Get a summary of AI stats for display."""
        intel_score, intel_title, intel_desc = self.get_intelligence_level()
        return {
            'intelligence': intel_score,
            'title': intel_title,
            'description': intel_desc,
            'battles': self.total_battles,
            'wins': self.battles_won,
            'win_rate': (self.battles_won / self.total_battles * 100) if self.total_battles > 0 else 0,
            'highest_floor': self.highest_floor,
            'knowledge': len(self.combat_q) + len(self.minigame_q),
            'lessons': self.lessons_learned[-5:],  # Last 5 lessons
            'epsilon': self.epsilon,
            'player_taught': self.player_taught_actions
        }

    def decay_epsilon(self):
        """Decay exploration rate."""
        self.epsilon = max(EPSILON_MIN, self.epsilon * EPSILON_DECAY)

    def update_alpha_with_intelligence(self, intelligence: int):
        """Scale learning rate based on agent's intelligence stat."""
        modifier = 1.0 + (intelligence - 1) * 0.1
        self.alpha = self.base_alpha * modifier

    def reset_episode(self):
        """Reset episode-specific tracking."""
        self.last_state = None
        self.last_action = None
        self.last_reward = 0.0
        self.cumulative_reward = 0.0

    def get_q_table_dict(self) -> dict:
        """Convert all Q-tables to serializable dictionary."""
        data = {
            'combat': {},
            'base': {},
            'minigame': {},
            'stats': {
                'total_battles': self.total_battles,
                'battles_won': self.battles_won,
                'floors_cleared': self.floors_cleared,
                'highest_floor': self.highest_floor,
                'total_learning_updates': self.total_learning_updates,
                'lessons_learned': self.lessons_learned,
                'player_taught_actions': self.player_taught_actions
            }
        }

        for context, q_table in [('combat', self.combat_q),
                                  ('base', self.base_q),
                                  ('minigame', self.minigame_q)]:
            for (state, action), value in q_table.items():
                key = f"{state}:{action}"
                data[context][key] = value

        return data

    def load_q_table_dict(self, data: dict):
        """Load Q-tables from serialized dictionary."""
        self.combat_q = {}
        self.base_q = {}
        self.minigame_q = {}

        # Load stats if present
        if 'stats' in data:
            stats = data['stats']
            self.total_battles = stats.get('total_battles', 0)
            self.battles_won = stats.get('battles_won', 0)
            self.floors_cleared = stats.get('floors_cleared', 0)
            self.highest_floor = stats.get('highest_floor', 0)
            self.total_learning_updates = stats.get('total_learning_updates', 0)
            self.lessons_learned = stats.get('lessons_learned', [])
            self.player_taught_actions = stats.get('player_taught_actions', 0)

        for context, q_dict in data.items():
            if context == 'stats':
                continue  # Skip stats, already handled
            q_table = self._get_q_table(context)
            for key, value in q_dict.items():
                parts = key.rsplit(':', 1)
                state_str = parts[0]
                action = int(parts[1])
                state_str = state_str.strip('()')
                state = tuple(int(x.strip()) for x in state_str.split(','))
                q_table[(state, action)] = value

    @staticmethod
    def get_action_name(action: int, context: str = 'combat') -> str:
        """Get human-readable action name."""
        if context == 'combat':
            if action == ACTION_ATTACK:
                return "ATTACK"
            elif action == ACTION_RUN:
                return "RUN"
            elif action == ACTION_CHARGE:
                return "CHARGE"
        elif context == 'base':
            names = {
                ACTION_TRAIN_STRENGTH: "TRAIN STRENGTH",
                ACTION_TRAIN_INTELLIGENCE: "TRAIN INTELLIGENCE",
                ACTION_TRAIN_AGILITY: "TRAIN AGILITY",
                ACTION_TRAIN_DEFENSE: "TRAIN DEFENSE",
                ACTION_TRAIN_LUCK: "TRAIN LUCK",
                ACTION_START_CLIMB: "START CLIMB"
            }
            return names.get(action, "UNKNOWN")
        elif context == 'minigame':
            if action == ACTION_MINIGAME_PRESS:
                return "PRESS"
            elif action == ACTION_MINIGAME_WAIT:
                return "WAIT"

        return "UNKNOWN"

    @staticmethod
    def action_to_stat(action: int) -> str:
        """Convert a training action to stat name."""
        mapping = {
            ACTION_TRAIN_STRENGTH: 'strength',
            ACTION_TRAIN_INTELLIGENCE: 'intelligence',
            ACTION_TRAIN_AGILITY: 'agility',
            ACTION_TRAIN_DEFENSE: 'defense',
            ACTION_TRAIN_LUCK: 'luck'
        }
        return mapping.get(action, None)

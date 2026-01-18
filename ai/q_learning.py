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
            'minigame': {}
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

        for context, q_dict in data.items():
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

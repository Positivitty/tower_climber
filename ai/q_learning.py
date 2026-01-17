"""Q-learning agent for the tower climber AI."""

import random
from config import (
    BASE_ALPHA, GAMMA, EPSILON_START, EPSILON_MIN, EPSILON_DECAY,
    ACTIONS, ACTION_ATTACK, ACTION_RUN
)


class QLearningAgent:
    """Tabular Q-learning agent.

    Uses a dictionary-based Q-table for state-action value storage.
    """

    def __init__(self, alpha: float = BASE_ALPHA, gamma: float = GAMMA,
                 epsilon: float = EPSILON_START):
        self.q_table = {}  # (state, action) -> Q-value
        self.base_alpha = alpha
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

        # Tracking for debug/explainability
        self.last_state = None
        self.last_action = None
        self.last_reward = 0.0
        self.cumulative_reward = 0.0

    def get_q(self, state: tuple, action: int) -> float:
        """Get Q-value for a state-action pair."""
        return self.q_table.get((state, action), 0.0)

    def set_q(self, state: tuple, action: int, value: float):
        """Set Q-value for a state-action pair."""
        self.q_table[(state, action)] = value

    def get_all_q_values(self, state: tuple) -> dict:
        """Get Q-values for all actions in a state."""
        return {action: self.get_q(state, action) for action in ACTIONS}

    def choose_action(self, state: tuple) -> int:
        """Choose an action using epsilon-greedy policy.

        Args:
            state: Current discretized state tuple

        Returns:
            int: Selected action (ACTION_ATTACK or ACTION_RUN)
        """
        # Exploration: random action
        if random.random() < self.epsilon:
            action = random.choice(ACTIONS)
        else:
            # Exploitation: choose best action
            q_values = [self.get_q(state, a) for a in ACTIONS]
            max_q = max(q_values)

            # If multiple actions have the same Q-value, choose randomly among them
            best_actions = [a for a, q in zip(ACTIONS, q_values) if q == max_q]
            action = random.choice(best_actions)

        self.last_state = state
        self.last_action = action
        return action

    def learn(self, state: tuple, action: int, reward: float, next_state: tuple,
              done: bool = False):
        """Update Q-value using the Q-learning update rule.

        Q(s,a) <- Q(s,a) + alpha * [r + gamma * max Q(s',a') - Q(s,a)]

        Args:
            state: Previous state
            action: Action taken
            reward: Reward received
            next_state: Resulting state
            done: Whether the episode is finished
        """
        current_q = self.get_q(state, action)

        if done:
            # Terminal state - no future rewards
            target = reward
        else:
            # Non-terminal - include discounted future value
            max_next_q = max(self.get_q(next_state, a) for a in ACTIONS)
            target = reward + self.gamma * max_next_q

        # Q-learning update
        new_q = current_q + self.alpha * (target - current_q)
        self.set_q(state, action, new_q)

        # Track reward
        self.last_reward = reward
        self.cumulative_reward += reward

    def decay_epsilon(self):
        """Decay exploration rate."""
        self.epsilon = max(EPSILON_MIN, self.epsilon * EPSILON_DECAY)

    def update_alpha_with_intelligence(self, intelligence: int):
        """Scale learning rate based on agent's intelligence stat.

        Higher intelligence = faster learning.
        """
        modifier = 1.0 + (intelligence - 1) * 0.1
        self.alpha = self.base_alpha * modifier

    def reset_episode(self):
        """Reset episode-specific tracking."""
        self.last_state = None
        self.last_action = None
        self.last_reward = 0.0
        self.cumulative_reward = 0.0

    def get_q_table_dict(self) -> dict:
        """Convert Q-table to serializable dictionary."""
        return {
            f"{state}:{action}": value
            for (state, action), value in self.q_table.items()
        }

    def load_q_table_dict(self, data: dict):
        """Load Q-table from serialized dictionary."""
        self.q_table = {}
        for key, value in data.items():
            # Parse "state:action" format
            parts = key.rsplit(':', 1)
            state_str = parts[0]
            action = int(parts[1])

            # Parse state tuple from string representation
            # Format: "(a, b, c, d)"
            state_str = state_str.strip('()')
            state = tuple(int(x.strip()) for x in state_str.split(','))

            self.q_table[(state, action)] = value

    @staticmethod
    def get_action_name(action: int) -> str:
        """Get human-readable action name."""
        if action == ACTION_ATTACK:
            return "ATTACK"
        elif action == ACTION_RUN:
            return "RUN"
        return "UNKNOWN"

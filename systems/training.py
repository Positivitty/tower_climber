"""Base training system for stat upgrades."""


class TrainingSystem:
    """Handles training stat upgrades at base."""

    def __init__(self):
        self.training_configs = {
            'strength': {
                'base_reps': 10,
                'scaling': 1.2,
                'description': 'Increases attack damage'
            },
            'intelligence': {
                'base_reps': 15,
                'scaling': 1.3,
                'description': 'Increases learning rate'
            }
        }

    def get_cost(self, stat: str, current_level: int) -> int:
        """Calculate reps required to train a stat.

        Args:
            stat: The stat to train ('strength' or 'intelligence')
            current_level: Current level of the stat

        Returns:
            Number of reps required
        """
        if stat not in self.training_configs:
            return 0

        config = self.training_configs[stat]
        base = config['base_reps']
        scale = config['scaling']

        return int(base * (scale ** (current_level - 1)))

    def get_description(self, stat: str) -> str:
        """Get description of what a stat does."""
        if stat not in self.training_configs:
            return "Unknown stat"
        return self.training_configs[stat]['description']

    def train_stat(self, agent, stat: str) -> bool:
        """Apply training to increase a stat by 1.

        Args:
            agent: The agent to train
            stat: The stat to train

        Returns:
            True if training was successful
        """
        if stat == 'strength':
            agent.strength += 1
            return True
        elif stat == 'intelligence':
            agent.intelligence += 1
            return True

        return False

    def get_training_info(self, agent, stat: str) -> dict:
        """Get information about training a stat.

        Returns:
            dict with keys: current_level, cost, description
        """
        if stat == 'strength':
            current_level = agent.strength
        elif stat == 'intelligence':
            current_level = agent.intelligence
        else:
            return None

        return {
            'stat': stat,
            'current_level': current_level,
            'cost': self.get_cost(stat, current_level),
            'description': self.get_description(stat)
        }

    def get_all_training_info(self, agent) -> list:
        """Get training info for all trainable stats."""
        return [
            self.get_training_info(agent, 'strength'),
            self.get_training_info(agent, 'intelligence')
        ]

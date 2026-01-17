"""Save/load functionality for game state."""

import json
import os
from config import SAVE_FILE, EPSILON_START


def get_save_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, SAVE_FILE)


def save_game(agent, q_agent, current_floor: int, extra_data: dict = None) -> bool:
    """Save game state to file."""
    try:
        save_data = {
            'version': 2,
            'agent_stats': agent.get_stats_dict(),
            'q_table': q_agent.get_q_table_dict(),
            'epsilon': q_agent.epsilon,
            'current_floor': current_floor
        }

        # Add extra data if provided
        if extra_data:
            save_data.update(extra_data)

        save_path = get_save_path()
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)

        return True

    except Exception as e:
        print(f"Error saving game: {e}")
        return False


def load_game(agent, q_agent) -> dict:
    """Load game state from file."""
    save_path = get_save_path()

    if not os.path.exists(save_path):
        return None

    try:
        with open(save_path, 'r') as f:
            save_data = json.load(f)

        version = save_data.get('version', 1)

        # Load agent stats
        if 'agent_stats' in save_data:
            agent.load_stats_dict(save_data['agent_stats'])

        # Load Q-table
        if 'q_table' in save_data:
            q_table_data = save_data['q_table']
            # Handle both old and new format
            if isinstance(q_table_data, dict):
                if 'combat' in q_table_data:
                    # New format with contexts
                    q_agent.load_q_table_dict(q_table_data)
                else:
                    # Old format - treat as combat only
                    q_agent.combat_q = {}
                    for key, value in q_table_data.items():
                        parts = key.rsplit(':', 1)
                        state_str = parts[0].strip('()')
                        action = int(parts[1])
                        state = tuple(int(x.strip()) for x in state_str.split(','))
                        q_agent.combat_q[(state, action)] = value

        # Load epsilon
        q_agent.epsilon = save_data.get('epsilon', EPSILON_START)

        return {
            'current_floor': save_data.get('current_floor', 1),
            'equipment': save_data.get('equipment')
        }

    except Exception as e:
        print(f"Error loading game: {e}")
        return None


def delete_save() -> bool:
    save_path = get_save_path()
    if not os.path.exists(save_path):
        return True
    try:
        os.remove(save_path)
        return True
    except Exception as e:
        print(f"Error deleting save: {e}")
        return False


def save_exists() -> bool:
    return os.path.exists(get_save_path())

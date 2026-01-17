"""Save/load functionality for game state."""

import json
import os
from config import SAVE_FILE, EPSILON_START


def get_save_path() -> str:
    """Get the full path to the save file."""
    # Save in the same directory as the game
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, SAVE_FILE)


def save_game(agent, q_agent, current_floor: int) -> bool:
    """Save game state to file.

    Args:
        agent: The player's agent
        q_agent: The Q-learning agent
        current_floor: Current floor number

    Returns:
        True if save was successful
    """
    try:
        save_data = {
            'version': 1,
            'agent_stats': agent.get_stats_dict(),
            'q_table': q_agent.get_q_table_dict(),
            'epsilon': q_agent.epsilon,
            'current_floor': current_floor
        }

        save_path = get_save_path()
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)

        return True

    except Exception as e:
        print(f"Error saving game: {e}")
        return False


def load_game(agent, q_agent) -> dict:
    """Load game state from file.

    Args:
        agent: The player's agent to load stats into
        q_agent: The Q-learning agent to load Q-table into

    Returns:
        dict with loaded data, or None if no save exists
    """
    save_path = get_save_path()

    if not os.path.exists(save_path):
        return None

    try:
        with open(save_path, 'r') as f:
            save_data = json.load(f)

        # Validate version
        version = save_data.get('version', 0)
        if version != 1:
            print(f"Unknown save version: {version}")
            return None

        # Load agent stats
        if 'agent_stats' in save_data:
            agent.load_stats_dict(save_data['agent_stats'])

        # Load Q-table
        if 'q_table' in save_data:
            q_agent.load_q_table_dict(save_data['q_table'])

        # Load epsilon
        q_agent.epsilon = save_data.get('epsilon', EPSILON_START)

        return {
            'current_floor': save_data.get('current_floor', 1)
        }

    except Exception as e:
        print(f"Error loading game: {e}")
        return None


def delete_save() -> bool:
    """Delete the save file.

    Returns:
        True if deletion was successful or file didn't exist
    """
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
    """Check if a save file exists."""
    return os.path.exists(get_save_path())

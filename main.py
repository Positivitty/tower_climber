#!/usr/bin/env python3
"""Tower Climber AI - Entry point.

A tower-climbing game where an AI agent learns via tabular Q-learning
to defeat enemies. The player influences progression through equipment
and training at base.
"""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game import Game


def main():
    """Run the Tower Climber AI game."""
    print("=" * 50)
    print("  TOWER CLIMBER AI")
    print("  Q-Learning Combat Game")
    print("=" * 50)
    print()
    print("Controls:")
    print("  UP/DOWN   - Navigate menus")
    print("  ENTER     - Select option")
    print("  SPACE     - Do training reps")
    print("  D         - Toggle debug overlay")
    print("  ESC       - Return to base (during combat)")
    print()
    print("Starting game...")
    print()

    game = Game()
    game.run()

    print()
    print("Thanks for playing!")


if __name__ == '__main__':
    main()

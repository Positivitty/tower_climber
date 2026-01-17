# Tower Climber AI

A tower-climbing game where an AI agent learns via tabular Q-learning to defeat enemies. The player influences progression through equipment and training at base.

## Features

- **Q-Learning AI**: Watch the AI learn combat strategies in real-time
- **Stick Figure Combat**: Physics-based combat with gravity and knockback
- **Base Training**: Train strength (damage) and intelligence (learning rate)
- **Debug Overlay**: See the AI's decision-making process
- **Persistent Progress**: Save/load Q-table and stats

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/tower_climber.git
cd tower_climber

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| UP/DOWN | Navigate menus |
| ENTER | Select option |
| SPACE | Do training reps |
| D | Toggle debug overlay |
| ESC | Return to base (during combat) |

## How It Works

### State Space (72 states)
- **HP Bucket**: high, medium, low, critical (4 values)
- **Nearest Enemy Type**: melee, ranged, none (3 values)
- **Threat Level**: low, medium, high (3 values)
- **In Attack Range**: yes, no (2 values)

### Action Space (2 actions)
- **ATTACK**: Move toward nearest enemy and attack when in range
- **RUN**: Move away from nearest enemy

### Rewards
- Damage dealt: +5
- Enemy defeated: +50
- Floor cleared: +100
- Damage taken: -3
- Death: -100

### Training
- **Strength**: Increases attack damage
- **Intelligence**: Increases learning rate (alpha modifier)

## Project Structure

```
tower_climber/
├── main.py              # Entry point
├── config.py            # Game constants and hyperparameters
├── game.py              # Main Game class
├── entities/
│   ├── agent.py         # Player's AI agent
│   ├── enemy.py         # Enemy classes (Melee, Ranged)
│   └── projectile.py    # Ranged attack projectiles
├── ai/
│   ├── q_learning.py    # Q-table and learning logic
│   └── state.py         # State discretization
├── systems/
│   ├── physics.py       # Gravity, knockback, collision
│   ├── combat.py        # Combat resolution
│   ├── training.py      # Base training system
│   └── persistence.py   # Save/load functionality
└── ui/
    ├── renderer.py      # Pygame rendering
    ├── debug_overlay.py # AI explainability UI
    └── menus.py         # Menu screens
```

## License

MIT License

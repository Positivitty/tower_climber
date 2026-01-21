# Tower Climber AI

A roguelike tower-climbing game where an AI agent learns combat through Q-learning. Watch the AI develop strategies, teach it new techniques, and guide its growth through character building and equipment.

## Features

### Core Gameplay
- **Q-Learning AI**: Watch the AI learn and adapt its combat strategies in real-time
- **Character Creation**: Choose from 5 races and 5 classes with unique bonuses
- **Equipment System**: Find and equip weapons, armor, and accessories
- **Skill System**: Collect active and passive skills from defeated enemies
- **Persistent Progress**: Auto-save with Q-table, stats, equipment, and skills

### Combat System
- **8 Combat Actions**: Attack (high/mid/low), Run, Charge, Dodge, Parry, Jump
- **Body Part Targeting**: Head (1.5x damage, stun chance), Body (1.0x), Legs (0.8x, slow)
- **Wounds System**: Heavy hits cause lasting wounds that affect performance
- **Status Effects**: Burn (DoT), Freeze (slow), Poison (DoT + healing reduction)
- **Dodge Roll**: i-frames for full invincibility during animation
- **Parry System**: Time blocks for 80% damage reduction and 1.5x counter-attack window

### Enemy Variety
- **Melee**: Standard close-range fighters
- **Ranged**: Projectile-based attackers
- **Tank**: High HP, slower but hits harder
- **Assassin**: Fast, teleports behind you, high crit chance
- **Bosses**: Inferno Guardian, Frost Warden, Plague Lord (every 5 floors)
- **Elemental Variants**: Fire, Ice, Poison versions with status effects

### Terrain System
- **Platforms**: Wooden, Stone, Crumbling (breaks when stood on)
- **Hazards**:
  - Spikes (instant damage + knockback)
  - Ice Patches (reduced friction)
  - Poison Pools (applies poison DoT)
  - Lava (continuous burn damage)
  - Fire Geysers (periodic eruptions)
- **Height Advantage**: +15% damage from above, -10% from below

### Player Interaction
- **Teaching Mode**: Press T during combat to manually control AI decisions
- **AI Priority**: Set combat strategy (Aggressive/Balanced/Defensive)
- **AI Brain View**: See the AI's intelligence level, lessons learned, and statistics
- **Training Mini-games**: Improve stats through timing-based challenges

## Installation

```bash
# Clone the repository
git clone https://github.com/Positivitty/tower_climber.git
cd tower_climber

# Install dependencies
pip install pygame

# Run the game
python game.py
```

## Controls

### Menus
| Key | Action |
|-----|--------|
| UP/DOWN | Navigate options |
| LEFT/RIGHT | Switch tabs/selections |
| ENTER/SPACE | Confirm selection |
| ESC | Go back |

### Combat (Teaching Mode - Press T to toggle)
| Key | Action |
|-----|--------|
| 1 | Attack High (head) |
| 2 | Attack Mid (body) |
| 3 | Attack Low (legs) |
| R | Run away |
| C | Charge toward enemy |
| D | Dodge roll |
| P | Parry |
| J | Jump |

## How the AI Works

### State Space (864 states)
| Dimension | Values | Description |
|-----------|--------|-------------|
| HP Bucket | 4 | High, Medium, Low, Critical |
| Stamina | 2 | High (can dodge), Low |
| Enemy Type | 3 | Melee, Ranged, None |
| Threat Level | 3 | Low, Medium, High |
| In Range | 2 | Yes, No |
| Height | 3 | Above, Same, Below enemy |
| Near Hazard | 2 | Yes, No |

### Action Space (8 combat actions)
- **ATK HEAD**: Target head for bonus damage and stun chance
- **ATK BODY**: Standard body attack
- **ATK LEGS**: Target legs to slow enemy movement
- **RUN**: Retreat from nearest enemy
- **CHARGE**: Rush toward enemy at double speed
- **DODGE**: Roll with i-frames (costs 25 stamina)
- **PARRY**: Block with counter window (costs 15 stamina)
- **JUMP**: Jump to reach platforms (costs 10 stamina)

### Rewards
| Event | Reward |
|-------|--------|
| Damage dealt | +5 |
| Enemy defeated | +50 |
| Floor cleared | +100 |
| High ground kill | +10 |
| Successful dodge | +8 |
| Successful parry | +12 |
| Counter attack | +15 |
| Damage taken | -3 |
| Hazard damage | -5 |
| Death | -100 |

## Character Options

### Races
| Race | Bonus |
|------|-------|
| Human | +1 to all stats |
| Elf | +3 Agility, +2 Intelligence |
| Dwarf | +3 Defense, +2 Strength |
| Undead | Survive fatal hit once per climb |
| Angel | Heal 10% HP after each floor |
| Demon | +50% damage when below 30% HP |

### Classes
| Class | Bonus |
|-------|-------|
| Knight | +3 Defense, +2 Strength |
| Wizard | 2x learning rate |
| Assassin | +10% crit, +5% dodge |
| Berserker | +5 Strength, -2 Defense |
| Cleric | Start with HP Regen passive |

## Project Structure

```
tower_climber/
├── game.py              # Main game loop and state management
├── config.py            # Game constants and hyperparameters
├── entities/
│   ├── agent.py         # Player's AI agent with all mechanics
│   ├── enemy.py         # Enemy types including bosses
│   └── projectile.py    # Ranged attack projectiles
├── ai/
│   ├── q_learning.py    # Q-table, learning, and intelligence tracking
│   ├── state.py         # State discretization (864 states)
│   └── dialogue.py      # AI thought/commentary system
├── systems/
│   ├── physics.py       # Gravity, knockback, platform collision
│   ├── combat.py        # Damage calculation, rewards
│   ├── terrain.py       # Platforms and hazards
│   ├── training.py      # Training mini-games
│   ├── skills.py        # Active and passive skill definitions
│   ├── status_effects.py # Burn, freeze, poison effects
│   ├── character.py     # Races, classes, equipment, loot
│   ├── minigames.py     # Training mini-game logic
│   ├── particles.py     # Visual particle effects
│   └── persistence.py   # Save/load system
└── ui/
    └── renderer.py      # All pygame rendering
```

## Tips

1. **Watch the AI Learn**: The AI starts random but quickly learns what works
2. **Use Teaching Mode**: Guide the AI through tough situations with T key
3. **Set AI Priority**: Defensive is safer for progression, Aggressive clears faster
4. **Check AI Brain**: See what lessons the AI has learned from combat
5. **Height Matters**: Platforms give damage bonuses - teach the AI to use them
6. **Parry > Dodge for Counter**: Parry enables 1.5x damage counter-attacks
7. **Watch Your Stamina**: Dodge and parry cost stamina - don't spam them

## License

MIT License

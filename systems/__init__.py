"""Systems package - physics, combat, training, and persistence."""

from .physics import PhysicsBody
from .combat import CombatSystem
from .training import TrainingSystem
from .persistence import save_game, load_game

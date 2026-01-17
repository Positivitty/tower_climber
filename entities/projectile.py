"""Projectile entity for ranged attacks."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PROJECTILE_SPEED, SCREEN_WIDTH, RANGED_DAMAGE, COLOR_YELLOW


class Projectile:
    """A projectile fired by ranged enemies."""

    def __init__(self, x: float, y: float, direction: int, damage: int = None):
        """Create a projectile.

        Args:
            x: Starting x position
            y: Starting y position
            direction: 1 for right, -1 for left
            damage: Damage dealt on hit (defaults to RANGED_DAMAGE)
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = PROJECTILE_SPEED
        self.damage = damage if damage is not None else RANGED_DAMAGE
        self.radius = 5
        self.active = True
        self.color = COLOR_YELLOW

    def update(self):
        """Update projectile position."""
        self.x += self.direction * self.speed

        # Deactivate if off screen
        if self.x < -self.radius or self.x > SCREEN_WIDTH + self.radius:
            self.active = False

    def get_rect(self) -> tuple:
        """Get collision rectangle."""
        return (
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def collides_with(self, entity) -> bool:
        """Check if projectile collides with an entity."""
        if not self.active:
            return False

        # Get entity rect
        entity_rect = entity.get_rect()

        # Simple AABB collision
        proj_rect = self.get_rect()

        return (proj_rect[0] < entity_rect[0] + entity_rect[2] and
                proj_rect[0] + proj_rect[2] > entity_rect[0] and
                proj_rect[1] < entity_rect[1] + entity_rect[3] and
                proj_rect[1] + proj_rect[3] > entity_rect[1])

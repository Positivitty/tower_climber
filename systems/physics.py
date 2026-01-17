"""Physics system - gravity, knockback, collision detection."""

from config import GRAVITY, GROUND_Y, FRICTION, SCREEN_WIDTH


class PhysicsBody:
    """Base class for entities with physics (gravity, knockback, etc.)."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vx = 0.0  # Horizontal velocity
        self.vy = 0.0  # Vertical velocity
        self.grounded = False
        self.width = 30   # Collision box width
        self.height = 60  # Collision box height

    def apply_gravity(self):
        """Apply gravity if not grounded."""
        if not self.grounded:
            self.vy += GRAVITY

    def apply_knockback(self, direction: int, force: float):
        """Apply knockback force.

        Args:
            direction: 1 for right, -1 for left
            force: Knockback magnitude
        """
        self.vx += direction * force
        self.vy -= force * 0.5  # Pop up slightly
        self.grounded = False

    def update_physics(self):
        """Update position based on velocity and handle ground collision."""
        # Apply gravity
        self.apply_gravity()

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Apply friction to horizontal movement
        self.vx *= FRICTION

        # Clamp very small velocities to zero
        if abs(self.vx) < 0.1:
            self.vx = 0

        # Ground collision
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            self.grounded = True
        else:
            self.grounded = False

        # Keep within screen bounds horizontally
        self.x = max(self.width // 2, min(SCREEN_WIDTH - self.width // 2, self.x))

    def get_rect(self) -> tuple:
        """Get collision rectangle (left, top, width, height)."""
        return (
            self.x - self.width // 2,
            self.y - self.height,
            self.width,
            self.height
        )

    def collides_with(self, other: 'PhysicsBody') -> bool:
        """Check if this body collides with another."""
        r1 = self.get_rect()
        r2 = other.get_rect()

        return (r1[0] < r2[0] + r2[2] and
                r1[0] + r1[2] > r2[0] and
                r1[1] < r2[1] + r2[3] and
                r1[1] + r1[3] > r2[1])

    def distance_to(self, other: 'PhysicsBody') -> float:
        """Calculate distance to another physics body."""
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx * dx + dy * dy) ** 0.5

    def direction_to(self, other: 'PhysicsBody') -> int:
        """Get direction to another body (1 = right, -1 = left)."""
        if other.x > self.x:
            return 1
        elif other.x < self.x:
            return -1
        return 0

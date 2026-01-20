"""Particle system for blood and hit effects."""

import random


class Particle:
    """A single particle."""

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color: tuple, size: int, lifetime: int):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.active = True

    def update(self):
        if not self.active:
            return

        # Apply velocity
        self.x += self.vx
        self.y += self.vy

        # Apply gravity
        self.vy += 0.3

        # Apply friction
        self.vx *= 0.98

        # Decrease lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False

    def get_alpha(self) -> float:
        """Get alpha based on remaining lifetime."""
        return self.lifetime / self.max_lifetime


class ParticleSystem:
    """Manages all particles in the game."""

    def __init__(self):
        self.particles = []

    def spawn_blood(self, x: float, y: float, direction: int, amount: int = 10):
        """Spawn blood particles at a position.

        Args:
            x: X position
            y: Y position
            direction: Direction of impact (-1 or 1)
            amount: Number of particles
        """
        for _ in range(amount):
            # Blood colors (various red shades)
            color = random.choice([
                (180, 0, 0),
                (150, 0, 0),
                (200, 20, 20),
                (120, 0, 0),
                (160, 10, 10)
            ])

            # Random velocity in spray pattern
            vx = direction * random.uniform(2, 6) + random.uniform(-1, 1)
            vy = random.uniform(-4, -1)

            size = random.randint(2, 5)
            lifetime = random.randint(20, 40)

            particle = Particle(x, y, vx, vy, color, size, lifetime)
            self.particles.append(particle)

    def spawn_hit_effect(self, x: float, y: float, color: tuple = (255, 255, 200)):
        """Spawn a hit spark effect."""
        for _ in range(5):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-3, 3)
            size = random.randint(2, 4)
            lifetime = random.randint(5, 15)

            particle = Particle(x, y, vx, vy, color, size, lifetime)
            self.particles.append(particle)

    def spawn_stun_stars(self, x: float, y: float):
        """Spawn stars above head when stunned."""
        for i in range(3):
            color = (255, 255, 0)  # Yellow stars
            angle_offset = i * 2.1  # Spread them out
            vx = random.uniform(-0.5, 0.5)
            vy = -1
            size = 4
            lifetime = 30

            particle = Particle(x + (i - 1) * 10, y - 60, vx, vy, color, size, lifetime)
            self.particles.append(particle)

    def spawn_burn_particles(self, x: float, y: float, amount: int = 5):
        """Spawn fire/burn particles rising from entity."""
        for _ in range(amount):
            color = random.choice([
                (255, 100, 0),   # Orange
                (255, 150, 0),   # Bright orange
                (255, 50, 0),    # Red-orange
                (255, 200, 50),  # Yellow-orange
            ])

            # Fire rises up with some drift
            vx = random.uniform(-1, 1)
            vy = random.uniform(-3, -1)  # Upward

            size = random.randint(3, 6)
            lifetime = random.randint(15, 30)

            # Spawn around the entity
            spawn_x = x + random.uniform(-10, 10)
            spawn_y = y - 30 + random.uniform(-10, 10)

            particle = Particle(spawn_x, spawn_y, vx, vy, color, size, lifetime)
            particle.vy_gravity = -0.1  # Fire rises instead of falls
            self.particles.append(particle)

    def spawn_freeze_particles(self, x: float, y: float, amount: int = 5):
        """Spawn ice/frost particles around entity."""
        for _ in range(amount):
            color = random.choice([
                (100, 200, 255),  # Light blue
                (150, 220, 255),  # Lighter blue
                (200, 240, 255),  # Near white
                (80, 180, 230),   # Medium blue
            ])

            # Ice drifts slowly outward and down
            vx = random.uniform(-2, 2)
            vy = random.uniform(-0.5, 1)

            size = random.randint(2, 4)
            lifetime = random.randint(20, 40)

            # Spawn around the entity
            spawn_x = x + random.uniform(-15, 15)
            spawn_y = y - 30 + random.uniform(-15, 5)

            particle = Particle(spawn_x, spawn_y, vx, vy, color, size, lifetime)
            self.particles.append(particle)

    def spawn_poison_particles(self, x: float, y: float, amount: int = 5):
        """Spawn poison/toxic particles bubbling up."""
        for _ in range(amount):
            color = random.choice([
                (100, 200, 50),   # Green
                (80, 180, 40),    # Darker green
                (120, 220, 60),   # Bright green
                (60, 150, 30),    # Dark green
            ])

            # Poison bubbles up with some wobble
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-2, -0.5)

            size = random.randint(2, 5)
            lifetime = random.randint(25, 45)

            # Spawn around the entity
            spawn_x = x + random.uniform(-12, 12)
            spawn_y = y - 25 + random.uniform(-5, 10)

            particle = Particle(spawn_x, spawn_y, vx, vy, color, size, lifetime)
            self.particles.append(particle)

    def spawn_element_particles(self, x: float, y: float, element: str, amount: int = 5):
        """Spawn particles based on element type."""
        if element == 'fire':
            self.spawn_burn_particles(x, y, amount)
        elif element == 'ice':
            self.spawn_freeze_particles(x, y, amount)
        elif element == 'poison':
            self.spawn_poison_particles(x, y, amount)

    def update(self):
        """Update all particles."""
        for particle in self.particles:
            particle.update()

        # Remove dead particles
        self.particles = [p for p in self.particles if p.active]

    def clear(self):
        """Clear all particles."""
        self.particles = []

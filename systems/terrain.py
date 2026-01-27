"""Terrain system for platforms and hazards."""

import random
from config import (
    SCREEN_WIDTH, GROUND_Y,
    PLATFORM_WOODEN, PLATFORM_STONE, PLATFORM_CRUMBLING,
    PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH, PLATFORM_HEIGHT,
    PLATFORM_CRUMBLE_TIME, PLATFORM_HEIGHTS,
    HAZARD_LAVA, HAZARD_SPIKES, HAZARD_POISON_POOL,
    HAZARD_FIRE_GEYSER, HAZARD_ICE_PATCH,
    LAVA_DAMAGE_PER_FRAME, SPIKE_DAMAGE, SPIKE_COOLDOWN,
    FIRE_GEYSER_DAMAGE, FIRE_GEYSER_INTERVAL, FIRE_GEYSER_DURATION,
    HAZARD_MIN_WIDTH, HAZARD_MAX_WIDTH,
    ELEMENT_POISON
)
from systems.status_effects import create_effect
from stages import STAGE_1, STAGE_2, STAGE_3


class Platform:
    """A platform that entities can stand on."""

    def __init__(self, x: float, y: float, width: int, platform_type: str = PLATFORM_WOODEN):
        self.x = x
        self.y = y
        self.width = width
        self.height = PLATFORM_HEIGHT
        self.platform_type = platform_type
        self.active = True

        # Crumbling platform state
        self.crumble_timer = 0
        self.entity_on_platform = False

    def get_rect(self) -> tuple:
        """Return (x, y, width, height) for collision."""
        return (self.x, self.y, self.width, self.height)

    def is_entity_on_platform(self, entity) -> bool:
        """Check if an entity is standing on this platform."""
        if not self.active:
            return False

        # Check horizontal overlap
        entity_left = entity.x - entity.width // 2
        entity_right = entity.x + entity.width // 2

        if entity_right < self.x or entity_left > self.x + self.width:
            return False

        # Check if entity feet are at platform level (with small tolerance)
        return abs(entity.y - self.y) < 5 and entity.grounded

    def update(self, entities: list = None):
        """Update platform state."""
        if not self.active:
            return

        if self.platform_type == PLATFORM_CRUMBLING:
            # Check if any entity is on the platform
            entity_on = False
            if entities:
                for entity in entities:
                    if self.is_entity_on_platform(entity):
                        entity_on = True
                        break

            if entity_on:
                self.entity_on_platform = True
                self.crumble_timer += 1
                if self.crumble_timer >= PLATFORM_CRUMBLE_TIME:
                    self.active = False
            elif self.entity_on_platform:
                # Entity left, platform still crumbling
                self.crumble_timer += 1
                if self.crumble_timer >= PLATFORM_CRUMBLE_TIME:
                    self.active = False


class Hazard:
    """Environmental hazard that damages entities."""

    def __init__(self, x: float, y: float, width: int, hazard_type: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = 15  # Visual height
        self.hazard_type = hazard_type
        self.active = True

        # Fire geyser state
        self.geyser_timer = random.randint(0, FIRE_GEYSER_INTERVAL)  # Stagger eruptions
        self.geyser_active = False

        # Spike cooldown tracking per entity
        self.spike_cooldowns = {}  # entity_id -> frames remaining

    def get_rect(self) -> tuple:
        """Return (x, y, width, height) for collision."""
        return (self.x, self.y - self.height, self.width, self.height)

    def is_entity_in_hazard(self, entity) -> bool:
        """Check if an entity is in the hazard zone."""
        if not self.active:
            return False

        # Check horizontal overlap
        entity_left = entity.x - entity.width // 2
        entity_right = entity.x + entity.width // 2

        if entity_right < self.x or entity_left > self.x + self.width:
            return False

        # Check vertical - entity feet near hazard level
        if self.hazard_type == HAZARD_FIRE_GEYSER:
            # Geyser affects a tall column when active
            if self.geyser_active:
                return entity.y > self.y - 100 and entity.y <= self.y
            return False
        else:
            # Ground-level hazards
            return abs(entity.y - self.y) < 20

    def update(self):
        """Update hazard state (timers, etc.)."""
        if self.hazard_type == HAZARD_FIRE_GEYSER:
            self.geyser_timer += 1
            if self.geyser_active:
                if self.geyser_timer >= FIRE_GEYSER_DURATION:
                    self.geyser_active = False
                    self.geyser_timer = 0
            else:
                if self.geyser_timer >= FIRE_GEYSER_INTERVAL:
                    self.geyser_active = True
                    self.geyser_timer = 0

        # Update spike cooldowns
        for entity_id in list(self.spike_cooldowns.keys()):
            self.spike_cooldowns[entity_id] -= 1
            if self.spike_cooldowns[entity_id] <= 0:
                del self.spike_cooldowns[entity_id]

    def apply_effect(self, entity, particle_system=None) -> int:
        """Apply hazard effect to entity. Returns damage dealt."""
        if not self.is_entity_in_hazard(entity):
            return 0

        damage = 0

        if self.hazard_type == HAZARD_LAVA:
            damage = LAVA_DAMAGE_PER_FRAME
            entity.hp -= damage
            entity.hp = max(0, entity.hp)
            if particle_system:
                particle_system.spawn_burn_particles(entity.x, entity.y, 2)

        elif self.hazard_type == HAZARD_SPIKES:
            entity_id = id(entity)
            if entity_id not in self.spike_cooldowns:
                damage = SPIKE_DAMAGE
                actual = entity.take_damage(damage)
                self.spike_cooldowns[entity_id] = SPIKE_COOLDOWN
                # Knockback up
                entity.vy = -8
                entity.grounded = False
                if particle_system:
                    particle_system.spawn_blood(entity.x, entity.y, 1, 5)
                return actual

        elif self.hazard_type == HAZARD_POISON_POOL:
            effect = create_effect(ELEMENT_POISON)
            if effect and hasattr(entity, 'status_effects'):
                entity.status_effects.add_effect(effect, entity)
            if particle_system:
                particle_system.spawn_poison_particles(entity.x, entity.y, 2)

        elif self.hazard_type == HAZARD_FIRE_GEYSER:
            if self.geyser_active:
                damage = FIRE_GEYSER_DAMAGE
                entity.take_damage(damage)
                entity.vy = -15  # Launch upward
                entity.grounded = False
                if particle_system:
                    particle_system.spawn_burn_particles(entity.x, entity.y, 10)

        elif self.hazard_type == HAZARD_ICE_PATCH:
            # Ice patch applies freeze effect
            from config import ELEMENT_ICE
            effect = create_effect(ELEMENT_ICE)
            if effect and hasattr(entity, 'status_effects'):
                entity.status_effects.add_effect(effect, entity)

        return damage


class TerrainManager:
    """Manages all platforms and hazards for a floor."""

    def __init__(self):
        self.platforms = []
        self.hazards = []

    def _parse_stage(self, stage_layout: list):
        """Parse a stage layout string into platforms and hazards.
        
        Stage format:
        B = Block/Platform
        H = Hazard
        . = Empty space
        P = Player (spawn point - we ignore this)
        E = Enemy (spawn point - we ignore this)
        """
        # Tile size - divide screen into grid based on stage width
        tile_width = SCREEN_WIDTH // len(stage_layout[0])
        
        # Ground level is at the bottom - work backwards
        num_rows = len(stage_layout)
        
        for row_idx, row in enumerate(stage_layout):
            for col_idx, tile in enumerate(row):
                x = col_idx * tile_width
                y = GROUND_Y - (num_rows - row_idx - 1) * 50  # Each row is 50 pixels high
                
                if tile == 'B':
                    # Create platform from blocks
                    platform_width = tile_width
                    self.platforms.append(Platform(x, y, platform_width, PLATFORM_STONE))
                elif tile == 'H':
                    # Create hazard (spikes on platforms, lava on ground)
                    if y >= GROUND_Y - 20:
                        hazard_type = HAZARD_SPIKES
                    else:
                        hazard_type = random.choice([HAZARD_SPIKES, HAZARD_FIRE_GEYSER])
                    self.hazards.append(Hazard(x, y, tile_width, hazard_type))

    def clear(self):
        """Clear all platforms and hazards."""
        self.platforms = []
        self.hazards = []

    def generate_for_floor(self, floor_number: int):
        """Generate terrain layout based on floor number."""
        self.clear()

        # Use predefined stages for first 3 floors
        if floor_number == 1:
            self._parse_stage(STAGE_1)
            return
        elif floor_number == 2:
            self._parse_stage(STAGE_2)
            return
        elif floor_number == 3:
            self._parse_stage(STAGE_3)
            return

        # Check for boss floor - special terrain
        from config import BOSS_FLOOR_INTERVAL
        if floor_number % BOSS_FLOOR_INTERVAL == 0:
            self._generate_boss_terrain(floor_number)
            return

        # Determine complexity based on floor tier
        tier = min(4, floor_number // 3)

        # Platform count: 3-5 based on tier and preference for complex terrain
        num_platforms = min(5, 3 + tier // 2)

        # Shuffle available heights
        available_heights = PLATFORM_HEIGHTS.copy()
        random.shuffle(available_heights)

        # Generate platforms
        for i in range(num_platforms):
            if i >= len(available_heights):
                break

            platform_y = available_heights[i]
            platform_width = random.randint(PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH)
            platform_x = random.randint(50, SCREEN_WIDTH - platform_width - 50)

            # Platform type based on floor
            if floor_number >= 8 and random.random() < 0.3:
                p_type = PLATFORM_CRUMBLING
            elif floor_number >= 5 and random.random() < 0.3:
                p_type = PLATFORM_STONE
            else:
                p_type = PLATFORM_WOODEN

            self.platforms.append(Platform(platform_x, platform_y, platform_width, p_type))

        # Generate hazards
        hazard_pool = self._get_hazard_pool(floor_number)
        num_hazards = min(3, 1 + tier // 2)

        for _ in range(num_hazards):
            if not hazard_pool:
                break

            hazard_type = random.choice(hazard_pool)
            hazard_width = random.randint(HAZARD_MIN_WIDTH, HAZARD_MAX_WIDTH)

            # Place hazard - prefer ground level
            if random.random() < 0.7 or not self.platforms:
                hazard_y = GROUND_Y
                hazard_x = random.randint(150, SCREEN_WIDTH - hazard_width - 150)
            else:
                # Place on a platform
                platform = random.choice(self.platforms)
                hazard_y = platform.y
                max_x = max(0, platform.width - hazard_width)
                hazard_x = platform.x + random.randint(0, max_x)

            self.hazards.append(Hazard(hazard_x, hazard_y, hazard_width, hazard_type))

    def _get_hazard_pool(self, floor_number: int) -> list:
        """Get available hazard types for floor."""
        pool = [HAZARD_SPIKES]  # Always available

        if floor_number >= 2:
            pool.append(HAZARD_ICE_PATCH)
        if floor_number >= 3:
            pool.append(HAZARD_POISON_POOL)
        if floor_number >= 5:
            pool.append(HAZARD_LAVA)
        if floor_number >= 7:
            pool.append(HAZARD_FIRE_GEYSER)

        return pool

    def _generate_boss_terrain(self, floor_number: int):
        """Generate terrain suited to the boss."""
        from config import BOSS_FLOOR_INTERVAL

        boss_index = floor_number // BOSS_FLOOR_INTERVAL

        if boss_index == 1:  # Floor 5 - Inferno Guardian
            # Fire theme - lava pools, some platforms for safety
            self.hazards = [
                Hazard(100, GROUND_Y, 80, HAZARD_LAVA),
                Hazard(500, GROUND_Y, 80, HAZARD_LAVA),
                Hazard(300, GROUND_Y, 60, HAZARD_FIRE_GEYSER)
            ]
            self.platforms = [
                Platform(200, 350, 150, PLATFORM_STONE),
                Platform(450, 300, 120, PLATFORM_STONE)
            ]

        elif boss_index == 2:  # Floor 10 - Frost Warden
            # Ice theme - ice patches, elevated platforms
            self.hazards = [
                Hazard(100, GROUND_Y, 150, HAZARD_ICE_PATCH),
                Hazard(400, GROUND_Y, 150, HAZARD_ICE_PATCH)
            ]
            self.platforms = [
                Platform(100, 320, 120, PLATFORM_STONE),
                Platform(350, 250, 150, PLATFORM_STONE),
                Platform(550, 320, 120, PLATFORM_STONE)
            ]

        elif boss_index == 3:  # Floor 15 - Plague Lord
            # Poison theme - poison pools, crumbling platforms
            self.hazards = [
                Hazard(150, GROUND_Y, 120, HAZARD_POISON_POOL),
                Hazard(450, GROUND_Y, 120, HAZARD_POISON_POOL)
            ]
            self.platforms = [
                Platform(100, 350, 100, PLATFORM_WOODEN),
                Platform(300, 280, 150, PLATFORM_CRUMBLING),
                Platform(500, 350, 100, PLATFORM_WOODEN)
            ]

        else:  # Higher bosses - mixed dangerous terrain
            self.hazards = [
                Hazard(100, GROUND_Y, 80, HAZARD_LAVA),
                Hazard(350, GROUND_Y, 60, HAZARD_FIRE_GEYSER),
                Hazard(550, GROUND_Y, 80, HAZARD_POISON_POOL)
            ]
            self.platforms = [
                Platform(150, 350, 100, PLATFORM_STONE),
                Platform(350, 280, 120, PLATFORM_CRUMBLING),
                Platform(550, 350, 100, PLATFORM_STONE)
            ]

    def get_platform_at(self, x: float, y: float):
        """Get platform at position, or None."""
        for platform in self.platforms:
            if not platform.active:
                continue
            if platform.x <= x <= platform.x + platform.width:
                if abs(y - platform.y) < 20:
                    return platform
        return None

    def get_ground_y(self, x: float) -> float:
        """Get the ground/platform level at x position."""
        # Check platforms from top to bottom (highest first)
        sorted_platforms = sorted(
            [p for p in self.platforms if p.active],
            key=lambda p: p.y
        )

        for platform in sorted_platforms:
            if platform.x <= x <= platform.x + platform.width:
                return platform.y

        return GROUND_Y

    def update(self, entities: list = None):
        """Update all terrain elements."""
        for platform in self.platforms:
            platform.update(entities)

        for hazard in self.hazards:
            hazard.update()

    def apply_hazard_effects(self, entities: list, particle_system=None) -> dict:
        """Apply hazard effects to all entities. Returns damage per entity."""
        damage_dealt = {}

        for entity in entities:
            if not entity.is_alive():
                continue

            total_damage = 0
            for hazard in self.hazards:
                damage = hazard.apply_effect(entity, particle_system)
                total_damage += damage

            if total_damage > 0:
                damage_dealt[id(entity)] = total_damage

        return damage_dealt

    def is_near_hazard(self, entity, distance: float = 60) -> bool:
        """Check if entity is near any hazard."""
        for hazard in self.hazards:
            hazard_center_x = hazard.x + hazard.width / 2
            if abs(entity.x - hazard_center_x) < hazard.width / 2 + distance:
                if abs(entity.y - hazard.y) < 50:
                    return True
        return False

    def clear(self):
        """Clear all terrain."""
        self.platforms = []
        self.hazards = []

"""Sprite management system for loading and managing game sprites."""

import pygame
import os
from typing import Dict, List, Tuple, Optional

# Asset paths
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
SPRITES_DIR = os.path.join(ASSETS_DIR, 'sprites')
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, 'backgrounds')
TILES_DIR = os.path.join(ASSETS_DIR, 'tiles')


class SpriteSheet:
    """Handles loading and extracting frames from sprite sheets."""

    def __init__(self, filepath: str, frame_width: int, frame_height: int):
        """Load a sprite sheet.

        Args:
            filepath: Path to the sprite sheet image
            frame_width: Width of each frame
            frame_height: Height of each frame
        """
        self.filepath = filepath
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.sheet = None
        self.frames: List[pygame.Surface] = []

        if os.path.exists(filepath):
            self._load()

    def _load(self):
        """Load the sprite sheet image."""
        self.sheet = pygame.image.load(self.filepath).convert_alpha()
        self._extract_frames()

    def _extract_frames(self):
        """Extract individual frames from the sprite sheet."""
        if not self.sheet:
            return

        sheet_width = self.sheet.get_width()
        sheet_height = self.sheet.get_height()

        cols = sheet_width // self.frame_width
        rows = sheet_height // self.frame_height

        for row in range(rows):
            for col in range(cols):
                x = col * self.frame_width
                y = row * self.frame_height
                frame = self.sheet.subsurface((x, y, self.frame_width, self.frame_height))
                self.frames.append(frame)

    def get_frame(self, index: int) -> Optional[pygame.Surface]:
        """Get a specific frame by index."""
        if 0 <= index < len(self.frames):
            return self.frames[index]
        return None

    def get_animation_frames(self, start: int, count: int) -> List[pygame.Surface]:
        """Get a sequence of frames for animation."""
        return self.frames[start:start + count]


class Animation:
    """Handles sprite animation playback."""

    def __init__(self, frames: List[pygame.Surface], frame_duration: int = 6, loop: bool = True):
        """Create an animation.

        Args:
            frames: List of sprite frames
            frame_duration: How many game frames each sprite frame lasts
            loop: Whether to loop the animation
        """
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.frame_counter = 0
        self.finished = False

    def update(self):
        """Advance the animation by one game frame."""
        if self.finished and not self.loop:
            return

        self.frame_counter += 1
        if self.frame_counter >= self.frame_duration:
            self.frame_counter = 0
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True

    def get_current_frame(self) -> Optional[pygame.Surface]:
        """Get the current animation frame."""
        if self.frames:
            return self.frames[self.current_frame]
        return None

    def reset(self):
        """Reset animation to beginning."""
        self.current_frame = 0
        self.frame_counter = 0
        self.finished = False


class SpriteGenerator:
    """Generates placeholder sprites programmatically when assets don't exist."""

    @staticmethod
    def create_character_sprite(width: int, height: int,
                                primary_color: Tuple[int, int, int],
                                secondary_color: Tuple[int, int, int],
                                is_enemy: bool = False) -> pygame.Surface:
        """Generate a character sprite."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Body proportions
        head_size = width // 2
        body_width = int(width * 0.7)
        body_height = int(height * 0.4)
        leg_width = width // 4
        leg_height = int(height * 0.25)

        # Calculate positions (centered horizontally, bottom-aligned)
        center_x = width // 2
        body_y = height - leg_height - body_height
        head_y = body_y - head_size + 4

        # Draw legs
        leg_offset = body_width // 4
        pygame.draw.rect(surface, secondary_color,
                        (center_x - leg_offset - leg_width // 2, height - leg_height,
                         leg_width, leg_height))
        pygame.draw.rect(surface, secondary_color,
                        (center_x + leg_offset - leg_width // 2, height - leg_height,
                         leg_width, leg_height))

        # Draw body
        pygame.draw.rect(surface, primary_color,
                        (center_x - body_width // 2, body_y, body_width, body_height))

        # Draw head
        pygame.draw.rect(surface, primary_color,
                        (center_x - head_size // 2, head_y, head_size, head_size))

        # Draw eyes
        eye_y = head_y + head_size // 3
        eye_offset = head_size // 4
        eye_color = (255, 255, 0) if is_enemy else (255, 255, 255)
        pygame.draw.circle(surface, eye_color, (center_x - eye_offset, eye_y), 2)
        pygame.draw.circle(surface, eye_color, (center_x + eye_offset, eye_y), 2)

        return surface

    @staticmethod
    def create_attack_sprite(width: int, height: int,
                            primary_color: Tuple[int, int, int],
                            secondary_color: Tuple[int, int, int],
                            facing: int = 1,
                            is_enemy: bool = False) -> pygame.Surface:
        """Generate an attack animation sprite."""
        surface = pygame.Surface((width + 20, height), pygame.SRCALPHA)

        # Base character (offset if facing left)
        offset_x = 0 if facing > 0 else 20

        # Body proportions
        head_size = width // 2
        body_width = int(width * 0.7)
        body_height = int(height * 0.4)
        leg_width = width // 4
        leg_height = int(height * 0.25)

        center_x = offset_x + width // 2
        body_y = height - leg_height - body_height
        head_y = body_y - head_size + 4

        # Draw legs
        leg_offset = body_width // 4
        pygame.draw.rect(surface, secondary_color,
                        (center_x - leg_offset - leg_width // 2, height - leg_height,
                         leg_width, leg_height))
        pygame.draw.rect(surface, secondary_color,
                        (center_x + leg_offset - leg_width // 2, height - leg_height,
                         leg_width, leg_height))

        # Draw body
        pygame.draw.rect(surface, primary_color,
                        (center_x - body_width // 2, body_y, body_width, body_height))

        # Draw head
        pygame.draw.rect(surface, primary_color,
                        (center_x - head_size // 2, head_y, head_size, head_size))

        # Draw extended arm with attack effect
        arm_y = body_y + body_height // 4
        arm_length = 25 * facing
        arm_start_x = center_x + (body_width // 2 * facing)
        pygame.draw.rect(surface, secondary_color,
                        (arm_start_x if facing > 0 else arm_start_x + arm_length,
                         arm_y, abs(arm_length), 6))

        # Attack effect (fist/slash)
        effect_x = arm_start_x + arm_length
        pygame.draw.circle(surface, (255, 255, 255), (effect_x, arm_y + 3), 6)

        # Draw eyes
        eye_y = head_y + head_size // 3
        eye_offset = head_size // 4
        eye_color = (255, 255, 0) if is_enemy else (255, 255, 255)
        pygame.draw.circle(surface, eye_color, (center_x - eye_offset, eye_y), 2)
        pygame.draw.circle(surface, eye_color, (center_x + eye_offset, eye_y), 2)

        return surface

    @staticmethod
    def create_dodge_sprite(width: int, height: int,
                           primary_color: Tuple[int, int, int],
                           secondary_color: Tuple[int, int, int],
                           frame: int = 0) -> pygame.Surface:
        """Generate a dodge roll sprite frame."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Create a curled/rolling appearance based on frame
        center_x = width // 2
        center_y = height // 2

        # Roll is basically a ball shape that rotates
        radius = min(width, height) // 3

        # Draw main body as oval/ball
        pygame.draw.ellipse(surface, primary_color,
                           (center_x - radius, center_y - radius // 2,
                            radius * 2, radius))

        # Add motion blur effect
        for i in range(3):
            alpha = 100 - i * 30
            blur_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            blur_color = (*primary_color[:3], alpha)
            pygame.draw.ellipse(blur_surf, blur_color,
                               (center_x - radius - (i + 1) * 5, center_y - radius // 2,
                                radius * 2, radius))
            surface.blit(blur_surf, (0, 0))

        return surface

    @staticmethod
    def create_platform_tile(width: int, height: int,
                            platform_type: str) -> pygame.Surface:
        """Generate a platform tile sprite."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        if platform_type == 'wooden':
            base_color = (139, 90, 43)
            dark_color = (101, 67, 33)
            highlight = (170, 120, 60)
        elif platform_type == 'stone':
            base_color = (128, 128, 128)
            dark_color = (96, 96, 96)
            highlight = (160, 160, 160)
        else:  # crumbling
            base_color = (120, 80, 40)
            dark_color = (80, 50, 25)
            highlight = (140, 100, 50)

        # Main body
        pygame.draw.rect(surface, base_color, (0, 3, width, height - 3))

        # Top highlight
        pygame.draw.rect(surface, highlight, (0, 0, width, 4))

        # Depth/shadow on bottom
        pygame.draw.rect(surface, dark_color, (0, height - 3, width, 3))

        # Wood grain or stone texture
        if platform_type == 'wooden':
            for i in range(0, width, 8):
                pygame.draw.line(surface, dark_color, (i, 5), (i, height - 4), 1)
        elif platform_type == 'stone':
            # Stone cracks
            pygame.draw.line(surface, dark_color, (width // 3, 4), (width // 3 + 5, height - 3), 1)
            pygame.draw.line(surface, dark_color, (2 * width // 3, 4), (2 * width // 3 - 3, height - 3), 1)

        return surface

    @staticmethod
    def create_hazard_tile(width: int, height: int, hazard_type: str) -> pygame.Surface:
        """Generate a hazard tile sprite."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        if hazard_type == 'spikes':
            spike_color = (150, 150, 150)
            highlight = (200, 200, 200)
            spike_width = 12
            num_spikes = width // spike_width

            for i in range(num_spikes):
                sx = i * spike_width
                points = [
                    (sx, height),
                    (sx + spike_width // 2, 0),
                    (sx + spike_width, height)
                ]
                pygame.draw.polygon(surface, spike_color, points)
                pygame.draw.line(surface, highlight, points[0], points[1], 1)

        elif hazard_type == 'lava':
            # Gradient lava
            for y in range(height):
                ratio = y / height
                r = int(255 - 50 * ratio)
                g = int(100 - 50 * ratio)
                b = 0
                pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

            # Bubbles
            pygame.draw.circle(surface, (255, 200, 50), (width // 4, height // 3), 4)
            pygame.draw.circle(surface, (255, 200, 50), (3 * width // 4, height // 2), 3)

        elif hazard_type == 'poison_pool':
            pygame.draw.rect(surface, (100, 200, 50), (0, 0, width, height))
            # Bubbles
            pygame.draw.circle(surface, (150, 255, 100), (width // 3, height // 2), 3)
            pygame.draw.circle(surface, (150, 255, 100), (2 * width // 3, height // 3), 2)

        elif hazard_type == 'ice_patch':
            # Translucent ice
            pygame.draw.rect(surface, (180, 220, 255), (0, 0, width, height))
            # Shine highlights
            pygame.draw.line(surface, (220, 240, 255), (5, 2), (width // 3, 2), 2)
            pygame.draw.line(surface, (255, 255, 255), (width // 2, height // 2),
                           (width - 10, height // 2), 1)

        return surface


class BackgroundManager:
    """Manages themed backgrounds for different floor ranges."""

    # Floor themes
    THEMES = {
        'dungeon': (1, 5),      # Floors 1-5: Dark dungeon
        'cave': (6, 10),        # Floors 6-10: Underground cave
        'tower': (11, 15),      # Floors 11-15: Tower interior
        'sky': (16, 20),        # Floors 16-20: Sky/clouds
        'void': (21, float('inf'))  # Floor 21+: Void/space
    }

    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.backgrounds: Dict[str, pygame.Surface] = {}
        self.current_theme = 'dungeon'
        self._generate_backgrounds()

    def _generate_backgrounds(self):
        """Generate background surfaces for each theme."""
        self.backgrounds['dungeon'] = self._create_dungeon_bg()
        self.backgrounds['cave'] = self._create_cave_bg()
        self.backgrounds['tower'] = self._create_tower_bg()
        self.backgrounds['sky'] = self._create_sky_bg()
        self.backgrounds['void'] = self._create_void_bg()

    def _create_dungeon_bg(self) -> pygame.Surface:
        """Create dark dungeon background."""
        surface = pygame.Surface((self.width, self.height))

        # Dark gradient
        for y in range(self.height):
            ratio = y / self.height
            color = (
                int(20 + 15 * ratio),
                int(15 + 20 * ratio),
                int(30 + 15 * ratio)
            )
            pygame.draw.line(surface, color, (0, y), (self.width, y))

        # Add brick pattern
        brick_color = (40, 35, 45)
        brick_h = 32
        brick_w = 64
        for row in range(self.height // brick_h + 1):
            offset = (row % 2) * (brick_w // 2)
            for col in range(-1, self.width // brick_w + 2):
                x = col * brick_w + offset
                y = row * brick_h
                pygame.draw.rect(surface, brick_color, (x, y, brick_w - 2, brick_h - 2), 1)

        # Add some torches (glowing spots)
        torch_positions = [(100, 150), (700, 150), (400, 100)]
        for tx, ty in torch_positions:
            for radius in range(30, 5, -5):
                alpha = int(50 * (1 - radius / 30))
                glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 150, 50, alpha), (radius, radius), radius)
                surface.blit(glow_surf, (tx - radius, ty - radius))

        return surface

    def _create_cave_bg(self) -> pygame.Surface:
        """Create underground cave background."""
        surface = pygame.Surface((self.width, self.height))

        # Dark earthy gradient
        for y in range(self.height):
            ratio = y / self.height
            color = (
                int(30 + 20 * ratio),
                int(25 + 15 * ratio),
                int(20 + 10 * ratio)
            )
            pygame.draw.line(surface, color, (0, y), (self.width, y))

        # Add stalactites at top
        import random
        random.seed(42)  # Consistent generation
        for x in range(0, self.width, 40):
            height = random.randint(20, 80)
            width = random.randint(10, 25)
            points = [
                (x, 0),
                (x + width, 0),
                (x + width // 2, height)
            ]
            pygame.draw.polygon(surface, (50, 45, 40), points)

        # Add some crystals (glowing)
        crystal_positions = [(150, 200), (650, 180), (400, 250)]
        crystal_colors = [(100, 200, 255), (200, 100, 255), (100, 255, 150)]
        for (cx, cy), color in zip(crystal_positions, crystal_colors):
            # Glow
            for radius in range(20, 5, -3):
                alpha = int(30 * (1 - radius / 20))
                glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, alpha), (radius, radius), radius)
                surface.blit(glow_surf, (cx - radius, cy - radius))
            # Crystal shape
            points = [(cx, cy - 15), (cx + 8, cy + 5), (cx - 8, cy + 5)]
            pygame.draw.polygon(surface, color, points)

        return surface

    def _create_tower_bg(self) -> pygame.Surface:
        """Create tower interior background."""
        surface = pygame.Surface((self.width, self.height))

        # Stone gray gradient with slight blue
        for y in range(self.height):
            ratio = y / self.height
            color = (
                int(60 + 20 * ratio),
                int(60 + 25 * ratio),
                int(70 + 20 * ratio)
            )
            pygame.draw.line(surface, color, (0, y), (self.width, y))

        # Large stone blocks
        block_color = (80, 80, 90)
        block_highlight = (100, 100, 110)
        block_h = 80
        block_w = 120
        for row in range(self.height // block_h + 1):
            offset = (row % 2) * (block_w // 2)
            for col in range(-1, self.width // block_w + 2):
                x = col * block_w + offset
                y = row * block_h
                pygame.draw.rect(surface, block_color, (x + 2, y + 2, block_w - 4, block_h - 4))
                pygame.draw.line(surface, block_highlight, (x + 2, y + 2), (x + block_w - 2, y + 2), 2)

        # Add window (light source)
        window_x, window_y = self.width // 2 - 40, 50
        window_w, window_h = 80, 120
        # Window frame
        pygame.draw.rect(surface, (50, 50, 60), (window_x - 5, window_y - 5, window_w + 10, window_h + 10))
        # Light through window
        for radius in range(100, 10, -10):
            alpha = int(20 * (1 - radius / 100))
            glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 200, alpha), (radius, radius), radius)
            surface.blit(glow_surf, (window_x + window_w // 2 - radius, window_y + window_h // 2 - radius))
        pygame.draw.rect(surface, (200, 220, 255), (window_x, window_y, window_w, window_h))

        return surface

    def _create_sky_bg(self) -> pygame.Surface:
        """Create sky/clouds background."""
        surface = pygame.Surface((self.width, self.height))

        # Sky gradient (light blue to darker blue)
        for y in range(self.height):
            ratio = y / self.height
            color = (
                int(135 - 50 * ratio),
                int(206 - 80 * ratio),
                int(250 - 50 * ratio)
            )
            pygame.draw.line(surface, color, (0, y), (self.width, y))

        # Add clouds
        cloud_positions = [(100, 80), (350, 120), (600, 60), (200, 200), (500, 180)]
        for cx, cy in cloud_positions:
            # Cloud is made of overlapping circles
            cloud_color = (255, 255, 255)
            for dx, dy, r in [(-20, 0, 25), (0, -10, 30), (25, 0, 25), (0, 10, 20)]:
                pygame.draw.circle(surface, cloud_color, (cx + dx, cy + dy), r)

        # Distant mountains/towers
        mountain_color = (100, 130, 160)
        for mx, mh in [(50, 300), (200, 350), (400, 380), (600, 320), (750, 340)]:
            points = [
                (mx - 60, self.height),
                (mx, self.height - mh),
                (mx + 60, self.height)
            ]
            pygame.draw.polygon(surface, mountain_color, points)

        return surface

    def _create_void_bg(self) -> pygame.Surface:
        """Create void/space background."""
        surface = pygame.Surface((self.width, self.height))

        # Deep purple/black gradient
        for y in range(self.height):
            ratio = y / self.height
            color = (
                int(15 + 10 * ratio),
                int(5 + 15 * ratio),
                int(30 + 20 * ratio)
            )
            pygame.draw.line(surface, color, (0, y), (self.width, y))

        # Stars
        import random
        random.seed(99)
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            brightness = random.randint(150, 255)
            size = random.choice([1, 1, 1, 2])
            pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), size)

        # Nebula glow
        nebula_positions = [(200, 300), (600, 150)]
        nebula_colors = [(100, 50, 150), (50, 100, 150)]
        for (nx, ny), color in zip(nebula_positions, nebula_colors):
            for radius in range(80, 20, -10):
                alpha = int(15 * (1 - radius / 80))
                glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, alpha), (radius, radius), radius)
                surface.blit(glow_surf, (nx - radius, ny - radius))

        # Floating debris/asteroids
        for _ in range(5):
            ax = random.randint(50, self.width - 50)
            ay = random.randint(50, self.height - 100)
            pygame.draw.circle(surface, (60, 50, 70), (ax, ay), random.randint(8, 20))

        return surface

    def get_theme_for_floor(self, floor: int) -> str:
        """Determine which theme to use for a given floor."""
        for theme, (start, end) in self.THEMES.items():
            if start <= floor <= end:
                return theme
        return 'void'

    def get_background(self, floor: int) -> pygame.Surface:
        """Get the background surface for a floor."""
        theme = self.get_theme_for_floor(floor)
        self.current_theme = theme
        return self.backgrounds.get(theme, self.backgrounds['dungeon'])

    def draw(self, screen: pygame.Surface, floor: int):
        """Draw the background for the current floor."""
        bg = self.get_background(floor)
        screen.blit(bg, (0, 0))


class SpriteManager:
    """Central manager for all game sprites."""

    def __init__(self):
        self.sprite_sheets: Dict[str, SpriteSheet] = {}
        self.sprites: Dict[str, pygame.Surface] = {}
        self.animations: Dict[str, List[pygame.Surface]] = {}
        self.generator = SpriteGenerator()
        self._initialized = False

    def initialize(self):
        """Initialize sprites - call after pygame.init()."""
        if self._initialized:
            return

        self._load_or_generate_sprites()
        self._initialized = True

    def _load_or_generate_sprites(self):
        """Load sprites from files or generate placeholders."""
        # Character sprites (32x48 pixels)
        char_width, char_height = 32, 48

        # Agent sprites
        agent_primary = (70, 130, 200)
        agent_secondary = (50, 100, 160)
        self.sprites['agent_idle'] = self.generator.create_character_sprite(
            char_width, char_height, agent_primary, agent_secondary, is_enemy=False)
        self.sprites['agent_attack_right'] = self.generator.create_attack_sprite(
            char_width, char_height, agent_primary, agent_secondary, facing=1, is_enemy=False)
        self.sprites['agent_attack_left'] = self.generator.create_attack_sprite(
            char_width, char_height, agent_primary, agent_secondary, facing=-1, is_enemy=False)
        self.sprites['agent_dodge'] = self.generator.create_dodge_sprite(
            char_width, char_height, agent_primary, agent_secondary)

        # Enemy melee sprites
        enemy_primary = (200, 70, 70)
        enemy_secondary = (160, 50, 50)
        self.sprites['enemy_melee_idle'] = self.generator.create_character_sprite(
            char_width, char_height, enemy_primary, enemy_secondary, is_enemy=True)
        self.sprites['enemy_melee_attack_right'] = self.generator.create_attack_sprite(
            char_width, char_height, enemy_primary, enemy_secondary, facing=1, is_enemy=True)
        self.sprites['enemy_melee_attack_left'] = self.generator.create_attack_sprite(
            char_width, char_height, enemy_primary, enemy_secondary, facing=-1, is_enemy=True)

        # Enemy ranged sprites (slightly different color)
        ranged_primary = (180, 100, 70)
        ranged_secondary = (140, 80, 50)
        self.sprites['enemy_ranged_idle'] = self.generator.create_character_sprite(
            char_width, char_height, ranged_primary, ranged_secondary, is_enemy=True)

        # Tank enemy sprites
        tank_primary = (100, 100, 150)
        tank_secondary = (80, 80, 120)
        self.sprites['enemy_tank_idle'] = self.generator.create_character_sprite(
            int(char_width * 1.3), int(char_height * 1.2), tank_primary, tank_secondary, is_enemy=True)

        # Assassin enemy sprites
        assassin_primary = (80, 0, 80)
        assassin_secondary = (60, 0, 60)
        self.sprites['enemy_assassin_idle'] = self.generator.create_character_sprite(
            int(char_width * 0.9), char_height, assassin_primary, assassin_secondary, is_enemy=True)

        # Platform tiles
        for ptype in ['wooden', 'stone', 'crumbling']:
            self.sprites[f'platform_{ptype}'] = self.generator.create_platform_tile(64, 20, ptype)

        # Hazard tiles
        for htype in ['spikes', 'lava', 'poison_pool', 'ice_patch']:
            self.sprites[f'hazard_{htype}'] = self.generator.create_hazard_tile(64, 20, htype)

    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get a sprite by name."""
        return self.sprites.get(name)

    def get_scaled_sprite(self, name: str, width: int, height: int) -> Optional[pygame.Surface]:
        """Get a sprite scaled to specific dimensions."""
        sprite = self.sprites.get(name)
        if sprite:
            return pygame.transform.scale(sprite, (width, height))
        return None

    def get_flipped_sprite(self, name: str, flip_x: bool = False, flip_y: bool = False) -> Optional[pygame.Surface]:
        """Get a horizontally/vertically flipped sprite."""
        sprite = self.sprites.get(name)
        if sprite:
            return pygame.transform.flip(sprite, flip_x, flip_y)
        return None


# Global instances (initialized after pygame.init())
sprite_manager = SpriteManager()
background_manager = None


def init_sprite_system(screen_width: int, screen_height: int):
    """Initialize the sprite system - call after pygame.init()."""
    global background_manager
    sprite_manager.initialize()
    background_manager = BackgroundManager(screen_width, screen_height)

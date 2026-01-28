"""Pygame rendering for sprites and game elements."""

import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_Y,
    COLOR_WHITE, COLOR_BLACK, COLOR_GRAY, COLOR_DARK_GRAY,
    COLOR_GREEN, COLOR_RED, COLOR_YELLOW, COLOR_BLUE, COLOR_CYAN,
    SPRITE_AGENT_PRIMARY, SPRITE_AGENT_SECONDARY,
    SPRITE_ENEMY_PRIMARY, SPRITE_ENEMY_SECONDARY,
    COLOR_TANK, COLOR_ASSASSIN, COLOR_BOSS,
    COLOR_FIRE_ENEMY, COLOR_ICE_ENEMY, COLOR_POISON_ENEMY,
    ELEMENT_FIRE, ELEMENT_ICE, ELEMENT_POISON,
    PLATFORM_WOODEN, PLATFORM_STONE, PLATFORM_CRUMBLING,
    HAZARD_LAVA, HAZARD_SPIKES, HAZARD_POISON_POOL,
    HAZARD_FIRE_GEYSER, HAZARD_ICE_PATCH,
    COLOR_LAVA, COLOR_SPIKES, COLOR_POISON_POOL, COLOR_ICE_PATCH,
    MAX_STAMINA
)
from ui import sprites
from ui.sprites import sprite_manager, init_sprite_system


class Renderer:
    """Handles all game rendering."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 42)
        self.current_floor = 1
        self.use_themed_backgrounds = True

        # Initialize sprite system
        init_sprite_system(SCREEN_WIDTH, SCREEN_HEIGHT)

    def set_floor(self, floor: int):
        """Set current floor for themed backgrounds."""
        self.current_floor = floor

    def clear(self, use_theme: bool = True):
        """Clear the screen with background color or themed background."""
        if self.use_themed_backgrounds and use_theme and sprites.background_manager:
            sprites.background_manager.draw(self.screen, self.current_floor)
        else:
            # Fallback gradient background
            for y in range(SCREEN_HEIGHT):
                ratio = y / SCREEN_HEIGHT
                color = (
                    int(30 + 20 * ratio),
                    int(30 + 30 * ratio),
                    int(50 + 30 * ratio)
                )
                pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

    def draw_ground(self):
        """Draw the ground with themed textures."""
        # Get theme-appropriate ground colors
        if sprites.background_manager:
            theme = sprites.background_manager.current_theme
        else:
            theme = 'dungeon'

        # Theme-specific ground colors
        ground_colors = {
            'dungeon': {'base': (50, 40, 35), 'top': (70, 55, 45), 'detail': (40, 30, 25)},
            'cave': {'base': (45, 35, 30), 'top': (65, 50, 40), 'detail': (35, 25, 20)},
            'tower': {'base': (70, 65, 60), 'top': (90, 85, 80), 'detail': (50, 45, 40)},
            'sky': {'base': (80, 70, 55), 'top': (100, 90, 70), 'detail': (60, 50, 35)},
            'void': {'base': (30, 20, 40), 'top': (50, 35, 60), 'detail': (20, 10, 30)}
        }

        colors = ground_colors.get(theme, ground_colors['dungeon'])
        ground_height = SCREEN_HEIGHT - GROUND_Y

        # Main ground fill with slight gradient
        for y in range(ground_height):
            ratio = y / ground_height
            color = (
                int(colors['base'][0] + (colors['detail'][0] - colors['base'][0]) * ratio),
                int(colors['base'][1] + (colors['detail'][1] - colors['base'][1]) * ratio),
                int(colors['base'][2] + (colors['detail'][2] - colors['base'][2]) * ratio)
            )
            pygame.draw.line(self.screen, color, (0, GROUND_Y + y), (SCREEN_WIDTH, GROUND_Y + y))

        # Top edge highlight
        pygame.draw.line(self.screen, colors['top'], (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 4)
        pygame.draw.line(self.screen, colors['base'], (0, GROUND_Y + 4), (SCREEN_WIDTH, GROUND_Y + 4), 2)

        # Add texture details based on theme
        if theme == 'dungeon':
            # Stone tile pattern
            for x in range(0, SCREEN_WIDTH, 64):
                pygame.draw.line(self.screen, colors['detail'], (x, GROUND_Y), (x, SCREEN_HEIGHT), 1)
            for y in range(GROUND_Y + 32, SCREEN_HEIGHT, 32):
                pygame.draw.line(self.screen, colors['detail'], (0, y), (SCREEN_WIDTH, y), 1)
        elif theme == 'cave':
            # Rough rock texture
            import random
            random.seed(42)
            for _ in range(30):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(GROUND_Y + 5, SCREEN_HEIGHT - 5)
                size = random.randint(3, 8)
                pygame.draw.circle(self.screen, colors['detail'], (x, y), size)
        elif theme == 'tower':
            # Large stone blocks
            block_w = 80
            for x in range(0, SCREEN_WIDTH, block_w):
                pygame.draw.line(self.screen, colors['detail'], (x, GROUND_Y), (x, SCREEN_HEIGHT), 2)
        elif theme == 'sky':
            # Cloud platform look - puffy edges
            for x in range(0, SCREEN_WIDTH, 30):
                pygame.draw.circle(self.screen, colors['top'], (x + 15, GROUND_Y + 5), 20)
        elif theme == 'void':
            # Floating platform with glow
            pygame.draw.rect(self.screen, (60, 40, 80), (0, GROUND_Y - 5, SCREEN_WIDTH, 10))

    def draw_sprite(self, x: float, y: float, facing: int,
                    primary_color: tuple, secondary_color: tuple,
                    attacking: bool = False, hp_ratio: float = 1.0,
                    is_enemy: bool = False):
        """Draw a simple sprite character.

        Args:
            x: X position (center of feet)
            y: Y position (feet on ground)
            facing: 1 for right, -1 for left
            primary_color: Main body color
            secondary_color: Accent color
            attacking: Whether in attack animation
            hp_ratio: Health ratio for HP bar (0.0 to 1.0)
            is_enemy: Whether this is an enemy (affects some visuals)
        """
        x = int(x)
        y = int(y)

        # Character dimensions
        body_width = 24
        body_height = 32
        head_size = 16
        leg_width = 8
        leg_height = 12
        arm_width = 6
        arm_length = 14

        # Body position (y is feet, so body is above)
        body_x = x - body_width // 2
        body_y = y - leg_height - body_height

        # Head position
        head_x = x - head_size // 2
        head_y = body_y - head_size + 2

        # Draw shadow
        shadow_width = body_width + 8
        pygame.draw.ellipse(
            self.screen,
            (30, 30, 30),
            (x - shadow_width // 2, y - 4, shadow_width, 8)
        )

        # Draw legs
        leg_offset = 4
        pygame.draw.rect(self.screen, secondary_color,
                         (x - leg_offset - leg_width // 2, y - leg_height, leg_width, leg_height))
        pygame.draw.rect(self.screen, secondary_color,
                         (x + leg_offset - leg_width // 2, y - leg_height, leg_width, leg_height))

        # Draw body
        pygame.draw.rect(self.screen, primary_color,
                         (body_x, body_y, body_width, body_height))

        # Draw arms
        arm_y = body_y + 6
        if attacking:
            # Attack pose - arm extended forward
            arm_extend = facing * (arm_length + 8)
            pygame.draw.rect(self.screen, secondary_color,
                             (x + facing * 8, arm_y, arm_extend, arm_width))
            # Draw weapon/fist
            fist_x = x + facing * 8 + arm_extend - (4 if facing > 0 else -4)
            pygame.draw.circle(self.screen, COLOR_WHITE, (fist_x, arm_y + 3), 5)
        else:
            # Normal pose - arms at sides
            pygame.draw.rect(self.screen, secondary_color,
                             (body_x - arm_width, arm_y, arm_width, arm_length))
            pygame.draw.rect(self.screen, secondary_color,
                             (body_x + body_width, arm_y, arm_width, arm_length))

        # Draw head
        pygame.draw.rect(self.screen, primary_color,
                         (head_x, head_y, head_size, head_size))

        # Draw face (eyes)
        eye_y = head_y + 5
        eye_offset = 3
        eye_color = COLOR_WHITE if not is_enemy else COLOR_YELLOW
        pygame.draw.circle(self.screen, eye_color,
                           (x - eye_offset, eye_y), 2)
        pygame.draw.circle(self.screen, eye_color,
                           (x + eye_offset, eye_y), 2)

        # Draw HP bar above head
        bar_width = 30
        bar_height = 4
        bar_x = x - bar_width // 2
        bar_y = head_y - 10

        # Background (dark)
        pygame.draw.rect(self.screen, (40, 40, 40),
                         (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
        # Background (red)
        pygame.draw.rect(self.screen, COLOR_RED,
                         (bar_x, bar_y, bar_width, bar_height))
        # Foreground (green)
        pygame.draw.rect(self.screen, COLOR_GREEN,
                         (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))

    def draw_agent(self, agent):
        """Draw the player's agent."""
        hp_ratio = agent.hp / agent.max_hp if agent.max_hp > 0 else 0
        x = int(agent.x)
        y = int(agent.y)

        # Scale factor for sprites (pixel art looks good at integer scales)
        SPRITE_SCALE = 2

        # Try to use sprite images
        sprite = None
        if agent.is_dodging:
            sprite = sprite_manager.get_sprite('agent_dodge')
        elif agent.is_attacking:
            if agent.facing > 0:
                sprite = sprite_manager.get_sprite('agent_attack_right')
            else:
                sprite = sprite_manager.get_sprite('agent_attack_left')
        else:
            sprite = sprite_manager.get_sprite('agent_idle')

        if sprite:
            # Scale up the sprite
            scaled_width = sprite.get_width() * SPRITE_SCALE
            scaled_height = sprite.get_height() * SPRITE_SCALE
            sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))

            # Draw shadow
            shadow_width = scaled_width + 8
            pygame.draw.ellipse(
                self.screen,
                (30, 30, 30),
                (x - shadow_width // 2, y - 4, shadow_width, 8)
            )

            # Flip sprite if facing left (for idle sprite)
            if agent.facing < 0 and not agent.is_attacking:
                sprite = pygame.transform.flip(sprite, True, False)

            # Position sprite (center horizontally, bottom at y)
            sprite_x = x - sprite.get_width() // 2
            sprite_y = y - sprite.get_height()
            self.screen.blit(sprite, (sprite_x, sprite_y))

            # Draw HP bar above sprite
            bar_width = 30
            bar_height = 4
            bar_x = x - bar_width // 2
            bar_y = sprite_y - 10

            pygame.draw.rect(self.screen, (40, 40, 40),
                             (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
            pygame.draw.rect(self.screen, COLOR_RED,
                             (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, COLOR_GREEN,
                             (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
        else:
            # Fallback to procedural drawing
            self.draw_sprite(
                agent.x, agent.y,
                agent.facing,
                SPRITE_AGENT_PRIMARY, SPRITE_AGENT_SECONDARY,
                attacking=agent.is_attacking,
                hp_ratio=hp_ratio,
                is_enemy=False
            )

        # Draw status effects on agent
        self._draw_status_effects(agent)

    def draw_enemy(self, enemy):
        """Draw an enemy."""
        if not enemy.is_alive():
            return

        hp_ratio = enemy.hp / enemy.max_hp if enemy.max_hp > 0 else 0
        x = int(enemy.x)
        y = int(enemy.y)

        # Scale factor for sprites
        SPRITE_SCALE = 2

        # Determine which sprite to use based on enemy type and element
        sprite = None

        # Check for boss sprites first (elemental bosses)
        if enemy.element == ELEMENT_FIRE:
            sprite = sprite_manager.get_sprite('boss_fire')
        elif enemy.element == ELEMENT_ICE:
            sprite = sprite_manager.get_sprite('boss_ice')
        elif enemy.element == ELEMENT_POISON:
            sprite = sprite_manager.get_sprite('boss_poison')
        # Then check enemy type
        elif enemy.enemy_type == 'tank':
            sprite = sprite_manager.get_sprite('enemy_tank_idle')
        elif enemy.enemy_type == 'assassin':
            sprite = sprite_manager.get_sprite('enemy_assassin_idle')
        elif enemy.enemy_type == 'ranged':
            sprite = sprite_manager.get_sprite('enemy_ranged_idle')
        else:  # melee
            sprite = sprite_manager.get_sprite('enemy_melee_idle')

        if sprite:
            # Scale up the sprite
            scaled_width = sprite.get_width() * SPRITE_SCALE
            scaled_height = sprite.get_height() * SPRITE_SCALE
            sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))

            # Draw shadow
            shadow_width = scaled_width + 8
            pygame.draw.ellipse(
                self.screen,
                (30, 30, 30),
                (x - shadow_width // 2, y - 4, shadow_width, 8)
            )

            # Flip sprite based on facing direction
            if enemy.facing < 0:
                sprite = pygame.transform.flip(sprite, True, False)

            # Position sprite (center horizontally, bottom at y)
            sprite_x = x - sprite.get_width() // 2
            sprite_y = y - sprite.get_height()
            self.screen.blit(sprite, (sprite_x, sprite_y))

            # Draw HP bar above sprite
            bar_width = 30
            bar_height = 4
            bar_x = x - bar_width // 2
            bar_y = sprite_y - 10

            pygame.draw.rect(self.screen, (40, 40, 40),
                             (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
            pygame.draw.rect(self.screen, COLOR_RED,
                             (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, COLOR_GREEN,
                             (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
        else:
            # Fallback to procedural drawing
            primary_color = SPRITE_ENEMY_PRIMARY
            secondary_color = SPRITE_ENEMY_SECONDARY

            if enemy.enemy_type == 'tank':
                primary_color = COLOR_TANK
                secondary_color = (80, 80, 120)
            elif enemy.enemy_type == 'assassin':
                primary_color = COLOR_ASSASSIN
                secondary_color = (60, 0, 60)
            elif enemy.enemy_type == 'boss':
                primary_color = COLOR_BOSS
                secondary_color = (160, 40, 160)

            if enemy.element == ELEMENT_FIRE:
                primary_color = COLOR_FIRE_ENEMY
                secondary_color = (200, 80, 0)
            elif enemy.element == ELEMENT_ICE:
                primary_color = COLOR_ICE_ENEMY
                secondary_color = (80, 160, 200)
            elif enemy.element == ELEMENT_POISON:
                primary_color = COLOR_POISON_ENEMY
                secondary_color = (80, 160, 40)

            self.draw_sprite(
                enemy.x, enemy.y,
                enemy.facing,
                primary_color, secondary_color,
                attacking=enemy.is_attacking,
                hp_ratio=hp_ratio,
                is_enemy=True
            )

        # Determine label and color
        label_color = COLOR_YELLOW
        if enemy.enemy_type == 'melee':
            label = "MELEE"
        elif enemy.enemy_type == 'ranged':
            label = "RANGED"
        elif enemy.enemy_type == 'tank':
            label = "TANK"
            label_color = COLOR_TANK
        elif enemy.enemy_type == 'assassin':
            label = "ASSASSIN"
            label_color = COLOR_ASSASSIN
        elif enemy.enemy_type == 'boss':
            label = enemy.name if hasattr(enemy, 'name') else "BOSS"
            label_color = COLOR_BOSS
        else:
            label = enemy.enemy_type.upper()

        # Add element prefix if elemental
        if enemy.element:
            element_prefix = enemy.element.upper()
            label = f"{element_prefix} {label}"
            if enemy.element == ELEMENT_FIRE:
                label_color = COLOR_FIRE_ENEMY
            elif enemy.element == ELEMENT_ICE:
                label_color = COLOR_ICE_ENEMY
            elif enemy.element == ELEMENT_POISON:
                label_color = COLOR_POISON_ENEMY

        # Draw label
        text = self.font_small.render(label, True, label_color)
        text_rect = text.get_rect(center=(int(enemy.x), int(enemy.y - 75)))
        self.screen.blit(text, text_rect)

        # Draw boss-specific indicators
        if enemy.enemy_type == 'boss':
            self._draw_boss_indicators(enemy)

        # Draw status effect indicators
        self._draw_status_effects(enemy)

    def _draw_boss_indicators(self, boss):
        """Draw boss phase dots and enrage status."""
        # Draw phase dots below HP bar
        if hasattr(boss, 'phase') and hasattr(boss, 'max_phase'):
            dot_y = int(boss.y - 85)
            dot_spacing = 12
            total_width = (boss.max_phase - 1) * dot_spacing
            start_x = int(boss.x) - total_width // 2

            for i in range(boss.max_phase):
                dot_x = start_x + i * dot_spacing
                color = COLOR_BOSS if i < boss.phase else COLOR_DARK_GRAY
                pygame.draw.circle(self.screen, color, (dot_x, dot_y), 4)

        # Draw enrage indicator
        if hasattr(boss, 'enraged') and boss.enraged:
            enrage_text = self.font_small.render("ENRAGED!", True, COLOR_RED)
            enrage_rect = enrage_text.get_rect(center=(int(boss.x), int(boss.y - 95)))
            self.screen.blit(enrage_text, enrage_rect)

    def _draw_status_effects(self, entity):
        """Draw status effect indicators above entity."""
        if not hasattr(entity, 'status_effects'):
            return

        effects = entity.status_effects.effects
        if not effects:
            return

        # Draw effect icons to the right of the entity
        icon_x = int(entity.x) + 25
        icon_y = int(entity.y) - 50

        for i, effect in enumerate(effects):
            # Determine color based on effect type
            if effect.effect_type == ELEMENT_FIRE:
                color = COLOR_FIRE_ENEMY
                symbol = "B"  # Burn
            elif effect.effect_type == ELEMENT_ICE:
                color = COLOR_ICE_ENEMY
                symbol = "F"  # Freeze
            elif effect.effect_type == ELEMENT_POISON:
                color = COLOR_POISON_ENEMY
                symbol = "P"  # Poison
            else:
                color = COLOR_WHITE
                symbol = "?"

            # Draw effect indicator
            pygame.draw.circle(self.screen, color, (icon_x, icon_y + i * 15), 6)
            text = self.font_small.render(symbol, True, COLOR_WHITE)
            text_rect = text.get_rect(center=(icon_x, icon_y + i * 15))
            self.screen.blit(text, text_rect)

    def draw_projectile(self, projectile, color=None):
        """Draw a projectile."""
        if not projectile.active:
            return

        # Determine color based on element
        if color:
            outer_color = color
        elif hasattr(projectile, 'element') and projectile.element:
            if projectile.element == ELEMENT_FIRE:
                outer_color = COLOR_FIRE_ENEMY
            elif projectile.element == ELEMENT_ICE:
                outer_color = COLOR_ICE_ENEMY
            elif projectile.element == ELEMENT_POISON:
                outer_color = COLOR_POISON_ENEMY
            else:
                outer_color = COLOR_YELLOW
        else:
            outer_color = COLOR_YELLOW

        # Draw glowing projectile
        pygame.draw.circle(
            self.screen,
            outer_color,
            (int(projectile.x), int(projectile.y)),
            projectile.radius + 2
        )
        pygame.draw.circle(
            self.screen,
            COLOR_WHITE,
            (int(projectile.x), int(projectile.y)),
            projectile.radius
        )

    def draw_projectiles(self, projectiles: list, color=None):
        """Draw all projectiles."""
        for projectile in projectiles:
            self.draw_projectile(projectile, color)

    def draw_text(self, text: str, x: int, y: int, color: tuple = COLOR_WHITE,
                  font_size: str = 'small', center: bool = False):
        """Draw text at a position."""
        if font_size == 'large':
            font = self.font_large
        elif font_size == 'medium':
            font = self.font_medium
        else:
            font = self.font_small

        surface = font.render(text, True, color)
        rect = surface.get_rect()

        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)

        self.screen.blit(surface, rect)

    def draw_button(self, text: str, x: int, y: int, width: int, height: int,
                    selected: bool = False) -> pygame.Rect:
        """Draw a button and return its rect."""
        rect = pygame.Rect(x, y, width, height)

        # Background
        bg_color = (80, 80, 100) if selected else (50, 50, 60)
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=5)

        # Border
        border_color = COLOR_WHITE if selected else COLOR_GRAY
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=5)

        # Text
        self.draw_text(text, rect.centerx, rect.centery,
                       color=COLOR_WHITE, font_size='medium', center=True)

        return rect

    def draw_floor_info(self, floor: int):
        """Draw current floor number - top right corner."""
        self.draw_text(f"Floor {floor}", SCREEN_WIDTH - 80, 10,
                       font_size='medium', color=COLOR_YELLOW)

    def draw_agent_stats_compact(self, agent):
        """Draw agent stats in top right - compact horizontal layout."""
        # Stats panel background
        panel_width = 200
        panel_height = 50
        panel_x = SCREEN_WIDTH - panel_width - 10
        panel_y = 35

        pygame.draw.rect(self.screen, (30, 30, 40, 200),
                         (panel_x, panel_y, panel_width, panel_height),
                         border_radius=5)
        pygame.draw.rect(self.screen, COLOR_GRAY,
                         (panel_x, panel_y, panel_width, panel_height),
                         1, border_radius=5)

        # HP bar
        hp_ratio = agent.hp / agent.max_hp if agent.max_hp > 0 else 0
        bar_x = panel_x + 10
        bar_y = panel_y + 8
        bar_width = panel_width - 20
        bar_height = 12

        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, COLOR_GREEN, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
        self.draw_text(f"{agent.hp}/{agent.max_hp}", bar_x + bar_width // 2, bar_y + 6,
                       color=COLOR_WHITE, font_size='small', center=True)

        # Stats row
        stats_y = panel_y + 28
        stats = [
            f"STR:{agent.strength}",
            f"INT:{agent.intelligence}",
            f"AGI:{agent.agility}",
            f"DEF:{agent.defense}",
            f"LCK:{agent.luck}"
        ]
        stat_text = " ".join(stats)
        self.draw_text(stat_text, panel_x + panel_width // 2, stats_y,
                       color=COLOR_WHITE, font_size='small', center=True)

    def draw_dialogue_box(self, messages: list, title: str = "AI Thoughts"):
        """Draw AI dialogue box at the bottom of the screen."""
        box_height = 120
        box_y = SCREEN_HEIGHT - box_height - 10
        box_x = 10
        box_width = SCREEN_WIDTH - 20

        # Background
        pygame.draw.rect(self.screen, (20, 20, 30),
                         (box_x, box_y, box_width, box_height),
                         border_radius=8)
        pygame.draw.rect(self.screen, COLOR_BLUE,
                         (box_x, box_y, box_width, box_height),
                         2, border_radius=8)

        # Title
        self.draw_text(title, box_x + 15, box_y + 8, COLOR_BLUE, 'medium')

        # Messages (last 4)
        msg_y = box_y + 35
        for msg in messages[-4:]:
            self.draw_text(f"> {msg}", box_x + 15, msg_y, COLOR_WHITE, 'small')
            msg_y += 20

    def draw_timing_bar(self, progress: float, target_start: float, target_end: float,
                        success: bool = None):
        """Draw a timing mini-game bar.

        Args:
            progress: Current position (0.0 to 1.0)
            target_start: Start of target zone (0.0 to 1.0)
            target_end: End of target zone (0.0 to 1.0)
            success: None if in progress, True/False for result
        """
        bar_width = 400
        bar_height = 30
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT // 2 - 50

        # Background
        pygame.draw.rect(self.screen, (40, 40, 50),
                         (bar_x, bar_y, bar_width, bar_height),
                         border_radius=5)

        # Target zone
        target_x = bar_x + int(bar_width * target_start)
        target_w = int(bar_width * (target_end - target_start))
        target_color = COLOR_GREEN if success else (COLOR_RED if success is False else (80, 180, 80))
        pygame.draw.rect(self.screen, target_color,
                         (target_x, bar_y, target_w, bar_height),
                         border_radius=5)

        # Moving indicator
        indicator_x = bar_x + int(bar_width * progress)
        pygame.draw.rect(self.screen, COLOR_WHITE,
                         (indicator_x - 3, bar_y - 5, 6, bar_height + 10),
                         border_radius=2)

        # Border
        pygame.draw.rect(self.screen, COLOR_WHITE,
                         (bar_x, bar_y, bar_width, bar_height),
                         2, border_radius=5)

        # Instructions
        self.draw_text("AI must press at the right time!",
                       SCREEN_WIDTH // 2, bar_y - 30, COLOR_YELLOW, 'medium', center=True)

    def draw_particles(self, particles: list):
        """Draw all particles from the particle system."""
        for particle in particles:
            if not particle.active:
                continue

            # Calculate alpha-faded color
            alpha = particle.get_alpha()
            color = particle.color

            # Draw the particle
            size = max(1, int(particle.size * alpha))
            pygame.draw.circle(
                self.screen,
                color,
                (int(particle.x), int(particle.y)),
                size
            )

    def draw_wound_indicator(self, x: float, y: float, body_part: str):
        """Draw a wound indicator at a specific body part location."""
        # Determine y offset based on body part
        if body_part == 'head':
            indicator_y = y - 60
        elif body_part == 'body':
            indicator_y = y - 40
        else:  # legs
            indicator_y = y - 15

        # Draw red X to indicate wound
        size = 6
        pygame.draw.line(self.screen, COLOR_RED,
                         (x - size, indicator_y - size),
                         (x + size, indicator_y + size), 2)
        pygame.draw.line(self.screen, COLOR_RED,
                         (x + size, indicator_y - size),
                         (x - size, indicator_y + size), 2)

    def draw_platforms(self, terrain_manager):
        """Draw all platforms."""
        for platform in terrain_manager.platforms:
            if not platform.active:
                continue

            x, y, width, height = int(platform.x), int(platform.y), platform.width, platform.height

            # Determine color based on platform type
            if platform.platform_type == PLATFORM_WOODEN:
                top_color = (139, 90, 43)  # Brown
                side_color = (101, 67, 33)  # Darker brown
            elif platform.platform_type == PLATFORM_STONE:
                top_color = (128, 128, 128)  # Gray
                side_color = (96, 96, 96)  # Darker gray
            elif platform.platform_type == PLATFORM_CRUMBLING:
                # Fade based on crumble timer
                fade = platform.crumble_timer / 60.0 if platform.entity_on_platform else 0
                r = int(139 * (1 - fade * 0.5))
                g = int(90 * (1 - fade * 0.5))
                b = int(43 * (1 - fade * 0.5))
                top_color = (r, g, b)
                side_color = (r - 30, g - 20, b - 10)
            else:
                top_color = (139, 90, 43)
                side_color = (101, 67, 33)

            # Draw platform side (depth)
            pygame.draw.rect(self.screen, side_color, (x, y, width, height + 5))

            # Draw platform top
            pygame.draw.rect(self.screen, top_color, (x, y - 3, width, height))

            # Draw edge highlight
            pygame.draw.line(self.screen, (180, 140, 90), (x, y - 3), (x + width, y - 3), 2)

            # Draw crumbling cracks if applicable
            if platform.platform_type == PLATFORM_CRUMBLING and platform.entity_on_platform:
                crack_count = int(platform.crumble_timer / 20) + 1
                for i in range(min(crack_count, 5)):
                    crack_x = x + 20 + i * (width - 40) // 5
                    pygame.draw.line(self.screen, (60, 40, 20),
                                     (crack_x, y - 2), (crack_x + 5, y + height), 1)

    def draw_hazards(self, terrain_manager):
        """Draw all hazards."""
        for hazard in terrain_manager.hazards:
            if not hazard.active:
                continue

            x, y = int(hazard.x), int(hazard.y)
            width, height = hazard.width, hazard.height

            if hazard.hazard_type == HAZARD_LAVA:
                # Animated lava with bubbling effect
                pygame.draw.rect(self.screen, COLOR_LAVA, (x, y - height, width, height))
                # Bubbles
                import random
                random.seed(int(hazard.x) + pygame.time.get_ticks() // 200)
                for _ in range(3):
                    bx = x + random.randint(5, width - 5)
                    by = y - random.randint(5, height - 5)
                    pygame.draw.circle(self.screen, (255, 200, 50), (bx, by), 3)
                # Glow on top
                pygame.draw.line(self.screen, (255, 200, 100), (x, y - height), (x + width, y - height), 2)

            elif hazard.hazard_type == HAZARD_SPIKES:
                # Draw triangular spikes
                spike_width = 12
                num_spikes = width // spike_width
                for i in range(num_spikes):
                    sx = x + i * spike_width
                    points = [
                        (sx, y),
                        (sx + spike_width // 2, y - height - 10),
                        (sx + spike_width, y)
                    ]
                    pygame.draw.polygon(self.screen, COLOR_SPIKES, points)
                    # Highlight
                    pygame.draw.line(self.screen, (180, 180, 180),
                                     points[0], points[1], 1)

            elif hazard.hazard_type == HAZARD_POISON_POOL:
                # Green bubbling pool
                pygame.draw.rect(self.screen, COLOR_POISON_POOL, (x, y - height, width, height))
                # Bubbles
                import random
                random.seed(int(hazard.x) + pygame.time.get_ticks() // 300)
                for _ in range(2):
                    bx = x + random.randint(5, width - 5)
                    by = y - random.randint(3, height - 3)
                    pygame.draw.circle(self.screen, (150, 255, 100), (bx, by), 2)

            elif hazard.hazard_type == HAZARD_ICE_PATCH:
                # Translucent ice
                pygame.draw.rect(self.screen, COLOR_ICE_PATCH, (x, y - 5, width, 8))
                # Shine highlights
                pygame.draw.line(self.screen, (220, 240, 255),
                                 (x + 5, y - 3), (x + width // 3, y - 3), 2)
                pygame.draw.line(self.screen, (220, 240, 255),
                                 (x + width // 2, y - 2), (x + width - 10, y - 2), 1)

            elif hazard.hazard_type == HAZARD_FIRE_GEYSER:
                # Base vent
                vent_width = 30
                vent_x = x + width // 2 - vent_width // 2
                pygame.draw.rect(self.screen, (80, 60, 40), (vent_x, y - 10, vent_width, 10))
                pygame.draw.arc(self.screen, (60, 40, 20),
                                (vent_x - 5, y - 15, vent_width + 10, 15), 0, 3.14, 3)

                # Fire column when active
                if hazard.geyser_active:
                    flame_height = 100
                    for i in range(5):
                        flame_x = vent_x + 5 + i * 5
                        flame_w = 8
                        alpha = 1.0 - i * 0.15
                        color = (int(255 * alpha), int(150 * alpha), 0)
                        pygame.draw.rect(self.screen, color,
                                         (flame_x, y - flame_height, flame_w, flame_height - 10))
                    # Glow at base
                    pygame.draw.circle(self.screen, (255, 200, 50),
                                       (vent_x + vent_width // 2, y - 10), 15)
                else:
                    # Smoke/steam when inactive
                    import random
                    random.seed(int(hazard.geyser_timer))
                    for _ in range(2):
                        sx = vent_x + vent_width // 2 + random.randint(-5, 5)
                        sy = y - 15 - random.randint(5, 20)
                        pygame.draw.circle(self.screen, (100, 100, 100), (sx, sy), 3)

    def draw_stamina_bar(self, agent):
        """Draw stamina bar below HP bar."""
        panel_x = SCREEN_WIDTH - 210
        bar_x = panel_x + 10
        bar_y = 58  # Below HP bar
        bar_width = 180
        bar_height = 8

        # Background
        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))

        # Stamina fill (yellow)
        stamina_ratio = agent.stamina / MAX_STAMINA
        pygame.draw.rect(self.screen, COLOR_YELLOW, (bar_x, bar_y, int(bar_width * stamina_ratio), bar_height))

        # Border
        pygame.draw.rect(self.screen, COLOR_GRAY, (bar_x, bar_y, bar_width, bar_height), 1)

        # Label
        self.draw_text("STA", bar_x - 25, bar_y + 4, COLOR_YELLOW, 'small', center=True)

    def draw_dodge_parry_status(self, agent):
        """Draw dodge/parry cooldown and active status indicators."""
        status_x = SCREEN_WIDTH - 200
        status_y = 70

        # Dodge status
        if agent.is_dodging:
            self.draw_text("DODGING", status_x, status_y, COLOR_CYAN, 'small')
        elif agent.dodge_cooldown > 0:
            cd_pct = agent.dodge_cooldown / 45  # DODGE_COOLDOWN_FRAMES
            self.draw_text(f"Dodge CD: {int(cd_pct * 100)}%", status_x, status_y, COLOR_GRAY, 'small')

        # Parry status
        status_y += 15
        if agent.is_parrying:
            self.draw_text("PARRYING", status_x, status_y, COLOR_GREEN, 'small')
        elif agent.counter_window > 0:
            self.draw_text("COUNTER!", status_x, status_y, COLOR_YELLOW, 'small')
        elif agent.parry_cooldown > 0:
            cd_pct = agent.parry_cooldown / 60  # PARRY_COOLDOWN_FRAMES
            self.draw_text(f"Parry CD: {int(cd_pct * 100)}%", status_x, status_y, COLOR_GRAY, 'small')

        # Invincibility indicator (i-frames)
        if agent.invincible:
            pygame.draw.circle(self.screen, COLOR_CYAN, (int(agent.x), int(agent.y - 70)), 5)

    def draw_guidance_indicators(self, q_agent):
        """Draw indicators for active player guidance effects."""
        status = q_agent.get_guidance_status()
        indicators = []

        if status['strategy_bias']:
            bias = status['strategy_bias'].upper()
            timer = status['strategy_timer'] / 60  # Convert to seconds
            color = COLOR_RED if bias == 'AGGRESSIVE' else COLOR_BLUE
            indicators.append((f"{bias} ({timer:.1f}s)", color))

        if status['learning_boost']:
            timer = status['learning_timer'] / 60
            indicators.append((f"LEARNING x1.5 ({timer:.1f}s)", COLOR_GREEN))

        if status['encouragement']:
            timer = status['encouragement_timer'] / 60
            indicators.append((f"FOCUSED ({timer:.1f}s)", COLOR_CYAN))

        if not indicators:
            return

        # Draw indicators at top left
        y = 10
        for text, color in indicators:
            # Background pill
            text_surface = self.font_small.render(text, True, color)
            text_width = text_surface.get_width()
            pill_rect = pygame.Rect(10, y - 2, text_width + 16, 20)
            pygame.draw.rect(self.screen, (30, 30, 40), pill_rect, border_radius=10)
            pygame.draw.rect(self.screen, color, pill_rect, 1, border_radius=10)
            self.screen.blit(text_surface, (18, y))
            y += 25

    def draw_conversation_freeze_overlay(self):
        """Draw a subtle overlay to indicate combat is frozen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 30, 60))  # Subtle blue tint
        self.screen.blit(overlay, (0, 0))

        # Draw "PAUSED" indicator at top
        pause_text = self.font_medium.render("CONVERSATION", True, COLOR_CYAN)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, 30))

        # Background for visibility
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (20, 25, 35), bg_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLOR_CYAN, bg_rect, 1, border_radius=5)

        self.screen.blit(pause_text, text_rect)

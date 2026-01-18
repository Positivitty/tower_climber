"""Pygame rendering for sprites and game elements."""

import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_Y,
    COLOR_WHITE, COLOR_BLACK, COLOR_GRAY, COLOR_DARK_GRAY,
    COLOR_GREEN, COLOR_RED, COLOR_YELLOW, COLOR_BLUE,
    SPRITE_AGENT_PRIMARY, SPRITE_AGENT_SECONDARY,
    SPRITE_ENEMY_PRIMARY, SPRITE_ENEMY_SECONDARY
)


class Renderer:
    """Handles all game rendering."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 42)

    def clear(self):
        """Clear the screen with background color."""
        # Draw gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = (
                int(30 + 20 * ratio),
                int(30 + 30 * ratio),
                int(50 + 30 * ratio)
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

    def draw_ground(self):
        """Draw the ground."""
        # Ground fill
        pygame.draw.rect(
            self.screen,
            (60, 50, 40),
            (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y)
        )
        # Ground line
        pygame.draw.line(
            self.screen,
            (80, 70, 60),
            (0, GROUND_Y),
            (SCREEN_WIDTH, GROUND_Y),
            3
        )

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
        self.draw_sprite(
            agent.x, agent.y,
            agent.facing,
            SPRITE_AGENT_PRIMARY, SPRITE_AGENT_SECONDARY,
            attacking=agent.is_attacking,
            hp_ratio=hp_ratio,
            is_enemy=False
        )

    def draw_enemy(self, enemy):
        """Draw an enemy."""
        if not enemy.is_alive():
            return

        hp_ratio = enemy.hp / enemy.max_hp if enemy.max_hp > 0 else 0
        self.draw_sprite(
            enemy.x, enemy.y,
            enemy.facing,
            SPRITE_ENEMY_PRIMARY, SPRITE_ENEMY_SECONDARY,
            attacking=enemy.is_attacking,
            hp_ratio=hp_ratio,
            is_enemy=True
        )

        # Draw enemy type indicator above HP bar
        label = "MELEE" if enemy.enemy_type == 'melee' else "RANGED"
        text = self.font_small.render(label, True, COLOR_YELLOW)
        text_rect = text.get_rect(center=(int(enemy.x), int(enemy.y - 75)))
        self.screen.blit(text, text_rect)

    def draw_projectile(self, projectile, color=None):
        """Draw a projectile."""
        if not projectile.active:
            return

        outer_color = color if color else COLOR_YELLOW
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

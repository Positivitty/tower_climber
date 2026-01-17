"""Pygame rendering for stick figures and game elements."""

import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_Y,
    COLOR_WHITE, COLOR_BLACK, COLOR_GRAY, COLOR_DARK_GRAY,
    COLOR_GREEN, COLOR_RED, COLOR_YELLOW
)


class Renderer:
    """Handles all game rendering."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)

    def clear(self):
        """Clear the screen with background color."""
        self.screen.fill(COLOR_DARK_GRAY)

    def draw_ground(self):
        """Draw the ground line."""
        pygame.draw.line(
            self.screen,
            COLOR_GRAY,
            (0, GROUND_Y),
            (SCREEN_WIDTH, GROUND_Y),
            3
        )

    def draw_stick_figure(self, x: float, y: float, facing: int, color: tuple,
                          attacking: bool = False, hp_ratio: float = 1.0):
        """Draw a stick figure at the given position.

        Args:
            x: X position (center of feet)
            y: Y position (feet on ground)
            facing: 1 for right, -1 for left
            color: RGB color tuple
            attacking: Whether the figure is in attack animation
            hp_ratio: Health ratio for HP bar (0.0 to 1.0)
        """
        x = int(x)
        y = int(y)

        # Head
        head_y = y - 60
        pygame.draw.circle(self.screen, color, (x, head_y), 10, 2)

        # Body
        body_top = (x, head_y + 10)
        body_bottom = (x, y - 25)
        pygame.draw.line(self.screen, color, body_top, body_bottom, 2)

        # Arms
        shoulder_y = y - 45
        if attacking:
            # Extended arm forward (attack pose)
            front_arm = (x + facing * 30, shoulder_y - 5)
            back_arm = (x - facing * 15, shoulder_y + 10)
        else:
            # Relaxed arms
            front_arm = (x + facing * 15, shoulder_y + 15)
            back_arm = (x - facing * 10, shoulder_y + 15)

        pygame.draw.line(self.screen, color, (x, shoulder_y), front_arm, 2)
        pygame.draw.line(self.screen, color, (x, shoulder_y), back_arm, 2)

        # Legs
        pygame.draw.line(self.screen, color, body_bottom, (x - 12, y), 2)
        pygame.draw.line(self.screen, color, body_bottom, (x + 12, y), 2)

        # HP bar above head
        bar_width = 30
        bar_height = 4
        bar_x = x - bar_width // 2
        bar_y = head_y - 20

        # Background (red)
        pygame.draw.rect(self.screen, COLOR_RED,
                         (bar_x, bar_y, bar_width, bar_height))
        # Foreground (green)
        pygame.draw.rect(self.screen, COLOR_GREEN,
                         (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))

    def draw_agent(self, agent):
        """Draw the player's agent."""
        hp_ratio = agent.hp / agent.max_hp if agent.max_hp > 0 else 0
        self.draw_stick_figure(
            agent.x, agent.y,
            agent.facing, agent.color,
            attacking=agent.is_attacking,
            hp_ratio=hp_ratio
        )

    def draw_enemy(self, enemy):
        """Draw an enemy."""
        if not enemy.is_alive():
            return

        hp_ratio = enemy.hp / enemy.max_hp if enemy.max_hp > 0 else 0
        self.draw_stick_figure(
            enemy.x, enemy.y,
            enemy.facing, enemy.color,
            attacking=enemy.is_attacking,
            hp_ratio=hp_ratio
        )

        # Draw enemy type indicator
        label = "M" if enemy.enemy_type == 'melee' else "R"
        text = self.font_small.render(label, True, COLOR_WHITE)
        text_rect = text.get_rect(center=(int(enemy.x), int(enemy.y - 80)))
        self.screen.blit(text, text_rect)

    def draw_projectile(self, projectile):
        """Draw a projectile."""
        if not projectile.active:
            return

        pygame.draw.circle(
            self.screen,
            projectile.color,
            (int(projectile.x), int(projectile.y)),
            projectile.radius
        )

    def draw_projectiles(self, projectiles: list):
        """Draw all projectiles."""
        for projectile in projectiles:
            self.draw_projectile(projectile)

    def draw_text(self, text: str, x: int, y: int, color: tuple = COLOR_WHITE,
                  font_size: str = 'small', center: bool = False):
        """Draw text at a position.

        Args:
            text: Text to draw
            x, y: Position
            color: Text color
            font_size: 'small', 'medium', or 'large'
            center: Whether to center the text at the position
        """
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
        """Draw a button and return its rect.

        Args:
            text: Button text
            x, y: Top-left position
            width, height: Button dimensions
            selected: Whether button is highlighted

        Returns:
            pygame.Rect of the button
        """
        rect = pygame.Rect(x, y, width, height)

        # Background
        bg_color = COLOR_GRAY if selected else COLOR_DARK_GRAY
        pygame.draw.rect(self.screen, bg_color, rect)

        # Border
        border_color = COLOR_WHITE if selected else COLOR_GRAY
        pygame.draw.rect(self.screen, border_color, rect, 2)

        # Text
        self.draw_text(text, rect.centerx, rect.centery,
                       color=COLOR_WHITE, font_size='medium', center=True)

        return rect

    def draw_floor_info(self, floor: int):
        """Draw current floor number."""
        self.draw_text(f"Floor {floor}", SCREEN_WIDTH - 100, 10,
                       font_size='medium')

    def draw_agent_stats(self, agent):
        """Draw agent stats in corner."""
        stats = [
            f"HP: {agent.hp}/{agent.max_hp}",
            f"STR: {agent.strength}",
            f"INT: {agent.intelligence}"
        ]

        y = 10
        for stat in stats:
            self.draw_text(stat, 10, y, font_size='small')
            y += 20

"""Improved HUD components for cleaner UI."""

import pygame
import math
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_WHITE, COLOR_BLACK, COLOR_RED, COLOR_GREEN, COLOR_YELLOW,
    COLOR_CYAN, COLOR_GRAY, COLOR_DARK_GRAY, COLOR_BLUE, COLOR_PURPLE,
    MAX_STAMINA, DODGE_COOLDOWN_FRAMES, PARRY_COOLDOWN_FRAMES
)


class HUD:
    """Improved HUD with consolidated, cleaner layout."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_small = pygame.font.Font(None, 18)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 32)

        # Colors
        self.bg_color = (20, 22, 30)
        self.border_color = (60, 65, 80)
        self.hp_color = (220, 60, 60)
        self.hp_bg_color = (80, 30, 30)
        self.stamina_color = (220, 180, 50)
        self.stamina_bg_color = (80, 65, 20)

    def draw_panel(self, x: int, y: int, width: int, height: int,
                   border_color=None, alpha: int = 230):
        """Draw a styled panel background."""
        if border_color is None:
            border_color = self.border_color

        # Create surface with alpha
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((*self.bg_color, alpha))
        self.screen.blit(panel, (x, y))

        # Border
        pygame.draw.rect(self.screen, border_color,
                        (x, y, width, height), 2, border_radius=6)

        # Subtle inner highlight
        pygame.draw.line(self.screen, (*border_color, 100),
                        (x + 3, y + 2), (x + width - 3, y + 2), 1)

    def draw_bar(self, x: int, y: int, width: int, height: int,
                 value: float, max_value: float, fill_color: tuple,
                 bg_color: tuple, show_text: bool = True, label: str = None):
        """Draw a styled progress bar."""
        ratio = value / max_value if max_value > 0 else 0
        ratio = max(0, min(1, ratio))

        # Background
        pygame.draw.rect(self.screen, bg_color,
                        (x, y, width, height), border_radius=3)

        # Fill
        fill_width = int(width * ratio)
        if fill_width > 0:
            pygame.draw.rect(self.screen, fill_color,
                            (x, y, fill_width, height), border_radius=3)

        # Border
        pygame.draw.rect(self.screen, (100, 105, 120),
                        (x, y, width, height), 1, border_radius=3)

        # Text
        if show_text:
            text = f"{int(value)}/{int(max_value)}"
            text_surf = self.font_small.render(text, True, COLOR_WHITE)
            text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
            self.screen.blit(text_surf, text_rect)

        # Label
        if label:
            label_surf = self.font_small.render(label, True, fill_color)
            self.screen.blit(label_surf, (x - label_surf.get_width() - 5, y + 1))

    def draw_cooldown_circle(self, x: int, y: int, radius: int,
                              cooldown: int, max_cooldown: int,
                              color: tuple, label: str = None, active: bool = False):
        """Draw a circular cooldown indicator."""
        ratio = cooldown / max_cooldown if max_cooldown > 0 else 0

        # Background circle
        pygame.draw.circle(self.screen, (40, 42, 50), (x, y), radius)

        if active:
            # Fully filled when active
            pygame.draw.circle(self.screen, color, (x, y), radius - 2)
        elif ratio > 0:
            # Draw arc for cooldown
            rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
            start_angle = math.pi / 2
            end_angle = start_angle + (1 - ratio) * 2 * math.pi

            # Fill the available portion
            if ratio < 1:
                points = [(x, y)]
                for i in range(20):
                    angle = start_angle + (1 - ratio) * 2 * math.pi * i / 19
                    px = x + int((radius - 2) * math.cos(angle))
                    py = y - int((radius - 2) * math.sin(angle))
                    points.append((px, py))
                points.append((x, y))
                if len(points) > 2:
                    pygame.draw.polygon(self.screen, (*color, 150), points)
        else:
            # Ready - full circle
            pygame.draw.circle(self.screen, color, (x, y), radius - 2)

        # Border
        pygame.draw.circle(self.screen, (80, 85, 100), (x, y), radius, 2)

        # Label below
        if label:
            label_surf = self.font_small.render(label, True, color if cooldown <= 0 else COLOR_GRAY)
            label_rect = label_surf.get_rect(center=(x, y + radius + 10))
            self.screen.blit(label_surf, label_rect)

    def draw_icon(self, x: int, y: int, icon_type: str, color: tuple, size: int = 16):
        """Draw simple geometric icons."""
        half = size // 2

        if icon_type == 'heart':
            # Simple heart shape
            pygame.draw.circle(self.screen, color, (x - half // 2, y), half // 2)
            pygame.draw.circle(self.screen, color, (x + half // 2, y), half // 2)
            pygame.draw.polygon(self.screen, color, [
                (x - half, y),
                (x + half, y),
                (x, y + half + 2)
            ])
        elif icon_type == 'lightning':
            # Lightning bolt
            points = [
                (x + half // 2, y - half),
                (x - half // 4, y),
                (x + half // 4, y),
                (x - half // 2, y + half)
            ]
            pygame.draw.polygon(self.screen, color, points)
        elif icon_type == 'shield':
            # Shield shape
            pygame.draw.polygon(self.screen, color, [
                (x, y - half),
                (x + half, y - half // 2),
                (x + half, y + half // 2),
                (x, y + half),
                (x - half, y + half // 2),
                (x - half, y - half // 2)
            ])
        elif icon_type == 'sword':
            # Sword
            pygame.draw.line(self.screen, color, (x, y - half), (x, y + half), 2)
            pygame.draw.line(self.screen, color, (x - half // 2, y - half // 2),
                           (x + half // 2, y - half // 2), 2)
        elif icon_type == 'star':
            # Simple star
            for i in range(5):
                angle = math.pi / 2 + i * 2 * math.pi / 5
                px = x + int(half * math.cos(angle))
                py = y - int(half * math.sin(angle))
                pygame.draw.line(self.screen, color, (x, y), (px, py), 2)

    def draw_main_hud(self, agent, floor: int, q_agent=None):
        """Draw the main HUD panel with all agent info."""
        # Main panel - top left
        panel_x, panel_y = 10, 10
        panel_width, panel_height = 220, 95

        self.draw_panel(panel_x, panel_y, panel_width, panel_height)

        # HP Bar
        bar_x = panel_x + 30
        bar_y = panel_y + 12
        bar_width = panel_width - 45
        bar_height = 16

        self.draw_icon(panel_x + 18, bar_y + 8, 'heart', self.hp_color, 12)
        self.draw_bar(bar_x, bar_y, bar_width, bar_height,
                     agent.hp, agent.max_hp, self.hp_color, self.hp_bg_color)

        # Stamina Bar
        bar_y += 22
        self.draw_icon(panel_x + 18, bar_y + 6, 'lightning', self.stamina_color, 12)
        self.draw_bar(bar_x, bar_y, bar_width, bar_height - 4,
                     agent.stamina, MAX_STAMINA, self.stamina_color, self.stamina_bg_color,
                     show_text=False)

        # Cooldown indicators
        cd_y = bar_y + 24
        cd_radius = 14

        # Dodge cooldown
        dodge_cd = agent.dodge_cooldown if hasattr(agent, 'dodge_cooldown') else 0
        self.draw_cooldown_circle(panel_x + 35, cd_y + cd_radius,
                                  cd_radius, dodge_cd, DODGE_COOLDOWN_FRAMES,
                                  COLOR_CYAN, "D", agent.is_dodging if hasattr(agent, 'is_dodging') else False)

        # Parry cooldown
        parry_cd = agent.parry_cooldown if hasattr(agent, 'parry_cooldown') else 0
        is_parrying = agent.is_parrying if hasattr(agent, 'is_parrying') else False
        counter_window = agent.counter_window if hasattr(agent, 'counter_window') else 0

        parry_color = COLOR_YELLOW if counter_window > 0 else COLOR_GREEN
        self.draw_cooldown_circle(panel_x + 75, cd_y + cd_radius,
                                  cd_radius, parry_cd, PARRY_COOLDOWN_FRAMES,
                                  parry_color, "P", is_parrying or counter_window > 0)

        # Stats display (compact)
        stats_x = panel_x + 110
        stats_y = cd_y + 5
        stats = [
            ("STR", agent.strength, COLOR_RED),
            ("DEF", agent.defense, COLOR_BLUE),
            ("AGI", agent.agility, COLOR_GREEN),
        ]
        for i, (name, val, color) in enumerate(stats):
            x = stats_x + (i % 3) * 36
            y = stats_y + (i // 3) * 18
            text = f"{name[0]}:{val}"
            surf = self.font_small.render(text, True, color)
            self.screen.blit(surf, (x, y))

        # Floor badge - top right
        self.draw_floor_badge(floor)

    def draw_floor_badge(self, floor: int):
        """Draw floor number as a styled badge."""
        badge_x = SCREEN_WIDTH - 90
        badge_y = 10
        badge_width = 80
        badge_height = 30

        # Gradient-like effect
        self.draw_panel(badge_x, badge_y, badge_width, badge_height,
                       border_color=COLOR_YELLOW, alpha=200)

        # Floor text
        text = f"F{floor}"
        text_surf = self.font_large.render(text, True, COLOR_YELLOW)
        text_rect = text_surf.get_rect(center=(badge_x + badge_width // 2, badge_y + badge_height // 2))
        self.screen.blit(text_surf, text_rect)

    def draw_guidance_effects(self, q_agent):
        """Draw active guidance effects as compact badges."""
        if not q_agent.has_active_guidance():
            return

        status = q_agent.get_guidance_status()
        badges = []

        if status['strategy_bias']:
            bias = status['strategy_bias']
            timer = status['strategy_timer'] / 60
            color = (255, 100, 100) if bias == 'aggressive' else (100, 150, 255)
            icon = 'sword' if bias == 'aggressive' else 'shield'
            badges.append((icon, bias[:3].upper(), f"{timer:.0f}s", color))

        if status['learning_boost']:
            timer = status['learning_timer'] / 60
            badges.append(('star', "LRN", f"{timer:.0f}s", COLOR_GREEN))

        if status['encouragement']:
            timer = status['encouragement_timer'] / 60
            badges.append(('heart', "FOC", f"{timer:.0f}s", COLOR_CYAN))

        # Draw badges below main HUD
        y = 115
        for icon, label, timer, color in badges:
            self.draw_panel(10, y, 70, 22, border_color=color, alpha=200)
            self.draw_icon(22, y + 11, icon, color, 10)
            text = f"{label}"
            surf = self.font_small.render(text, True, color)
            self.screen.blit(surf, (32, y + 5))
            y += 26


class MenuRenderer:
    """Improved menu rendering with consistent styling."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 42)

        # Colors
        self.bg_color = (25, 28, 38)
        self.border_color = (70, 75, 90)
        self.selected_color = (50, 55, 70)
        self.highlight_color = COLOR_CYAN

    def draw_menu_panel(self, x: int, y: int, width: int, height: int,
                        title: str = None, alpha: int = 240):
        """Draw a styled menu panel with optional title."""
        # Background
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((*self.bg_color, alpha))
        self.screen.blit(panel, (x, y))

        # Border with glow effect
        pygame.draw.rect(self.screen, self.border_color,
                        (x, y, width, height), 2, border_radius=8)

        # Title bar
        if title:
            title_height = 35
            pygame.draw.rect(self.screen, (35, 40, 55),
                           (x + 2, y + 2, width - 4, title_height), border_radius=6)
            title_surf = self.font_medium.render(title, True, self.highlight_color)
            title_rect = title_surf.get_rect(center=(x + width // 2, y + title_height // 2 + 2))
            self.screen.blit(title_surf, title_rect)

            return y + title_height + 10  # Return content start y

        return y + 10

    def draw_menu_option(self, x: int, y: int, width: int, text: str,
                         selected: bool = False, icon: str = None,
                         description: str = None, number: int = None):
        """Draw a styled menu option."""
        height = 32 if not description else 48

        # Selection highlight
        if selected:
            highlight = pygame.Surface((width, height), pygame.SRCALPHA)
            highlight.fill((*self.selected_color, 200))
            self.screen.blit(highlight, (x, y))
            pygame.draw.rect(self.screen, self.highlight_color,
                           (x, y, width, height), 2, border_radius=4)

            # Left accent bar
            pygame.draw.rect(self.screen, self.highlight_color,
                           (x, y + 4, 3, height - 8), border_radius=1)

        # Number prefix
        text_x = x + 15
        if number is not None:
            num_color = self.highlight_color if selected else COLOR_GRAY
            num_surf = self.font_small.render(f"{number}.", True, num_color)
            self.screen.blit(num_surf, (text_x, y + 8))
            text_x += 20

        # Icon
        if icon:
            icon_color = self.highlight_color if selected else COLOR_WHITE
            self._draw_menu_icon(text_x + 8, y + height // 2, icon, icon_color)
            text_x += 28

        # Main text
        text_color = COLOR_WHITE if selected else (180, 180, 190)
        text_surf = self.font_medium.render(text, True, text_color)
        self.screen.blit(text_surf, (text_x, y + 6))

        # Description
        if description and selected:
            desc_surf = self.font_small.render(description, True, (140, 145, 160))
            self.screen.blit(desc_surf, (text_x, y + 28))

        return height

    def _draw_menu_icon(self, x: int, y: int, icon_type: str, color: tuple):
        """Draw menu icons."""
        size = 10

        if icon_type == 'train':
            # Dumbbell
            pygame.draw.line(self.screen, color, (x - size, y), (x + size, y), 3)
            pygame.draw.rect(self.screen, color, (x - size - 3, y - 4, 6, 8))
            pygame.draw.rect(self.screen, color, (x + size - 3, y - 4, 6, 8))
        elif icon_type == 'equipment':
            # Chest/box
            pygame.draw.rect(self.screen, color, (x - size, y - size // 2, size * 2, size), 2)
            pygame.draw.line(self.screen, color, (x - size, y), (x + size, y), 1)
        elif icon_type == 'skills':
            # Star
            for i in range(5):
                angle = -math.pi / 2 + i * 2 * math.pi / 5
                px = x + int(size * math.cos(angle))
                py = y + int(size * math.sin(angle))
                pygame.draw.line(self.screen, color, (x, y), (px, py), 2)
        elif icon_type == 'strategy':
            # Chess piece / brain
            pygame.draw.circle(self.screen, color, (x, y - 3), 5)
            pygame.draw.rect(self.screen, color, (x - 4, y + 2, 8, 4))
        elif icon_type == 'brain':
            # Brain/cog
            pygame.draw.circle(self.screen, color, (x, y), 6, 2)
            for i in range(6):
                angle = i * math.pi / 3
                px = x + int(8 * math.cos(angle))
                py = y + int(8 * math.sin(angle))
                pygame.draw.circle(self.screen, color, (px, py), 2)
        elif icon_type == 'climb':
            # Arrow up
            pygame.draw.polygon(self.screen, color, [
                (x, y - size),
                (x - size, y + size // 2),
                (x + size, y + size // 2)
            ])
        elif icon_type == 'sword':
            pygame.draw.line(self.screen, color, (x, y - size), (x, y + size), 2)
            pygame.draw.line(self.screen, color, (x - 5, y - 3), (x + 5, y - 3), 2)
        elif icon_type == 'shield':
            pygame.draw.polygon(self.screen, color, [
                (x, y - size),
                (x + size, y - size // 2),
                (x + size, y + size // 2),
                (x, y + size),
                (x - size, y + size // 2),
                (x - size, y - size // 2)
            ], 2)
        elif icon_type == 'lightning':
            # Lightning bolt
            points = [
                (x + 3, y - size),
                (x - 2, y),
                (x + 2, y),
                (x - 3, y + size)
            ]
            pygame.draw.lines(self.screen, color, False, points, 2)
        elif icon_type == 'star':
            # 5-pointed star
            for i in range(5):
                angle = -math.pi / 2 + i * 2 * math.pi / 5
                px = x + int(size * math.cos(angle))
                py = y + int(size * math.sin(angle))
                pygame.draw.line(self.screen, color, (x, y), (px, py), 2)

    def draw_controls_hint(self, y: int, text: str):
        """Draw controls hint at bottom of screen."""
        hint_surf = self.font_small.render(text, True, (100, 105, 120))
        hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.screen.blit(hint_surf, hint_rect)

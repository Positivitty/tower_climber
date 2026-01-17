"""Menu screens for base and post-floor choices."""

import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_WHITE, COLOR_YELLOW, COLOR_GREEN, COLOR_RED
)


class BaseMenu:
    """Menu displayed at the base between climbs."""

    def __init__(self, renderer, training_system):
        self.renderer = renderer
        self.training_system = training_system
        self.selected_option = 0
        self.options = ['Train Strength', 'Train Intelligence', 'Start Climb']
        self.training_in_progress = False
        self.current_reps = 0
        self.required_reps = 0
        self.training_stat = None

    def handle_input(self, event, agent) -> str:
        """Handle menu input.

        Returns:
            'climb' to start climbing
            'stay' to stay at base
            None for no state change
        """
        if self.training_in_progress:
            # During training, space bar does reps
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.current_reps += 1
                if self.current_reps >= self.required_reps:
                    # Training complete
                    self.training_system.train_stat(agent, self.training_stat)
                    self.training_in_progress = False
                    self.training_stat = None
            return 'stay'

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._select_option(agent)

        return 'stay'

    def _select_option(self, agent) -> str:
        """Process selected menu option."""
        if self.selected_option == 0:
            # Train Strength
            self._start_training(agent, 'strength')
            return 'stay'
        elif self.selected_option == 1:
            # Train Intelligence
            self._start_training(agent, 'intelligence')
            return 'stay'
        elif self.selected_option == 2:
            # Start Climb
            return 'climb'

        return 'stay'

    def _start_training(self, agent, stat: str):
        """Start training a stat."""
        info = self.training_system.get_training_info(agent, stat)
        self.training_in_progress = True
        self.training_stat = stat
        self.current_reps = 0
        self.required_reps = info['cost']

    def draw(self, agent):
        """Draw the base menu."""
        self.renderer.clear()

        # Title
        self.renderer.draw_text(
            "BASE CAMP",
            SCREEN_WIDTH // 2, 80,
            COLOR_YELLOW, 'large', center=True
        )

        # Agent stats
        stats_y = 140
        self.renderer.draw_text(
            f"HP: {agent.max_hp}  |  STR: {agent.strength}  |  INT: {agent.intelligence}",
            SCREEN_WIDTH // 2, stats_y,
            COLOR_WHITE, 'medium', center=True
        )

        if self.training_in_progress:
            self._draw_training_screen()
        else:
            self._draw_menu_options(agent)

    def _draw_menu_options(self, agent):
        """Draw menu options."""
        start_y = 220
        button_height = 50
        button_width = 300
        spacing = 20

        for i, option in enumerate(self.options):
            x = (SCREEN_WIDTH - button_width) // 2
            y = start_y + i * (button_height + spacing)

            # Add cost info for training options
            display_text = option
            if i < 2:  # Training options
                stat = 'strength' if i == 0 else 'intelligence'
                info = self.training_system.get_training_info(agent, stat)
                display_text = f"{option} ({info['cost']} reps)"

            self.renderer.draw_button(
                display_text, x, y,
                button_width, button_height,
                selected=(i == self.selected_option)
            )

        # Instructions
        self.renderer.draw_text(
            "Use UP/DOWN to select, ENTER to confirm",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50,
            COLOR_WHITE, 'small', center=True
        )

    def _draw_training_screen(self):
        """Draw the training mini-game screen."""
        center_y = SCREEN_HEIGHT // 2

        # Training title
        self.renderer.draw_text(
            f"Training {self.training_stat.upper()}",
            SCREEN_WIDTH // 2, center_y - 60,
            COLOR_YELLOW, 'large', center=True
        )

        # Progress bar
        bar_width = 400
        bar_height = 30
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = center_y - 15

        # Background
        pygame.draw.rect(self.renderer.screen, (50, 50, 50),
                         (bar_x, bar_y, bar_width, bar_height))

        # Progress
        progress = self.current_reps / self.required_reps if self.required_reps > 0 else 0
        pygame.draw.rect(self.renderer.screen, COLOR_GREEN,
                         (bar_x, bar_y, int(bar_width * progress), bar_height))

        # Border
        pygame.draw.rect(self.renderer.screen, COLOR_WHITE,
                         (bar_x, bar_y, bar_width, bar_height), 2)

        # Rep counter
        self.renderer.draw_text(
            f"{self.current_reps} / {self.required_reps}",
            SCREEN_WIDTH // 2, center_y + 40,
            COLOR_WHITE, 'medium', center=True
        )

        # Instructions
        self.renderer.draw_text(
            "Press SPACE to do reps!",
            SCREEN_WIDTH // 2, center_y + 100,
            COLOR_YELLOW, 'medium', center=True
        )


class PostFloorMenu:
    """Menu displayed after completing a floor."""

    def __init__(self, renderer):
        self.renderer = renderer
        self.selected_option = 0
        self.options = ['Continue Climbing', 'Return to Base']
        self.floor_result = None  # 'cleared' or 'died'
        self.rewards_earned = 0

    def set_result(self, floor_cleared: bool, rewards: float):
        """Set the floor result for display."""
        self.floor_result = 'cleared' if floor_cleared else 'died'
        self.rewards_earned = rewards
        self.selected_option = 0

    def handle_input(self, event) -> str:
        """Handle menu input.

        Returns:
            'continue' to continue climbing
            'base' to return to base
            None for no state change
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selected_option == 0:
                    return 'continue'
                else:
                    return 'base'

        return None

    def draw(self, current_floor: int):
        """Draw the post-floor menu."""
        self.renderer.clear()

        # Result title
        if self.floor_result == 'cleared':
            title = f"FLOOR {current_floor} CLEARED!"
            title_color = COLOR_GREEN
        else:
            title = "DEFEATED"
            title_color = COLOR_RED

        self.renderer.draw_text(
            title,
            SCREEN_WIDTH // 2, 100,
            title_color, 'large', center=True
        )

        # Rewards
        self.renderer.draw_text(
            f"Rewards earned: {self.rewards_earned:.0f}",
            SCREEN_WIDTH // 2, 160,
            COLOR_WHITE, 'medium', center=True
        )

        # Menu options
        start_y = 250
        button_height = 50
        button_width = 300
        spacing = 20

        for i, option in enumerate(self.options):
            x = (SCREEN_WIDTH - button_width) // 2
            y = start_y + i * (button_height + spacing)

            self.renderer.draw_button(
                option, x, y,
                button_width, button_height,
                selected=(i == self.selected_option)
            )

        # Instructions
        self.renderer.draw_text(
            "Use UP/DOWN to select, ENTER to confirm",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50,
            COLOR_WHITE, 'small', center=True
        )

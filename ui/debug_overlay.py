"""Debug overlay for AI explainability."""

import pygame
from config import COLOR_WHITE, COLOR_YELLOW, COLOR_GREEN, SCREEN_HEIGHT
from ai.state import StateEncoder
from ai.q_learning import QLearningAgent


class DebugOverlay:
    """Displays debug information about the AI's decision making."""

    def __init__(self, renderer):
        self.renderer = renderer
        self.visible = True

    def toggle(self):
        """Toggle overlay visibility."""
        self.visible = not self.visible

    def draw(self, state: tuple, q_agent: QLearningAgent,
             combat_system, current_floor: int):
        """Draw the debug overlay.

        Args:
            state: Current discretized state tuple
            q_agent: The Q-learning agent
            combat_system: Combat system for damage info
            current_floor: Current floor number
        """
        if not self.visible:
            return

        y = SCREEN_HEIGHT - 180
        line_height = 18

        # Background panel
        panel_rect = pygame.Rect(5, y - 10, 350, 185)
        pygame.draw.rect(self.renderer.screen, (0, 0, 0, 180), panel_rect)
        pygame.draw.rect(self.renderer.screen, COLOR_WHITE, panel_rect, 1)

        # Title
        self.renderer.draw_text("AI Debug", 10, y, COLOR_YELLOW, 'small')
        y += line_height + 5

        # Current state
        if state:
            state_desc = StateEncoder.get_state_description(state)
            self.renderer.draw_text(f"State: {state_desc}", 10, y, COLOR_WHITE, 'small')
        else:
            self.renderer.draw_text("State: None", 10, y, COLOR_WHITE, 'small')
        y += line_height

        # Current action
        if q_agent.last_action is not None:
            action_name = QLearningAgent.get_action_name(q_agent.last_action)
            self.renderer.draw_text(f"Action: {action_name}", 10, y, COLOR_GREEN, 'small')
        else:
            self.renderer.draw_text("Action: None", 10, y, COLOR_WHITE, 'small')
        y += line_height

        # Last reward
        reward_text = f"Last Reward: {q_agent.last_reward:+.1f}"
        self.renderer.draw_text(reward_text, 10, y, COLOR_WHITE, 'small')
        y += line_height

        # Cumulative reward
        self.renderer.draw_text(
            f"Total Reward: {q_agent.cumulative_reward:.1f}",
            10, y, COLOR_WHITE, 'small'
        )
        y += line_height

        # Epsilon
        self.renderer.draw_text(
            f"Epsilon: {q_agent.epsilon:.3f}",
            10, y, COLOR_WHITE, 'small'
        )
        y += line_height

        # Alpha (effective)
        self.renderer.draw_text(
            f"Alpha: {q_agent.alpha:.3f}",
            10, y, COLOR_WHITE, 'small'
        )
        y += line_height

        # Q-values for current state
        if state:
            q_values = q_agent.get_all_q_values(state)
            q_text = " | ".join(
                f"{QLearningAgent.get_action_name(a)}: {v:.1f}"
                for a, v in q_values.items()
            )
            self.renderer.draw_text(f"Q-values: {q_text}", 10, y, COLOR_WHITE, 'small')
        y += line_height

        # Q-table size
        self.renderer.draw_text(
            f"Q-table entries: {len(q_agent.q_table)}",
            10, y, COLOR_WHITE, 'small'
        )

    def draw_controls(self):
        """Draw control hints."""
        if not self.visible:
            return

        hints = [
            "D: Toggle debug",
            "ESC: Pause/Menu"
        ]

        y = 80
        for hint in hints:
            self.renderer.draw_text(hint, 10, y, COLOR_WHITE, 'small')
            y += 18

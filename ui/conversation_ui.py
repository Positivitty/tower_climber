"""Conversation overlay UI with typewriter effect and player choices."""

import pygame
from typing import List, Optional

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_WHITE, COLOR_YELLOW, COLOR_CYAN, COLOR_GRAY, COLOR_BLACK,
    PORTRAIT_DISPLAY_SIZE,
    TYPEWRITER_SPEED
)
from ui.portrait import Portrait
from ai.conversation import ConversationManager, ConversationChoice


class ConversationUI:
    """UI overlay for AI companion conversations."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.portrait = Portrait()
        self.conversation_manager = ConversationManager()

        # Fonts
        self.font_dialogue = pygame.font.Font(None, 28)
        self.font_choice = pygame.font.Font(None, 24)
        self.font_hint = pygame.font.Font(None, 20)

        # Layout
        self.box_padding = 20
        self.box_height = 180
        self.box_y = SCREEN_HEIGHT - self.box_height - 20

        # Portrait position (left side of dialogue box)
        self.portrait_x = 30
        self.portrait_y = self.box_y - PORTRAIT_DISPLAY_SIZE // 2 + 20

        # Dialogue text area
        self.text_x = self.portrait_x + PORTRAIT_DISPLAY_SIZE + 30
        self.text_y = self.box_y + 25
        self.text_max_width = SCREEN_WIDTH - self.text_x - 40

        # Animation
        self.frame_counter = 0

    def start_conversation(self, trigger: str, context: dict = None) -> bool:
        """Start a conversation for the given trigger."""
        success = self.conversation_manager.start_conversation(trigger, context)
        if success:
            # Set portrait emotion to match conversation
            emotion = self.conversation_manager.get_emotion()
            self.portrait.set_emotion_immediate(emotion)
        return success

    def queue_conversation(self, trigger: str, context: dict = None):
        """Queue a conversation to show later."""
        self.conversation_manager.queue_conversation(trigger, context)

    def update(self, dt: int = 1):
        """Update conversation and portrait state."""
        self.frame_counter += dt

        # Update portrait animation
        self.portrait.update(dt)

        # Update conversation typewriter
        self.conversation_manager.update(TYPEWRITER_SPEED)

        # Update portrait emotion if it changed
        if self.conversation_manager.is_active():
            emotion = self.conversation_manager.get_emotion()
            self.portrait.set_emotion(emotion)

    def handle_input(self, key) -> Optional[ConversationChoice]:
        """Handle keyboard input. Returns chosen choice if one was selected."""
        if not self.conversation_manager.is_active():
            return None

        if self.conversation_manager.is_showing_choices():
            # Navigate choices
            if key == pygame.K_UP:
                self.conversation_manager.navigate_choice(-1)
            elif key == pygame.K_DOWN:
                self.conversation_manager.navigate_choice(1)
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                index = self.conversation_manager.get_selected_choice_index()
                return self.conversation_manager.select_choice(index)
            # Number keys for quick selection
            elif pygame.K_1 <= key <= pygame.K_9:
                index = key - pygame.K_1
                choices = self.conversation_manager.get_choices()
                if index < len(choices):
                    return self.conversation_manager.select_choice(index)
        else:
            # Advance dialogue
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self.conversation_manager.advance()

        return None

    def is_active(self) -> bool:
        """Check if conversation is active."""
        return self.conversation_manager.is_active()

    def has_queued(self) -> bool:
        """Check if there are queued conversations."""
        return self.conversation_manager.has_queued_conversations()

    def start_next_queued(self) -> bool:
        """Start the next queued conversation."""
        success = self.conversation_manager.start_next_conversation()
        if success:
            emotion = self.conversation_manager.get_emotion()
            self.portrait.set_emotion_immediate(emotion)
        return success

    def clear(self):
        """Clear all conversations."""
        self.conversation_manager.clear()

    def render(self):
        """Render the conversation overlay."""
        if not self.conversation_manager.is_active():
            return

        # Draw semi-transparent overlay to dim background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))

        # Draw dialogue box
        self._draw_dialogue_box()

        # Draw portrait
        self.portrait.render(self.screen, self.portrait_x, self.portrait_y)

        # Draw dialogue text
        self._draw_dialogue_text()

        # Draw choices if showing
        if self.conversation_manager.is_showing_choices():
            self._draw_choices()
        else:
            # Draw continue hint
            self._draw_continue_hint()

    def _draw_dialogue_box(self):
        """Draw the main dialogue box."""
        box_rect = pygame.Rect(
            10, self.box_y,
            SCREEN_WIDTH - 20, self.box_height
        )

        # Background with gradient effect
        pygame.draw.rect(self.screen, (20, 25, 35), box_rect, border_radius=10)

        # Border with glow
        emotion_color = self.portrait.get_emotion()
        from config import EMOTION_COLORS
        border_color = EMOTION_COLORS.get(emotion_color, (100, 100, 100))

        # Outer glow
        glow_rect = box_rect.inflate(4, 4)
        pygame.draw.rect(self.screen, (*border_color, 50), glow_rect, 3, border_radius=12)

        # Main border
        pygame.draw.rect(self.screen, border_color, box_rect, 2, border_radius=10)

        # Inner highlight
        highlight_rect = pygame.Rect(box_rect.x + 3, box_rect.y + 3,
                                     box_rect.width - 6, 2)
        pygame.draw.rect(self.screen, (*border_color, 100), highlight_rect)

    def _draw_dialogue_text(self):
        """Draw the current dialogue text with word wrapping."""
        text = self.conversation_manager.get_current_text()
        if not text:
            return

        # Word wrap the text
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_surface = self.font_dialogue.render(test_line, True, COLOR_WHITE)
            if test_surface.get_width() <= self.text_max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        # Draw each line
        y = self.text_y
        for line in lines[:4]:  # Max 4 lines
            text_surface = self.font_dialogue.render(line, True, COLOR_WHITE)
            self.screen.blit(text_surface, (self.text_x, y))
            y += 28

    def _draw_choices(self):
        """Draw choice options."""
        choices = self.conversation_manager.get_choices()
        if not choices:
            return

        selected_index = self.conversation_manager.get_selected_choice_index()

        # Position choices below dialogue
        choice_y = self.box_y + 100
        choice_x = self.text_x

        for i, choice in enumerate(choices):
            is_selected = i == selected_index

            # Highlight selected choice
            if is_selected:
                # Selection background
                text_width = self.font_choice.size(f"{i+1}. {choice.text}")[0]
                highlight_rect = pygame.Rect(
                    choice_x - 5, choice_y - 2,
                    text_width + 15, 22
                )
                pygame.draw.rect(self.screen, (50, 60, 80), highlight_rect, border_radius=3)
                pygame.draw.rect(self.screen, COLOR_CYAN, highlight_rect, 1, border_radius=3)

                color = COLOR_CYAN
                prefix = "> "
            else:
                color = COLOR_GRAY
                prefix = "  "

            # Draw choice text
            choice_text = f"{prefix}{i+1}. {choice.text}"
            text_surface = self.font_choice.render(choice_text, True, color)
            self.screen.blit(text_surface, (choice_x, choice_y))

            choice_y += 25

        # Draw hint
        hint_text = "UP/DOWN or 1-4 to select, ENTER to confirm"
        hint_surface = self.font_hint.render(hint_text, True, COLOR_GRAY)
        self.screen.blit(hint_surface, (choice_x, choice_y + 5))

    def _draw_continue_hint(self):
        """Draw the continue hint."""
        # Blinking continue indicator
        if (self.frame_counter // 30) % 2 == 0:
            hint_text = "Press ENTER to continue..."
            hint_surface = self.font_hint.render(hint_text, True, COLOR_GRAY)
            hint_x = SCREEN_WIDTH - hint_surface.get_width() - 30
            hint_y = self.box_y + self.box_height - 25
            self.screen.blit(hint_surface, (hint_x, hint_y))

            # Small triangle indicator
            triangle_x = hint_x - 15
            triangle_y = hint_y + 8
            pygame.draw.polygon(self.screen, COLOR_GRAY, [
                (triangle_x, triangle_y - 5),
                (triangle_x, triangle_y + 5),
                (triangle_x + 8, triangle_y)
            ])


def create_conversation_ui(screen: pygame.Surface) -> ConversationUI:
    """Factory function to create a ConversationUI instance."""
    return ConversationUI(screen)

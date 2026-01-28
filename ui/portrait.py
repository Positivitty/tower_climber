"""Portrait rendering with emotion management for AI companion."""

import pygame
import math
from config import (
    EMOTION_NEUTRAL, EMOTION_WORRIED, EMOTION_EXCITED,
    EMOTION_HURT, EMOTION_QUESTIONING, EMOTION_DETERMINED,
    EMOTION_COLORS,
    PORTRAIT_SIZE, PORTRAIT_DISPLAY_SIZE
)


class Portrait:
    """Programmatic portrait with emotion-based appearance."""

    def __init__(self):
        self.current_emotion = EMOTION_NEUTRAL
        self.target_emotion = EMOTION_NEUTRAL
        self.transition_progress = 1.0
        self.transition_speed = 0.1

        # Animation state
        self.animation_frame = 0
        self.blink_timer = 0
        self.blink_duration = 8
        self.is_blinking = False

        # Cache surfaces for each emotion
        self.portrait_cache = {}
        self._generate_all_portraits()

    def _generate_all_portraits(self):
        """Pre-generate portrait surfaces for all emotions."""
        emotions = [
            EMOTION_NEUTRAL, EMOTION_WORRIED, EMOTION_EXCITED,
            EMOTION_HURT, EMOTION_QUESTIONING, EMOTION_DETERMINED
        ]
        for emotion in emotions:
            self.portrait_cache[emotion] = self._generate_portrait(emotion)

    def _generate_portrait(self, emotion: str) -> pygame.Surface:
        """Generate a portrait surface for an emotion."""
        surface = pygame.Surface((PORTRAIT_SIZE, PORTRAIT_SIZE), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))  # Transparent background

        # Get emotion color
        eye_color = EMOTION_COLORS.get(emotion, (0, 255, 255))

        # Face background - dark oval
        center = PORTRAIT_SIZE // 2
        face_color = (30, 35, 45)
        pygame.draw.ellipse(
            surface, face_color,
            (10, 15, PORTRAIT_SIZE - 20, PORTRAIT_SIZE - 25)
        )

        # Face outline glow
        glow_color = tuple(min(255, c // 3) for c in eye_color)
        pygame.draw.ellipse(
            surface, glow_color,
            (10, 15, PORTRAIT_SIZE - 20, PORTRAIT_SIZE - 25),
            2
        )

        # Draw features based on emotion
        self._draw_eyes(surface, emotion, eye_color)
        self._draw_mouth(surface, emotion, eye_color)
        self._draw_extras(surface, emotion, eye_color)

        return surface

    def _draw_eyes(self, surface: pygame.Surface, emotion: str, color: tuple):
        """Draw eyes based on emotion."""
        center = PORTRAIT_SIZE // 2
        eye_y = center - 10

        # Eye positions
        left_eye_x = center - 22
        right_eye_x = center + 22

        if emotion == EMOTION_NEUTRAL:
            # Normal eyes - simple circles with glow
            for eye_x in [left_eye_x, right_eye_x]:
                # Outer glow
                pygame.draw.circle(surface, color, (eye_x, eye_y), 12)
                # Inner dark
                pygame.draw.circle(surface, (20, 25, 35), (eye_x, eye_y), 9)
                # Bright center
                pygame.draw.circle(surface, color, (eye_x, eye_y), 5)
                # Highlight
                pygame.draw.circle(surface, (255, 255, 255), (eye_x - 2, eye_y - 2), 2)

        elif emotion == EMOTION_WORRIED:
            # Worried - eyes looking to side, furrowed brow effect
            for i, eye_x in enumerate([left_eye_x, right_eye_x]):
                # Outer
                pygame.draw.circle(surface, color, (eye_x, eye_y), 12)
                pygame.draw.circle(surface, (20, 25, 35), (eye_x, eye_y), 9)
                # Offset pupil (looking up/side)
                offset = -3 if i == 0 else 3
                pygame.draw.circle(surface, color, (eye_x + offset, eye_y - 2), 5)
                # Highlight
                pygame.draw.circle(surface, (255, 255, 255), (eye_x + offset - 1, eye_y - 4), 2)
                # Brow line (worried)
                brow_offset = 5 if i == 0 else -5
                pygame.draw.line(surface, color, (eye_x - 10, eye_y - 15 + (3 if i == 0 else 0)),
                                (eye_x + 10, eye_y - 15 + (0 if i == 0 else 3)), 2)

        elif emotion == EMOTION_EXCITED:
            # Excited - wide open eyes, bigger pupils
            for eye_x in [left_eye_x, right_eye_x]:
                # Larger outer
                pygame.draw.circle(surface, color, (eye_x, eye_y), 15)
                pygame.draw.circle(surface, (20, 25, 35), (eye_x, eye_y), 11)
                # Bigger bright center
                pygame.draw.circle(surface, color, (eye_x, eye_y), 7)
                # Multiple highlights for sparkle
                pygame.draw.circle(surface, (255, 255, 255), (eye_x - 3, eye_y - 3), 3)
                pygame.draw.circle(surface, (255, 255, 255), (eye_x + 2, eye_y + 2), 1)

        elif emotion == EMOTION_HURT:
            # Hurt - squinted eyes, pained
            for i, eye_x in enumerate([left_eye_x, right_eye_x]):
                # Squinted shape
                pygame.draw.ellipse(surface, color, (eye_x - 12, eye_y - 4, 24, 12))
                pygame.draw.ellipse(surface, (20, 25, 35), (eye_x - 9, eye_y - 2, 18, 8))
                # Small pupil
                pygame.draw.circle(surface, color, (eye_x, eye_y), 3)

        elif emotion == EMOTION_QUESTIONING:
            # Questioning - one raised eyebrow, tilted head effect
            for i, eye_x in enumerate([left_eye_x, right_eye_x]):
                pygame.draw.circle(surface, color, (eye_x, eye_y + (0 if i == 0 else -3)), 12)
                pygame.draw.circle(surface, (20, 25, 35), (eye_x, eye_y + (0 if i == 0 else -3)), 9)
                pygame.draw.circle(surface, color, (eye_x, eye_y + (0 if i == 0 else -3)), 5)
                # Raised eyebrow on right
                if i == 1:
                    pygame.draw.arc(surface, color,
                                   (eye_x - 15, eye_y - 25, 30, 15),
                                   0.5, 2.6, 2)
                else:
                    pygame.draw.line(surface, color,
                                    (eye_x - 10, eye_y - 14),
                                    (eye_x + 10, eye_y - 14), 2)

        elif emotion == EMOTION_DETERMINED:
            # Determined - intense eyes with strong glow
            for eye_x in [left_eye_x, right_eye_x]:
                # Strong glow effect
                for r in range(18, 10, -2):
                    alpha = 100 + (18 - r) * 15
                    glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*color, alpha), (r, r), r)
                    surface.blit(glow_surf, (eye_x - r, eye_y - r))
                # Core eye
                pygame.draw.circle(surface, (20, 25, 35), (eye_x, eye_y), 9)
                pygame.draw.circle(surface, color, (eye_x, eye_y), 6)
                pygame.draw.circle(surface, (255, 255, 255), (eye_x, eye_y), 2)

    def _draw_mouth(self, surface: pygame.Surface, emotion: str, color: tuple):
        """Draw mouth based on emotion."""
        center = PORTRAIT_SIZE // 2
        mouth_y = center + 25

        if emotion == EMOTION_NEUTRAL:
            # Simple line
            pygame.draw.line(surface, color, (center - 15, mouth_y), (center + 15, mouth_y), 2)

        elif emotion == EMOTION_WORRIED:
            # Slight frown
            pygame.draw.arc(surface, color,
                           (center - 15, mouth_y - 5, 30, 15),
                           3.4, 6.0, 2)

        elif emotion == EMOTION_EXCITED:
            # Smile
            pygame.draw.arc(surface, color,
                           (center - 18, mouth_y - 10, 36, 20),
                           0.3, 2.9, 2)

        elif emotion == EMOTION_HURT:
            # Open in pain
            pygame.draw.ellipse(surface, color, (center - 10, mouth_y - 5, 20, 12), 2)

        elif emotion == EMOTION_QUESTIONING:
            # Slight side smirk
            pygame.draw.arc(surface, color,
                           (center - 10, mouth_y - 3, 25, 10),
                           0.2, 2.5, 2)

        elif emotion == EMOTION_DETERMINED:
            # Firm line
            pygame.draw.line(surface, color, (center - 18, mouth_y), (center + 18, mouth_y), 3)

    def _draw_extras(self, surface: pygame.Surface, emotion: str, color: tuple):
        """Draw additional features based on emotion."""
        center = PORTRAIT_SIZE // 2

        if emotion == EMOTION_WORRIED:
            # Sweat drop
            drop_x = center + 40
            drop_y = center - 5
            # Draw teardrop shape
            pygame.draw.polygon(surface, (100, 200, 255), [
                (drop_x, drop_y - 8),
                (drop_x - 4, drop_y + 3),
                (drop_x + 4, drop_y + 3)
            ])
            pygame.draw.circle(surface, (100, 200, 255), (drop_x, drop_y + 3), 4)

        elif emotion == EMOTION_EXCITED:
            # Sparkle effects
            for offset in [(35, -20), (-35, -15), (30, 20)]:
                self._draw_sparkle(surface, center + offset[0], center + offset[1], color)

        elif emotion == EMOTION_HURT:
            # Damage lines
            pygame.draw.line(surface, (255, 100, 100),
                            (15, 25), (30, 40), 2)
            pygame.draw.line(surface, (255, 100, 100),
                            (PORTRAIT_SIZE - 15, 35), (PORTRAIT_SIZE - 30, 50), 2)

        elif emotion == EMOTION_DETERMINED:
            # Glowing aura at edges
            for i in range(3):
                glow_rect = pygame.Rect(5 - i * 2, 10 - i * 2,
                                        PORTRAIT_SIZE - 10 + i * 4,
                                        PORTRAIT_SIZE - 15 + i * 4)
                glow_color = (*color, 50 - i * 15)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.ellipse(glow_surf, glow_color, (0, 0, glow_rect.width, glow_rect.height), 1)
                surface.blit(glow_surf, (glow_rect.x, glow_rect.y))

    def _draw_sparkle(self, surface: pygame.Surface, x: int, y: int, color: tuple):
        """Draw a small sparkle effect."""
        size = 6
        pygame.draw.line(surface, color, (x - size, y), (x + size, y), 1)
        pygame.draw.line(surface, color, (x, y - size), (x, y + size), 1)
        pygame.draw.line(surface, (255, 255, 255), (x - 2, y - 2), (x + 2, y + 2), 1)
        pygame.draw.line(surface, (255, 255, 255), (x + 2, y - 2), (x - 2, y + 2), 1)

    def set_emotion(self, emotion: str):
        """Set the target emotion (with transition)."""
        if emotion != self.current_emotion:
            self.target_emotion = emotion
            self.transition_progress = 0.0

    def set_emotion_immediate(self, emotion: str):
        """Set emotion immediately without transition."""
        self.current_emotion = emotion
        self.target_emotion = emotion
        self.transition_progress = 1.0

    def update(self, dt: int = 1):
        """Update animation state."""
        self.animation_frame += dt

        # Handle emotion transition
        if self.transition_progress < 1.0:
            self.transition_progress = min(1.0, self.transition_progress + self.transition_speed)
            if self.transition_progress >= 1.0:
                self.current_emotion = self.target_emotion

        # Handle blinking
        self.blink_timer += dt
        if not self.is_blinking and self.blink_timer > 180:  # ~3 seconds
            if self.blink_timer > 180 + (hash(self.animation_frame) % 60):  # Random delay
                self.is_blinking = True
                self.blink_timer = 0
        elif self.is_blinking:
            if self.blink_timer > self.blink_duration:
                self.is_blinking = False
                self.blink_timer = 0

    def render(self, screen: pygame.Surface, x: int, y: int):
        """Render the portrait at the given position."""
        # Get the current portrait
        portrait = self.portrait_cache.get(self.current_emotion)
        if portrait is None:
            portrait = self.portrait_cache.get(EMOTION_NEUTRAL)

        # Scale to display size
        scaled = pygame.transform.scale(portrait, (PORTRAIT_DISPLAY_SIZE, PORTRAIT_DISPLAY_SIZE))

        # Apply subtle breathing animation
        breath_offset = math.sin(self.animation_frame * 0.05) * 2

        # Draw frame/border
        frame_rect = pygame.Rect(
            x - 5, y - 5 + breath_offset,
            PORTRAIT_DISPLAY_SIZE + 10, PORTRAIT_DISPLAY_SIZE + 10
        )
        pygame.draw.rect(screen, (40, 45, 55), frame_rect, border_radius=8)
        pygame.draw.rect(screen, EMOTION_COLORS.get(self.current_emotion, (100, 100, 100)),
                        frame_rect, 2, border_radius=8)

        # Blit portrait
        screen.blit(scaled, (x, y + breath_offset))

        # Draw blink overlay if blinking
        if self.is_blinking:
            blink_surf = pygame.Surface((PORTRAIT_DISPLAY_SIZE, PORTRAIT_DISPLAY_SIZE), pygame.SRCALPHA)
            eye_color = EMOTION_COLORS.get(self.current_emotion, (100, 100, 100))
            # Draw closed eyes as lines
            scaled_center = PORTRAIT_DISPLAY_SIZE // 2
            scaled_eye_y = scaled_center - int(10 * PORTRAIT_DISPLAY_SIZE / PORTRAIT_SIZE)
            left_x = scaled_center - int(22 * PORTRAIT_DISPLAY_SIZE / PORTRAIT_SIZE)
            right_x = scaled_center + int(22 * PORTRAIT_DISPLAY_SIZE / PORTRAIT_SIZE)
            line_len = int(12 * PORTRAIT_DISPLAY_SIZE / PORTRAIT_SIZE)

            # Black rectangles to cover eyes
            pygame.draw.rect(blink_surf, (30, 35, 45),
                            (left_x - line_len, scaled_eye_y - line_len,
                             line_len * 2, line_len * 2))
            pygame.draw.rect(blink_surf, (30, 35, 45),
                            (right_x - line_len, scaled_eye_y - line_len,
                             line_len * 2, line_len * 2))

            # Closed eye lines
            pygame.draw.line(blink_surf, eye_color,
                            (left_x - line_len, scaled_eye_y),
                            (left_x + line_len, scaled_eye_y), 2)
            pygame.draw.line(blink_surf, eye_color,
                            (right_x - line_len, scaled_eye_y),
                            (right_x + line_len, scaled_eye_y), 2)

            screen.blit(blink_surf, (x, y + breath_offset))

    def get_emotion(self) -> str:
        """Get the current emotion."""
        return self.current_emotion

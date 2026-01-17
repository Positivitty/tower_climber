"""Training mini-games that the AI learns to play."""

import random
import math
from config import (
    MINIGAME_DURATION_FRAMES, MINIGAME_TARGET_WIDTH,
    REWARD_TRAINING_SUCCESS, REWARD_TRAINING_FAIL, REWARD_MINIGAME_PERFECT,
    ACTION_MINIGAME_PRESS, ACTION_MINIGAME_WAIT, MINIGAME_ACTIONS
)


class MiniGame:
    """Base class for training mini-games."""

    def __init__(self, stat: str, difficulty: int = 1):
        self.stat = stat
        self.difficulty = difficulty
        self.frame = 0
        self.duration = MINIGAME_DURATION_FRAMES
        self.finished = False
        self.success = False
        self.perfect = False
        self.result_message = ""

    def update(self, action: int = None) -> float:
        """Update mini-game state. Returns reward if finished."""
        raise NotImplementedError

    def get_state(self) -> tuple:
        """Get discretized state for Q-learning."""
        raise NotImplementedError

    def get_progress(self) -> float:
        """Get progress (0.0 to 1.0) for display."""
        return self.frame / self.duration

    def is_finished(self) -> bool:
        return self.finished

    def get_reward(self) -> float:
        """Get the reward for this mini-game attempt."""
        if not self.finished:
            return 0
        if self.perfect:
            return REWARD_MINIGAME_PERFECT
        if self.success:
            return REWARD_TRAINING_SUCCESS
        return REWARD_TRAINING_FAIL


class TimingBarGame(MiniGame):
    """Timing bar mini-game - press when indicator is in target zone.

    Used for: Strength (lifting weights)
    """

    def __init__(self, stat: str, difficulty: int = 1):
        super().__init__(stat, difficulty)

        # Bar moves back and forth
        self.bar_position = 0.0  # 0.0 to 1.0
        self.bar_direction = 1  # 1 = right, -1 = left
        self.bar_speed = 0.015 + difficulty * 0.005  # Speed increases with difficulty

        # Target zone (smaller = harder)
        target_width = max(0.08, 0.15 - difficulty * 0.02)
        self.target_start = random.uniform(0.3, 0.7 - target_width)
        self.target_end = self.target_start + target_width

        # Perfect zone (center of target)
        perfect_margin = target_width * 0.3
        self.perfect_start = self.target_start + perfect_margin
        self.perfect_end = self.target_end - perfect_margin

        self.pressed = False
        self.press_position = None

    def update(self, action: int = None) -> float:
        """Update the timing bar."""
        if self.finished:
            return 0

        self.frame += 1

        # Move the bar
        self.bar_position += self.bar_direction * self.bar_speed
        if self.bar_position >= 1.0:
            self.bar_position = 1.0
            self.bar_direction = -1
        elif self.bar_position <= 0.0:
            self.bar_position = 0.0
            self.bar_direction = 1

        # Check for press action
        if action == ACTION_MINIGAME_PRESS and not self.pressed:
            self.pressed = True
            self.press_position = self.bar_position
            self._evaluate_press()

        # Auto-fail if time runs out
        if self.frame >= self.duration and not self.pressed:
            self.finished = True
            self.success = False
            self.result_message = "Too slow! Time ran out."

        return self.get_reward() if self.finished else 0

    def _evaluate_press(self):
        """Evaluate the press position."""
        self.finished = True

        if self.perfect_start <= self.press_position <= self.perfect_end:
            self.success = True
            self.perfect = True
            self.result_message = "PERFECT! Excellent timing!"
        elif self.target_start <= self.press_position <= self.target_end:
            self.success = True
            self.perfect = False
            self.result_message = "Good! Hit the target zone."
        else:
            self.success = False
            self.result_message = "Missed! Try to hit the green zone."

    def get_state(self) -> tuple:
        """Get state: (position_bucket, in_target, in_perfect, approaching)."""
        # Position bucket (0-9)
        pos_bucket = min(9, int(self.bar_position * 10))

        # In target zone
        in_target = 1 if self.target_start <= self.bar_position <= self.target_end else 0

        # In perfect zone
        in_perfect = 1 if self.perfect_start <= self.bar_position <= self.perfect_end else 0

        # Approaching target (heading toward it)
        target_center = (self.target_start + self.target_end) / 2
        approaching = 1 if (
            (self.bar_position < target_center and self.bar_direction > 0) or
            (self.bar_position > target_center and self.bar_direction < 0)
        ) else 0

        return (pos_bucket, in_target, in_perfect, approaching)

    def get_visual_data(self) -> dict:
        """Get data for rendering."""
        return {
            'progress': self.bar_position,
            'target_start': self.target_start,
            'target_end': self.target_end,
            'success': self.success if self.finished else None
        }


class PatternGame(MiniGame):
    """Pattern memory game - remember and repeat a sequence.

    Used for: Intelligence
    """

    def __init__(self, stat: str, difficulty: int = 1):
        super().__init__(stat, difficulty)

        # Generate pattern (length based on difficulty)
        self.pattern_length = 2 + difficulty
        self.pattern = [random.randint(0, 3) for _ in range(self.pattern_length)]

        # Player's input
        self.player_input = []
        self.current_index = 0

        # Phases: show pattern, then input
        self.phase = 'show'  # 'show' or 'input'
        self.show_frame = 0
        self.show_duration = 40  # Frames per pattern element

        self.highlighted = None  # Currently highlighted button (0-3 or None)

    def update(self, action: int = None) -> float:
        """Update the pattern game."""
        if self.finished:
            return 0

        self.frame += 1

        if self.phase == 'show':
            # Showing the pattern
            pattern_idx = self.show_frame // self.show_duration
            if pattern_idx < len(self.pattern):
                self.highlighted = self.pattern[pattern_idx]
            else:
                self.highlighted = None
                self.phase = 'input'

            self.show_frame += 1

        elif self.phase == 'input':
            # Waiting for input
            if action is not None and action < 4:  # Actions 0-3 for buttons
                self.player_input.append(action)

                if action == self.pattern[self.current_index]:
                    self.current_index += 1
                    if self.current_index >= len(self.pattern):
                        # Completed successfully
                        self.finished = True
                        self.success = True
                        self.perfect = self.frame < self.duration * 0.5
                        self.result_message = "Perfect memory!" if self.perfect else "Pattern matched!"
                else:
                    # Wrong input
                    self.finished = True
                    self.success = False
                    self.result_message = "Wrong pattern! Keep practicing."

            # Time limit
            if self.frame >= self.duration and not self.finished:
                self.finished = True
                self.success = False
                self.result_message = "Time's up!"

        return self.get_reward() if self.finished else 0

    def get_state(self) -> tuple:
        """Get state for pattern game."""
        # Phase
        phase_val = 0 if self.phase == 'show' else 1

        # Progress through pattern
        progress = min(4, self.current_index)

        # Next expected button (during input phase)
        next_btn = self.pattern[self.current_index] if self.current_index < len(self.pattern) else 0

        return (phase_val, progress, next_btn)


class ReactionGame(MiniGame):
    """Reaction time game - press as fast as possible when signal appears.

    Used for: Agility
    """

    def __init__(self, stat: str, difficulty: int = 1):
        super().__init__(stat, difficulty)

        # Random delay before signal
        self.signal_frame = random.randint(60, 120)  # 1-2 seconds
        self.signal_active = False

        # Reaction tracking
        self.reaction_time = None
        self.pressed_early = False

        # Thresholds (in frames, smaller = harder)
        self.perfect_threshold = 10 - difficulty  # frames
        self.success_threshold = 25 - difficulty * 2

    def update(self, action: int = None) -> float:
        """Update the reaction game."""
        if self.finished:
            return 0

        self.frame += 1

        # Check for signal
        if self.frame >= self.signal_frame and not self.signal_active:
            self.signal_active = True

        # Check for press
        if action == ACTION_MINIGAME_PRESS:
            if not self.signal_active:
                # Pressed too early
                self.finished = True
                self.success = False
                self.pressed_early = True
                self.result_message = "Too early! Wait for the signal."
            else:
                # Calculate reaction time
                self.reaction_time = self.frame - self.signal_frame
                self.finished = True

                if self.reaction_time <= self.perfect_threshold:
                    self.success = True
                    self.perfect = True
                    self.result_message = f"PERFECT! {self.reaction_time} frames!"
                elif self.reaction_time <= self.success_threshold:
                    self.success = True
                    self.result_message = f"Good reaction! {self.reaction_time} frames."
                else:
                    self.success = False
                    self.result_message = f"Too slow! {self.reaction_time} frames."

        # Time limit
        if self.frame >= self.duration and not self.finished:
            self.finished = True
            self.success = False
            self.result_message = "No reaction detected!"

        return self.get_reward() if self.finished else 0

    def get_state(self) -> tuple:
        """Get state: (signal_active, frames_since_signal_bucket)."""
        signal_val = 1 if self.signal_active else 0

        if self.signal_active:
            frames_since = self.frame - self.signal_frame
            bucket = min(5, frames_since // 5)  # 0-5 buckets
        else:
            bucket = 0

        return (signal_val, bucket)


class BlockGame(MiniGame):
    """Block timing game - press to block incoming attacks.

    Used for: Defense
    """

    def __init__(self, stat: str, difficulty: int = 1):
        super().__init__(stat, difficulty)

        # Attack timing
        self.attack_frame = random.randint(40, 100)
        self.attack_active = False
        self.attack_progress = 0.0  # 0.0 to 1.0 as attack approaches

        # Block window
        self.block_window_start = 0.7  # Block must be timed when attack is 70-90% through
        self.block_window_end = 0.95
        self.perfect_window_start = 0.8
        self.perfect_window_end = 0.9

        self.blocked = False

    def update(self, action: int = None) -> float:
        """Update the block game."""
        if self.finished:
            return 0

        self.frame += 1

        # Start attack
        if self.frame >= self.attack_frame and not self.attack_active:
            self.attack_active = True

        # Progress attack
        if self.attack_active:
            attack_duration = 60 - self.difficulty * 5
            frames_in_attack = self.frame - self.attack_frame
            self.attack_progress = min(1.0, frames_in_attack / attack_duration)

            # Attack lands
            if self.attack_progress >= 1.0 and not self.blocked:
                self.finished = True
                self.success = False
                self.result_message = "Hit! Failed to block in time."

        # Check for block
        if action == ACTION_MINIGAME_PRESS and self.attack_active and not self.blocked:
            self.blocked = True
            self.finished = True

            if self.perfect_window_start <= self.attack_progress <= self.perfect_window_end:
                self.success = True
                self.perfect = True
                self.result_message = "PERFECT BLOCK! Excellent timing!"
            elif self.block_window_start <= self.attack_progress <= self.block_window_end:
                self.success = True
                self.result_message = "Blocked! Good defense."
            else:
                self.success = False
                self.result_message = "Bad timing! Block was too early or late."

        # Time limit
        if self.frame >= self.duration and not self.finished:
            self.finished = True
            self.success = False
            self.result_message = "Time's up!"

        return self.get_reward() if self.finished else 0

    def get_state(self) -> tuple:
        """Get state: (attack_active, progress_bucket, in_window)."""
        attack_val = 1 if self.attack_active else 0
        progress_bucket = min(9, int(self.attack_progress * 10))
        in_window = 1 if self.block_window_start <= self.attack_progress <= self.block_window_end else 0

        return (attack_val, progress_bucket, in_window)


class DiceGame(MiniGame):
    """Luck-based dice game - some skill, mostly luck.

    Used for: Luck
    """

    def __init__(self, stat: str, difficulty: int = 1):
        super().__init__(stat, difficulty)

        # Dice values
        self.dice = [0, 0, 0]
        self.rolling = [True, True, True]
        self.roll_speed = [3, 4, 5]  # Different speeds for each die

        # Target (sum needed to win)
        self.target = 10 + difficulty * 2
        self.stops_remaining = 3

    def update(self, action: int = None) -> float:
        """Update the dice game."""
        if self.finished:
            return 0

        self.frame += 1

        # Roll dice
        for i in range(3):
            if self.rolling[i]:
                if self.frame % self.roll_speed[i] == 0:
                    self.dice[i] = random.randint(1, 6)

        # Stop a die on press
        if action == ACTION_MINIGAME_PRESS and self.stops_remaining > 0:
            for i in range(3):
                if self.rolling[i]:
                    self.rolling[i] = False
                    self.stops_remaining -= 1
                    break

            # Check if all stopped
            if not any(self.rolling):
                self._evaluate_dice()

        # Auto-stop if time runs out
        if self.frame >= self.duration and not self.finished:
            for i in range(3):
                self.rolling[i] = False
            self._evaluate_dice()

        return self.get_reward() if self.finished else 0

    def _evaluate_dice(self):
        """Evaluate the dice roll."""
        self.finished = True
        total = sum(self.dice)

        if total >= self.target + 3:
            self.success = True
            self.perfect = True
            self.result_message = f"LUCKY! Rolled {total} (needed {self.target})"
        elif total >= self.target:
            self.success = True
            self.result_message = f"Success! Rolled {total} (needed {self.target})"
        else:
            self.success = False
            self.result_message = f"Unlucky... Rolled {total} (needed {self.target})"

    def get_state(self) -> tuple:
        """Get state: (current_sum_bucket, dice_rolling_count)."""
        current_sum = sum(self.dice)
        sum_bucket = min(5, current_sum // 4)
        rolling_count = sum(1 for r in self.rolling if r)

        return (sum_bucket, rolling_count)


def create_minigame(stat: str, difficulty: int = 1) -> MiniGame:
    """Create a mini-game for the given stat."""
    games = {
        'strength': TimingBarGame,
        'intelligence': PatternGame,
        'agility': ReactionGame,
        'defense': BlockGame,
        'luck': DiceGame
    }

    game_class = games.get(stat, TimingBarGame)
    return game_class(stat, difficulty)

"""Training mini-games that the AI learns to play."""

import random
from config import (
    MINIGAME_DURATION_FRAMES,
    REWARD_TRAINING_SUCCESS, REWARD_TRAINING_FAIL, REWARD_MINIGAME_PERFECT,
    ACTION_MINIGAME_PRESS, ACTION_MINIGAME_WAIT
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
        self.game_type = "base"

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

    def get_visual_data(self) -> dict:
        """Get data for rendering - override in subclasses."""
        return {
            'type': self.game_type,
            'progress': self.get_progress(),
            'finished': self.finished,
            'success': self.success if self.finished else None
        }


class TimingBarGame(MiniGame):
    """Timing bar mini-game - press when indicator is in target zone.
    Used for: Strength (lifting weights)
    """

    def __init__(self, stat: str, difficulty: int = 1):
        super().__init__(stat, difficulty)
        self.game_type = "timing_bar"

        self.bar_position = 0.0
        self.bar_direction = 1
        self.bar_speed = 0.02 + difficulty * 0.008

        target_width = max(0.1, 0.18 - difficulty * 0.02)
        self.target_start = random.uniform(0.25, 0.75 - target_width)
        self.target_end = self.target_start + target_width

        perfect_margin = target_width * 0.25
        self.perfect_start = self.target_start + perfect_margin
        self.perfect_end = self.target_end - perfect_margin

        self.pressed = False

    def update(self, action: int = None) -> float:
        if self.finished:
            return 0

        self.frame += 1

        self.bar_position += self.bar_direction * self.bar_speed
        if self.bar_position >= 1.0:
            self.bar_position = 1.0
            self.bar_direction = -1
        elif self.bar_position <= 0.0:
            self.bar_position = 0.0
            self.bar_direction = 1

        if action == ACTION_MINIGAME_PRESS and not self.pressed:
            self.pressed = True
            self._evaluate_press()

        if self.frame >= self.duration and not self.pressed:
            self.finished = True
            self.success = False
            self.result_message = "Too slow! Time ran out."

        return self.get_reward() if self.finished else 0

    def _evaluate_press(self):
        self.finished = True
        if self.perfect_start <= self.bar_position <= self.perfect_end:
            self.success = True
            self.perfect = True
            self.result_message = "PERFECT! Excellent timing!"
        elif self.target_start <= self.bar_position <= self.target_end:
            self.success = True
            self.result_message = "Good! Hit the target zone."
        else:
            self.success = False
            self.result_message = "Missed! Try to hit the green zone."

    def get_state(self) -> tuple:
        pos_bucket = min(9, int(self.bar_position * 10))
        in_target = 1 if self.target_start <= self.bar_position <= self.target_end else 0
        in_perfect = 1 if self.perfect_start <= self.bar_position <= self.perfect_end else 0
        target_center = (self.target_start + self.target_end) / 2
        approaching = 1 if (
            (self.bar_position < target_center and self.bar_direction > 0) or
            (self.bar_position > target_center and self.bar_direction < 0)
        ) else 0
        return (pos_bucket, in_target, in_perfect, approaching)

    def get_visual_data(self) -> dict:
        return {
            'type': self.game_type,
            'progress': self.bar_position,
            'target_start': self.target_start,
            'target_end': self.target_end,
            'finished': self.finished,
            'success': self.success if self.finished else None
        }


class ReactionGame(MiniGame):
    """Reaction time game - press when the signal appears.
    Used for: Agility
    """

    def __init__(self, stat: str, difficulty: int = 1):
        super().__init__(stat, difficulty)
        self.game_type = "reaction"

        self.signal_frame = random.randint(40, 90)
        self.signal_active = False
        self.reaction_time = None

        self.perfect_threshold = max(5, 12 - difficulty * 2)
        self.success_threshold = max(15, 30 - difficulty * 3)

    def update(self, action: int = None) -> float:
        if self.finished:
            return 0

        self.frame += 1

        if self.frame >= self.signal_frame and not self.signal_active:
            self.signal_active = True

        if action == ACTION_MINIGAME_PRESS:
            if not self.signal_active:
                self.finished = True
                self.success = False
                self.result_message = "Too early! Wait for GO!"
            else:
                self.reaction_time = self.frame - self.signal_frame
                self.finished = True
                if self.reaction_time <= self.perfect_threshold:
                    self.success = True
                    self.perfect = True
                    self.result_message = f"PERFECT! {self.reaction_time} frames!"
                elif self.reaction_time <= self.success_threshold:
                    self.success = True
                    self.result_message = f"Good! {self.reaction_time} frames."
                else:
                    self.success = False
                    self.result_message = f"Too slow! {self.reaction_time} frames."

        if self.frame >= self.duration and not self.finished:
            self.finished = True
            self.success = False
            self.result_message = "No reaction!"

        return self.get_reward() if self.finished else 0

    def get_state(self) -> tuple:
        signal_val = 1 if self.signal_active else 0
        if self.signal_active:
            frames_since = self.frame - self.signal_frame
            bucket = min(5, frames_since // 5)
        else:
            bucket = 0
        return (signal_val, bucket)

    def get_visual_data(self) -> dict:
        return {
            'type': self.game_type,
            'signal_active': self.signal_active,
            'progress': self.get_progress(),
            'finished': self.finished,
            'success': self.success if self.finished else None
        }


class BlockGame(MiniGame):
    """Block timing game - press to block incoming attack.
    Used for: Defense
    """

    def __init__(self, stat: str, difficulty: int = 1):
        super().__init__(stat, difficulty)
        self.game_type = "block"

        self.attack_frame = random.randint(30, 70)
        self.attack_active = False
        self.attack_progress = 0.0
        self.attack_duration = max(40, 60 - difficulty * 5)

        self.block_window_start = 0.65
        self.block_window_end = 0.95
        self.perfect_window_start = 0.75
        self.perfect_window_end = 0.88
        self.blocked = False

    def update(self, action: int = None) -> float:
        if self.finished:
            return 0

        self.frame += 1

        if self.frame >= self.attack_frame and not self.attack_active:
            self.attack_active = True

        if self.attack_active and not self.blocked:
            frames_in_attack = self.frame - self.attack_frame
            self.attack_progress = min(1.0, frames_in_attack / self.attack_duration)

            if self.attack_progress >= 1.0:
                self.finished = True
                self.success = False
                self.result_message = "Hit! Failed to block."

        if action == ACTION_MINIGAME_PRESS and self.attack_active and not self.blocked:
            self.blocked = True
            self.finished = True
            if self.perfect_window_start <= self.attack_progress <= self.perfect_window_end:
                self.success = True
                self.perfect = True
                self.result_message = "PERFECT BLOCK!"
            elif self.block_window_start <= self.attack_progress <= self.block_window_end:
                self.success = True
                self.result_message = "Blocked!"
            else:
                self.success = False
                self.result_message = "Bad timing!"

        if self.frame >= self.duration and not self.finished:
            self.finished = True
            self.success = False
            self.result_message = "Time's up!"

        return self.get_reward() if self.finished else 0

    def get_state(self) -> tuple:
        attack_val = 1 if self.attack_active else 0
        progress_bucket = min(9, int(self.attack_progress * 10))
        in_window = 1 if self.block_window_start <= self.attack_progress <= self.block_window_end else 0
        return (attack_val, progress_bucket, in_window)

    def get_visual_data(self) -> dict:
        return {
            'type': self.game_type,
            'attack_active': self.attack_active,
            'attack_progress': self.attack_progress,
            'block_window_start': self.block_window_start,
            'block_window_end': self.block_window_end,
            'finished': self.finished,
            'success': self.success if self.finished else None
        }


class DiceGame(MiniGame):
    """Luck-based dice game.
    Used for: Luck
    """

    def __init__(self, stat: str, difficulty: int = 1):
        super().__init__(stat, difficulty)
        self.game_type = "dice"

        self.dice = [1, 1, 1]
        self.rolling = [True, True, True]
        self.roll_speed = [2, 3, 4]
        self.target = 9 + difficulty
        self.stops_remaining = 3

    def update(self, action: int = None) -> float:
        if self.finished:
            return 0

        self.frame += 1

        for i in range(3):
            if self.rolling[i] and self.frame % self.roll_speed[i] == 0:
                self.dice[i] = random.randint(1, 6)

        if action == ACTION_MINIGAME_PRESS and self.stops_remaining > 0:
            for i in range(3):
                if self.rolling[i]:
                    self.rolling[i] = False
                    self.stops_remaining -= 1
                    break
            if not any(self.rolling):
                self._evaluate()

        if self.frame >= self.duration and not self.finished:
            for i in range(3):
                self.rolling[i] = False
            self._evaluate()

        return self.get_reward() if self.finished else 0

    def _evaluate(self):
        self.finished = True
        total = sum(self.dice)
        if total >= self.target + 4:
            self.success = True
            self.perfect = True
            self.result_message = f"LUCKY! {total} (need {self.target})"
        elif total >= self.target:
            self.success = True
            self.result_message = f"Success! {total} (need {self.target})"
        else:
            self.success = False
            self.result_message = f"Unlucky... {total} (need {self.target})"

    def get_state(self) -> tuple:
        current_sum = sum(self.dice)
        sum_bucket = min(5, current_sum // 4)
        rolling_count = sum(1 for r in self.rolling if r)
        return (sum_bucket, rolling_count)

    def get_visual_data(self) -> dict:
        return {
            'type': self.game_type,
            'dice': self.dice.copy(),
            'rolling': self.rolling.copy(),
            'target': self.target,
            'finished': self.finished,
            'success': self.success if self.finished else None
        }


class PatternGame(MiniGame):
    """Pattern memory - simplified to timing for AI.
    Used for: Intelligence
    """

    def __init__(self, stat: str, difficulty: int = 1):
        super().__init__(stat, difficulty)
        self.game_type = "timing_bar"  # Use timing bar for consistency

        # Slower bar for intelligence - requires more patience
        self.bar_position = 0.0
        self.bar_direction = 1
        self.bar_speed = 0.008 + difficulty * 0.002  # Much slower than strength

        target_width = max(0.1, 0.18 - difficulty * 0.02)
        self.target_start = random.uniform(0.25, 0.75 - target_width)
        self.target_end = self.target_start + target_width

        perfect_margin = target_width * 0.25
        self.perfect_start = self.target_start + perfect_margin
        self.perfect_end = self.target_end - perfect_margin

        self.pressed = False

    def update(self, action: int = None) -> float:
        if self.finished:
            return 0

        self.frame += 1

        self.bar_position += self.bar_direction * self.bar_speed
        if self.bar_position >= 1.0:
            self.bar_position = 1.0
            self.bar_direction = -1
        elif self.bar_position <= 0.0:
            self.bar_position = 0.0
            self.bar_direction = 1

        if action == ACTION_MINIGAME_PRESS and not self.pressed:
            self.pressed = True
            self._evaluate_press()

        if self.frame >= self.duration and not self.pressed:
            self.finished = True
            self.success = False
            self.result_message = "Time ran out!"

        return self.get_reward() if self.finished else 0

    def _evaluate_press(self):
        self.finished = True
        if self.perfect_start <= self.bar_position <= self.perfect_end:
            self.success = True
            self.perfect = True
            self.result_message = "PERFECT! Great focus!"
        elif self.target_start <= self.bar_position <= self.target_end:
            self.success = True
            self.result_message = "Good concentration!"
        else:
            self.success = False
            self.result_message = "Missed! Need more focus."

    def get_state(self) -> tuple:
        pos_bucket = min(9, int(self.bar_position * 10))
        in_target = 1 if self.target_start <= self.bar_position <= self.target_end else 0
        in_perfect = 1 if self.perfect_start <= self.bar_position <= self.perfect_end else 0
        target_center = (self.target_start + self.target_end) / 2
        approaching = 1 if (
            (self.bar_position < target_center and self.bar_direction > 0) or
            (self.bar_position > target_center and self.bar_direction < 0)
        ) else 0
        return (pos_bucket, in_target, in_perfect, approaching)

    def get_visual_data(self) -> dict:
        return {
            'type': self.game_type,
            'progress': self.bar_position,
            'target_start': self.target_start,
            'target_end': self.target_end,
            'finished': self.finished,
            'success': self.success if self.finished else None
        }


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

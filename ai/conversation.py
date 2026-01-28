"""Conversation system with data structures, templates, and flow management."""

import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from config import (
    TRIGGER_LOW_HP, TRIGGER_NEAR_DEATH, TRIGGER_BOSS_ENCOUNTER,
    TRIGGER_FIRST_ENEMY_TYPE, TRIGGER_VICTORY, TRIGGER_DEATH,
    TRIGGER_CLOSE_CALL, TRIGGER_STRATEGY_QUESTION,
    EMOTION_NEUTRAL, EMOTION_WORRIED, EMOTION_EXCITED,
    EMOTION_HURT, EMOTION_QUESTIONING, EMOTION_DETERMINED,
    CHOICE_EFFECT_STRATEGY, CHOICE_EFFECT_LEARNING_BOOST,
    CHOICE_EFFECT_ENCOURAGEMENT
)


@dataclass
class ConversationChoice:
    """A choice the player can make during conversation."""
    text: str
    effect_type: str  # strategy, learning_boost, encouragement
    effect_value: Any = None  # e.g., 'aggressive', 'defensive'
    response_text: str = ""  # AI response after selection


@dataclass
class ConversationTemplate:
    """Template for a conversation triggered by a critical moment."""
    trigger: str
    emotion: str
    dialogue_lines: List[str]
    choices: List[ConversationChoice] = field(default_factory=list)
    priority: int = 0  # Higher = more important (shown first)

    def get_dialogue(self, context: Dict[str, Any] = None) -> List[str]:
        """Get dialogue with context substitution."""
        if context is None:
            context = {}

        lines = []
        for line in self.dialogue_lines:
            try:
                formatted = line.format(**context)
            except KeyError:
                formatted = line
            lines.append(formatted)
        return lines


# Conversation templates for each trigger type
CONVERSATION_TEMPLATES = {
    TRIGGER_LOW_HP: [
        ConversationTemplate(
            trigger=TRIGGER_LOW_HP,
            emotion=EMOTION_WORRIED,
            dialogue_lines=[
                "My HP is critically low... only {hp}/{max_hp} remaining.",
                "I need to be more careful. One wrong move could end this.",
                "What should I focus on?"
            ],
            choices=[
                ConversationChoice(
                    text="Play it safe - dodge and retreat",
                    effect_type=CHOICE_EFFECT_STRATEGY,
                    effect_value='defensive',
                    response_text="Right, survival first. I'll focus on dodging."
                ),
                ConversationChoice(
                    text="Strike fast before they can finish you",
                    effect_type=CHOICE_EFFECT_STRATEGY,
                    effect_value='aggressive',
                    response_text="Good point - best defense is a good offense!"
                ),
                ConversationChoice(
                    text="Trust your instincts",
                    effect_type=CHOICE_EFFECT_ENCOURAGEMENT,
                    effect_value=None,
                    response_text="You're right. I've learned from my battles."
                )
            ],
            priority=8
        ),
        ConversationTemplate(
            trigger=TRIGGER_LOW_HP,
            emotion=EMOTION_HURT,
            dialogue_lines=[
                "Ugh... that hurt. {hp} HP left.",
                "I can't take many more hits like that.",
                "How should I approach this?"
            ],
            choices=[
                ConversationChoice(
                    text="Keep your distance",
                    effect_type=CHOICE_EFFECT_STRATEGY,
                    effect_value='defensive',
                    response_text="Distance is safety. I'll kite them."
                ),
                ConversationChoice(
                    text="Finish this quickly",
                    effect_type=CHOICE_EFFECT_STRATEGY,
                    effect_value='aggressive',
                    response_text="No time for caution - going all in!"
                )
            ],
            priority=7
        )
    ],

    TRIGGER_NEAR_DEATH: [
        ConversationTemplate(
            trigger=TRIGGER_NEAR_DEATH,
            emotion=EMOTION_WORRIED,
            dialogue_lines=[
                "That was way too close! Only {hp} HP left!",
                "I almost died there... my circuits are still shaking.",
                "I need to learn from that."
            ],
            choices=[
                ConversationChoice(
                    text="Pay more attention to defense",
                    effect_type=CHOICE_EFFECT_LEARNING_BOOST,
                    effect_value='defensive',
                    response_text="Analyzing defensive patterns more carefully..."
                ),
                ConversationChoice(
                    text="Kill them before they kill you",
                    effect_type=CHOICE_EFFECT_LEARNING_BOOST,
                    effect_value='aggressive',
                    response_text="Right - more damage means less time for them to hit me."
                )
            ],
            priority=9
        )
    ],

    TRIGGER_BOSS_ENCOUNTER: [
        ConversationTemplate(
            trigger=TRIGGER_BOSS_ENCOUNTER,
            emotion=EMOTION_DETERMINED,
            dialogue_lines=[
                "A boss! {boss_name} stands before us!",
                "This is a real challenge. I've never faced one of these before.",
                "Any advice for this fight?"
            ],
            choices=[
                ConversationChoice(
                    text="Learn its patterns first",
                    effect_type=CHOICE_EFFECT_LEARNING_BOOST,
                    effect_value=None,
                    response_text="Good thinking. I'll study its movements carefully."
                ),
                ConversationChoice(
                    text="Show it what you've learned",
                    effect_type=CHOICE_EFFECT_ENCOURAGEMENT,
                    effect_value=None,
                    response_text="You're right - all my training has led to this!"
                ),
                ConversationChoice(
                    text="Be aggressive - bosses hit hard anyway",
                    effect_type=CHOICE_EFFECT_STRATEGY,
                    effect_value='aggressive',
                    response_text="True. Might as well go down swinging!"
                )
            ],
            priority=10
        )
    ],

    TRIGGER_FIRST_ENEMY_TYPE: [
        ConversationTemplate(
            trigger=TRIGGER_FIRST_ENEMY_TYPE,
            emotion=EMOTION_QUESTIONING,
            dialogue_lines=[
                "Interesting... a {enemy_type} enemy.",
                "I haven't encountered this type before.",
                "Let me analyze and adapt."
            ],
            choices=[
                ConversationChoice(
                    text="Be careful until you learn its patterns",
                    effect_type=CHOICE_EFFECT_LEARNING_BOOST,
                    effect_value=None,
                    response_text="Smart. I'll observe before committing."
                ),
                ConversationChoice(
                    text="It's just another enemy - fight!",
                    effect_type=CHOICE_EFFECT_STRATEGY,
                    effect_value='aggressive',
                    response_text="You're right, fundamentals still apply!"
                )
            ],
            priority=5
        ),
        ConversationTemplate(
            trigger=TRIGGER_FIRST_ENEMY_TYPE,
            emotion=EMOTION_EXCITED,
            dialogue_lines=[
                "Oh! A {enemy_type}! First time seeing one.",
                "New data to collect! This is exciting.",
                "Let's see what it can do."
            ],
            choices=[
                ConversationChoice(
                    text="Focus on learning",
                    effect_type=CHOICE_EFFECT_LEARNING_BOOST,
                    effect_value=None,
                    response_text="Processing... new patterns detected!"
                )
            ],
            priority=4
        )
    ],

    TRIGGER_VICTORY: [
        ConversationTemplate(
            trigger=TRIGGER_VICTORY,
            emotion=EMOTION_EXCITED,
            dialogue_lines=[
                "Floor {floor} cleared!",
                "We defeated {enemies_defeated} enemies together.",
                "On to the next challenge!"
            ],
            choices=[],
            priority=3
        ),
        ConversationTemplate(
            trigger=TRIGGER_VICTORY,
            emotion=EMOTION_DETERMINED,
            dialogue_lines=[
                "Victory! Floor {floor} is behind us now.",
                "Every floor makes me stronger.",
                "What's next?"
            ],
            choices=[
                ConversationChoice(
                    text="Keep pushing forward",
                    effect_type=CHOICE_EFFECT_ENCOURAGEMENT,
                    effect_value=None,
                    response_text="Let's see how far we can go!"
                ),
                ConversationChoice(
                    text="Take a moment to rest",
                    effect_type=CHOICE_EFFECT_STRATEGY,
                    effect_value='defensive',
                    response_text="Good idea. I'll recover and prepare."
                )
            ],
            priority=2
        )
    ],

    TRIGGER_DEATH: [
        ConversationTemplate(
            trigger=TRIGGER_DEATH,
            emotion=EMOTION_HURT,
            dialogue_lines=[
                "I... I failed on floor {floor}.",
                "But failure is just data. I'll learn from this.",
                "Next time will be different."
            ],
            choices=[
                ConversationChoice(
                    text="You did your best",
                    effect_type=CHOICE_EFFECT_ENCOURAGEMENT,
                    effect_value=None,
                    response_text="Thank you. I'll use this experience."
                ),
                ConversationChoice(
                    text="Let's analyze what went wrong",
                    effect_type=CHOICE_EFFECT_LEARNING_BOOST,
                    effect_value=None,
                    response_text="Yes... reviewing combat logs... lessons learned."
                )
            ],
            priority=6
        )
    ],

    TRIGGER_CLOSE_CALL: [
        ConversationTemplate(
            trigger=TRIGGER_CLOSE_CALL,
            emotion=EMOTION_EXCITED,
            dialogue_lines=[
                "Phew! Dodged that by a pixel!",
                "That attack would have done {damage_avoided} damage!",
                "Good reflexes are paying off."
            ],
            choices=[
                ConversationChoice(
                    text="Great dodge! Keep it up",
                    effect_type=CHOICE_EFFECT_ENCOURAGEMENT,
                    effect_value=None,
                    response_text="Thanks! My dodge timing is improving!"
                ),
                ConversationChoice(
                    text="Don't get cocky",
                    effect_type=CHOICE_EFFECT_STRATEGY,
                    effect_value='defensive',
                    response_text="You're right, stay focused..."
                )
            ],
            priority=4
        )
    ],

    TRIGGER_STRATEGY_QUESTION: [
        ConversationTemplate(
            trigger=TRIGGER_STRATEGY_QUESTION,
            emotion=EMOTION_QUESTIONING,
            dialogue_lines=[
                "I've been thinking about my combat approach...",
                "What style do you think suits me best?"
            ],
            choices=[
                ConversationChoice(
                    text="Be more aggressive",
                    effect_type=CHOICE_EFFECT_STRATEGY,
                    effect_value='aggressive',
                    response_text="Alright! Time to bring the fight to them!"
                ),
                ConversationChoice(
                    text="Play more defensively",
                    effect_type=CHOICE_EFFECT_STRATEGY,
                    effect_value='defensive',
                    response_text="Safety first. I'll be more careful."
                ),
                ConversationChoice(
                    text="Stay balanced",
                    effect_type=CHOICE_EFFECT_STRATEGY,
                    effect_value='balanced',
                    response_text="Balance is key. I'll adapt to each situation."
                ),
                ConversationChoice(
                    text="You're doing great, keep learning",
                    effect_type=CHOICE_EFFECT_ENCOURAGEMENT,
                    effect_value=None,
                    response_text="Thanks for the support! I'll trust my training."
                )
            ],
            priority=1
        ),
        ConversationTemplate(
            trigger=TRIGGER_STRATEGY_QUESTION,
            emotion=EMOTION_NEUTRAL,
            dialogue_lines=[
                "Quick check-in: How am I doing?",
                "Any adjustments you'd like me to make?"
            ],
            choices=[
                ConversationChoice(
                    text="More offense please",
                    effect_type=CHOICE_EFFECT_STRATEGY,
                    effect_value='aggressive',
                    response_text="Switching to offensive mode!"
                ),
                ConversationChoice(
                    text="More defense please",
                    effect_type=CHOICE_EFFECT_STRATEGY,
                    effect_value='defensive',
                    response_text="Engaging defensive protocols!"
                ),
                ConversationChoice(
                    text="You're doing fine",
                    effect_type=CHOICE_EFFECT_ENCOURAGEMENT,
                    effect_value=None,
                    response_text="Great! Continuing current strategy."
                )
            ],
            priority=0
        )
    ]
}


class Conversation:
    """Active conversation state and flow management."""

    def __init__(self, template: ConversationTemplate, context: Dict[str, Any] = None):
        self.template = template
        self.context = context or {}

        # Current state
        self.dialogue_lines = template.get_dialogue(context)
        self.current_line_index = 0
        self.current_char_index = 0

        # Typewriter effect
        self.displayed_text = ""
        self.text_complete = False

        # Choice state
        self.showing_choices = False
        self.selected_choice_index = 0
        self.choice_made = False
        self.chosen_choice: Optional[ConversationChoice] = None

        # Response after choice
        self.showing_response = False
        self.response_text = ""
        self.response_char_index = 0
        self.response_complete = False

        # Completion state
        self.finished = False

    def update(self, chars_per_frame: int = 2):
        """Update typewriter effect."""
        if self.finished:
            return

        if self.showing_response:
            # Typing out the response
            if self.response_char_index < len(self.response_text):
                self.response_char_index = min(
                    self.response_char_index + chars_per_frame,
                    len(self.response_text)
                )
                if self.response_char_index >= len(self.response_text):
                    self.response_complete = True
        elif not self.text_complete:
            # Typing out current dialogue line
            current_line = self.dialogue_lines[self.current_line_index]
            if self.current_char_index < len(current_line):
                self.current_char_index = min(
                    self.current_char_index + chars_per_frame,
                    len(current_line)
                )
                self.displayed_text = current_line[:self.current_char_index]

                if self.current_char_index >= len(current_line):
                    self.text_complete = True

    def advance(self) -> bool:
        """Advance to next line or show choices. Returns True if conversation continues."""
        if self.finished:
            return False

        if self.showing_response:
            if self.response_complete:
                self.finished = True
                return False
            else:
                # Skip to end of response
                self.response_char_index = len(self.response_text)
                self.response_complete = True
                return True

        if not self.text_complete:
            # Skip to end of current line
            current_line = self.dialogue_lines[self.current_line_index]
            self.current_char_index = len(current_line)
            self.displayed_text = current_line
            self.text_complete = True
            return True

        # Move to next line
        self.current_line_index += 1

        if self.current_line_index >= len(self.dialogue_lines):
            # All dialogue shown
            if self.template.choices and not self.choice_made:
                self.showing_choices = True
                return True
            else:
                self.finished = True
                return False

        # Reset for next line
        self.current_char_index = 0
        self.displayed_text = ""
        self.text_complete = False
        return True

    def select_choice(self, index: int) -> ConversationChoice:
        """Select a choice and return it."""
        if not self.showing_choices or index < 0 or index >= len(self.template.choices):
            return None

        self.chosen_choice = self.template.choices[index]
        self.choice_made = True
        self.showing_choices = False

        # Show response if there is one
        if self.chosen_choice.response_text:
            self.showing_response = True
            self.response_text = self.chosen_choice.response_text
            self.response_char_index = 0
            self.response_complete = False
        else:
            self.finished = True

        return self.chosen_choice

    def navigate_choice(self, delta: int):
        """Navigate choice selection."""
        if self.showing_choices and self.template.choices:
            self.selected_choice_index = (
                self.selected_choice_index + delta
            ) % len(self.template.choices)

    def get_current_text(self) -> str:
        """Get the current displayed text."""
        if self.showing_response:
            return self.response_text[:self.response_char_index]
        return self.displayed_text

    def get_emotion(self) -> str:
        """Get the current emotion for portrait."""
        return self.template.emotion

    def get_choices(self) -> List[ConversationChoice]:
        """Get available choices."""
        return self.template.choices if self.showing_choices else []


class ConversationManager:
    """Manages conversation flow and template selection."""

    def __init__(self):
        self.active_conversation: Optional[Conversation] = None
        self.conversation_queue: List[tuple] = []  # (trigger, context) pairs

    def queue_conversation(self, trigger: str, context: Dict[str, Any] = None):
        """Queue a conversation to be shown."""
        self.conversation_queue.append((trigger, context or {}))

    def start_next_conversation(self) -> bool:
        """Start the next queued conversation. Returns True if started."""
        if not self.conversation_queue:
            return False

        trigger, context = self.conversation_queue.pop(0)
        return self.start_conversation(trigger, context)

    def start_conversation(self, trigger: str, context: Dict[str, Any] = None) -> bool:
        """Start a conversation for the given trigger."""
        templates = CONVERSATION_TEMPLATES.get(trigger, [])
        if not templates:
            return False

        # Pick a random template (could be weighted by priority in future)
        template = random.choice(templates)
        self.active_conversation = Conversation(template, context)
        return True

    def update(self, chars_per_frame: int = 2):
        """Update the active conversation."""
        if self.active_conversation:
            self.active_conversation.update(chars_per_frame)

    def advance(self) -> bool:
        """Advance the conversation. Returns True if still active."""
        if self.active_conversation:
            result = self.active_conversation.advance()
            if not result and self.active_conversation.finished:
                self.active_conversation = None
            return result
        return False

    def select_choice(self, index: int) -> Optional[ConversationChoice]:
        """Select a choice in the active conversation."""
        if self.active_conversation:
            return self.active_conversation.select_choice(index)
        return None

    def navigate_choice(self, delta: int):
        """Navigate choices in the active conversation."""
        if self.active_conversation:
            self.active_conversation.navigate_choice(delta)

    def is_active(self) -> bool:
        """Check if there's an active conversation."""
        return self.active_conversation is not None

    def is_showing_choices(self) -> bool:
        """Check if currently showing choices."""
        return (self.active_conversation is not None and
                self.active_conversation.showing_choices)

    def get_current_text(self) -> str:
        """Get the current conversation text."""
        if self.active_conversation:
            return self.active_conversation.get_current_text()
        return ""

    def get_emotion(self) -> str:
        """Get the current emotion."""
        if self.active_conversation:
            return self.active_conversation.get_emotion()
        return EMOTION_NEUTRAL

    def get_choices(self) -> List[ConversationChoice]:
        """Get current choices."""
        if self.active_conversation:
            return self.active_conversation.get_choices()
        return []

    def get_selected_choice_index(self) -> int:
        """Get the currently selected choice index."""
        if self.active_conversation:
            return self.active_conversation.selected_choice_index
        return 0

    def has_queued_conversations(self) -> bool:
        """Check if there are queued conversations."""
        return len(self.conversation_queue) > 0

    def clear(self):
        """Clear active conversation and queue."""
        self.active_conversation = None
        self.conversation_queue.clear()

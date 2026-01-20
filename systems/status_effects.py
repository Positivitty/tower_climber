"""Status effect system for elemental damage types."""

from config import (
    ELEMENT_FIRE, ELEMENT_ICE, ELEMENT_POISON,
    BURN_DURATION, BURN_TICK_DAMAGE, BURN_TICK_INTERVAL,
    FREEZE_DURATION, FREEZE_SPEED_MULT,
    POISON_DURATION, POISON_TICK_DAMAGE, POISON_TICK_INTERVAL
)


class StatusEffect:
    """Base class for status effects."""

    def __init__(self, effect_type: str, duration: int):
        self.effect_type = effect_type
        self.duration = duration
        self.remaining = duration

    def update(self, target) -> bool:
        """Update effect. Returns True if effect expired."""
        self.remaining -= 1
        return self.remaining <= 0

    def on_apply(self, target):
        """Called when effect is first applied."""
        pass

    def on_remove(self, target):
        """Called when effect expires or is removed."""
        pass


class BurnEffect(StatusEffect):
    """Fire damage over time."""

    def __init__(self, duration: int = BURN_DURATION):
        super().__init__(ELEMENT_FIRE, duration)
        self.tick_counter = 0

    def update(self, target) -> bool:
        self.tick_counter += 1
        if self.tick_counter >= BURN_TICK_INTERVAL:
            self.tick_counter = 0
            # Direct HP reduction (bypasses defense)
            target.hp -= BURN_TICK_DAMAGE
            target.hp = max(0, target.hp)
        return super().update(target)


class FreezeEffect(StatusEffect):
    """Slow movement speed."""

    def __init__(self, duration: int = FREEZE_DURATION):
        super().__init__(ELEMENT_ICE, duration)
        self.original_speed = None

    def on_apply(self, target):
        self.original_speed = target.speed
        target.speed *= FREEZE_SPEED_MULT

    def on_remove(self, target):
        if self.original_speed is not None:
            target.speed = self.original_speed


class PoisonEffect(StatusEffect):
    """Poison damage over time (longer duration, lower damage)."""

    def __init__(self, duration: int = POISON_DURATION):
        super().__init__(ELEMENT_POISON, duration)
        self.tick_counter = 0

    def update(self, target) -> bool:
        self.tick_counter += 1
        if self.tick_counter >= POISON_TICK_INTERVAL:
            self.tick_counter = 0
            # Direct HP reduction (bypasses defense)
            target.hp -= POISON_TICK_DAMAGE
            target.hp = max(0, target.hp)
        return super().update(target)


class StatusEffectManager:
    """Manages status effects on a target."""

    def __init__(self):
        self.effects = []

    def add_effect(self, effect: StatusEffect, target):
        """Add a status effect. Refreshes duration if already exists."""
        # Check for existing effect of same type
        for existing in self.effects:
            if existing.effect_type == effect.effect_type:
                # Refresh duration instead of stacking
                existing.remaining = effect.duration
                return

        # New effect
        effect.on_apply(target)
        self.effects.append(effect)

    def update(self, target):
        """Update all effects. Removes expired ones."""
        expired = []
        for effect in self.effects:
            if effect.update(target):
                expired.append(effect)

        for effect in expired:
            effect.on_remove(target)
            self.effects.remove(effect)

    def has_effect(self, effect_type: str) -> bool:
        """Check if target has a specific effect type."""
        return any(e.effect_type == effect_type for e in self.effects)

    def get_effect(self, effect_type: str) -> StatusEffect:
        """Get effect by type, or None."""
        for effect in self.effects:
            if effect.effect_type == effect_type:
                return effect
        return None

    def clear(self):
        """Remove all effects without calling on_remove."""
        self.effects = []

    def clear_with_removal(self, target):
        """Remove all effects, calling on_remove for each."""
        for effect in self.effects:
            effect.on_remove(target)
        self.effects = []


def create_effect(element: str) -> StatusEffect:
    """Factory function to create status effect from element type."""
    if element == ELEMENT_FIRE:
        return BurnEffect()
    elif element == ELEMENT_ICE:
        return FreezeEffect()
    elif element == ELEMENT_POISON:
        return PoisonEffect()
    return None

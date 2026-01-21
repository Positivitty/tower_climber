"""State discretization and encoding for Q-learning."""

from config import HP_THRESHOLDS, ATTACK_RANGE, MAX_STAMINA, GROUND_Y


class StateEncoder:
    """Encodes game state into discrete tuples for Q-table lookup.

    State space:
    - HP Bucket: (high, medium, low, critical) - 4 values
    - Stamina Bucket: (high, low) - 2 values
    - Nearest Enemy Type: (melee, ranged, none) - 3 values
    - Threat Level: (low, medium, high) - 3 values
    - In Attack Range: (yes, no) - 2 values
    - Height Advantage: (above, same, below) - 3 values
    - Near Hazard: (yes, no) - 2 values

    Total: 4 x 2 x 3 x 3 x 2 x 3 x 2 = 864 states
    """

    HP_HIGH = 0
    HP_MEDIUM = 1
    HP_LOW = 2
    HP_CRITICAL = 3

    STAMINA_HIGH = 0
    STAMINA_LOW = 1

    ENEMY_MELEE = 0
    ENEMY_RANGED = 1
    ENEMY_NONE = 2

    THREAT_LOW = 0
    THREAT_MEDIUM = 1
    THREAT_HIGH = 2

    IN_RANGE_NO = 0
    IN_RANGE_YES = 1

    HEIGHT_ABOVE = 0
    HEIGHT_SAME = 1
    HEIGHT_BELOW = 2

    NEAR_HAZARD_NO = 0
    NEAR_HAZARD_YES = 1

    def __init__(self):
        self.recent_damage = 0  # Damage taken in recent ticks
        self.damage_decay = 0.8  # Decay factor per decision tick

    def get_hp_bucket(self, hp: int, max_hp: int) -> int:
        """Discretize HP into buckets."""
        ratio = hp / max_hp if max_hp > 0 else 0

        if ratio <= HP_THRESHOLDS['critical']:
            return self.HP_CRITICAL
        elif ratio <= HP_THRESHOLDS['low']:
            return self.HP_LOW
        elif ratio <= HP_THRESHOLDS['medium']:
            return self.HP_MEDIUM
        else:
            return self.HP_HIGH

    def get_stamina_bucket(self, stamina: float) -> int:
        """Discretize stamina into buckets."""
        # High if can dodge (>= 25 stamina), low otherwise
        return self.STAMINA_HIGH if stamina >= 25 else self.STAMINA_LOW

    def get_height_advantage(self, agent, nearest_enemy) -> int:
        """Determine height advantage relative to nearest enemy."""
        if nearest_enemy is None:
            return self.HEIGHT_SAME

        height_diff = nearest_enemy.y - agent.y  # Positive if agent is higher
        if height_diff > 30:
            return self.HEIGHT_ABOVE
        elif height_diff < -30:
            return self.HEIGHT_BELOW
        return self.HEIGHT_SAME

    def is_near_hazard(self, agent, terrain_manager) -> int:
        """Check if agent is near a hazard."""
        if terrain_manager is None:
            return self.NEAR_HAZARD_NO

        if terrain_manager.is_near_hazard(agent, distance=60):
            return self.NEAR_HAZARD_YES

        return self.NEAR_HAZARD_NO

    def get_nearest_enemy_type(self, agent, enemies: list) -> tuple:
        """Find the nearest enemy and return its type and reference.

        Returns:
            tuple: (enemy_type_code, nearest_enemy or None)
        """
        if not enemies:
            return self.ENEMY_NONE, None

        alive_enemies = [e for e in enemies if e.hp > 0]
        if not alive_enemies:
            return self.ENEMY_NONE, None

        nearest = min(alive_enemies, key=lambda e: agent.distance_to(e))
        enemy_type = self.ENEMY_MELEE if nearest.enemy_type == 'melee' else self.ENEMY_RANGED

        return enemy_type, nearest

    def get_threat_level(self, agent, enemies: list) -> int:
        """Calculate threat level based on enemy proximity and count."""
        alive_enemies = [e for e in enemies if e.hp > 0]

        if not alive_enemies:
            return self.THREAT_LOW

        # Count close enemies (within 150 pixels)
        close_enemies = sum(1 for e in alive_enemies if agent.distance_to(e) < 150)

        # Factor in recent damage
        threat_score = close_enemies + (self.recent_damage / 20)

        if threat_score >= 2:
            return self.THREAT_HIGH
        elif threat_score >= 1:
            return self.THREAT_MEDIUM
        else:
            return self.THREAT_LOW

    def is_in_attack_range(self, agent, nearest_enemy) -> int:
        """Check if nearest enemy is within attack range."""
        if nearest_enemy is None:
            return self.IN_RANGE_NO

        distance = agent.distance_to(nearest_enemy)
        return self.IN_RANGE_YES if distance <= ATTACK_RANGE else self.IN_RANGE_NO

    def encode_state(self, agent, enemies: list, terrain_manager=None) -> tuple:
        """Encode the current game state into a discrete tuple.

        Returns:
            tuple: (hp_bucket, stamina_bucket, enemy_type, threat_level,
                   in_range, height_advantage, near_hazard)
        """
        hp_bucket = self.get_hp_bucket(agent.hp, agent.max_hp)
        stamina_bucket = self.get_stamina_bucket(getattr(agent, 'stamina', MAX_STAMINA))
        enemy_type, nearest_enemy = self.get_nearest_enemy_type(agent, enemies)
        threat_level = self.get_threat_level(agent, enemies)
        in_range = self.is_in_attack_range(agent, nearest_enemy)
        height_adv = self.get_height_advantage(agent, nearest_enemy)
        near_hazard = self.is_near_hazard(agent, terrain_manager)

        return (hp_bucket, stamina_bucket, enemy_type, threat_level,
                in_range, height_adv, near_hazard)

    def record_damage(self, damage: int):
        """Record damage taken for threat calculation."""
        self.recent_damage += damage

    def decay_damage(self):
        """Decay recorded damage (call each decision tick)."""
        self.recent_damage *= self.damage_decay

    def reset(self):
        """Reset state encoder for new floor."""
        self.recent_damage = 0

    @staticmethod
    def get_state_description(state: tuple) -> str:
        """Get human-readable description of a state."""
        hp_names = ['High', 'Medium', 'Low', 'Critical']
        stamina_names = ['Full', 'Low']
        enemy_names = ['Melee', 'Ranged', 'None']
        threat_names = ['Low', 'Medium', 'High']
        range_names = ['No', 'Yes']
        height_names = ['Above', 'Same', 'Below']
        hazard_names = ['Safe', 'Hazard']

        # Handle both old 4-tuple and new 7-tuple formats
        if len(state) == 4:
            hp_bucket, enemy_type, threat_level, in_range = state
            return (f"HP: {hp_names[hp_bucket]} | "
                    f"Enemy: {enemy_names[enemy_type]} | "
                    f"Threat: {threat_names[threat_level]} | "
                    f"In Range: {range_names[in_range]}")
        else:
            (hp_bucket, stamina_bucket, enemy_type, threat_level,
             in_range, height_adv, near_hazard) = state

            return (f"HP:{hp_names[hp_bucket]} | "
                    f"Stam:{stamina_names[stamina_bucket]} | "
                    f"Enemy:{enemy_names[enemy_type]} | "
                    f"Threat:{threat_names[threat_level]} | "
                    f"Range:{range_names[in_range]} | "
                    f"Height:{height_names[height_adv]} | "
                    f"{hazard_names[near_hazard]}")

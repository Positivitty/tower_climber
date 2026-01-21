"""Combat resolution system."""

from config import (
    ATTACK_RANGE, KNOCKBACK_FORCE,
    REWARD_DAMAGE_DEALT, REWARD_ENEMY_DEFEATED, REWARD_FLOOR_CLEARED,
    REWARD_DAMAGE_TAKEN, REWARD_DEATH, REWARD_HIGH_GROUND_KILL,
    REWARD_SUCCESSFUL_PARRY, REWARD_PARRY_COUNTER,
    BODY_PART_HEAD, BODY_PART_BODY, BODY_PART_LEGS,
    HEAD_DAMAGE_MULT, BODY_DAMAGE_MULT, LEGS_DAMAGE_MULT,
    WOUND_THRESHOLD,
    HIGH_GROUND_DAMAGE_BONUS, LOW_GROUND_DAMAGE_PENALTY,
    PARRY_COUNTER_DAMAGE_MULT
)
from entities.projectile import Projectile
from systems.status_effects import create_effect


# Map attack height to body part
ATTACK_HEIGHT_TO_BODY_PART = {
    'high': BODY_PART_HEAD,
    'mid': BODY_PART_BODY,
    'low': BODY_PART_LEGS
}

# Damage multipliers for each body part
BODY_PART_DAMAGE_MULT = {
    BODY_PART_HEAD: HEAD_DAMAGE_MULT,
    BODY_PART_BODY: BODY_DAMAGE_MULT,
    BODY_PART_LEGS: LEGS_DAMAGE_MULT
}


class CombatSystem:
    """Handles combat resolution, damage calculation, and rewards."""

    def __init__(self, particle_system=None):
        self.projectiles = []  # Enemy projectiles
        self.agent_projectiles = []  # Agent projectiles (for bows)
        self.particle_system = particle_system  # For blood effects
        self.pending_rewards = 0.0
        self.enemies_defeated_this_tick = 0
        self.damage_dealt_this_tick = 0
        self.damage_taken_this_tick = 0
        self.last_hit_body_part = None  # Track last hit for effects
        self.parry_success_this_tick = False
        self.counter_attack_this_tick = False

    def _calculate_height_modifier(self, attacker, defender) -> float:
        """Calculate damage modifier based on relative heights."""
        height_diff = defender.y - attacker.y  # Positive if attacker is higher

        if height_diff > 30:  # Attacker has high ground
            return 1.0 + HIGH_GROUND_DAMAGE_BONUS
        elif height_diff < -30:  # Attacker has low ground
            return 1.0 - LOW_GROUND_DAMAGE_PENALTY
        return 1.0

    def reset_tick_tracking(self):
        """Reset per-tick tracking variables."""
        self.pending_rewards = 0.0
        self.enemies_defeated_this_tick = 0
        self.damage_dealt_this_tick = 0
        self.damage_taken_this_tick = 0
        self.parry_success_this_tick = False
        self.counter_attack_this_tick = False

    def spawn_projectile(self, enemy):
        """Spawn a projectile from a ranged enemy."""
        # Spawn projectile at enemy position, moving toward agent
        projectile = Projectile(
            x=enemy.x + enemy.facing * 20,
            y=enemy.y - 40,  # At torso height
            direction=enemy.facing,
            damage=enemy.damage,
            element=enemy.element
        )
        self.projectiles.append(projectile)

    def spawn_agent_projectile(self, agent):
        """Spawn a projectile from the agent (for bows)."""
        projectile = Projectile(
            x=agent.x + agent.facing * 20,
            y=agent.y - 40,
            direction=agent.facing,
            damage=agent.get_damage()
        )
        self.agent_projectiles.append(projectile)

    def update_projectiles(self, agent):
        """Update all projectiles and check for collisions with agent."""
        import random

        for projectile in self.projectiles:
            if not projectile.active:
                continue

            projectile.update()

            # Check collision with agent
            if projectile.collides_with(agent):
                # Projectiles hit random body part
                body_part = random.choice([BODY_PART_HEAD, BODY_PART_BODY, BODY_PART_LEGS])
                damage_mult = BODY_PART_DAMAGE_MULT.get(body_part, 1.0)

                damage = int(projectile.damage * damage_mult)
                actual_damage = agent.take_damage(damage)

                if actual_damage > 0:
                    # Apply knockback to agent
                    agent.apply_knockback(-projectile.direction, KNOCKBACK_FORCE * 0.5)

                    # Spawn blood particles
                    if self.particle_system:
                        blood_y = agent.y - 40
                        if body_part == BODY_PART_HEAD:
                            blood_y = agent.y - 60
                        elif body_part == BODY_PART_LEGS:
                            blood_y = agent.y - 15
                        self.particle_system.spawn_blood(agent.x, blood_y, -projectile.direction, amount=5)

                    # Check for wound
                    if actual_damage >= agent.max_hp * WOUND_THRESHOLD:
                        agent.apply_wound(body_part)

                    self.damage_taken_this_tick += actual_damage
                    self.pending_rewards += REWARD_DAMAGE_TAKEN

                    # Apply elemental status effect if projectile has an element
                    if projectile.element:
                        effect = create_effect(projectile.element)
                        if effect:
                            agent.status_effects.add_effect(effect, agent)

                    # Note: Thorns doesn't reflect projectile damage (only melee)

                projectile.active = False

        # Remove inactive projectiles
        self.projectiles = [p for p in self.projectiles if p.active]

    def update_agent_projectiles(self, enemies: list, agent=None):
        """Update agent projectiles and check for collisions with enemies."""
        import random

        for projectile in self.agent_projectiles:
            if not projectile.active:
                continue

            projectile.update()

            # Check collision with each enemy
            for enemy in enemies:
                if not enemy.is_alive():
                    continue
                if projectile.collides_with(enemy):
                    # Projectile hits body part based on agent's attack height
                    attack_height = agent.attack_height if agent else 'mid'
                    body_part = ATTACK_HEIGHT_TO_BODY_PART.get(attack_height, BODY_PART_BODY)
                    damage_mult = BODY_PART_DAMAGE_MULT.get(body_part, 1.0)

                    damage = int(projectile.damage * damage_mult)
                    actual_damage = enemy.take_damage(damage)

                    if actual_damage > 0:
                        enemy.apply_knockback(projectile.direction, KNOCKBACK_FORCE)

                        # Spawn blood particles
                        if self.particle_system:
                            blood_y = enemy.y - 40
                            if body_part == BODY_PART_HEAD:
                                blood_y = enemy.y - 60
                            elif body_part == BODY_PART_LEGS:
                                blood_y = enemy.y - 15
                            self.particle_system.spawn_blood(enemy.x, blood_y, projectile.direction, amount=5)

                        # Check for wound
                        if actual_damage >= enemy.max_hp * WOUND_THRESHOLD:
                            enemy.apply_wound(body_part)

                        self.damage_dealt_this_tick += actual_damage
                        self.pending_rewards += REWARD_DAMAGE_DEALT

                        # Apply lifesteal from passive skill
                        if agent:
                            lifesteal_percent = agent.get_lifesteal_percent()
                            if lifesteal_percent > 0:
                                heal_amount = int(actual_damage * lifesteal_percent)
                                if heal_amount > 0:
                                    agent.heal(heal_amount)

                        if not enemy.is_alive():
                            self.enemies_defeated_this_tick += 1
                            self.pending_rewards += REWARD_ENEMY_DEFEATED

                    projectile.active = False
                    break

        # Remove inactive projectiles
        self.agent_projectiles = [p for p in self.agent_projectiles if p.active]

    def process_agent_attack(self, agent, enemies: list):
        """Process agent's attack against enemies."""
        if agent.is_stunned():
            return

        if not agent.is_attacking or agent.attack_timer != 9:
            # Only deal damage at the start of attack animation
            return

        for enemy in enemies:
            if not enemy.is_alive():
                continue

            distance = agent.distance_to(enemy)
            if distance <= ATTACK_RANGE:
                # Determine body part hit based on attack height
                body_part = ATTACK_HEIGHT_TO_BODY_PART.get(agent.attack_height, BODY_PART_BODY)
                damage_mult = BODY_PART_DAMAGE_MULT.get(body_part, 1.0)

                # Apply height modifier
                height_mod = self._calculate_height_modifier(agent, enemy)

                # Check for counter attack bonus
                counter_mod = 1.0
                if hasattr(agent, 'counter_window') and agent.counter_window > 0:
                    counter_mod = PARRY_COUNTER_DAMAGE_MULT
                    agent.counter_window = 0  # Consume counter window
                    self.counter_attack_this_tick = True
                    self.pending_rewards += REWARD_PARRY_COUNTER

                # Calculate damage with all multipliers
                base_damage = agent.get_damage()
                damage = int(base_damage * damage_mult * height_mod * counter_mod)
                actual_damage = enemy.take_damage(damage)

                if actual_damage > 0:
                    # Apply knockback to enemy
                    direction = agent.direction_to(enemy)
                    enemy.apply_knockback(direction, KNOCKBACK_FORCE)

                    # Spawn blood particles
                    if self.particle_system:
                        blood_y = enemy.y - 40  # Default torso height
                        if body_part == BODY_PART_HEAD:
                            blood_y = enemy.y - 60
                        elif body_part == BODY_PART_LEGS:
                            blood_y = enemy.y - 15
                        self.particle_system.spawn_blood(enemy.x, blood_y, direction)

                    # Check for wound (if damage exceeds threshold)
                    if actual_damage >= enemy.max_hp * WOUND_THRESHOLD:
                        enemy.apply_wound(body_part)

                    self.damage_dealt_this_tick += actual_damage
                    self.pending_rewards += REWARD_DAMAGE_DEALT
                    self.last_hit_body_part = body_part

                    # Apply lifesteal from passive skill
                    lifesteal_percent = agent.get_lifesteal_percent()
                    if lifesteal_percent > 0:
                        heal_amount = int(actual_damage * lifesteal_percent)
                        if heal_amount > 0:
                            agent.heal(heal_amount)

                    # Check if enemy defeated
                    if not enemy.is_alive():
                        self.enemies_defeated_this_tick += 1
                        self.pending_rewards += REWARD_ENEMY_DEFEATED
                        # Bonus for high ground kill
                        if height_mod > 1.0:
                            self.pending_rewards += REWARD_HIGH_GROUND_KILL

    def process_enemy_attacks(self, agent, enemies: list):
        """Process enemy melee attacks against agent."""
        import random

        for enemy in enemies:
            if not enemy.is_alive():
                continue

            if enemy.enemy_type == 'ranged':
                # Ranged enemies spawn projectiles instead
                if enemy.should_spawn_projectile():
                    self.spawn_projectile(enemy)
                continue

            # Melee enemy attack
            if not enemy.is_attacking or enemy.attack_timer != 9:
                continue

            distance = agent.distance_to(enemy)
            if distance <= ATTACK_RANGE:
                # Enemy randomly targets a body part
                body_part = random.choice([BODY_PART_HEAD, BODY_PART_BODY, BODY_PART_LEGS])
                damage_mult = BODY_PART_DAMAGE_MULT.get(body_part, 1.0)

                base_damage = enemy.get_damage()
                damage = int(base_damage * damage_mult)

                # Track if agent was parrying before damage
                was_parrying = hasattr(agent, 'is_parrying') and agent.is_parrying

                actual_damage = agent.take_damage(damage)

                # Check if parry was successful (agent parried and took reduced damage)
                if was_parrying and hasattr(agent, 'parry_success') and agent.parry_success:
                    self.parry_success_this_tick = True
                    self.pending_rewards += REWARD_SUCCESSFUL_PARRY

                if actual_damage > 0:
                    # Apply knockback to agent
                    direction = enemy.direction_to(agent)
                    agent.apply_knockback(direction, KNOCKBACK_FORCE)

                    # Spawn blood particles
                    if self.particle_system:
                        blood_y = agent.y - 40  # Default torso height
                        if body_part == BODY_PART_HEAD:
                            blood_y = agent.y - 60
                        elif body_part == BODY_PART_LEGS:
                            blood_y = agent.y - 15
                        self.particle_system.spawn_blood(agent.x, blood_y, direction)

                    # Check for wound
                    if actual_damage >= agent.max_hp * WOUND_THRESHOLD:
                        agent.apply_wound(body_part)

                    self.damage_taken_this_tick += actual_damage
                    self.pending_rewards += REWARD_DAMAGE_TAKEN

                    # Apply elemental status effect if enemy has an element
                    if enemy.element:
                        effect = create_effect(enemy.element)
                        if effect:
                            agent.status_effects.add_effect(effect, agent)

                    # Apply thorns damage reflection
                    thorns_percent = agent.get_thorns_percent()
                    if thorns_percent > 0:
                        thorns_damage = int(actual_damage * thorns_percent)
                        if thorns_damage > 0:
                            enemy.take_damage(thorns_damage)
                            # Check if enemy defeated by thorns
                            if not enemy.is_alive():
                                self.enemies_defeated_this_tick += 1
                                self.pending_rewards += REWARD_ENEMY_DEFEATED

    def check_floor_cleared(self, enemies: list) -> bool:
        """Check if all enemies are defeated."""
        return all(not e.is_alive() for e in enemies)

    def get_rewards(self, agent, enemies: list, floor_cleared: bool) -> float:
        """Calculate and return rewards for the current tick."""
        total_reward = self.pending_rewards

        if floor_cleared:
            total_reward += REWARD_FLOOR_CLEARED

        if not agent.is_alive():
            total_reward += REWARD_DEATH

        return total_reward

    def reset_for_floor(self):
        """Reset combat system for a new floor."""
        self.projectiles = []
        self.agent_projectiles = []
        self.reset_tick_tracking()

"""Combat resolution system."""

from config import (
    ATTACK_RANGE, KNOCKBACK_FORCE,
    REWARD_DAMAGE_DEALT, REWARD_ENEMY_DEFEATED, REWARD_FLOOR_CLEARED,
    REWARD_DAMAGE_TAKEN, REWARD_DEATH
)
from entities.projectile import Projectile


class CombatSystem:
    """Handles combat resolution, damage calculation, and rewards."""

    def __init__(self):
        self.projectiles = []
        self.pending_rewards = 0.0
        self.enemies_defeated_this_tick = 0
        self.damage_dealt_this_tick = 0
        self.damage_taken_this_tick = 0

    def reset_tick_tracking(self):
        """Reset per-tick tracking variables."""
        self.pending_rewards = 0.0
        self.enemies_defeated_this_tick = 0
        self.damage_dealt_this_tick = 0
        self.damage_taken_this_tick = 0

    def spawn_projectile(self, enemy):
        """Spawn a projectile from a ranged enemy."""
        # Spawn projectile at enemy position, moving toward agent
        projectile = Projectile(
            x=enemy.x + enemy.facing * 20,
            y=enemy.y - 40,  # At torso height
            direction=enemy.facing,
            damage=enemy.damage
        )
        self.projectiles.append(projectile)

    def update_projectiles(self, agent):
        """Update all projectiles and check for collisions with agent."""
        for projectile in self.projectiles:
            if not projectile.active:
                continue

            projectile.update()

            # Check collision with agent
            if projectile.collides_with(agent):
                damage = agent.take_damage(projectile.damage)
                if damage > 0:
                    # Apply knockback to agent
                    agent.apply_knockback(-projectile.direction, KNOCKBACK_FORCE * 0.5)
                    self.damage_taken_this_tick += damage
                    self.pending_rewards += REWARD_DAMAGE_TAKEN

                projectile.active = False

        # Remove inactive projectiles
        self.projectiles = [p for p in self.projectiles if p.active]

    def process_agent_attack(self, agent, enemies: list):
        """Process agent's attack against enemies."""
        if not agent.is_attacking or agent.attack_timer != 9:
            # Only deal damage at the start of attack animation
            return

        for enemy in enemies:
            if not enemy.is_alive():
                continue

            distance = agent.distance_to(enemy)
            if distance <= ATTACK_RANGE:
                # Deal damage
                damage = agent.get_damage()
                actual_damage = enemy.take_damage(damage)

                if actual_damage > 0:
                    # Apply knockback to enemy
                    direction = agent.direction_to(enemy)
                    enemy.apply_knockback(direction, KNOCKBACK_FORCE)

                    self.damage_dealt_this_tick += actual_damage
                    self.pending_rewards += REWARD_DAMAGE_DEALT

                    # Check if enemy defeated
                    if not enemy.is_alive():
                        self.enemies_defeated_this_tick += 1
                        self.pending_rewards += REWARD_ENEMY_DEFEATED

    def process_enemy_attacks(self, agent, enemies: list):
        """Process enemy melee attacks against agent."""
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
                damage = agent.take_damage(enemy.damage)
                if damage > 0:
                    # Apply knockback to agent
                    direction = enemy.direction_to(agent)
                    agent.apply_knockback(direction, KNOCKBACK_FORCE)

                    self.damage_taken_this_tick += damage
                    self.pending_rewards += REWARD_DAMAGE_TAKEN

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
        self.reset_tick_tracking()

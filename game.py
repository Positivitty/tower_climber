"""Main Game class - orchestrates all game systems."""

import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DECISION_TICK_FRAMES,
    STATE_BASE, STATE_COMBAT, STATE_POST_FLOOR,
    ACTION_ATTACK, ACTION_RUN, ATTACK_RANGE
)
from entities.agent import Agent
from entities.enemy import MeleeEnemy, RangedEnemy
from ai.q_learning import QLearningAgent
from ai.state import StateEncoder
from systems.combat import CombatSystem
from systems.training import TrainingSystem
from systems.persistence import save_game, load_game
from ui.renderer import Renderer
from ui.debug_overlay import DebugOverlay
from ui.menus import BaseMenu, PostFloorMenu


class Game:
    """Main game class that manages game state and loop."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tower Climber AI")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.state = STATE_BASE
        self.current_floor = 1
        self.decision_tick_counter = 0

        # Initialize systems
        self.renderer = Renderer(self.screen)
        self.combat_system = CombatSystem()
        self.training_system = TrainingSystem()
        self.state_encoder = StateEncoder()

        # Initialize entities
        self.agent = Agent()
        self.enemies = []

        # Initialize AI
        self.q_agent = QLearningAgent()
        self.current_state = None

        # Initialize UI
        self.debug_overlay = DebugOverlay(self.renderer)
        self.base_menu = BaseMenu(self.renderer, self.training_system)
        self.post_floor_menu = PostFloorMenu(self.renderer)

        # Load saved game if exists
        self._load_game()

    def _load_game(self):
        """Load saved game state."""
        result = load_game(self.agent, self.q_agent)
        if result:
            self.current_floor = result.get('current_floor', 1)
            # Update alpha based on loaded intelligence
            self.q_agent.update_alpha_with_intelligence(self.agent.intelligence)
            print(f"Loaded save: Floor {self.current_floor}, "
                  f"Q-table entries: {len(self.q_agent.q_table)}")

    def _save_game(self):
        """Save current game state."""
        if save_game(self.agent, self.q_agent, self.current_floor):
            print("Game saved.")

    def _spawn_enemies(self):
        """Spawn enemies for the current floor."""
        self.enemies = []

        # For MVP: 1 melee + 1 ranged enemy
        melee = MeleeEnemy(SCREEN_WIDTH * 0.7)
        ranged = RangedEnemy(SCREEN_WIDTH * 0.85)

        self.enemies = [melee, ranged]

    def _start_floor(self):
        """Initialize a new floor."""
        self.agent.reset_for_floor()
        self.combat_system.reset_for_floor()
        self.state_encoder.reset()
        self.q_agent.reset_episode()
        self._spawn_enemies()
        self.decision_tick_counter = 0
        self.state = STATE_COMBAT

    def _execute_action(self, action: int):
        """Execute the chosen action."""
        # Find nearest alive enemy
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        if not alive_enemies:
            return

        nearest = min(alive_enemies, key=lambda e: self.agent.distance_to(e))

        if action == ACTION_ATTACK:
            # Move toward and attack
            distance = self.agent.distance_to(nearest)
            if distance > ATTACK_RANGE:
                self.agent.move_toward(nearest.x)
            else:
                self.agent.vx = 0
                if self.agent.can_attack():
                    self.agent.start_attack()

        elif action == ACTION_RUN:
            # Move away from nearest enemy
            self.agent.move_away_from(nearest.x)

    def _update_combat(self):
        """Update combat state each frame."""
        # Update agent
        self.agent.update()

        # Update enemies
        for enemy in self.enemies:
            if enemy.is_alive():
                enemy.update(self.agent)

        # Process combat
        self.combat_system.process_agent_attack(self.agent, self.enemies)
        self.combat_system.process_enemy_attacks(self.agent, self.enemies)
        self.combat_system.update_projectiles(self.agent)

        # Decision tick (Q-learning update)
        self.decision_tick_counter += 1
        if self.decision_tick_counter >= DECISION_TICK_FRAMES:
            self._decision_tick()
            self.decision_tick_counter = 0

        # Check end conditions
        floor_cleared = self.combat_system.check_floor_cleared(self.enemies)
        agent_died = not self.agent.is_alive()

        if floor_cleared or agent_died:
            self._end_floor(floor_cleared)

    def _decision_tick(self):
        """Process a decision tick for the Q-learning agent."""
        # Encode current state
        new_state = self.state_encoder.encode_state(self.agent, self.enemies)

        # If we have a previous state, do learning
        if self.current_state is not None:
            floor_cleared = self.combat_system.check_floor_cleared(self.enemies)
            reward = self.combat_system.get_rewards(
                self.agent, self.enemies, floor_cleared
            )
            done = floor_cleared or not self.agent.is_alive()

            self.q_agent.learn(
                self.current_state,
                self.q_agent.last_action,
                reward,
                new_state,
                done
            )

        # Reset combat system tick tracking
        self.combat_system.reset_tick_tracking()

        # Choose and execute new action
        action = self.q_agent.choose_action(new_state)
        self._execute_action(action)

        # Record damage for threat calculation
        self.state_encoder.decay_damage()
        if self.combat_system.damage_taken_this_tick > 0:
            self.state_encoder.record_damage(self.combat_system.damage_taken_this_tick)

        self.current_state = new_state

    def _end_floor(self, floor_cleared: bool):
        """Handle floor completion."""
        # Final Q-learning update
        if self.current_state is not None:
            final_state = self.state_encoder.encode_state(self.agent, self.enemies)
            reward = self.combat_system.get_rewards(
                self.agent, self.enemies, floor_cleared
            )
            self.q_agent.learn(
                self.current_state,
                self.q_agent.last_action,
                reward,
                final_state,
                done=True
            )

        # Decay epsilon
        self.q_agent.decay_epsilon()

        # Set up post-floor menu
        self.post_floor_menu.set_result(floor_cleared, self.q_agent.cumulative_reward)
        self.state = STATE_POST_FLOOR

        # Increment floor if cleared
        if floor_cleared:
            self.current_floor += 1

        # Save game
        self._save_game()

    def _handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                # Global key handlers
                if event.key == pygame.K_d:
                    self.debug_overlay.toggle()
                elif event.key == pygame.K_ESCAPE:
                    if self.state == STATE_COMBAT:
                        # Return to base (forfeit floor)
                        self._end_floor(floor_cleared=False)
                    continue

            # State-specific input handling
            if self.state == STATE_BASE:
                result = self.base_menu.handle_input(event, self.agent)
                if result == 'climb':
                    # Update alpha based on intelligence before starting
                    self.q_agent.update_alpha_with_intelligence(self.agent.intelligence)
                    self._start_floor()

            elif self.state == STATE_POST_FLOOR:
                result = self.post_floor_menu.handle_input(event)
                if result == 'continue':
                    self._start_floor()
                elif result == 'base':
                    self.state = STATE_BASE

    def _update(self):
        """Update game state."""
        if self.state == STATE_COMBAT:
            self._update_combat()

    def _render(self):
        """Render the current frame."""
        if self.state == STATE_BASE:
            self.base_menu.draw(self.agent)

        elif self.state == STATE_COMBAT:
            self.renderer.clear()
            self.renderer.draw_ground()

            # Draw entities
            self.renderer.draw_agent(self.agent)
            for enemy in self.enemies:
                self.renderer.draw_enemy(enemy)
            self.renderer.draw_projectiles(self.combat_system.projectiles)

            # Draw UI
            self.renderer.draw_floor_info(self.current_floor)
            self.renderer.draw_agent_stats(self.agent)

            # Draw debug overlay
            self.debug_overlay.draw(
                self.current_state, self.q_agent,
                self.combat_system, self.current_floor
            )
            self.debug_overlay.draw_controls()

        elif self.state == STATE_POST_FLOOR:
            self.post_floor_menu.draw(self.current_floor - 1)

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(FPS)

        # Save on exit
        self._save_game()
        pygame.quit()

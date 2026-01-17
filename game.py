"""Main Game class - orchestrates all game systems."""

import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DECISION_TICK_FRAMES,
    STATE_BASE, STATE_COMBAT, STATE_POST_FLOOR, STATE_TRAINING,
    ACTION_ATTACK, ACTION_RUN, ACTION_START_CLIMB,
    ACTION_MINIGAME_PRESS, ACTION_MINIGAME_WAIT,
    ATTACK_RANGE, TRAINABLE_STATS, AI_THINK_DELAY_FRAMES,
    COLOR_WHITE, COLOR_YELLOW, COLOR_GREEN, GROUND_Y
)
from entities.agent import Agent
from entities.enemy import MeleeEnemy, RangedEnemy
from ai.q_learning import QLearningAgent
from ai.state import StateEncoder
from ai.dialogue import AIDialogue
from systems.combat import CombatSystem
from systems.training import TrainingSystem
from systems.persistence import save_game, load_game
from systems.minigames import create_minigame
from ui.renderer import Renderer


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
        self.ai_think_counter = 0

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
        self.ai_dialogue = AIDialogue()
        self.current_state = None

        # Mini-game state
        self.current_minigame = None
        self.minigame_stat = None
        self.minigame_state = None

        # Base state for Q-learning
        self.base_state = None

        # Load saved game if exists
        self._load_game()

        # Initial AI thoughts
        self.ai_dialogue.add_thought("Initializing... Ready to climb the tower!")
        self.ai_dialogue.think_about_base(self.agent, self.q_agent.epsilon)

    def _load_game(self):
        """Load saved game state."""
        result = load_game(self.agent, self.q_agent)
        if result:
            self.current_floor = result.get('current_floor', 1)
            self.q_agent.update_alpha_with_intelligence(self.agent.intelligence)
            self.ai_dialogue.add_thought(f"Loaded save: Floor {self.current_floor}")

    def _save_game(self):
        """Save current game state."""
        if save_game(self.agent, self.q_agent, self.current_floor):
            self.ai_dialogue.add_thought("Progress saved.")

    def _get_base_state(self) -> tuple:
        """Get discretized state for base decisions."""
        # State: (floor_bucket, lowest_stat_bucket, highest_stat_bucket, total_stats_bucket)
        floor_bucket = min(4, self.current_floor // 5)

        stats = [self.agent.strength, self.agent.intelligence,
                 self.agent.agility, self.agent.defense, self.agent.luck]
        lowest = min(stats)
        highest = max(stats)
        total = sum(stats)

        lowest_bucket = min(4, lowest // 5)
        highest_bucket = min(4, highest // 5)
        total_bucket = min(4, total // 20)

        return (floor_bucket, lowest_bucket, highest_bucket, total_bucket)

    def _spawn_enemies(self):
        """Spawn enemies for the current floor."""
        self.enemies = []

        # Scale difficulty with floor
        melee = MeleeEnemy(SCREEN_WIDTH * 0.7)
        ranged = RangedEnemy(SCREEN_WIDTH * 0.85)

        # Scale enemy HP with floor
        floor_mult = 1 + (self.current_floor - 1) * 0.1
        melee.hp = int(melee.hp * floor_mult)
        melee.max_hp = melee.hp
        ranged.hp = int(ranged.hp * floor_mult)
        ranged.max_hp = ranged.hp

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

        self.ai_dialogue.add_thought(f"Entering Floor {self.current_floor}...")
        self.ai_dialogue.add_thought(f"Enemies: {len(self.enemies)} hostiles detected!")

    def _start_training(self, stat: str):
        """Start a training mini-game."""
        difficulty = self.agent.get_stat(stat) // 5 + 1  # Harder as stat increases
        self.current_minigame = create_minigame(stat, difficulty)
        self.minigame_stat = stat
        self.minigame_state = None
        self.state = STATE_TRAINING

        self.ai_dialogue.think_about_training(stat, difficulty)

    def _execute_combat_action(self, action: int):
        """Execute the chosen combat action."""
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        if not alive_enemies:
            return

        nearest = min(alive_enemies, key=lambda e: self.agent.distance_to(e))

        if action == ACTION_ATTACK:
            distance = self.agent.distance_to(nearest)
            if distance > ATTACK_RANGE:
                self.agent.move_toward(nearest.x)
            else:
                self.agent.vx = 0
                if self.agent.can_attack():
                    self.agent.start_attack()

        elif action == ACTION_RUN:
            self.agent.move_away_from(nearest.x)

    def _update_base(self):
        """Update base state - AI decides what to do."""
        self.ai_think_counter += 1

        if self.ai_think_counter >= AI_THINK_DELAY_FRAMES:
            self.ai_think_counter = 0

            # Get base state and choose action
            self.base_state = self._get_base_state()
            action = self.q_agent.choose_action(self.base_state, context='base')

            action_name = QLearningAgent.get_action_name(action, 'base')
            self.ai_dialogue.add_thought(f"Decision: {action_name}")

            if action == ACTION_START_CLIMB:
                # Learn from base decision
                self.q_agent.learn(
                    self.base_state, action, 0,
                    self.base_state, context='base', done=True
                )
                self.q_agent.update_alpha_with_intelligence(self.agent.intelligence)
                self._start_floor()
            else:
                # Training action
                stat = QLearningAgent.action_to_stat(action)
                if stat:
                    self._start_training(stat)

    def _update_training(self):
        """Update training mini-game."""
        if self.current_minigame is None:
            self.state = STATE_BASE
            return

        # Get mini-game state
        mg_state = self.current_minigame.get_state()

        # AI decides action for mini-game
        if self.minigame_state != mg_state:
            action = self.q_agent.choose_action(mg_state, context='minigame')

            # Execute action
            reward = self.current_minigame.update(action)

            # Learn
            if self.minigame_state is not None:
                self.q_agent.learn(
                    self.minigame_state, self.q_agent.last_action, reward,
                    mg_state, context='minigame',
                    done=self.current_minigame.is_finished()
                )

            self.minigame_state = mg_state

            # Add thoughts during minigame
            if not self.current_minigame.is_finished():
                action_name = QLearningAgent.get_action_name(action, 'minigame')
                if action == ACTION_MINIGAME_PRESS:
                    self.ai_dialogue.add_thought("NOW!")
        else:
            # Still same state, just update without AI action
            self.current_minigame.update(ACTION_MINIGAME_WAIT)

        # Check if mini-game finished
        if self.current_minigame.is_finished():
            success = self.current_minigame.success
            perfect = self.current_minigame.perfect
            message = self.current_minigame.result_message

            self.ai_dialogue.think_about_result(success, perfect, message)

            # Apply training if successful
            if success:
                self.agent.train_stat(self.minigame_stat)
                self.ai_dialogue.add_thought(
                    f"{self.minigame_stat.upper()} increased to {self.agent.get_stat(self.minigame_stat)}!"
                )

            # Learn from base decision (now that we know the outcome)
            reward = self.current_minigame.get_reward()
            new_base_state = self._get_base_state()
            self.q_agent.learn(
                self.base_state,
                self.q_agent.last_action,
                reward,
                new_base_state,
                context='base',
                done=False
            )

            self.current_minigame = None
            self.minigame_stat = None
            self.state = STATE_BASE

            # Think about next decision
            self.ai_dialogue.think_about_base(self.agent, self.q_agent.epsilon)

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
        """Process a decision tick for combat."""
        new_state = self.state_encoder.encode_state(self.agent, self.enemies)

        # Learn from previous state
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
                context='combat',
                done=done
            )

        self.combat_system.reset_tick_tracking()

        # Choose and execute new action
        action = self.q_agent.choose_action(new_state, context='combat')
        self._execute_combat_action(action)

        # AI thoughts about combat
        action_name = QLearningAgent.get_action_name(action, 'combat')
        q_values = self.q_agent.get_all_q_values(new_state, 'combat')
        self.ai_dialogue.think_about_combat(new_state, action_name, q_values)

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
                context='combat',
                done=True
            )

        # Decay epsilon
        self.q_agent.decay_epsilon()

        if floor_cleared:
            self.ai_dialogue.add_thought(f"Floor {self.current_floor} CLEARED!")
            self.current_floor += 1
        else:
            self.ai_dialogue.add_thought("Defeated! Need to train more...")

        # Return to base
        self.state = STATE_BASE
        self.ai_dialogue.think_about_base(self.agent, self.q_agent.epsilon)

        # Save game
        self._save_game()

    def _handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_COMBAT:
                        self._end_floor(floor_cleared=False)
                    elif self.state == STATE_TRAINING:
                        # Cancel training
                        self.current_minigame = None
                        self.state = STATE_BASE
                        self.ai_dialogue.add_thought("Training cancelled.")

                # Speed up AI (hold space to speed up decisions)
                elif event.key == pygame.K_SPACE:
                    if self.state == STATE_BASE:
                        self.ai_think_counter = AI_THINK_DELAY_FRAMES - 1

    def _update(self):
        """Update game state."""
        if self.state == STATE_BASE:
            self._update_base()
        elif self.state == STATE_COMBAT:
            self._update_combat()
        elif self.state == STATE_TRAINING:
            self._update_training()

    def _render(self):
        """Render the current frame."""
        self.renderer.clear()

        if self.state == STATE_BASE:
            self._render_base()
        elif self.state == STATE_COMBAT:
            self._render_combat()
        elif self.state == STATE_TRAINING:
            self._render_training()

        # Always draw dialogue box
        self.renderer.draw_dialogue_box(self.ai_dialogue.get_recent_messages())

        pygame.display.flip()

    def _render_base(self):
        """Render base screen."""
        # Title
        self.renderer.draw_text(
            "BASE CAMP",
            SCREEN_WIDTH // 2, 50,
            COLOR_YELLOW, 'large', center=True
        )

        # Agent in center
        self.agent.x = SCREEN_WIDTH // 2
        self.agent.y = GROUND_Y - 100
        self.renderer.draw_ground()
        self.renderer.draw_agent(self.agent)

        # Stats display
        self.renderer.draw_agent_stats_compact(self.agent)
        self.renderer.draw_floor_info(self.current_floor)

        # Instructions
        self.renderer.draw_text(
            "AI is deciding... (SPACE to speed up)",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
            COLOR_WHITE, 'small', center=True
        )

    def _render_combat(self):
        """Render combat screen."""
        self.renderer.draw_ground()

        # Draw entities
        self.renderer.draw_agent(self.agent)
        for enemy in self.enemies:
            self.renderer.draw_enemy(enemy)
        self.renderer.draw_projectiles(self.combat_system.projectiles)

        # Draw UI
        self.renderer.draw_floor_info(self.current_floor)
        self.renderer.draw_agent_stats_compact(self.agent)

    def _render_training(self):
        """Render training mini-game."""
        # Title
        stat_name = self.minigame_stat.upper() if self.minigame_stat else "TRAINING"
        self.renderer.draw_text(
            f"TRAINING: {stat_name}",
            SCREEN_WIDTH // 2, 50,
            COLOR_YELLOW, 'large', center=True
        )

        # Draw mini-game
        if self.current_minigame and hasattr(self.current_minigame, 'get_visual_data'):
            data = self.current_minigame.get_visual_data()
            self.renderer.draw_timing_bar(
                data['progress'],
                data['target_start'],
                data['target_end'],
                data.get('success')
            )
        elif self.current_minigame:
            # Generic progress display for other mini-games
            progress = self.current_minigame.get_progress()
            self.renderer.draw_text(
                f"Progress: {int(progress * 100)}%",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                COLOR_WHITE, 'medium', center=True
            )

        # Draw stats
        self.renderer.draw_agent_stats_compact(self.agent)

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

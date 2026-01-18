"""Main Game class - orchestrates all game systems."""

import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DECISION_TICK_FRAMES,
    STATE_BASE, STATE_COMBAT, STATE_POST_FLOOR, STATE_TRAINING,
    ACTION_ATTACK, ACTION_RUN, ACTION_CHARGE, ACTION_START_CLIMB,
    ACTION_MINIGAME_PRESS, ACTION_MINIGAME_WAIT,
    ATTACK_RANGE, AI_THINK_DELAY_FRAMES, AGENT_CHARGE_SPEED,
    MINIGAME_RESULT_DISPLAY_FRAMES, MINIGAME_AI_DECISION_DELAY,
    COLOR_WHITE, COLOR_YELLOW, COLOR_GREEN, COLOR_RED, COLOR_CYAN, COLOR_DARK_GRAY, GROUND_Y
)
from entities.agent import Agent
from entities.enemy import MeleeEnemy, RangedEnemy
from ai.q_learning import QLearningAgent
from ai.state import StateEncoder
from ai.dialogue import AIDialogue
from systems.combat import CombatSystem
from systems.training import TrainingSystem
from systems.persistence import save_game, load_game, save_exists
from systems.minigames import create_minigame
from systems.character import (
    RACES, CLASSES, Equipment, generate_loot,
    apply_race_class_bonuses, get_character_color
)
from ui.renderer import Renderer


# Game states
STATE_CHAR_CREATE = 'char_create'
STATE_LOOT = 'loot'
STATE_TRAIN_SELECT = 'train_select'  # Player picks which stat to train
STATE_EQUIPMENT = 'equipment'  # Player manages equipment
STATE_AI_PRIORITY = 'ai_priority'  # Player sets AI combat priority
STATE_AI_BRAIN = 'ai_brain'  # View AI intelligence and learning


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tower Climber AI")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.state = STATE_CHAR_CREATE
        self.current_floor = 1
        self.decision_tick_counter = 0
        self.ai_think_counter = 0

        # Character creation state
        self.selected_race = 0
        self.selected_class = 0
        self.race_list = list(RACES.keys())
        self.class_list = list(CLASSES.keys())
        self.char_created = False

        # Post-floor state
        self.post_floor_selection = 0  # 0 = continue, 1 = return to base
        self.floor_cleared = False
        self.pending_loot = []

        # Initialize systems
        self.renderer = Renderer(self.screen)
        self.combat_system = CombatSystem()
        self.training_system = TrainingSystem()
        self.state_encoder = StateEncoder()

        # Initialize entities
        self.agent = Agent()
        self.agent.equipment = Equipment()
        self.enemies = []

        # Initialize AI
        self.q_agent = QLearningAgent()
        self.ai_dialogue = AIDialogue()
        self.current_state = None

        # Mini-game state
        self.current_minigame = None
        self.minigame_stat = None
        self.minigame_state = None
        self.base_state = None
        self.minigame_result_timer = 0  # Timer to display result
        self.minigame_ai_delay = 0  # Delay between AI decisions in minigames

        # Player menu state
        self.base_menu_selection = 0  # Which base option is selected
        self.train_menu_selection = 0  # Which stat is selected
        self.equipment_menu_selection = 0  # Which slot is selected
        self.equipment_submenu = False  # Are we in inventory view?
        self.inventory_selection = 0  # Which inventory item is selected

        # AI priority (player can guide the AI)
        self.ai_priority = 'balanced'  # 'aggressive', 'defensive', 'balanced'
        self.priority_selection = 1  # Menu selection (0=aggressive, 1=balanced, 2=defensive)

        # Player teaching mode
        self.player_teaching = False  # Is player controlling AI?
        self.player_action = None  # Action chosen by player

        # Check for existing save
        if save_exists():
            self._load_game()
            self.char_created = True
            self.state = STATE_BASE
            self.ai_dialogue.add_thought("Welcome back! Ready to continue climbing.")
        else:
            self.ai_dialogue.add_thought("Welcome! Create your character to begin.")

    def _load_game(self):
        result = load_game(self.agent, self.q_agent)
        if result:
            self.current_floor = result.get('current_floor', 1)
            if 'equipment' in result:
                self.agent.equipment = Equipment.from_dict(result['equipment'])
            self.q_agent.alpha = self.q_agent.base_alpha * self.agent.get_learning_modifier()

    def _save_game(self):
        # Add equipment to save
        extra_data = {'equipment': self.agent.equipment.to_dict()}
        save_game(self.agent, self.q_agent, self.current_floor, extra_data)

    def _create_character(self):
        """Finalize character creation."""
        race = self.race_list[self.selected_race]
        char_class = self.class_list[self.selected_class]

        self.agent.race = race
        self.agent.char_class = char_class
        apply_race_class_bonuses(self.agent, race, char_class)

        self.agent.color = get_character_color(race, char_class)
        self.char_created = True
        self.state = STATE_BASE

        race_name = RACES[race]['name']
        class_name = CLASSES[char_class]['name']
        self.ai_dialogue.add_thought(f"Character created: {race_name} {class_name}!")
        self.ai_dialogue.add_thought(RACES[race]['special'])
        self.ai_dialogue.add_thought(CLASSES[char_class]['special'])
        self.ai_dialogue.think_about_base(self.agent, self.q_agent.epsilon)

        self._save_game()

    def _get_base_state(self) -> tuple:
        floor_bucket = min(4, self.current_floor // 5)
        stats = [self.agent.strength, self.agent.intelligence,
                 self.agent.agility, self.agent.defense, self.agent.luck]
        lowest = min(stats)
        highest = max(stats)
        total = sum(stats)
        return (floor_bucket, min(4, lowest // 5), min(4, highest // 5), min(4, total // 20))

    def _spawn_enemies(self):
        self.enemies = []
        melee = MeleeEnemy(SCREEN_WIDTH * 0.7)
        ranged = RangedEnemy(SCREEN_WIDTH * 0.85)
        floor_mult = 1 + (self.current_floor - 1) * 0.15
        melee.hp = int(melee.hp * floor_mult)
        melee.max_hp = melee.hp
        ranged.hp = int(ranged.hp * floor_mult)
        ranged.max_hp = ranged.hp
        self.enemies = [melee, ranged]

    def _start_floor(self):
        self.agent.reset_for_floor()
        self.combat_system.reset_for_floor()
        self.state_encoder.reset()
        self.q_agent.reset_episode()
        self._spawn_enemies()
        self.decision_tick_counter = 0
        self.state = STATE_COMBAT
        self.ai_dialogue.add_thought(f"Entering Floor {self.current_floor}...")

    def _start_training(self, stat: str):
        difficulty = self.agent.get_stat(stat) // 5 + 1
        self.current_minigame = create_minigame(stat, difficulty)
        self.minigame_stat = stat
        self.minigame_state = None
        self.minigame_result_timer = 0
        self.minigame_ai_delay = 0
        self.state = STATE_TRAINING
        self.ai_dialogue.think_about_training(stat, difficulty)

    def _process_ranged_agent_attack(self):
        """Handle ranged attack (bow) - spawn projectile instead of melee."""
        if not self.agent.is_attacking or self.agent.attack_timer != 9:
            return
        # Spawn projectile
        self.combat_system.spawn_agent_projectile(self.agent)

    def _execute_combat_action(self, action: int):
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        if not alive_enemies:
            return
        nearest = min(alive_enemies, key=lambda e: self.agent.distance_to(e))

        # Ranged weapons have longer attack range
        attack_range = 200 if self.agent.has_ranged_weapon() else ATTACK_RANGE

        if action == ACTION_ATTACK:
            distance = self.agent.distance_to(nearest)
            if distance > attack_range:
                self.agent.move_toward(nearest.x)
            else:
                self.agent.vx = 0
                self.agent.facing = 1 if nearest.x > self.agent.x else -1
                if self.agent.can_attack():
                    self.agent.start_attack()
        elif action == ACTION_RUN:
            self.agent.move_away_from(nearest.x)
        elif action == ACTION_CHARGE:
            # Rush toward enemy at double speed
            distance = self.agent.distance_to(nearest)
            if distance > attack_range:
                direction = 1 if nearest.x > self.agent.x else -1
                self.agent.vx = direction * AGENT_CHARGE_SPEED
                self.agent.facing = direction
            else:
                # In range - attack
                self.agent.vx = 0
                self.agent.facing = 1 if nearest.x > self.agent.x else -1
                if self.agent.can_attack():
                    self.agent.start_attack()

    def _update_char_create(self):
        pass  # Handled by events

    def _update_base(self):
        # Base is now a player-controlled menu, no automatic AI decisions
        pass  # Handled by events

    def _update_training(self):
        if self.current_minigame is None:
            self.state = STATE_BASE
            return

        # If showing result, count down timer
        if self.minigame_result_timer > 0:
            self.minigame_result_timer -= 1
            if self.minigame_result_timer <= 0:
                # Done showing result, go back to base
                self.current_minigame = None
                self.minigame_stat = None
                self.state = STATE_BASE
                self._save_game()
                self.ai_dialogue.think_about_base(self.agent, self.q_agent.epsilon)
            return

        # Check if minigame just finished
        if self.current_minigame.is_finished():
            success = self.current_minigame.success
            message = self.current_minigame.result_message
            self.ai_dialogue.think_about_result(success, self.current_minigame.perfect, message)

            if success:
                self.agent.train_stat(self.minigame_stat)
                self.ai_dialogue.add_thought(
                    f"{self.minigame_stat.upper()} increased to {self.agent.get_stat(self.minigame_stat)}!"
                )

            reward = self.current_minigame.get_reward()
            new_base_state = self._get_base_state()
            self.q_agent.learn(self.base_state, self.q_agent.last_action, reward,
                               new_base_state, context='base', done=False)

            # Start result display timer
            self.minigame_result_timer = MINIGAME_RESULT_DISPLAY_FRAMES
            return

        # AI decision delay - don't decide every frame
        self.minigame_ai_delay -= 1
        if self.minigame_ai_delay > 0:
            # Still waiting, just update the minigame with WAIT
            self.current_minigame.update(ACTION_MINIGAME_WAIT)
            return

        # Time for AI to make a decision
        self.minigame_ai_delay = MINIGAME_AI_DECISION_DELAY

        mg_state = self.current_minigame.get_state()
        action = self.q_agent.choose_action(mg_state, context='minigame')
        reward = self.current_minigame.update(action)

        if self.minigame_state is not None:
            self.q_agent.learn(
                self.minigame_state, self.q_agent.last_action, reward,
                mg_state, context='minigame',
                done=self.current_minigame.is_finished()
            )
        self.minigame_state = mg_state

    def _update_combat(self):
        self.agent.update()
        for enemy in self.enemies:
            if enemy.is_alive():
                enemy.update(self.agent)

        # Process agent attacks - ranged or melee based on weapon
        if self.agent.has_ranged_weapon():
            self._process_ranged_agent_attack()
        else:
            self.combat_system.process_agent_attack(self.agent, self.enemies)

        self.combat_system.process_enemy_attacks(self.agent, self.enemies)
        self.combat_system.update_projectiles(self.agent)
        self.combat_system.update_agent_projectiles(self.enemies)

        self.decision_tick_counter += 1
        if self.decision_tick_counter >= DECISION_TICK_FRAMES:
            self._decision_tick()
            self.decision_tick_counter = 0

        floor_cleared = self.combat_system.check_floor_cleared(self.enemies)
        agent_died = not self.agent.is_alive()

        if floor_cleared or agent_died:
            self._end_floor(floor_cleared)

    def _decision_tick(self):
        new_state = self.state_encoder.encode_state(self.agent, self.enemies)

        if self.current_state is not None:
            floor_cleared = self.combat_system.check_floor_cleared(self.enemies)
            reward = self.combat_system.get_rewards(self.agent, self.enemies, floor_cleared)
            done = floor_cleared or not self.agent.is_alive()
            self.q_agent.learn(self.current_state, self.q_agent.last_action, reward,
                               new_state, context='combat', done=done)

        self.combat_system.reset_tick_tracking()

        # Check if player is teaching
        if self.player_teaching and self.player_action is not None:
            action = self.player_action
            self.player_action = None  # Reset after use
            self.q_agent.player_taught_actions += 1
        else:
            # Apply AI priority bias to action selection
            action = self._choose_action_with_priority(new_state)

        self.q_agent.last_action = action  # Track for learning
        self._execute_combat_action(action)

        action_name = QLearningAgent.get_action_name(action, 'combat')
        q_values = self.q_agent.get_all_q_values(new_state, 'combat')
        self.ai_dialogue.think_about_combat(new_state, action_name, q_values)

        self.state_encoder.decay_damage()
        if self.combat_system.damage_taken_this_tick > 0:
            self.state_encoder.record_damage(self.combat_system.damage_taken_this_tick)

        self.current_state = new_state

    def _choose_action_with_priority(self, state):
        """Choose action with bias based on player-set AI priority."""
        import random

        # Get Q-values for all actions
        q_values = self.q_agent.get_all_q_values(state, 'combat')

        # If exploring, return random action
        if random.random() < self.q_agent.epsilon:
            return random.choice(list(q_values.keys()))

        # Apply priority biases
        hp_ratio = self.agent.hp / self.agent.max_hp

        if self.ai_priority == 'aggressive':
            # Prefer ATTACK and CHARGE
            q_values[ACTION_ATTACK] += 5
            q_values[ACTION_CHARGE] += 8  # Extra bias for closing distance
            q_values[ACTION_RUN] -= 3
        elif self.ai_priority == 'defensive':
            # Run more when HP is low
            if hp_ratio < 0.5:
                q_values[ACTION_RUN] += 10
                q_values[ACTION_ATTACK] -= 5
            elif hp_ratio < 0.75:
                q_values[ACTION_RUN] += 3
        # 'balanced' - no bias, use pure Q-values

        # Choose action with highest (biased) Q-value
        best_action = max(q_values.keys(), key=lambda a: q_values[a])
        return best_action

    def _end_floor(self, floor_cleared: bool):
        if self.current_state is not None:
            final_state = self.state_encoder.encode_state(self.agent, self.enemies)
            reward = self.combat_system.get_rewards(self.agent, self.enemies, floor_cleared)
            self.q_agent.learn(self.current_state, self.q_agent.last_action, reward,
                               final_state, context='combat', done=True)

        # Record battle result for intelligence tracking
        self.q_agent.record_battle_result(floor_cleared, self.current_floor)

        self.q_agent.decay_epsilon()
        self.floor_cleared = floor_cleared
        self.agent.end_floor(floor_cleared)
        self.player_teaching = False  # Reset teaching mode

        if floor_cleared:
            self.ai_dialogue.add_thought(f"Floor {self.current_floor} CLEARED!")
            # Generate loot
            self.pending_loot = []
            for enemy in self.enemies:
                self.pending_loot.extend(generate_loot(self.current_floor, enemy.enemy_type))
            if self.pending_loot:
                self.ai_dialogue.add_thought(f"Found {len(self.pending_loot)} item(s)!")
            self.current_floor += 1
        else:
            self.ai_dialogue.add_thought("Defeated! Returning to base...")
            self.pending_loot = []

        self.post_floor_selection = 0
        self.state = STATE_POST_FLOOR
        self._save_game()

    def _update_post_floor(self):
        pass  # Handled by events

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if self.state == STATE_CHAR_CREATE:
                    self._handle_char_create_input(event.key)
                elif self.state == STATE_POST_FLOOR:
                    self._handle_post_floor_input(event.key)
                elif self.state == STATE_BASE:
                    self._handle_base_input(event.key)
                elif self.state == STATE_COMBAT:
                    if event.key == pygame.K_ESCAPE:
                        self._end_floor(floor_cleared=False)
                    # Player teaching controls
                    elif event.key == pygame.K_t:
                        self.player_teaching = not self.player_teaching
                        if self.player_teaching:
                            self.ai_dialogue.add_thought("Teaching mode ON - Press A/R/C to command")
                        else:
                            self.ai_dialogue.add_thought("Teaching mode OFF - AI decides")
                    elif self.player_teaching:
                        if event.key == pygame.K_a:
                            self.player_action = ACTION_ATTACK
                            self.ai_dialogue.add_thought("Player: ATTACK!")
                        elif event.key == pygame.K_r:
                            self.player_action = ACTION_RUN
                            self.ai_dialogue.add_thought("Player: RUN!")
                        elif event.key == pygame.K_c:
                            self.player_action = ACTION_CHARGE
                            self.ai_dialogue.add_thought("Player: CHARGE!")
                elif self.state == STATE_TRAINING:
                    if event.key == pygame.K_ESCAPE:
                        self.current_minigame = None
                        self.state = STATE_BASE
                elif self.state == STATE_TRAIN_SELECT:
                    self._handle_train_select_input(event.key)
                elif self.state == STATE_EQUIPMENT:
                    self._handle_equipment_input(event.key)
                elif self.state == STATE_AI_PRIORITY:
                    self._handle_priority_input(event.key)
                elif self.state == STATE_AI_BRAIN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_BASE

    def _handle_char_create_input(self, key):
        if key == pygame.K_UP:
            self.selected_race = (self.selected_race - 1) % len(self.race_list)
        elif key == pygame.K_DOWN:
            self.selected_race = (self.selected_race + 1) % len(self.race_list)
        elif key == pygame.K_LEFT:
            self.selected_class = (self.selected_class - 1) % len(self.class_list)
        elif key == pygame.K_RIGHT:
            self.selected_class = (self.selected_class + 1) % len(self.class_list)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._create_character()

    def _handle_base_input(self, key):
        # Arrow key navigation
        if key == pygame.K_UP:
            self.base_menu_selection = (self.base_menu_selection - 1) % 5
        elif key == pygame.K_DOWN:
            self.base_menu_selection = (self.base_menu_selection + 1) % 5
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            # Execute selected option
            if self.base_menu_selection == 0:
                self.state = STATE_TRAIN_SELECT
            elif self.base_menu_selection == 1:
                self.state = STATE_EQUIPMENT
                self.equipment_submenu = False
                self.equipment_menu_selection = 0
            elif self.base_menu_selection == 2:
                self.state = STATE_AI_PRIORITY
            elif self.base_menu_selection == 3:
                self.state = STATE_AI_BRAIN
            elif self.base_menu_selection == 4:
                self.q_agent.alpha = self.q_agent.base_alpha * self.agent.get_learning_modifier()
                self.agent.start_new_climb()
                self._start_floor()
        # Also support number keys for quick access
        elif key == pygame.K_1:
            self.state = STATE_TRAIN_SELECT
        elif key == pygame.K_2:
            self.state = STATE_EQUIPMENT
            self.equipment_submenu = False
            self.equipment_menu_selection = 0
        elif key == pygame.K_3:
            self.state = STATE_AI_PRIORITY
        elif key == pygame.K_4:
            self.state = STATE_AI_BRAIN
        elif key == pygame.K_5:
            self.q_agent.alpha = self.q_agent.base_alpha * self.agent.get_learning_modifier()
            self.agent.start_new_climb()
            self._start_floor()

    def _handle_train_select_input(self, key):
        stats = ['strength', 'intelligence', 'agility', 'defense', 'luck']
        if key == pygame.K_UP:
            self.train_menu_selection = (self.train_menu_selection - 1) % len(stats)
        elif key == pygame.K_DOWN:
            self.train_menu_selection = (self.train_menu_selection + 1) % len(stats)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            stat = stats[self.train_menu_selection]
            self._start_training(stat)
        elif key == pygame.K_ESCAPE:
            self.state = STATE_BASE

    def _handle_equipment_input(self, key):
        if not self.equipment_submenu:
            # Equipped items view
            slots = ['weapon', 'armor', 'accessory']
            if key == pygame.K_UP:
                self.equipment_menu_selection = (self.equipment_menu_selection - 1) % len(slots)
            elif key == pygame.K_DOWN:
                self.equipment_menu_selection = (self.equipment_menu_selection + 1) % len(slots)
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                self.equipment_submenu = True
                self.inventory_selection = 0
            elif key == pygame.K_ESCAPE:
                self.state = STATE_BASE
        else:
            # Inventory view
            inv_len = len(self.agent.equipment.inventory)
            if key == pygame.K_UP and inv_len > 0:
                self.inventory_selection = (self.inventory_selection - 1) % inv_len
            elif key == pygame.K_DOWN and inv_len > 0:
                self.inventory_selection = (self.inventory_selection + 1) % inv_len
            elif key in (pygame.K_RETURN, pygame.K_SPACE) and inv_len > 0:
                # Equip selected item
                item = self.agent.equipment.inventory[self.inventory_selection]
                self.agent.equipment.equip(item)
                self.ai_dialogue.add_thought(f"Equipped: {item.name}")
                self.inventory_selection = 0
                self._save_game()
            elif key == pygame.K_ESCAPE:
                self.equipment_submenu = False

    def _handle_priority_input(self, key):
        priorities = ['aggressive', 'balanced', 'defensive']
        if key == pygame.K_UP:
            self.priority_selection = (self.priority_selection - 1) % len(priorities)
        elif key == pygame.K_DOWN:
            self.priority_selection = (self.priority_selection + 1) % len(priorities)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.ai_priority = priorities[self.priority_selection]
            self.ai_dialogue.add_thought(f"AI strategy set to: {self.ai_priority.upper()}")
            self.state = STATE_BASE
        elif key == pygame.K_ESCAPE:
            self.state = STATE_BASE

    def _handle_post_floor_input(self, key):
        if key == pygame.K_UP or key == pygame.K_DOWN:
            self.post_floor_selection = 1 - self.post_floor_selection
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            # Handle loot first
            for item in self.pending_loot:
                self.agent.equipment.equip(item)
                self.ai_dialogue.add_thought(f"Equipped: {item.name}")
            self.pending_loot = []

            if self.post_floor_selection == 0 and self.floor_cleared:
                # Continue climbing
                self._start_floor()
            else:
                # Return to base
                self.state = STATE_BASE
                self.ai_dialogue.add_thought("Returned to base camp.")
                self.ai_dialogue.think_about_base(self.agent, self.q_agent.epsilon)

    def _update(self):
        if self.state == STATE_CHAR_CREATE:
            self._update_char_create()
        elif self.state == STATE_BASE:
            self._update_base()
        elif self.state == STATE_COMBAT:
            self._update_combat()
        elif self.state == STATE_TRAINING:
            self._update_training()
        elif self.state == STATE_POST_FLOOR:
            self._update_post_floor()
        elif self.state == STATE_TRAIN_SELECT:
            pass  # Handled by events
        elif self.state == STATE_EQUIPMENT:
            pass  # Handled by events
        elif self.state == STATE_AI_PRIORITY:
            pass  # Handled by events
        elif self.state == STATE_AI_BRAIN:
            pass  # Handled by events

    def _render(self):
        self.renderer.clear()

        if self.state == STATE_CHAR_CREATE:
            self._render_char_create()
        elif self.state == STATE_BASE:
            self._render_base()
        elif self.state == STATE_COMBAT:
            self._render_combat()
        elif self.state == STATE_TRAINING:
            self._render_training()
        elif self.state == STATE_POST_FLOOR:
            self._render_post_floor()
        elif self.state == STATE_TRAIN_SELECT:
            self._render_train_select()
        elif self.state == STATE_EQUIPMENT:
            self._render_equipment()
        elif self.state == STATE_AI_PRIORITY:
            self._render_ai_priority()
        elif self.state == STATE_AI_BRAIN:
            self._render_ai_brain()

        # Always draw dialogue box
        self.renderer.draw_dialogue_box(self.ai_dialogue.get_recent_messages())

        pygame.display.flip()

    def _render_char_create(self):
        self.renderer.draw_text("CREATE YOUR CHARACTER", SCREEN_WIDTH // 2, 40,
                                COLOR_YELLOW, 'large', center=True)

        # Race selection
        self.renderer.draw_text("RACE (UP/DOWN):", 100, 100, COLOR_WHITE, 'medium')
        y = 130
        for i, race_key in enumerate(self.race_list):
            race = RACES[race_key]
            color = COLOR_YELLOW if i == self.selected_race else COLOR_WHITE
            self.renderer.draw_text(f"{'>' if i == self.selected_race else ' '} {race['name']}", 120, y, color, 'small')
            if i == self.selected_race:
                self.renderer.draw_text(race['description'], 120, y + 18, COLOR_GREEN, 'small')
                self.renderer.draw_text(race['special'], 120, y + 36, COLOR_YELLOW, 'small')
            y += 60 if i == self.selected_race else 25

        # Class selection
        self.renderer.draw_text("CLASS (LEFT/RIGHT):", 450, 100, COLOR_WHITE, 'medium')
        y = 130
        for i, class_key in enumerate(self.class_list):
            char_class = CLASSES[class_key]
            color = COLOR_YELLOW if i == self.selected_class else COLOR_WHITE
            self.renderer.draw_text(f"{'>' if i == self.selected_class else ' '} {char_class['name']}", 470, y, color, 'small')
            if i == self.selected_class:
                self.renderer.draw_text(char_class['description'], 470, y + 18, COLOR_GREEN, 'small')
                self.renderer.draw_text(char_class['special'], 470, y + 36, COLOR_YELLOW, 'small')
            y += 60 if i == self.selected_class else 25

        self.renderer.draw_text("Press ENTER to start!", SCREEN_WIDTH // 2, 380, COLOR_GREEN, 'medium', center=True)

    def _render_base(self):
        self.renderer.draw_text("BASE CAMP", SCREEN_WIDTH // 2, 40, COLOR_YELLOW, 'large', center=True)

        race_name = RACES[self.agent.race]['name']
        class_name = CLASSES[self.agent.char_class]['name']
        self.renderer.draw_text(f"{race_name} {class_name}", SCREEN_WIDTH // 2, 75, COLOR_WHITE, 'small', center=True)

        # Draw agent in center
        self.agent.x = SCREEN_WIDTH // 2
        self.agent.y = GROUND_Y - 100
        self.renderer.draw_ground()
        self.renderer.draw_agent(self.agent)

        self.renderer.draw_agent_stats_compact(self.agent)
        self.renderer.draw_floor_info(self.current_floor)

        # Equipment display on left
        y = 120
        self.renderer.draw_text("Equipment:", 10, y, COLOR_YELLOW, 'small')
        for slot in ['weapon', 'armor', 'accessory']:
            y += 18
            item = self.agent.equipment.get_equipped_item(slot)
            if item:
                self.renderer.draw_text(f"  {slot}: {item.name}", 10, y, item.get_color(), 'small')
            else:
                self.renderer.draw_text(f"  {slot}: (empty)", 10, y, COLOR_WHITE, 'small')

        # Base menu options
        menu_y = 220
        options = ["Train Stats", "Equipment", "AI Strategy", "AI Brain", "Start Climb"]
        self.renderer.draw_text("What would you like to do?", SCREEN_WIDTH // 2, menu_y, COLOR_WHITE, 'medium', center=True)
        for i, label in enumerate(options):
            color = COLOR_YELLOW if i == self.base_menu_selection else COLOR_GREEN
            prefix = "> " if i == self.base_menu_selection else "  "
            self.renderer.draw_text(f"{prefix}{i+1}. {label}", SCREEN_WIDTH // 2, menu_y + 30 + i * 22, color, 'small', center=True)

        self.renderer.draw_text(f"AI Priority: {self.ai_priority.upper()}", SCREEN_WIDTH // 2, 370, COLOR_CYAN, 'small', center=True)

    def _render_combat(self):
        self.renderer.draw_ground()
        self.renderer.draw_agent(self.agent)
        for enemy in self.enemies:
            self.renderer.draw_enemy(enemy)
        self.renderer.draw_projectiles(self.combat_system.projectiles)
        self.renderer.draw_projectiles(self.combat_system.agent_projectiles, color=COLOR_CYAN)  # Agent arrows in cyan
        self.renderer.draw_floor_info(self.current_floor)
        self.renderer.draw_agent_stats_compact(self.agent)

        # Show teaching mode hint
        if self.player_teaching:
            self.renderer.draw_text("TEACHING MODE - A:Attack R:Run C:Charge", SCREEN_WIDTH // 2, 20, COLOR_YELLOW, 'small', center=True)
        else:
            self.renderer.draw_text("Press T to teach AI", SCREEN_WIDTH // 2, 20, COLOR_WHITE, 'small', center=True)

    def _render_training(self):
        stat_name = self.minigame_stat.upper() if self.minigame_stat else "TRAINING"
        self.renderer.draw_text(f"TRAINING: {stat_name}", SCREEN_WIDTH // 2, 40, COLOR_YELLOW, 'large', center=True)

        if self.current_minigame:
            data = self.current_minigame.get_visual_data()
            game_type = data.get('type', 'timing_bar')

            # Show result screen if finished
            if data.get('finished') and self.minigame_result_timer > 0:
                result_color = COLOR_GREEN if data.get('success') else COLOR_RED
                result_text = "SUCCESS!" if data.get('success') else "FAILED!"
                self.renderer.draw_text(result_text, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, result_color, 'large', center=True)
                self.renderer.draw_text(self.current_minigame.result_message, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, COLOR_WHITE, 'medium', center=True)
            elif game_type == 'timing_bar':
                self.renderer.draw_timing_bar(
                    data['progress'], data['target_start'], data['target_end'], data.get('success')
                )
            elif game_type == 'reaction':
                color = COLOR_GREEN if data['signal_active'] else COLOR_RED
                text = "GO!" if data['signal_active'] else "WAIT..."
                pygame.draw.circle(self.screen, color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50), 60)
                self.renderer.draw_text(text, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, COLOR_WHITE, 'large', center=True)
            elif game_type == 'block':
                # Draw attack indicator
                if data['attack_active']:
                    progress = data['attack_progress']
                    attack_x = int(SCREEN_WIDTH * 0.8 - progress * SCREEN_WIDTH * 0.5)
                    pygame.draw.circle(self.screen, COLOR_RED, (attack_x, SCREEN_HEIGHT // 2 - 50), 20)
                    # Block window indicator
                    if data['block_window_start'] <= progress <= data['block_window_end']:
                        self.renderer.draw_text("BLOCK NOW!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, COLOR_GREEN, 'medium', center=True)
                else:
                    self.renderer.draw_text("Attack incoming...", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, COLOR_YELLOW, 'medium', center=True)
            elif game_type == 'dice':
                # Draw dice
                dice_y = SCREEN_HEIGHT // 2 - 50
                for i, (die, rolling) in enumerate(zip(data['dice'], data['rolling'])):
                    dice_x = SCREEN_WIDTH // 2 - 80 + i * 80
                    color = COLOR_YELLOW if rolling else COLOR_WHITE
                    pygame.draw.rect(self.screen, color, (dice_x - 25, dice_y - 25, 50, 50), 0 if not rolling else 2)
                    self.renderer.draw_text(str(die), dice_x, dice_y, COLOR_RED if rolling else COLOR_WHITE, 'large', center=True)
                self.renderer.draw_text(f"Target: {data['target']}", SCREEN_WIDTH // 2, dice_y + 50, COLOR_YELLOW, 'medium', center=True)

        self.renderer.draw_agent_stats_compact(self.agent)

    def _render_post_floor(self):
        if self.floor_cleared:
            self.renderer.draw_text(f"FLOOR {self.current_floor - 1} CLEARED!", SCREEN_WIDTH // 2, 60, COLOR_GREEN, 'large', center=True)
        else:
            self.renderer.draw_text("DEFEATED", SCREEN_WIDTH // 2, 60, COLOR_RED, 'large', center=True)

        # Show loot
        if self.pending_loot:
            self.renderer.draw_text("Loot Found:", SCREEN_WIDTH // 2, 110, COLOR_YELLOW, 'medium', center=True)
            y = 140
            for item in self.pending_loot:
                self.renderer.draw_text(item.get_description(), SCREEN_WIDTH // 2, y, item.get_color(), 'small', center=True)
                y += 25

        # Options
        options_y = 220
        options = ["Continue Climbing", "Return to Base"]
        if not self.floor_cleared:
            options[0] = "(Cannot continue)"

        for i, opt in enumerate(options):
            color = COLOR_YELLOW if i == self.post_floor_selection else COLOR_WHITE
            if i == 0 and not self.floor_cleared:
                color = COLOR_RED
            prefix = ">" if i == self.post_floor_selection else " "
            self.renderer.draw_text(f"{prefix} {opt}", SCREEN_WIDTH // 2, options_y + i * 35, color, 'medium', center=True)

        self.renderer.draw_text("UP/DOWN to select, ENTER to confirm", SCREEN_WIDTH // 2, 320, COLOR_WHITE, 'small', center=True)

    def _render_train_select(self):
        self.renderer.draw_text("TRAIN STATS", SCREEN_WIDTH // 2, 40, COLOR_YELLOW, 'large', center=True)
        self.renderer.draw_text("Select a stat to train:", SCREEN_WIDTH // 2, 80, COLOR_WHITE, 'medium', center=True)

        stats = ['strength', 'intelligence', 'agility', 'defense', 'luck']
        stat_descriptions = {
            'strength': 'Increases damage dealt',
            'intelligence': 'Improves learning rate',
            'agility': 'Increases speed and dodge',
            'defense': 'Reduces damage taken',
            'luck': 'Improves crits and drops'
        }

        y = 130
        for i, stat in enumerate(stats):
            current_val = self.agent.get_stat(stat)
            color = COLOR_YELLOW if i == self.train_menu_selection else COLOR_WHITE
            prefix = ">" if i == self.train_menu_selection else " "
            self.renderer.draw_text(f"{prefix} {stat.upper()}: {current_val}", SCREEN_WIDTH // 2 - 80, y, color, 'medium')
            if i == self.train_menu_selection:
                self.renderer.draw_text(stat_descriptions[stat], SCREEN_WIDTH // 2, y + 22, COLOR_GREEN, 'small', center=True)
            y += 45 if i == self.train_menu_selection else 30

        self.renderer.draw_text("UP/DOWN to select, ENTER to train, ESC to go back", SCREEN_WIDTH // 2, 350, COLOR_WHITE, 'small', center=True)
        self.renderer.draw_agent_stats_compact(self.agent)

    def _render_equipment(self):
        self.renderer.draw_text("EQUIPMENT", SCREEN_WIDTH // 2, 40, COLOR_YELLOW, 'large', center=True)

        if not self.equipment_submenu:
            # Show equipped items
            self.renderer.draw_text("Equipped Items:", SCREEN_WIDTH // 2, 80, COLOR_WHITE, 'medium', center=True)
            slots = ['weapon', 'armor', 'accessory']
            y = 120
            for i, slot in enumerate(slots):
                item = self.agent.equipment.get_equipped_item(slot)
                color = COLOR_YELLOW if i == self.equipment_menu_selection else COLOR_WHITE
                prefix = ">" if i == self.equipment_menu_selection else " "
                if item:
                    self.renderer.draw_text(f"{prefix} {slot.upper()}: {item.name}", SCREEN_WIDTH // 2, y, color, 'small', center=True)
                    if i == self.equipment_menu_selection:
                        stat_str = ', '.join(f"+{v} {k[:3].upper()}" for k, v in item.stats.items())
                        self.renderer.draw_text(f"  ({item.rarity}) {stat_str}", SCREEN_WIDTH // 2, y + 18, item.get_color(), 'small', center=True)
                else:
                    self.renderer.draw_text(f"{prefix} {slot.upper()}: (empty)", SCREEN_WIDTH // 2, y, color, 'small', center=True)
                y += 50 if i == self.equipment_menu_selection and item else 30

            # Show inventory count
            inv_count = len(self.agent.equipment.inventory)
            self.renderer.draw_text(f"Inventory: {inv_count} items", SCREEN_WIDTH // 2, 280, COLOR_WHITE, 'small', center=True)
            self.renderer.draw_text("ENTER to view inventory, ESC to go back", SCREEN_WIDTH // 2, 320, COLOR_WHITE, 'small', center=True)
        else:
            # Show inventory
            self.renderer.draw_text("Inventory:", SCREEN_WIDTH // 2, 80, COLOR_WHITE, 'medium', center=True)
            if not self.agent.equipment.inventory:
                self.renderer.draw_text("(empty)", SCREEN_WIDTH // 2, 120, COLOR_WHITE, 'small', center=True)
            else:
                y = 110
                for i, item in enumerate(self.agent.equipment.inventory[:6]):  # Show max 6
                    color = COLOR_YELLOW if i == self.inventory_selection else COLOR_WHITE
                    prefix = ">" if i == self.inventory_selection else " "
                    self.renderer.draw_text(f"{prefix} {item.name}", SCREEN_WIDTH // 2, y, color, 'small', center=True)
                    if i == self.inventory_selection:
                        stat_str = ', '.join(f"+{v} {k[:3].upper()}" for k, v in item.stats.items())
                        self.renderer.draw_text(f"  ({item.rarity}) {stat_str}", SCREEN_WIDTH // 2, y + 18, item.get_color(), 'small', center=True)
                    y += 40 if i == self.inventory_selection else 25
            self.renderer.draw_text("ENTER to equip, ESC to go back", SCREEN_WIDTH // 2, 320, COLOR_WHITE, 'small', center=True)

        self.renderer.draw_agent_stats_compact(self.agent)

    def _render_ai_priority(self):
        self.renderer.draw_text("AI COMBAT STRATEGY", SCREEN_WIDTH // 2, 40, COLOR_YELLOW, 'large', center=True)
        self.renderer.draw_text("Choose how the AI should fight:", SCREEN_WIDTH // 2, 80, COLOR_WHITE, 'medium', center=True)

        priorities = [
            ('aggressive', 'AGGRESSIVE', 'Focus on attacking. Close distance quickly.'),
            ('balanced', 'BALANCED', 'Mix of attack and defense. Adapt to situation.'),
            ('defensive', 'DEFENSIVE', 'Play safe. Run when HP is low.')
        ]

        y = 140
        for i, (key, name, desc) in enumerate(priorities):
            is_current = key == self.ai_priority
            is_selected = i == self.priority_selection
            color = COLOR_YELLOW if is_selected else (COLOR_GREEN if is_current else COLOR_WHITE)
            prefix = ">" if is_selected else " "
            suffix = " (current)" if is_current else ""
            self.renderer.draw_text(f"{prefix} {name}{suffix}", SCREEN_WIDTH // 2, y, color, 'medium', center=True)
            if is_selected:
                self.renderer.draw_text(desc, SCREEN_WIDTH // 2, y + 25, COLOR_CYAN, 'small', center=True)
            y += 60 if is_selected else 35

        self.renderer.draw_text("UP/DOWN to select, ENTER to confirm, ESC to go back", SCREEN_WIDTH // 2, 320, COLOR_WHITE, 'small', center=True)

    def _render_ai_brain(self):
        self.renderer.draw_text("AI BRAIN", SCREEN_WIDTH // 2, 30, COLOR_YELLOW, 'large', center=True)

        stats = self.q_agent.get_stats_summary()

        # Draw brain meter (intelligence bar)
        intel = stats['intelligence']
        bar_width = 300
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 70

        # Background
        pygame.draw.rect(self.screen, COLOR_DARK_GRAY, (bar_x, bar_y, bar_width, 25))
        # Fill based on intelligence
        fill_width = int(bar_width * intel / 100)
        # Color gradient based on level
        if intel < 20:
            bar_color = COLOR_RED
        elif intel < 50:
            bar_color = COLOR_YELLOW
        elif intel < 80:
            bar_color = COLOR_GREEN
        else:
            bar_color = COLOR_CYAN
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, fill_width, 25))
        pygame.draw.rect(self.screen, COLOR_WHITE, (bar_x, bar_y, bar_width, 25), 2)

        # Title and description
        self.renderer.draw_text(f"{stats['title']} ({intel:.0f}%)", SCREEN_WIDTH // 2, bar_y + 12, COLOR_WHITE, 'medium', center=True)
        self.renderer.draw_text(stats['description'], SCREEN_WIDTH // 2, bar_y + 40, COLOR_CYAN, 'small', center=True)

        # Stats grid
        y = 130
        self.renderer.draw_text(f"Battles: {stats['battles']}  |  Wins: {stats['wins']}  |  Win Rate: {stats['win_rate']:.1f}%", SCREEN_WIDTH // 2, y, COLOR_WHITE, 'small', center=True)
        y += 25
        self.renderer.draw_text(f"Highest Floor: {stats['highest_floor']}  |  Knowledge: {stats['knowledge']} entries", SCREEN_WIDTH // 2, y, COLOR_WHITE, 'small', center=True)
        y += 25
        self.renderer.draw_text(f"Exploration: {stats['epsilon']*100:.1f}%  |  Player Taught: {stats['player_taught']} actions", SCREEN_WIDTH // 2, y, COLOR_WHITE, 'small', center=True)

        # Lessons learned
        y += 40
        self.renderer.draw_text("Recent Lessons:", SCREEN_WIDTH // 2, y, COLOR_YELLOW, 'medium', center=True)
        y += 25
        if stats['lessons']:
            for lesson in stats['lessons']:
                self.renderer.draw_text(lesson, SCREEN_WIDTH // 2, y, COLOR_GREEN, 'small', center=True)
                y += 20
        else:
            self.renderer.draw_text("(No lessons learned yet - keep fighting!)", SCREEN_WIDTH // 2, y, COLOR_WHITE, 'small', center=True)

        self.renderer.draw_text("Press ESC to go back", SCREEN_WIDTH // 2, 380, COLOR_WHITE, 'small', center=True)

    def run(self):
        while self.running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(FPS)

        self._save_game()
        pygame.quit()

# game/gameLoop/playing_handler.py
import pygame
import os
from ..entities import (
    cat_types, cat_costs, cat_cooldowns, enemy_types,
    YManager, CSmokeEffect, OriginalSpawnStrategy,
    AdvancedSpawnStrategy, MLSpawnStrategy, EnemySpawner
)
from ..battle_logic import update_battle
from ..ui import draw_game_ui
from ..constants import csmoke_images1, csmoke_images2
import asyncio

class PlayingHandler:
    def __init__(self, screen, clock, audio, reward_system, resource_manager):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        self.reward_system = reward_system
        self.resource_manager = resource_manager
        self.font = pygame.font.SysFont(None, 25)
        self.budget_font = pygame.font.SysFont(None, 40)

    async def run(self, levels, selected_level, selected_cats, completed_levels):
        current_level = levels[selected_level]
        camera_offset_x = current_level.background.get_width() - self.screen.get_width()

        current_level.reset_towers()
        our_tower = current_level.our_tower
        enemy_tower = current_level.enemy_tower

        # Tower smoke effects
        our_tower.csmoke_effects.extend([
            CSmokeEffect(our_tower.x + our_tower.width // 2, our_tower.y + our_tower.height // 2 - 30,
                         our_tower.x + our_tower.width // 2, our_tower.y + our_tower.height // 2 + 30,
                         csmoke_images1, csmoke_images2, 1000),
            CSmokeEffect(our_tower.x + our_tower.width // 3, our_tower.y + our_tower.height // 2 + 10,
                         our_tower.x + our_tower.width // 3, our_tower.y + our_tower.height // 2 + 20,
                         csmoke_images1, csmoke_images2, 1000),
            CSmokeEffect(our_tower.x + our_tower.width // 4, our_tower.y + our_tower.height // 2 + 40,
                         our_tower.x + our_tower.width // 5, our_tower.y + our_tower.height // 2,
                         csmoke_images1, csmoke_images2, 1000)
        ])
        enemy_tower.csmoke_effects.extend([
            CSmokeEffect(enemy_tower.x + enemy_tower.width // 2, enemy_tower.y + enemy_tower.height // 2 - 20,
                         enemy_tower.x + enemy_tower.width // 2, enemy_tower.y + enemy_tower.height // 3 + 20,
                         csmoke_images1, csmoke_images2, 1000),
            CSmokeEffect(enemy_tower.x + enemy_tower.width // 3, enemy_tower.y + enemy_tower.height // 2 + 30,
                         enemy_tower.x + enemy_tower.width // 3, enemy_tower.y + enemy_tower.height // 2,
                         csmoke_images1, csmoke_images2, 1000),
            CSmokeEffect(enemy_tower.x + enemy_tower.width // 4, enemy_tower.y + enemy_tower.height // 2 + 50,
                         enemy_tower.x + enemy_tower.width // 5, enemy_tower.y + enemy_tower.height // 2 + 60,
                         csmoke_images1, csmoke_images2, 1000)
        ])

        # Enemy spawner
        strategy_map = {
            "original": OriginalSpawnStrategy,
            "advanced": AdvancedSpawnStrategy,
            "ml": MLSpawnStrategy
        }
        strategy = strategy_map[current_level.spawn_strategy]()
        enemy_spawner = EnemySpawner(strategy)

        current_level.reset_spawn_counts()

        # Game objects
        cats = []
        enemies = []
        souls = []
        shockwave_effects = []
        current_budget = current_level.initial_budget
        last_budget_increase_time = pygame.time.get_ticks() - 333
        total_budget_limitation = 16500
        budget_rate = 33
        last_spawn_time = {cat_type: 0 for cat_type in cat_types}
        level_start_time = pygame.time.get_ticks()

        cat_y_manager = YManager(base_y=532, min_y=300, max_slots=15)
        enemy_y_manager = YManager(base_y=500, min_y=300, max_slots=15)

        cat_key_map = {pygame.K_1 + i: cat_type for i, cat_type in enumerate(selected_cats[:10])}
        button_rects = {cat_type: pygame.Rect(1100 + idx * 120, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}

        boss_music_active = False
        boss_shockwave_played = False

        self.audio.play_bgm(current_level.music_path)

        while True:
            current_time = pygame.time.get_ticks()
            bg_width = current_level.background.get_width()

            pause_rect, button_rects, camera_offset_x = draw_game_ui(
                self.screen, current_level, current_budget, enemy_tower, current_time,
                level_start_time, selected_cats, last_spawn_time, button_rects,
                self.font, cat_key_map, self.budget_font, camera_offset_x
            )

            # Boss appearance
            any_boss_present = any(getattr(enemy, 'is_boss', False) for enemy in enemies)
            if any_boss_present and not boss_shockwave_played:
                self.audio.play_boss_intro()
                boss_shockwave_played = True
                if current_level.switch_music_on_boss and not boss_music_active:
                    if current_level.boss_music_path and os.path.exists(current_level.boss_music_path):
                        self.audio.play_bgm(current_level.boss_music_path)
                        boss_music_active = True

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return ("quit",)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if pause_rect.collidepoint(pos):
                        self.audio.pause_bgm()
                        return ("paused",)
                    for cat_type, rect in button_rects.items():
                        if rect.collidepoint(pos):
                            cost = cat_costs.get(cat_type, 0)
                            cooldown = cat_cooldowns.get(cat_type, 0)
                            can_deploy = current_budget >= cost and (current_time - last_spawn_time.get(cat_type, 0) >= cooldown)
                            if can_deploy:
                                current_budget -= cost
                                our_tower_center = current_level.our_tower.x + current_level.our_tower.width / 2
                                cat_y, cat_slot = cat_y_manager.get_available_y()
                                cat = cat_types[cat_type](our_tower_center, cat_y)
                                cat.slot_index = cat_slot
                                cat.x = our_tower_center - cat.width / 2 - 90
                                cats.append(cat)
                                last_spawn_time[cat_type] = current_time
                                self.audio.play_cat_spawn()
                                self.audio.play_key_action('can_deploy')
                            else:
                                self.audio.play_key_action('cannot_deploy')
                elif event.type == pygame.KEYDOWN:
                    if event.key in cat_key_map:
                        cat_type = cat_key_map[event.key]
                        cost = cat_costs.get(cat_type, 0)
                        cooldown = cat_cooldowns.get(cat_type, 0)
                        can_deploy = current_budget >= cost and (current_time - last_spawn_time.get(cat_type, 0) >= cooldown)
                        if can_deploy:
                            current_budget -= cost
                            our_tower_center = current_level.our_tower.x + current_level.our_tower.width / 2
                            cat_y, cat_slot = cat_y_manager.get_available_y()
                            cat = cat_types[cat_type](our_tower_center, cat_y)
                            cat.slot_index = cat_slot
                            cat.x = our_tower_center - cat.width / 2 - 90
                            cats.append(cat)
                            last_spawn_time[cat_type] = current_time
                            self.audio.play_cat_spawn()
                            self.audio.play_key_action('can_deploy')
                        else:
                            self.audio.play_key_action('cannot_deploy')
                    else:
                        self.audio.play_key_action('other_button')

                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT]:
                        camera_offset_x -= 10
                    if keys[pygame.K_RIGHT]:
                        camera_offset_x += 10
                    camera_offset_x = max(0, min(camera_offset_x, bg_width - self.screen.get_width()))

            # Budget increase
            if current_time - last_budget_increase_time >= 333:
                if current_budget < total_budget_limitation:
                    current_budget = min(current_budget + budget_rate, total_budget_limitation)
                last_budget_increase_time = current_time

            # Enemy spawn
            tower_hp_percent = (enemy_tower.hp / enemy_tower.max_hp) * 100 if enemy_tower else 0
            context = {
                "tower_hp_percent": tower_hp_percent,
                "time": current_time,
                "level_start_time": level_start_time,
                "spawned_counts": current_level.spawned_counts,
                "last_spawn_times": current_level.last_spawn_times,
            }
            enemy_spawner.update(
                current_level=current_level,
                enemies=enemies,
                enemy_types=enemy_types,
                enemy_y_manager=enemy_y_manager,
                context=context
            )

            current_level.all_limited_spawned = current_level.check_all_limited_spawned()

            # Update status effects
            for cat in cats:
                cat.update_status_effects(current_time)
            for enemy in enemies:
                enemy.update_status_effects(current_time)

            # Battle update
            shockwave_effects = update_battle(
                cats, enemies, our_tower, enemy_tower, current_time, souls,
                cat_y_manager, enemy_y_manager, shockwave_effects, current_budget,
                self.audio.get_battle_sfx()
            )

            souls = [soul for soul in souls if soul.update()]

            # Drawing
            our_tower.draw(self.screen, camera_offset_x)
            if enemy_tower:
                enemy_tower.draw(self.screen, camera_offset_x)
            for soul in souls:
                soul.draw(self.screen, camera_offset_x)
            for shockwave in shockwave_effects:
                shockwave.draw(self.screen, camera_offset_x)
            for cat in cats:
                cat.draw(self.screen, camera_offset_x)
            for enemy in enemies:
                enemy.draw(self.screen, camera_offset_x)

            pygame.display.flip()

            # Defeat
            if our_tower.hp <= 0:
                self.audio.play_defeat()
                return ("end", "lose", [], 0, 0, False, False)

            # Victory
            if enemy_tower and enemy_tower.hp <= 0:
                clear_time_seconds = (current_time - level_start_time) / 1000
                is_first_completion = selected_level not in completed_levels
                earned_rewards, gold_earned, souls_earned = self.reward_system.calculate_rewards(
                    selected_level, clear_time_seconds, is_first_completion
                )
                self.resource_manager.add(gold_earned, souls_earned)
                self.audio.play_victory()
                is_last_level = selected_level == len(levels) - 1
                return ("end", "victory", earned_rewards, gold_earned, souls_earned, is_first_completion, is_last_level)

            await asyncio.sleep(0)
            self.clock.tick(60)
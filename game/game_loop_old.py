import json
import os
import asyncio
import pygame

# Load reward settings
from game.rewards import LEVEL_REWARDS

# Delay time (ms)
DELAY_TIME = 2000

# Player resources file
PLAYER_RESOURCES_FILE = "data/player_resources.json"

# --- Pygame mixer initialization ---
pygame.mixer.init()
print(f"Mixer initialized, channels: {pygame.mixer.get_num_channels()}")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.set_num_channels(16)
print(f"Set channels: {pygame.mixer.get_num_channels()}")

# --- Sound loading ---
cat_spawn_sfx = {}
if os.path.exists("audio/TBC/010.ogg"):
    cat_spawn_sfx['default'] = pygame.mixer.Sound("audio/TBC/010.ogg")
    cat_spawn_sfx['default'].set_volume(0.7)
else:
    print("Warning: 'audio/TBC/010.ogg' not found, cat spawn sound will not play.")

victory_sfx = pygame.mixer.Sound("audio/TBC/008.ogg") if os.path.exists("audio/TBC/008.ogg") else None
defeat_sfx = pygame.mixer.Sound("audio/TBC/009.ogg") if os.path.exists("audio/TBC/009.ogg") else None
if not victory_sfx:
    print("Warning: 'audio/TBC/008.ogg' not found, victory sound will not play.")
if not defeat_sfx:
    print("Warning: 'audio/TBC/009.ogg' not found, defeat sound will not play.")

key_action_sfx = {
    'cannot_deploy': pygame.mixer.Sound("audio/TBC/015.ogg") if os.path.exists("audio/TBC/015.ogg") else None,
    'can_deploy': pygame.mixer.Sound("audio/TBC/014.ogg") if os.path.exists("audio/TBC/014.ogg") else None,
    'other_button': pygame.mixer.Sound("audio/TBC/011.ogg") if os.path.exists("audio/TBC/011.ogg") else None
}
for key, sfx in key_action_sfx.items():
    if sfx:
        sfx.set_volume(0.6 if key in ['cannot_deploy', 'can_deploy'] else 0.5)
    else:
        print(f"Warning: sound for {key} not found.")

battle_sfx = {
    'hit_unit': pygame.mixer.Sound("audio/TBC/021.ogg") if os.path.exists("audio/TBC/021.ogg") else None,
    'hit_tower': pygame.mixer.Sound("audio/TBC/022.ogg") if os.path.exists("audio/TBC/022.ogg") else None,
    'unit_die': pygame.mixer.Sound("audio/TBC/023.ogg") if os.path.exists("audio/TBC/023.ogg") else None
}
for key, sfx in battle_sfx.items():
    if sfx:
        sfx.set_volume(0.6 if key in ['hit_unit', 'hit_tower'] else 0.7)
    else:
        print(f"Warning: sound for {key} not found.")

boss_intro_sfx = pygame.mixer.Sound("audio/TBC/036.ogg") if os.path.exists("audio/TBC/036.ogg") else None
if not boss_intro_sfx:
    print("Warning: 'audio/TBC/036.ogg' not found, boss shockwave sound will not play.")

# --- Main game loop ---
async def main_game_loop(screen, clock):
    FPS = 60
    font = pygame.font.SysFont(None, 25)
    end_font = pygame.font.SysFont(None, 96)
    select_font = pygame.font.SysFont(None, 60)
    budget_font = pygame.font.SysFont(None, 40)
    square_surface = pygame.Surface((1220, 480), pygame.SRCALPHA)
    square_surface.fill((150, 150, 150, 100))
    SCREEN_WIDTH = screen.get_width()
    camera_offset_x = 0
    game_state = "intro"

    from .battle_logic import update_battle
    from .ui import draw_level_selection, draw_game_ui, draw_pause_menu, draw_end_screen, draw_intro_screen, draw_ending_animation
    from .entities import cat_types, cat_costs, cat_cooldowns, levels, enemy_types, YManager, CSmokeEffect, load_cat_images, OriginalSpawnStrategy, AdvancedSpawnStrategy, MLSpawnStrategy, EnemySpawner, CannonSkill, CannonIcon
    from game.constants import csmoke_images1, csmoke_images2, cannon_images, icon_cfg

    selected_level = 0
    selected_cats = list(cat_types.keys())[:2]
    current_bgm_path = None
    boss_music_active = False
    boss_shockwave_played = False

    # Load completed levels
    completed_levels = set()
    save_file = "completed_levels.json"
    try:
        if os.path.exists(save_file):
            with open(save_file, "r") as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, list):
                    completed_levels = set(loaded_data)
                else:
                    print(f"Warning: save file '{save_file}' invalid format, initializing empty.")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Warning: error loading completed levels: {e}")

    # Load player cumulative resources (Gold & Souls)
    player_resources = {"gold": 0, "souls": 0}
    try:
        if os.path.exists(PLAYER_RESOURCES_FILE):
            with open(PLAYER_RESOURCES_FILE, "r") as f:
                loaded = json.load(f)
                player_resources["gold"] = loaded.get("gold", 0)
                player_resources["souls"] = loaded.get("souls", 0)
    except Exception as e:
        print(f"Warning: failed to load player resources: {e}")

    # Game entities and state
    cats = []
    enemies = []
    souls = []
    shockwave_effects = []
    our_tower = None
    enemy_tower = None
    cannon = None
    cannon_icon = None
    last_spawn_time = {cat_type: 0 for cat_type in cat_types}
    current_budget = 1000
    last_budget_increase_time = -333
    total_budget_limitation = 16500
    budget_rate = 33
    status = None
    level_start_time = 0
    cat_y_manager = YManager(base_y=532, min_y=300, max_slots=15)
    enemy_y_manager = YManager(base_y=500, min_y=300, max_slots=15)
    cat_key_map = {pygame.K_1 + i: cat_type for i, cat_type in enumerate(selected_cats[:10])}
    button_rects = {cat_type: pygame.Rect(1100 + idx * 120, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}
    cat_images = load_cat_images()
    intro_start_time = pygame.time.get_ticks()
    intro_duration = 35000
    fade_in_duration = 5000

    # Reward tracking variables
    clear_time_seconds = 0
    earned_rewards = []
    total_gold_earned = 0
    total_souls_earned = 0
    is_first_completion = False

    while True:
        current_time = pygame.time.get_ticks()
        screen.fill((0, 0, 0))

        if game_state == "intro":
            intro_music_path = "audio/TBC/000.ogg"
            if current_bgm_path != intro_music_path and os.path.exists(intro_music_path):
                pygame.mixer.music.load(intro_music_path)
                pygame.mixer.music.play(-1)
                current_bgm_path = intro_music_path
            elif not os.path.exists(intro_music_path):
                print(f"Warning: intro music '{intro_music_path}' not found.")
            elapsed_intro_time = current_time - intro_start_time
            current_fade_alpha = int(255 * min(1.0, elapsed_intro_time / fade_in_duration))
            y_offset = screen.get_height()
            if elapsed_intro_time >= fade_in_duration:
                text_progress_time = elapsed_intro_time - fade_in_duration
                text_scroll_duration = intro_duration - fade_in_duration
                text_scroll_progress = min(1.0, text_progress_time / text_scroll_duration)
                y_offset = screen.get_height() * (1 - text_scroll_progress * text_scroll_progress)
            skip_rect = draw_intro_screen(screen, font, y_offset, current_fade_alpha)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if skip_rect.collidepoint(event.pos):
                        game_state = "level_selection"
                        pygame.mixer.music.stop()
                        current_bgm_path = None
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                        print("Skipped intro animation.")
            if elapsed_intro_time >= intro_duration + DELAY_TIME:
                game_state = "level_selection"
                pygame.mixer.music.stop()
                current_bgm_path = None
                print("Intro animation finished.")

        elif game_state == "level_selection":
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                current_bgm_path = None
                boss_music_active = False
                boss_shockwave_played = False

            cat_rects, reset_rect, quit_rect, start_rect = draw_level_selection(screen, levels, selected_level, selected_cats, font, select_font, completed_levels, cat_images, square_surface)

            # Display current Gold and Souls on main menu
            resource_text = f"Gold: {player_resources['gold']}    Souls: {player_resources['souls']}"
            shadow_surf = select_font.render(resource_text, True, (0, 0, 0))
            resource_surf = select_font.render(resource_text, True, (255, 215, 0))  # Gold color
            screen.blit(shadow_surf, (52, 32))
            screen.blit(resource_surf, (50, 30))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for i, level in enumerate(levels):
                        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
                        if rect.collidepoint(pos):
                            if i == 0 or (i - 1) in completed_levels:
                                selected_level = i
                                print(f"Selected level: {selected_level} ({levels[selected_level].name})")
                                if key_action_sfx.get('other_button'):
                                    key_action_sfx['other_button'].play()
                            else:
                                if key_action_sfx.get('cannot_deploy'):
                                    key_action_sfx['cannot_deploy'].play()
                    for cat_type, rect in cat_rects.items():
                        if rect.collidepoint(pos):
                            if cat_type in selected_cats and len(selected_cats) > 1:
                                selected_cats.remove(cat_type)
                            elif cat_type not in selected_cats and len(selected_cats) < 10:
                                selected_cats.append(cat_type)
                            cat_key_map = {pygame.K_1 + i: cat_type for i, cat_type in enumerate(selected_cats[:10])}
                            button_rects = {cat_type: pygame.Rect(1100 + idx * 120, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}
                            print(f"Updated selected cats: {selected_cats}")
                            if key_action_sfx.get('other_button'):
                                key_action_sfx['other_button'].play()
                    if reset_rect.collidepoint(pos):
                        completed_levels.clear()
                        player_resources = {"gold": 0, "souls": 0}  # Reset resources too
                        if os.path.exists(save_file):
                            os.remove(save_file)
                        if os.path.exists(PLAYER_RESOURCES_FILE):
                            os.remove(PLAYER_RESOURCES_FILE)
                        try:
                            with open(save_file, "w") as f:
                                json.dump(list(completed_levels), f)
                            print(f"Reset '{save_file}'.")
                        except Exception as e:
                            print(f"Error resetting save: {e}")
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                    if quit_rect.collidepoint(pos):
                        print("Quit button clicked, exiting game.")
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                        return
                    if start_rect.collidepoint(pos):
                        if selected_level == 0 or (selected_level - 1) in completed_levels:
                            if selected_cats:
                                game_state = "playing"
                                current_level = levels[selected_level]
                                camera_offset_x = current_level.background.get_width() - SCREEN_WIDTH
                                current_level.reset_towers()
                                our_tower = current_level.our_tower
                                enemy_tower = current_level.enemy_tower
                                our_tower_center = current_level.background.get_width()/2 + current_level.tower_distance / 2
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
                                mode = current_level.spawn_strategy
                                if mode == "original":
                                    strategy = OriginalSpawnStrategy()
                                elif mode == "advanced":
                                    strategy = AdvancedSpawnStrategy()
                                elif mode == "ml":
                                    strategy = MLSpawnStrategy()
                                enemy_spawner = EnemySpawner(strategy)
                                cannon = CannonSkill(
                                    origin_pos=(our_tower_center-our_tower.width//4-10, 205),
                                    sweep_start_x=our_tower_center-our_tower.width//2,
                                    range=2600,
                                    ground_y=460,
                                    sweep_speed=2.5,
                                    cooldown=5000,
                                    damage=300,
                                    origin_frames=cannon_images["origin"],
                                    beam_frames=cannon_images["beam"],
                                    sweep_fx_frames=cannon_images["sweep_fx"],
                                    after_fx_frames=cannon_images["after_fx"],
                                    frame_duration1=80,# for sweep_fx
                                    frame_duration2=100# for after_fx
                                )
                                cannon_icon = CannonIcon(ui_pos=(1090, 420), icon_config=icon_cfg, ui_frame_duration=100)
                                current_level.reset_spawn_counts()
                                cats.clear()
                                souls.clear()
                                enemies.clear()
                                shockwave_effects.clear()
                                current_budget = current_level.initial_budget
                                last_budget_increase_time = current_time - 333
                                last_spawn_time = {cat_type: 0 for cat_type in cat_types}
                                status = None
                                level_start_time = current_time
                                clear_time_seconds = 0
                                earned_rewards = []
                                total_gold_earned = 0
                                total_souls_earned = 0
                                is_first_completion = selected_level not in completed_levels
                                if current_level.music_path and os.path.exists(current_level.music_path):
                                    pygame.mixer.music.load(current_level.music_path)
                                    pygame.mixer.music.play(-1)
                                    current_bgm_path = current_level.music_path
                                    boss_music_active = False
                                else:
                                    print(f"Warning: level music '{current_level.music_path}' not found.")
                                    pygame.mixer.music.stop()
                                    current_bgm_path = None
                                boss_shockwave_played = False
                                if key_action_sfx.get('other_button'):
                                    key_action_sfx['other_button'].play()
                                print(f"Starting level: {current_level.name}")
                            else:
                                print("Cannot start: no cats selected!")
                                if key_action_sfx.get('cannot_deploy'):
                                    key_action_sfx['cannot_deploy'].play()
                        else:
                            if key_action_sfx.get('cannot_deploy'):
                                key_action_sfx['cannot_deploy'].play()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Duplicate logic for Enter key (same as mouse start button)
                        if selected_level == 0 or (selected_level - 1) in completed_levels:
                            if selected_cats:
                                game_state = "playing"
                                current_level = levels[selected_level]
                                camera_offset_x = current_level.background.get_width() - SCREEN_WIDTH
                                current_level.reset_towers()
                                our_tower = current_level.our_tower
                                enemy_tower = current_level.enemy_tower
                                our_tower_center = current_level.background.get_width()/2 + current_level.tower_distance / 2
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
                                mode = current_level.spawn_strategy
                                if mode == "original":
                                    strategy = OriginalSpawnStrategy()
                                elif mode == "advanced":
                                    strategy = AdvancedSpawnStrategy()
                                elif mode == "ml":
                                    strategy = MLSpawnStrategy()
                                enemy_spawner = EnemySpawner(strategy)
                                cannon = CannonSkill(
                                    origin_pos=(our_tower_center-our_tower.width//4-10, 205),
                                    sweep_start_x=our_tower_center-our_tower.width//2,
                                    range=2600,
                                    ground_y=460,
                                    sweep_speed=2.5,
                                    cooldown=5000,
                                    damage=300,
                                    origin_frames=cannon_images["origin"],
                                    beam_frames=cannon_images["beam"],
                                    sweep_fx_frames=cannon_images["sweep_fx"],
                                    after_fx_frames=cannon_images["after_fx"],
                                    frame_duration1=80,# for sweep_fx
                                    frame_duration2=100,# for after_fx
                                )
                                cannon_icon = CannonIcon(ui_pos=(1090, 420), icon_config=icon_cfg, ui_frame_duration=100)
                                current_level.reset_spawn_counts()
                                cats.clear()
                                souls.clear()
                                enemies.clear()
                                shockwave_effects.clear()
                                current_budget = current_level.initial_budget
                                last_budget_increase_time = current_time - 333
                                last_spawn_time = {cat_type: 0 for cat_type in cat_types}
                                status = None
                                level_start_time = current_time
                                clear_time_seconds = 0
                                earned_rewards = []
                                total_gold_earned = 0
                                total_souls_earned = 0
                                is_first_completion = selected_level not in completed_levels
                                if current_level.music_path and os.path.exists(current_level.music_path):
                                    pygame.mixer.music.load(current_level.music_path)
                                    pygame.mixer.music.play(-1)
                                    current_bgm_path = current_level.music_path
                                    boss_music_active = False
                                else:
                                    print(f"Warning: level music '{current_level.music_path}' not found.")
                                    pygame.mixer.music.stop()
                                    current_bgm_path = None
                                boss_shockwave_played = False
                                if key_action_sfx.get('other_button'):
                                    key_action_sfx['other_button'].play()
                                print(f"Starting level: {current_level.name}")
                            else:
                                print("Cannot start: no cats selected!")
                                if key_action_sfx.get('cannot_deploy'):
                                    key_action_sfx['cannot_deploy'].play()

        elif game_state == "playing":
            current_level = levels[selected_level]
            bg_width = current_level.background.get_width()
            pause_rect, button_rects, camera_offset_x = draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time, selected_cats, last_spawn_time, button_rects, font, cat_key_map, budget_font, camera_offset_x)

            # Boss appearance logic
            any_boss_present = any(enemy.is_boss for enemy in enemies)
            if any_boss_present and not boss_shockwave_played:
                if boss_intro_sfx:
                    boss_intro_sfx.play()
                boss_shockwave_played = True
                print("Boss appeared, playing shockwave sound.")
                if current_level.switch_music_on_boss and not boss_music_active:
                    if current_level.boss_music_path and os.path.exists(current_level.boss_music_path):
                        pygame.mixer.music.load(current_level.boss_music_path)
                        pygame.mixer.music.play(-1)
                        current_bgm_path = current_level.boss_music_path
                        boss_music_active = True
                        print("Switched to boss music.")
                    else:
                        print(f"Warning: boss music '{current_level.boss_music_path}' not found.")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if cannon_icon.is_clicked(pos):
                        if cannon.state == "ready":
                            cannon.activate(current_time)
                            #sfx_laser.play()
                        #else:
                            #sfx_fail.play()
                    if pause_rect.collidepoint(pos):
                        game_state = "paused"
                        pygame.mixer.music.pause()
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
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
                                start_x = our_tower_center - cat.width / 2 - 90
                                cat.x = start_x
                                cats.append(cat)
                                last_spawn_time[cat_type] = current_time
                                if cat_spawn_sfx.get('default'):
                                    cat_spawn_sfx['default'].play()
                                if key_action_sfx.get('can_deploy'):
                                    key_action_sfx['can_deploy'].play()
                                print(f"Spawned {cat_type} at ({cat.x}, {cat.y}) via mouse")
                            else:
                                if key_action_sfx.get('cannot_deploy'):
                                    key_action_sfx['cannot_deploy'].play()
                                print(f"Cannot spawn '{cat_type}': {'Insufficient gold' if current_budget < cost else 'On cooldown'}")
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
                            start_x = our_tower_center - cat.width / 2 - 90
                            cat.x = start_x
                            cats.append(cat)
                            last_spawn_time[cat_type] = current_time
                            if cat_spawn_sfx.get('default'):
                                cat_spawn_sfx['default'].play()
                            if key_action_sfx.get('can_deploy'):
                                key_action_sfx['can_deploy'].play()
                            print(f"Spawned {cat_type} at ({cat.x}, {cat.y})")
                        else:
                            if key_action_sfx.get('cannot_deploy'):
                                key_action_sfx['cannot_deploy'].play()
                            print(f"Cannot spawn '{cat_type}': {'Insufficient gold' if current_budget < cost else 'On cooldown'}")
                    else:
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
            #處理畫面左右滑動
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                camera_offset_x -= 10
            if keys[pygame.K_RIGHT]:
                camera_offset_x += 10
            camera_offset_x = max(0, min(camera_offset_x, bg_width - SCREEN_WIDTH))

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

            for cat in cats:
                cat.update_status_effects(current_time)
            for enemy in enemies:
                enemy.update_status_effects(current_time)

            shockwave_effects = update_battle(cats, enemies, our_tower, enemy_tower, current_time, souls, cat_y_manager, enemy_y_manager, cannon, shockwave_effects, current_budget, battle_sfx)
            souls = [soul for soul in souls if soul.update()]

            our_tower.draw(screen, camera_offset_x)
            if enemy_tower:
                enemy_tower.draw(screen, camera_offset_x)
            for soul in souls:
                soul.draw(screen, camera_offset_x)
            for shockwave in shockwave_effects:
                shockwave.draw(screen, camera_offset_x)
            for cat in cats:
                cat.draw(screen, camera_offset_x)
            for enemy in enemies:
                enemy.draw(screen, camera_offset_x)
            # 1. 繪製世界物件 (會隨 camera_offset_x 移動)
            cannon.draw(screen, camera_offset_x)
            
            # 2. 繪製 UI 物件 (固定在螢幕上，不隨相機移動)
            # 計算進度比例：只有在冷卻時才有 0~1 的進度
            if cannon.state == "cooldown":
                progress = min(1.0, (current_time - cannon.cooldown_start) / cannon.cooldown)
            elif cannon.state == "ready":
                progress = 1.0
            else:
                progress = 0.0 # 掃射中或後效中，顯示為 0 進度（灰階）

            cannon_icon.draw(screen, cannon.state, progress, current_time)#cannon_icon.draw(screen, cannon.state, progress, cannon.anim_index)
            pygame.display.flip()

            # Victory / Defeat check
            if our_tower.hp <= 0:
                if status != "lose":
                    status = "lose"
                    game_state = "end"
                    pygame.mixer.music.stop()
                    current_bgm_path = None
                    boss_music_active = False
                    boss_shockwave_played = False
                    if defeat_sfx:
                        defeat_sfx.play()
                    print("Our tower destroyed, game over.")

            elif enemy_tower and enemy_tower.hp <= 0:
                if status != "victory":
                    status = "victory"
                    game_state = "end"
                    pygame.mixer.music.stop()
                    current_bgm_path = None
                    boss_music_active = False
                    boss_shockwave_played = False

                    # Calculate rewards
                    clear_time_seconds = (current_time - level_start_time) / 1000
                    reward_data = LEVEL_REWARDS.get(selected_level, {})

                    earned_rewards = []
                    total_gold_earned = 0
                    total_souls_earned = 0

                    base_gold = reward_data.get("base_gold", 100)
                    base_souls = reward_data.get("base_souls", 10)
                    total_gold_earned += base_gold
                    total_souls_earned += base_souls
                    earned_rewards.append(f"Stage Clear: {base_gold} Gold + {base_souls} Souls")

                    speed_bonus = reward_data.get("speed_bonus", {})
                    if speed_bonus and clear_time_seconds <= speed_bonus["threshold"]:
                        total_gold_earned += speed_bonus["gold"]
                        total_souls_earned += speed_bonus["souls"]
                        earned_rewards.append(f"★ Speed Clear Bonus: +{speed_bonus['gold']} Gold + {speed_bonus['souls']} Souls")

                    if is_first_completion:
                        first = reward_data.get("first_clear", {})
                        extra_gold = first.get("gold", 200)
                        extra_souls = first.get("souls", 30)
                        total_gold_earned += extra_gold
                        total_souls_earned += extra_souls
                        earned_rewards.append(f"★ First Clear Bonus: +{extra_gold} Gold + {extra_souls} Souls")
                        if "unlock_cat" in first:
                            cat_name = first["unlock_cat"].replace('_', ' ').title()
                            earned_rewards.append(f"★ New Cat Unlocked: {cat_name}!")

                    # Add to player resources and save
                    player_resources["gold"] += total_gold_earned
                    player_resources["souls"] += total_souls_earned
                    try:
                        os.makedirs(os.path.dirname(PLAYER_RESOURCES_FILE), exist_ok=True)
                        with open(PLAYER_RESOURCES_FILE, "w") as f:
                            json.dump(player_resources, f, indent=4)
                        print(f"Resources saved: {player_resources['gold']} Gold, {player_resources['souls']} Souls")
                    except Exception as e:
                        print(f"Failed to save resources: {e}")

                    print(f"Victory! Clear time: {clear_time_seconds:.1f}s")
                    for r in earned_rewards:
                        print(r)

                    if victory_sfx:
                        victory_sfx.set_volume(0.8)
                        victory_sfx.play()

        elif game_state == "paused":
            end_rect, continue_rect = draw_pause_menu(screen, font, current_level)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if end_rect.collidepoint(pos):
                        game_state = "level_selection"
                        our_tower = None
                        enemy_tower = None
                        cats.clear()
                        enemies.clear()
                        souls.clear()
                        shockwave_effects.clear()
                        current_budget = 1000
                        pygame.mixer.music.stop()
                        current_bgm_path = None
                        boss_music_active = False
                        boss_shockwave_played = False
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                        print("Battle ended, returning to level selection.")
                    elif continue_rect.collidepoint(pos):
                        game_state = "playing"
                        pygame.mixer.music.unpause()
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                        print("Resumed battle.")

        elif game_state == "end":
            current_level = levels[selected_level]
            is_last_level = selected_level == len(levels) - 1
            victory_display_time = getattr(pygame.time, "victory_display_time", 0)
            if status == "victory" and victory_display_time == 0:
                pygame.time.victory_display_time = pygame.time.get_ticks()

            continue_rect = draw_end_screen(screen, current_level, status, end_font, font, our_tower, enemy_tower, victory_display_time, camera_offset_x)

            if status == "victory" and earned_rewards:
                reward_y = 280
                title_surf = end_font.render("Rewards Earned!", True, (255, 255, 100))
                screen.blit(title_surf, (screen.get_width() // 2 - title_surf.get_width() // 2, reward_y))
                reward_y += 100
                for reward_text in earned_rewards:
                    text_surf = select_font.render(reward_text, True, (255, 255, 200))
                    screen.blit(text_surf, (screen.get_width() // 2 - text_surf.get_width() // 2, reward_y))
                    reward_y += 60
                total_text = select_font.render(f"Total: {total_gold_earned} Gold + {total_souls_earned} Souls", True, (255, 255, 0))
                screen.blit(total_text, (screen.get_width() // 2 - total_text.get_width() // 2, reward_y + 20))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if status == "victory" and is_first_completion:
                            completed_levels.add(selected_level)
                            try:
                                with open(save_file, "w") as f:
                                    json.dump(list(completed_levels), f)
                                print(f"Saved level {selected_level} completion.")
                            except Exception as e:
                                print(f"Save error: {e}")
                        if status == "victory" and is_last_level and is_first_completion:
                            game_state = "ending"
                            pygame.time.ending_start_time = pygame.time.get_ticks()
                            print("Entering ending animation.")
                        else:
                            game_state = "level_selection"
                            our_tower = None
                            enemy_tower = None
                            cats.clear()
                            enemies.clear()
                            souls.clear()
                            shockwave_effects.clear()
                            current_budget = 1000
                            pygame.mixer.music.stop()
                            current_bgm_path = None
                            boss_music_active = False
                            boss_shockwave_played = False
                            setattr(pygame.time, "victory_display_time", 0)
                            if key_action_sfx.get('other_button'):
                                key_action_sfx['other_button'].play()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if continue_rect and continue_rect.collidepoint(pos):
                        if status == "victory" and is_first_completion:
                            completed_levels.add(selected_level)
                            try:
                                with open(save_file, "w") as f:
                                    json.dump(list(completed_levels), f)
                                print(f"Saved level {selected_level} completion.")
                            except Exception as e:
                                print(f"Save error: {e}")
                        if status == "victory" and is_last_level and is_first_completion:
                            game_state = "ending"
                            pygame.time.ending_start_time = pygame.time.get_ticks()
                            print("Entering ending animation.")
                        else:
                            game_state = "level_selection"
                            our_tower = None
                            enemy_tower = None
                            cats.clear()
                            enemies.clear()
                            souls.clear()
                            shockwave_effects.clear()
                            current_budget = 1000
                            pygame.mixer.music.stop()
                            current_bgm_path = None
                            boss_music_active = False
                            boss_shockwave_played = False
                            setattr(pygame.time, "victory_display_time", 0)
                            if key_action_sfx.get('other_button'):
                                key_action_sfx['other_button'].play()

        elif game_state == "ending":
            ending_start_time = getattr(pygame.time, "ending_start_time", pygame.time.get_ticks())
            setattr(pygame.time, "ending_start_time", ending_start_time)
            ending_duration = 35000
            fade_in_duration = 5000
            if not hasattr(pygame.time, "ending_music_initialized") or not pygame.time.ending_music_initialized:
                pygame.mixer.set_num_channels(16)
                pygame.mixer.music.set_volume(0.5)
                print(f"Reinitialized mixer, channels: {pygame.mixer.get_num_channels()}")
                ending_music_path = "audio/TBC/005.ogg"
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                if os.path.exists(ending_music_path):
                    pygame.mixer.music.load(ending_music_path)
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
                    current_bgm_path = ending_music_path
                    pygame.time.ending_music_initialized = True
                    print(f"Playing ending music: {ending_music_path}")
                else:
                    print(f"Warning: ending music '{ending_music_path}' not found.")
                    pygame.time.ending_music_initialized = False
            elapsed_time = current_time - ending_start_time
            current_fade_alpha = int(255 * min(1.0, elapsed_time / fade_in_duration))
            y_offset = screen.get_height()
            if elapsed_time >= fade_in_duration:
                text_progress_time = elapsed_time - fade_in_duration
                text_scroll_duration = ending_duration - fade_in_duration
                text_scroll_progress = min(1.0, text_progress_time / text_scroll_duration)
                y_offset = screen.get_height() * (1 - text_scroll_progress * text_scroll_progress)
            skip_rect = draw_ending_animation(screen, font, y_offset, current_fade_alpha)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if skip_rect and skip_rect.collidepoint(event.pos):
                        game_state = "level_selection"
                        our_tower = None
                        enemy_tower = None
                        cats.clear()
                        enemies.clear()
                        souls.clear()
                        shockwave_effects.clear()
                        current_budget = 1000
                        pygame.mixer.music.stop()
                        current_bgm_path = None
                        boss_music_active = False
                        boss_shockwave_played = False
                        setattr(pygame.time, "ending_start_time", 0)
                        if hasattr(pygame.time, "ending_music_initialized"):
                            delattr(pygame.time, "ending_music_initialized")
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                        print("Skipped ending animation.")
            if elapsed_time >= ending_duration + DELAY_TIME:
                game_state = "level_selection"
                our_tower = None
                enemy_tower = None
                cats.clear()
                enemies.clear()
                souls.clear()
                shockwave_effects.clear()
                current_budget = 1000
                pygame.mixer.music.stop()
                current_bgm_path = None
                boss_music_active = False
                boss_shockwave_played = False
                setattr(pygame.time, "ending_start_time", 0)
                if hasattr(pygame.time, "ending_music_initialized"):
                    delattr(pygame.time, "ending_music_initialized")
                print("Ending animation finished.")

        await asyncio.sleep(0)
        clock.tick(FPS)# game/rewards.py

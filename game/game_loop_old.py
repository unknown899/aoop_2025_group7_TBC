# game/game_loop.py

import json
import os
import asyncio
import pygame
from game.rewards import LEVEL_REWARDS, draw_reward

# Delay time (ms)
DELAY_TIME = 2000

# Player files
PLAYER_RESOURCES_FILE = "data/player_resources.json"
PLAYER_UNLOCKED_CATS_FILE = "data/player_unlocked_cats.json"

# Global variables
unlocked_cats = {"basic", "eraser"}
completed_levels = set()
player_resources = {"gold": 0, "souls": 0}
selected_cats = []
selected_level = 0
game_state = "intro"

# 在其他載入存檔之後新增
FIRST_CLEAR_CLAIMED_FILE = "data/first_clear_rewards.json"
claimed_first_clear = {"0": [[], []], "1": [[], []], "2": [[], []], "3": [[], []], "4": [[], []]}  # 預設結構

try:
    if os.path.exists(FIRST_CLEAR_CLAIMED_FILE):
        with open(FIRST_CLEAR_CLAIMED_FILE, "r") as f:
            loaded = json.load(f)
            if isinstance(loaded, dict):
                claimed_first_clear = {str(k): v for k, v in loaded.items()}  # 確保 key 是 str
except Exception as e:
    print(f"Warning: failed to load first_clear claimed: {e}")

async def main_game_loop(screen, clock):
    global unlocked_cats, completed_levels, player_resources
    global selected_cats, selected_level, game_state, intro_start_time
    global current_bgm_path, boss_music_active, boss_shockwave_played

    FPS = 60
    font = pygame.font.SysFont(None, 25)
    end_font = pygame.font.SysFont(None, 96)
    select_font = pygame.font.SysFont(None, 60)
    budget_font = pygame.font.SysFont(None, 40)
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    # Load backgrounds
    try:
        main_menu_bg = pygame.image.load("./images/map_main_menu.png").convert_alpha()
        main_menu_bg = pygame.transform.scale(main_menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception as e:
        print(f"Warning: failed to load main_menu_bg: {e}")
        main_menu_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        main_menu_bg.fill((20, 40, 60))

    try:
        level_map_bg = pygame.image.load("./images/map_level_select.png").convert_alpha()
        level_map_bg = pygame.transform.scale(level_map_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception as e:
        print(f"Warning: failed to load level_map_bg: {e}")
        level_map_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        level_map_bg.fill((30, 60, 30))

    # Snail player
    try:
        snail_image = pygame.image.load("./images/character/snail.png").convert_alpha()
        snail_image = pygame.transform.scale(snail_image, (70, 70))
    except Exception as e:
        print(f"Warning: failed to load snail_image: {e}")
        snail_image = pygame.Surface((70, 70), pygame.SRCALPHA)
        pygame.draw.circle(snail_image, (0, 200, 0), (35, 35), 35)
        pygame.draw.circle(snail_image, (0, 255, 0), (35, 35), 35, 5)

    # Level nodes
    LEVEL_NODES = [
        (300, 400),
        (600, 250),
        (900, 450),
        (1100, 300),
        (700, 600),
    ]

    # Import entities and UI
    from .battle_logic import update_battle
    from .ui import draw_game_ui, draw_pause_menu, draw_end_screen, draw_intro_screen, draw_ending_animation, draw_level_selection
    from .entities import cat_types, cat_costs, cat_cooldowns, levels, enemy_types, YManager, CSmokeEffect, load_cat_images, OriginalSpawnStrategy, AdvancedSpawnStrategy, MLSpawnStrategy, EnemySpawner, CannonSkill, CannonIcon
    from game.constants import csmoke_images1, csmoke_images2, cannon_images, icon_cfg

    # Battle variables
    cats = []
    enemies = []
    souls = []
    shockwave_effects = []
    our_tower = None
    enemy_tower = None
    last_spawn_time = {}
    current_budget = 0
    last_budget_increase_time = 0
    total_budget_limitation = 16500
    budget_rate = 33
    status = None
    level_start_time = 0
    cat_y_manager = YManager(base_y=532, min_y=300, max_slots=15)
    enemy_y_manager = YManager(base_y=500, min_y=300, max_slots=15)
    cat_key_map = {}
    button_rects = {}
    camera_offset_x = 0
    square_surface = pygame.Surface((1220, 480), pygame.SRCALPHA)
    square_surface.fill((150, 150, 150, 100))
    cat_images = load_cat_images()

    # Load saved data
    save_file = "completed_levels.json"
    try:
        if os.path.exists(save_file):
            with open(save_file, "r") as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, list):
                    completed_levels = set(loaded_data)
    except Exception as e:
        print(f"Warning: error loading completed levels: {e}")

    try:
        if os.path.exists(PLAYER_RESOURCES_FILE):
            with open(PLAYER_RESOURCES_FILE, "r") as f:
                loaded = json.load(f)
                player_resources["gold"] = loaded.get("gold", 0)
                player_resources["souls"] = loaded.get("souls", 0)
    except Exception as e:
        print(f"Warning: failed to load player resources: {e}")

    try:
        if os.path.exists(PLAYER_UNLOCKED_CATS_FILE):
            with open(PLAYER_UNLOCKED_CATS_FILE, "r") as f:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    unlocked_cats = set(loaded)
    except Exception as e:
        print(f"Warning: failed to load unlocked cats: {e}")

    player_map_pos = [300, 400]
    intro_start_time = pygame.time.get_ticks()
    intro_duration = 35000
    fade_in_duration = 5000

    current_bgm_path = None
    boss_music_active = False
    boss_shockwave_played = False

    # Sound loading
    cat_spawn_sfx = {}
    if os.path.exists("audio/TBC/010.ogg"):
        cat_spawn_sfx['default'] = pygame.mixer.Sound("audio/TBC/010.ogg")
        cat_spawn_sfx['default'].set_volume(0.7)
    else:
        print("Warning: 'audio/TBC/010.ogg' not found, cat spawn sound will not play.")

    victory_sfx = pygame.mixer.Sound("audio/TBC/008.ogg") if os.path.exists("audio/TBC/008.ogg") else None
    defeat_sfx = pygame.mixer.Sound("audio/TBC/009.ogg") if os.path.exists("audio/TBC/009.ogg") else None
    boss_intro_sfx = pygame.mixer.Sound("audio/TBC/036.ogg") if os.path.exists("audio/TBC/036.ogg") else None

    key_action_sfx = {
        'cannot_deploy': pygame.mixer.Sound("audio/TBC/015.ogg") if os.path.exists("audio/TBC/015.ogg") else None,
        'can_deploy': pygame.mixer.Sound("audio/TBC/014.ogg") if os.path.exists("audio/TBC/014.ogg") else None,
        'other_button': pygame.mixer.Sound("audio/TBC/011.ogg") if os.path.exists("audio/TBC/011.ogg") else None
    }
    for key, sfx in key_action_sfx.items():
        if sfx:
            sfx.set_volume(0.6 if key in ['cannot_deploy', 'can_deploy'] else 0.5)

    battle_sfx = {
        'hit_unit': pygame.mixer.Sound("audio/TBC/021.ogg") if os.path.exists("audio/TBC/021.ogg") else None,
        'hit_tower': pygame.mixer.Sound("audio/TBC/022.ogg") if os.path.exists("audio/TBC/022.ogg") else None,
        'unit_die': pygame.mixer.Sound("audio/TBC/023.ogg") if os.path.exists("audio/TBC/023.ogg") else None
    }
    for key, sfx in battle_sfx.items():
        if sfx:
            sfx.set_volume(0.6 if key in ['hit_unit', 'hit_tower'] else 0.7)

    while True:
        current_time = pygame.time.get_ticks()
        screen.fill((0, 0, 0))

        if game_state == "intro":
            intro_music_path = "audio/TBC/000.ogg"
            if current_bgm_path != intro_music_path and os.path.exists(intro_music_path):
                pygame.mixer.music.load(intro_music_path)
                pygame.mixer.music.play(-1)
                current_bgm_path = intro_music_path

            elapsed_intro_time = current_time - intro_start_time
            current_fade_alpha = int(255 * min(1.0, elapsed_intro_time / fade_in_duration))
            y_offset = SCREEN_HEIGHT

            if elapsed_intro_time >= fade_in_duration:
                text_progress_time = elapsed_intro_time - fade_in_duration
                text_scroll_duration = intro_duration - fade_in_duration
                text_scroll_progress = min(1.0, text_progress_time / text_scroll_duration)
                y_offset = SCREEN_HEIGHT * (1 - text_scroll_progress * text_scroll_progress)

            skip_rect = draw_intro_screen(screen, font, y_offset, current_fade_alpha)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if skip_rect.collidepoint(event.pos):
                        game_state = "main_menu"
                        pygame.mixer.music.stop()
                        current_bgm_path = None
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()

            if elapsed_intro_time >= intro_duration + DELAY_TIME:
                game_state = "main_menu"
                pygame.mixer.music.stop()
                current_bgm_path = None

        elif game_state == "main_menu":
            screen.blit(main_menu_bg, (0, 0))

            battle_rect = pygame.Rect(200, 300, 400, 150)
            pygame.draw.rect(screen, (0, 100, 0), battle_rect, border_radius=30)
            pygame.draw.rect(screen, (0, 255, 0), battle_rect, 8, border_radius=30)
            battle_text = select_font.render("go to battle", True, (255, 255, 255))
            screen.blit(battle_text, battle_text.get_rect(center=battle_rect.center))

            gacha_rect = pygame.Rect(680, 300, 400, 150)
            pygame.draw.rect(screen, (100, 0, 100), gacha_rect, border_radius=30)
            pygame.draw.rect(screen, (255, 0, 255), gacha_rect, 8, border_radius=30)
            gacha_text = select_font.render("get gecha", True, (255, 255, 255))
            screen.blit(gacha_text, gacha_text.get_rect(center=gacha_rect.center))

            resource_text = f"Gold: {player_resources['gold']} Souls: {player_resources['souls']}"
            resource_surf = select_font.render(resource_text, True, (255, 215, 0))
            screen.blit(resource_surf, (50, 30))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if battle_rect.collidepoint(pos):
                        game_state = "level_map"
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                    elif gacha_rect.collidepoint(pos):
                        game_state = "gacha_developing"
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()

        elif game_state == "level_map":
            from .ui.battle_menu import draw_battle_map_selection
            selected_idx, new_state = draw_battle_map_selection(
                screen=screen,
                level_map_bg=level_map_bg,
                snail_image=snail_image,
                LEVEL_NODES=LEVEL_NODES,
                completed_levels=completed_levels,
                player_pos=player_map_pos,
                player_speed=6,
                select_font=select_font
            )
            if new_state == "main_menu":
                game_state = "main_menu"
                if key_action_sfx.get('other_button'):
                    key_action_sfx['other_button'].play()
            if selected_idx is not None:
                selected_level = selected_idx
                selected_cats = []  # 清空，讓 cat_selection 重新預選
                game_state = "cat_selection"
                if key_action_sfx.get('other_button'):
                    key_action_sfx['other_button'].play()
                print(f"選擇關卡 {selected_level + 1}: {levels[selected_level].name}")

        elif game_state == "cat_selection":
            # 使用 draw_level_selection（傳入 unlocked_cats）
            cat_rects, reset_rect, quit_rect, start_rect = draw_level_selection(
                screen=screen,
                levels=levels,
                selected_level=selected_level,
                selected_cats=selected_cats,
                font=font,
                select_font=select_font,
                completed_levels=completed_levels,
                cat_images=cat_images,
                square_surface=square_surface,
                unlock_cats=unlocked_cats
            )

            resource_text = f"Gold: {player_resources['gold']} Souls: {player_resources['souls']}"
            resource_surf = select_font.render(resource_text, True, (255, 215, 0))
            screen.blit(resource_surf, (50, 30))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for cat_type, rect in cat_rects.items():
                        if rect.collidepoint(pos):
                            if cat_type in selected_cats and len(selected_cats) > 1:
                                selected_cats.remove(cat_type)
                            elif cat_type not in selected_cats and len(selected_cats) < 10:
                                selected_cats.append(cat_type)
                            cat_key_map = {pygame.K_1 + i: cat_type for i, cat_type in enumerate(selected_cats[:10])}
                            button_rects = {cat_type: pygame.Rect(1100 + idx * 120, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}
                            if key_action_sfx.get('other_button'):
                                key_action_sfx['other_button'].play()

                    if reset_rect.collidepoint(pos):
                        completed_levels.clear()
                        player_resources = {"gold": 0, "souls": 0}
                        unlocked_cats = {"basic", "eraser"}
                        selected_cats = []
                        claimed_first_clear = {"0": [[], []], "1": [[], []], "2": [[], []], "3": [[], []], "4": [[], []]} 

                        for path in [save_file, PLAYER_RESOURCES_FILE, PLAYER_UNLOCKED_CATS_FILE, FIRST_CLEAR_CLAIMED_FILE]:
                            if os.path.exists(path):
                                os.remove(path)

                        with open(save_file, "w") as f:
                            json.dump([], f)
                        with open(PLAYER_UNLOCKED_CATS_FILE, "w") as f:
                            json.dump(list(unlocked_cats), f, indent=4)
                        with open(FIRST_CLEAR_CLAIMED_FILE, "w") as f:
                            json.dump(claimed_first_clear, f, indent=4)

                        game_state = "intro"
                        intro_start_time = pygame.time.get_ticks()
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()

                    if quit_rect.collidepoint(pos):
                        return

                    if start_rect.collidepoint(pos):
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
                            current_level.reset_spawn_counts()
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
                            cats = []
                            enemies = []
                            souls = []
                            shockwave_effects = []
                            current_budget = current_level.initial_budget
                            last_budget_increase_time = current_time - 333
                            last_spawn_time = {cat_type: 0 for cat_type in cat_types}
                            level_start_time = current_time
                            status = None
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
                                pygame.mixer.music.stop()
                                current_bgm_path = None
                            boss_shockwave_played = False

                            if key_action_sfx.get('other_button'):
                                key_action_sfx['other_button'].play()
                        else:
                            if key_action_sfx.get('cannot_deploy'):
                                key_action_sfx['cannot_deploy'].play()

        elif game_state == "gacha_developing":
            from .ui.gacha_ui import draw_gacha_developing_screen
            new_state = draw_gacha_developing_screen(
                screen=screen,
                select_font=select_font,
                font=font,
                key_action_sfx=key_action_sfx
            )
            if new_state == "main_menu":
                game_state = "main_menu"
                print("返回主選單 from 轉蛋頁面")

        elif game_state == "playing":
            current_level = levels[selected_level]
            bg_width = current_level.background.get_width()

            # 繪製遊戲 UI（返回 pause_rect 與更新後的 camera_offset_x）
            pause_rect, button_rects, camera_offset_x = draw_game_ui(
                screen, current_level, current_budget, enemy_tower, current_time, level_start_time,
                selected_cats, last_spawn_time, button_rects, font, cat_key_map, budget_font, camera_offset_x
            )

            # Boss 登場邏輯
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

            # 事件處理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos

                    # 點擊大炮（cannon）圖標
                    if cannon_icon.is_clicked(pos):
                        if cannon.state == "ready":
                            cannon.activate(current_time)
                            # sfx_laser.play()  # 註解中，需定義 sfx_laser
                        # else:
                        #     sfx_fail.play()  # 註解中，需定義 sfx_fail

                    # 點擊暫停按鈕
                    if pause_rect.collidepoint(pos):
                        game_state = "paused"
                        pygame.mixer.music.pause()
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()

                    # 點擊出貓按鈕
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

            # 處理畫面左右滑動
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                camera_offset_x -= 10
            if keys[pygame.K_RIGHT]:
                camera_offset_x += 10
            camera_offset_x = max(0, min(camera_offset_x, bg_width - SCREEN_WIDTH))

            # 預算增加
            if current_time - last_budget_increase_time >= 333:
                if current_budget < total_budget_limitation:
                    current_budget = min(current_budget + budget_rate, total_budget_limitation)
                last_budget_increase_time = current_time

            # 敵人生成
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

            # 更新狀態效果
            for cat in cats:
                cat.update_status_effects(current_time)
            for enemy in enemies:
                enemy.update_status_effects(current_time)

            # 戰鬥邏輯更新（包含炮台）
            shockwave_effects = update_battle(
                cats, enemies, our_tower, enemy_tower, current_time, souls,
                cat_y_manager, enemy_y_manager, cannon, shockwave_effects, current_budget, battle_sfx
            )
            souls = [soul for soul in souls if soul.update()]

            # 繪製所有物件
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

            # 繪製大炮（隨相機移動）
            cannon.draw(screen, camera_offset_x)

            # 繪製大炮 UI（固定在螢幕上）
            if cannon.state == "cooldown":
                progress = min(1.0, (current_time - cannon.cooldown_start) / cannon.cooldown)
            elif cannon.state == "ready":
                progress = 1.0
            else:  # "firing" 或其他狀態
                progress = 0.0
            cannon_icon.draw(screen, cannon.state, progress, current_time)

            pygame.display.flip()

            # 勝負判斷
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
            
            elif enemy_tower and enemy_tower.hp <= 0:
                if status != "victory":
                    status = "victory"
                    game_state = "end"
                    # ... 音效 ...

                    clear_time_seconds = (current_time - level_start_time) / 1000
                    reward_data = LEVEL_REWARDS.get(selected_level, {})
                    print(f"關卡 {selected_level} 獲得獎勵資料: {reward_data}")
                    earned_rewards = []
                    total_gold_earned = 0
                    total_souls_earned = 0
                    newly_unlocked_cat = None

                    # 1. repeatable：每次都抽
                    repeatable_pool = reward_data.get("repeatable", [])
                    if repeatable_pool:
                        r = draw_reward(repeatable_pool)
                        g = r.get("gold", 0)
                        s = r.get("souls", 0)
                        total_gold_earned += g
                        total_souls_earned += s
                        if g or s:
                            earned_rewards.append(f"Stage Clear: +{g} Gold + {s} Souls")
                    import random
                    # 2. first_clear 金幣靈魂：根據機率獨立觸發
                    claimed_first_clear =  {"0": [[], []], "1": [[], []], "2": [[], []], "3": [[], []], "4": [[], []]}
                    try:
                        if os.path.exists(FIRST_CLEAR_CLAIMED_FILE):
                            with open(FIRST_CLEAR_CLAIMED_FILE, "r") as f:
                                loaded = json.load(f)
                                if isinstance(loaded, dict):
                                    claimed_first_clear = {str(k): v for k, v in loaded.items()}  # 確保 key 是 str
                    except Exception as e:
                        print(f"Warning: failed to load first_clear claimed: {e}")

                    
                    for idx, fc in enumerate(reward_data.get("first_clear", [])):
                        # reward_type = fc.get("type")
                        chance = fc.get("weight", 0)
                        roll = min((random.random() * 101), 100)
                        # print(roll)
                        if roll <= chance and (idx not in claimed_first_clear[str(selected_level)][0]):
                            reward_idx = fc.get("reward")
                            # for r in reward_idx:
                            g = reward_idx.get("gold", 0)
                            s = reward_idx.get("souls", 0)
                            total_gold_earned += g
                            total_souls_earned += s
                            if g or s:
                                earned_rewards.append(f"First Clear Bonus: +{g} Gold + {s} Souls")
                            unlock = reward_idx.get("unlock_cat")
                            if unlock and unlock not in unlocked_cats:
                                unlocked_cats.add(unlock)
                                newly_unlocked_cat = unlock
                                earned_rewards.append(f"New Cat Unlocked: {unlock.capitalize()} Cat")
                            
                            claimed_first_clear[str(selected_level)][0].append(idx)

                    
                    # 3. speed_bonus：根據時間獨立給（僅第一次通關）
                    for idx, fc in enumerate(reward_data.get("speed_bonus", [])):
                        time_limit = fc.get("threshold", 0)
                        if clear_time_seconds <= time_limit and (idx not in claimed_first_clear[str(selected_level)][1]):
                            reward_gold = fc.get("reward", {}).get("gold", 0)
                            reward_souls = fc.get("reward", {}).get("souls", 0)
                            total_gold_earned += reward_gold
                            total_souls_earned += reward_souls
                            if reward_gold or reward_souls:
                                earned_rewards.append(f"Speed Bonus: +{reward_gold} Gold + {reward_souls} Souls")

                            reward_new_cat = fc.get("reward", {}).get("unlock_cat")
                            if reward_new_cat and reward_new_cat not in unlocked_cats:
                                unlocked_cats.add(reward_new_cat)
                                newly_unlocked_cat = reward_new_cat
                                earned_rewards.append(f"New Cat Unlocked: {reward_new_cat.capitalize()} Cat")

                            
                            
                            claimed_first_clear[str(selected_level)][1].append(idx)

                            # is_get.append(idx)
                        # 存 completed_levels
                    player_resources["souls"] += total_souls_earned
                    player_resources["gold"] += total_gold_earned
                    # 儲存所有記錄
                    try:
                        with open(PLAYER_RESOURCES_FILE, "w") as f:
                            json.dump({
                                "gold": player_resources["gold"] ,
                                "souls": player_resources["souls"] 
                            }, f, indent=4)
                        with open(PLAYER_UNLOCKED_CATS_FILE, "w") as f:
                            json.dump(list(unlocked_cats), f, indent=4)
                        with open(FIRST_CLEAR_CLAIMED_FILE, "w") as f:
                            json.dump(claimed_first_clear, f, indent=4)
                    except Exception as e:
                        print(f"Warning: failed to save player data: {e}")


        elif game_state == "paused":
            end_rect, continue_rect = draw_pause_menu(screen, font, current_level)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if end_rect.collidepoint(pos):
                        game_state = "main_menu"
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
                    elif continue_rect.collidepoint(pos):
                        game_state = "playing"
                        pygame.mixer.music.unpause()
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()

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
                screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, reward_y))
                reward_y += 100
                for reward_text in earned_rewards:
                    text_surf = select_font.render(reward_text, True, (255, 255, 200))
                    screen.blit(text_surf, (SCREEN_WIDTH // 2 - text_surf.get_width() // 2, reward_y))
                    reward_y += 60
                total_text = select_font.render(f"Total: {total_gold_earned} Gold + {total_souls_earned} Souls", True, (255, 255, 0))
                screen.blit(total_text, (SCREEN_WIDTH // 2 - total_text.get_width() // 2, reward_y + 20))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if status == "victory":
                            completed_levels.add(selected_level)
                            try:
                                with open(save_file, "w") as f:
                                    json.dump(list(completed_levels), f)
                            except Exception as e:
                                print(f"Save error: {e}")
                            if status == "victory" and is_last_level:
                                game_state = "ending"
                                pygame.time.ending_start_time = pygame.time.get_ticks()
                            else:
                                game_state = "main_menu"
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
                        elif status == "lose":
                            game_state = "main_menu"
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
                        if status == "victory":
                            completed_levels.add(selected_level)
                            try:
                                with open(save_file, "w") as f:
                                    json.dump(list(completed_levels), f)
                            except Exception as e:
                                print(f"Save error: {e}")
                            if status == "victory" and is_last_level:
                                game_state = "ending"
                                pygame.time.ending_start_time = pygame.time.get_ticks()
                            else:
                                game_state = "main_menu"
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
                        elif status == "lose":
                            game_state = "main_menu"
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
                ending_music_path = "audio/TBC/005.ogg"
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                if os.path.exists(ending_music_path):
                    pygame.mixer.music.load(ending_music_path)
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
                    current_bgm_path = ending_music_path
                    pygame.time.ending_music_initialized = True
                else:
                    pygame.time.ending_music_initialized = False
            elapsed_time = current_time - ending_start_time
            current_fade_alpha = int(255 * min(1.0, elapsed_time / fade_in_duration))
            y_offset = SCREEN_HEIGHT
            if elapsed_time >= fade_in_duration:
                text_progress_time = elapsed_time - fade_in_duration
                text_scroll_duration = ending_duration - fade_in_duration
                text_scroll_progress = min(1.0, text_progress_time / text_scroll_duration)
                y_offset = SCREEN_HEIGHT * (1 - text_scroll_progress * text_scroll_progress)
            skip_rect = draw_ending_animation(screen, font, y_offset, current_fade_alpha)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if skip_rect and skip_rect.collidepoint(event.pos):
                        game_state = "main_menu"
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
            if elapsed_time >= ending_duration + DELAY_TIME:
                game_state = "main_menu"
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

        await asyncio.sleep(0)
        clock.tick(FPS)
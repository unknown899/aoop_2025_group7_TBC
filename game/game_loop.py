# game/game_loop.py
import asyncio
import pygame
from .gameLoop.audio import AudioManager
from .gameLoop.resources import ResourceManager
from .gameLoop.reward_system import RewardSystem
from .gameLoop.intro_handler import IntroHandler
from .gameLoop.ending_headler import EndingHandler
from .gameLoop.state_manager import StateManager
from .entities import levels, load_cat_images, cat_types  # cat_types 必須 import
import os, json

async def main_game_loop(screen, clock):
    # 初始化所有管理器
    audio = AudioManager()
    resources = ResourceManager()
    rewards = RewardSystem()
    state_manager = StateManager(screen, clock, audio, resources, rewards)

    # 載入共享資料
    completed_levels = set()
    save_file = "completed_levels.json"
    try:
        if os.path.exists(save_file):
            with open(save_file, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    completed_levels = set(data)
    except Exception as e:
        print(f"Load completed levels error: {e}")

    cat_images = load_cat_images()
    square_surface = pygame.Surface((1220, 480), pygame.SRCALPHA)
    square_surface.fill((150, 150, 150, 100))

    selected_level = 0
    selected_cats = list(cat_types.keys())[:2]

    # 遊戲狀態
    current_state = "intro"

    intro_handler = IntroHandler(screen, audio)
    ending_handler = EndingHandler(screen, audio)

    while True:
        if current_state == "intro":
            next_state = await intro_handler.run()
            if next_state == "quit":
                return
            current_state = "level_selection"

        elif current_state == "level_selection":
            result = await state_manager.level_selection(
                levels, selected_level, selected_cats, completed_levels, cat_images, square_surface
            )
            if result[0] == "quit":
                return
            elif result[0] == "playing":
                current_state = "playing"
                selected_level = result[1]
                selected_cats = result[2]

        elif current_state == "playing":
            result = await state_manager.playing(levels, selected_level, selected_cats, completed_levels)
            # result = ("end" or "paused", status, earned_rewards, gold, souls, is_first, is_last)

            if result[0] == "paused":
                paused_result = await state_manager.paused(levels[selected_level])
                if paused_result == "quit":
                    return
                elif paused_result == "level_selection":
                    current_state = "level_selection"
                else:
                    current_state = "playing"

            elif result[0] == "end":
                end_result = await state_manager.end(
                    levels, selected_level,
                    result[1],  # status
                    result[2],  # earned_rewards
                    result[3],  # gold
                    result[4],  # souls
                    result[5],  # is_first
                    result[6],  # is_last
                    completed_levels
                )
                if end_result == "quit":
                    return
                current_state = end_result

        elif current_state == "ending":
            next_state = await ending_handler.run()
            if next_state == "quit":
                return
            current_state = "level_selection"

        await asyncio.sleep(0)
        clock.tick(60)
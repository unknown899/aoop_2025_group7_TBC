# game/gameLoop/state_manager.py
import pygame
import os
from ..constants import SAVE_FILE
import json, asyncio

class StateManager:
    def __init__(self, screen, clock, audio, resources, rewards):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        self.resources = resources
        self.rewards = rewards
        self.font = pygame.font.SysFont(None, 25)
        self.select_font = pygame.font.SysFont(None, 60)
        self.end_font = pygame.font.SysFont(None, 96)

    async def level_selection(self, levels, selected_level, selected_cats, completed_levels, cat_images, square_surface):
        from ..ui import draw_level_selection

        self.audio.stop_bgm()

        while True:
            cat_rects, reset_rect, quit_rect, start_rect = draw_level_selection(
                self.screen, levels, selected_level, selected_cats,
                self.font, self.select_font, completed_levels, cat_images, square_surface
            )

            self.resources.draw(self.screen, self.select_font)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return ("quit", selected_level, selected_cats)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    # 關卡選擇邏輯
                    for i in range(len(levels)):
                        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
                        if rect.collidepoint(pos):
                            if i == 0 or (i - 1) in completed_levels:
                                selected_level = i
                                self.audio.play_key_action('other_button')
                            else:
                                self.audio.play_key_action('cannot_deploy')
                    # 貓選擇邏輯
                    for cat_type, rect in cat_rects.items():
                        if rect.collidepoint(pos):
                            if cat_type in selected_cats and len(selected_cats) > 1:
                                selected_cats.remove(cat_type)
                            elif cat_type not in selected_cats and len(selected_cats) < 10:
                                selected_cats.append(cat_type)
                            self.audio.play_key_action('other_button')
                    # 重置
                    if reset_rect.collidepoint(pos):
                        completed_levels.clear()
                        self.resources.reset()
                        if os.path.exists(SAVE_FILE):
                            os.remove(SAVE_FILE)
                        if os.path.exists("data/player_resources.json"):
                            os.remove("data/player_resources.json")
                        try:
                            with open(SAVE_FILE, "w") as f:
                                json.dump([], f)
                        except Exception:
                            pass
                        self.audio.play_key_action('other_button')
                    # 退出
                    if quit_rect.collidepoint(pos):
                        return ("quit", selected_level, selected_cats)
                    # 開始
                    if start_rect.collidepoint(pos):
                        if selected_level == 0 or (selected_level - 1) in completed_levels:
                            if selected_cats:
                                return ("playing", selected_level, selected_cats)
                            else:
                                self.audio.play_key_action('cannot_deploy')
                        else:
                            self.audio.play_key_action('cannot_deploy')

            await asyncio.sleep(0)

    async def playing(self, levels, selected_level, selected_cats, completed_levels):
        from .playing_handler import PlayingHandler
        handler = PlayingHandler(self.screen, self.clock, self.audio, self.rewards, self.resources)
        return await handler.run(levels, selected_level, selected_cats, completed_levels)

    async def paused(self, current_level):
        from ..ui import draw_pause_menu
        while True:
            end_rect, continue_rect = draw_pause_menu(self.screen, self.font, current_level)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if end_rect.collidepoint(pos):
                        return "level_selection"
                    elif continue_rect.collidepoint(pos):
                        return "playing"
            await asyncio.sleep(0)

    async def end(self, levels, selected_level, status, earned_rewards, gold_earned, souls_earned, is_first_completion, is_last_level, completed_levels):
        from ..ui import draw_end_screen
        current_level = levels[selected_level]
        victory_display_time = pygame.time.get_ticks() if status == "victory" else 0

        while True:
            continue_rect = draw_end_screen(self.screen, current_level, status, self.end_font, self.font,
                                            current_level.our_tower, current_level.enemy_tower, victory_display_time, 0)

            if status == "victory":
                self.rewards.draw_rewards(self.screen, earned_rewards, gold_earned, souls_earned, self.end_font, self.select_font)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or \
                       (event.type == pygame.MOUSEBUTTONDOWN and continue_rect and continue_rect.collidepoint(event.pos)):
                        if status == "victory" and is_first_completion:
                            completed_levels.add(selected_level)
                            try:
                                with open(SAVE_FILE, "w") as f:
                                    json.dump(list(completed_levels), f)
                            except Exception:
                                pass
                        if status == "victory" and is_last_level:
                            return "ending"
                        else:
                            return "level_selection"

            await asyncio.sleep(0)
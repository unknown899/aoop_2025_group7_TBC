# game/gameLoop/ending_handler.py
import pygame
from ..ui import draw_ending_animation
from ..constants import DELAY_TIME
import asyncio

class EndingHandler:
    def __init__(self, screen, audio):
        self.screen = screen
        self.audio = audio
        self.font = pygame.font.SysFont(None, 25)
        self.ending_duration = 35000
        self.fade_in_duration = 5000

    async def run(self):
        ending_start_time = pygame.time.get_ticks()
        self.audio.play_bgm("audio/TBC/005.ogg")

        while True:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - ending_start_time
            alpha = int(255 * min(1.0, elapsed / self.fade_in_duration))
            y_offset = self.screen.get_height()
            if elapsed >= self.fade_in_duration:
                progress = min(1.0, (elapsed - self.fade_in_duration) / (self.ending_duration - self.fade_in_duration))
                y_offset = self.screen.get_height() * (1 - progress * progress)
            skip_rect = draw_ending_animation(self.screen, self.font, y_offset, alpha)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if skip_rect.collidepoint(event.pos):
                        self.audio.play_key_action('other_button')
                        return "level_selection"
            if elapsed >= self.ending_duration + DELAY_TIME:
                return "level_selection"
            await asyncio.sleep(0)
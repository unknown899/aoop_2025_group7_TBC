# game/gameLoop/audio.py
import pygame
import os

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)
        pygame.mixer.music.set_volume(0.5)

        self.cat_spawn = self._load_sound("audio/TBC/010.ogg", 0.7)
        self.victory = self._load_sound("audio/TBC/008.ogg")
        self.defeat = self._load_sound("audio/TBC/009.ogg")
        self.boss_intro = self._load_sound("audio/TBC/036.ogg")

        self.key_sfx = {
            'cannot_deploy': self._load_sound("audio/TBC/015.ogg", 0.6),
            'can_deploy': self._load_sound("audio/TBC/014.ogg", 0.6),
            'other_button': self._load_sound("audio/TBC/011.ogg", 0.5)
        }

        self.battle_sfx = {
            'hit_unit': self._load_sound("audio/TBC/021.ogg", 0.6),
            'hit_tower': self._load_sound("audio/TBC/022.ogg", 0.6),
            'unit_die': self._load_sound("audio/TBC/023.ogg", 0.7)
        }

        self.current_bgm = None

    def _load_sound(self, path, volume=None):
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            if volume is not None:
                sound.set_volume(volume)
            return sound
        print(f"Warning: sound '{path}' not found.")
        return None

    def play_bgm(self, path):
        if path and os.path.exists(path) and self.current_bgm != path:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
            self.current_bgm = path

    def stop_bgm(self):
        pygame.mixer.music.stop()
        self.current_bgm = None

    def pause_bgm(self):
        pygame.mixer.music.pause()

    def unpause_bgm(self):
        pygame.mixer.music.unpause()

    def play_victory(self):
        if self.victory:
            self.victory.set_volume(0.8)
            self.victory.play()

    def play_defeat(self):
        if self.defeat:
            self.defeat.play()

    def play_boss_intro(self):
        if self.boss_intro:
            self.boss_intro.play()

    def play_cat_spawn(self):
        if self.cat_spawn:
            self.cat_spawn.play()

    def play_key_action(self, key):
        sfx = self.key_sfx.get(key)
        if sfx:
            sfx.play()

    def get_battle_sfx(self):
        return self.battle_sfx
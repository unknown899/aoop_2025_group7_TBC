from game.entities.common import Common
from game.constants import BOTTOM_Y
from game.config_loader import load_config
import pygame
class Cat(Common):
    def __init__(self, x, y, hp, atk, speed, color, attack_range=50, is_aoe=False,
                 width=50, height=50, kb_limit=1, idle_frames=None, move_frames=None,
                 windup_frames=None, attack_frames=None, recovery_frames=None,
                 kb_frames=None, windup_duration=200, attack_duration=100, recovery_duration=50,
                 target_attributes=None, immunities=None, boosts=None, status_effects_config=None,
                 attack_interval=1000, delta_y=0, attack_type="gun"):
        super().__init__(x, y, hp, atk, speed, color, attack_range, is_aoe, width, height, kb_limit,
                         idle_frames, move_frames, windup_frames, attack_frames, recovery_frames,
                         kb_frames, windup_duration, attack_duration, recovery_duration, attack_interval, attack_type)
        self.y = y - height + delta_y  # 覆蓋 y 座標以處理 delta_y
        self.y0 = y - height + delta_y
        self.target_attributes = target_attributes if target_attributes is not None else []
        self.immunities = immunities if immunities is not None else {}
        self.boosts = boosts if boosts is not None else {}
        self.status_effects = {}
        self.status_effects_config = status_effects_config if status_effects_config is not None else {}
        self.has_retreated = False

    def move(self):
        if not self.is_attacking and not self.kb_animation and self.anim_state not in ["windup", "attacking", "recovery"]:
            self.x -= self.speed
            self.is_attacking = False
            self.anim_state = "moving"

    def get_attack_zone(self):
        center_x = self.x + self.width // 2
        return pygame.Rect(center_x - self.attack_range // 2, self.y - self.height // 2,
                          self.attack_range, self.height + self.attack_range)

    def knock_back(self, direction=50):  # 預設向左擊退，子類可覆蓋
        if not hasattr(self, 'immunities') or "Knockback Immunity" not in self.immunities.get("self", []):
            self.kb_animation = True
            self.kb_start_x = self.x
            self.kb_target_x = self.x + direction  # 方向可由子類指定
            self.kb_start_y = self.y
            self.kb_start_time = pygame.time.get_ticks()
            self.kb_progress = 0
            self.anim_state = "knockback"
            self.kb_count += 1
            if self.kb_count >= self.kb_limit:
                self.hp = 0

    def start_retreat(self, distance):
        if not self.is_attacking and not self.has_retreated:
            if not hasattr(self, 'immunities') or "Knockback Immunity" not in self.immunities.get("self", []):
                self.kb_animation = True
                self.kb_start_x = self.x
                self.kb_target_x = self.x + distance  # 方向可由子類指定
                self.kb_start_y = self.y
                self.kb_start_time = pygame.time.get_ticks()
                self.kb_progress = 0
                self.anim_state = "knockback"
                # self.kb_count += 1
                if self.kb_count >= self.kb_limit:
                    self.hp = 0

    def apply_status_effect(self, effect, duration, chance=0.3, target=None):
        """應用狀態效果到目標，考慮機率和免疫"""
        if not target or pygame.time.get_ticks() % 100 < chance * 100:
            target_attrs = getattr(target, 'attributes', [])
            for attr in target_attrs:
                if effect in self.immunities.get(attr, []):
                    return
            if target:
                target.status_effects[effect] = pygame.time.get_ticks() + duration * 1000
                if effect == "Knockback":
                    target.knock_back()
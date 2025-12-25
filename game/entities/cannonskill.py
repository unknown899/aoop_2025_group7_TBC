import pygame
import math

class CannonSkill:
    def __init__(
        self,
        origin_pos,
        sweep_start_x,
        sweep_end_x,
        ground_y,
        sweep_duration=1200,
        cooldown=5000,
        damage=300,
        origin_frames=None,
        beam_frames=None,
        sweep_fx_frames=None,
        after_fx_frames=None,  # ✅ 改成 2D： [frames_group1, frames_group2]
        frame_duration=100
    ):
        # --- 基本設定 ---
        self.origin_x, self.origin_y = origin_pos
        self.sweep_start_x = sweep_start_x
        self.sweep_end_x = sweep_end_x
        self.ground_y = ground_y
        self.sweep_duration = sweep_duration
        self.cooldown = cooldown
        self.damage = damage

        # --- 圖片 ---
        self.origin_frames = origin_frames or []
        self.beam_frames = beam_frames or []
        self.sweep_fx_frames = sweep_fx_frames or []

        # ✅ 讓 after_fx_frames 永遠是「二維」
        # 允許你傳：
        # 1) None
        # 2) [group1_frames, group2_frames]
        # 3) 單一 group（舊寫法） -> 會自動包成 [group]
        if after_fx_frames is None:
            self.after_fx_frames = []
        else:
            # 如果傳進來是「一維 frames(裡面是 Surface)」，就包成二維
            if len(after_fx_frames) > 0 and isinstance(after_fx_frames[0], pygame.Surface):
                self.after_fx_frames = [after_fx_frames]
            else:
                self.after_fx_frames = after_fx_frames

        # --- 狀態 ---
        self.state = "ready"
        self.start_time = 0
        self.cooldown_start = 0

        # --- 動畫 ---
        #self.anim_index = 0
        self.after_x = sweep_start_x
        self.frame_duration = frame_duration # 例如 100ms 代表 1秒 10 張圖
        self.current_time_ms = 0
    # ======================================================
    # 觸發技能
    # ======================================================
    def activate(self, current_time):
        if self.state == "ready":
            self.state = "sweeping"
            self.start_time = current_time
            self.anim_index = 0

    # ======================================================
    # 更新
    # ======================================================
    def update(self, current_time, enemies):
        #self.anim_index += 1
        self.current_time_ms = current_time

        # ---------- 掃射中 ----------
        if self.state == "sweeping":
            progress = (current_time - self.start_time) / self.sweep_duration

            if progress >= 1.0:
                # 掃射結束 → 進入後效
                self.state = "after"
                self.after_x = self.sweep_start_x

                # 結算傷害（只在這裡一次）
                self._apply_damage(enemies)

        # ---------- 掃射後地面殘影 ----------
        elif self.state == "after":
            speed = (self.sweep_end_x - self.sweep_start_x) / (self.sweep_duration / 16)
            self.after_x += speed

            if self.after_x >= self.sweep_end_x:
                self.state = "cooldown"
                self.cooldown_start = current_time

        # ---------- 冷卻 ----------
        elif self.state == "cooldown":
            if current_time - self.cooldown_start >= self.cooldown:
                self.state = "ready"

    def _get_frame(self, frames):
        """根據時間計算目前該顯示哪一張圖"""
        if not frames: return None
        # 總時間除以每幀時長，再對總幀數取餘數
        idx = (self.current_time_ms // self.frame_duration) % len(frames)
        return frames[idx]
    
    # ======================================================
    # 繪製
    # ======================================================
    def draw(self, screen, camera_offset_x):
        # ---------- 掃射中 ----------
        if self.state == "sweeping":
            self._draw_origin(screen, camera_offset_x)
            self._draw_beam(screen, camera_offset_x)
            self._draw_sweep_fx(screen, camera_offset_x)

        # ---------- 掃射後 ----------
        elif self.state == "after":
            self._draw_after_fx(screen, camera_offset_x)

    # ======================================================
    # 子功能
    # ======================================================
    def _draw_origin(self, screen, camera_offset_x):
        if not self.origin_frames:
            return
        img = self._get_frame(self.origin_frames)
        rect = img.get_rect(center=(self.origin_x-camera_offset_x, self.origin_y))
        screen.blit(img, rect)

    def _draw_beam(self, screen, camera_offset_x):
        if not self.beam_frames:
            return

        progress = (pygame.time.get_ticks() - self.start_time) / self.sweep_duration
        progress = max(0, min(1, progress))

        tx = self.sweep_start_x + (self.sweep_end_x - self.sweep_start_x) * progress
        ty = self.ground_y

        dx = tx - self.origin_x
        dy = ty - self.origin_y
        angle = -math.degrees(math.atan2(dy, dx))

        beam = self._get_frame(self.beam_frames)#self.beam_frames[self.anim_index % len(self.beam_frames)]
        rotated = pygame.transform.rotate(beam, angle)

        rect = rotated.get_rect(midleft=(self.origin_x-camera_offset_x, self.origin_y))
        screen.blit(rotated, rect)

    def _draw_sweep_fx(self, screen, camera_offset_x):
        if not self.sweep_fx_frames:
            return

        progress = (pygame.time.get_ticks() - self.start_time) / self.sweep_duration
        tx = self.sweep_start_x + (self.sweep_end_x - self.sweep_start_x) * progress
        ty = self.ground_y

        fx = self._get_frame(self.sweep_fx_frames)#self.sweep_fx_frames[self.anim_index % len(self.sweep_fx_frames)]
        rect = fx.get_rect(center=(tx-camera_offset_x, ty))
        screen.blit(fx, rect)

    def _draw_after_fx(self, screen, camera_offset_x):
        if not self.after_fx_frames:
            return

        ty = self.ground_y

        # ✅ 各組用各自的 idx（依各組自己的長度循環）
        for group in self.after_fx_frames:
            if not group:
                continue

            fx = self._get_frame(group)#group[idx]

            for offset in (0, -40):
                rect = fx.get_rect(center=(self.after_x-camera_offset_x + offset, ty))
                screen.blit(fx, rect)
    # ======================================================
    # 傷害計算（只在掃射結束）
    # ======================================================
    def _apply_damage(self, enemies):
        for e in enemies:
            enemy_center_x = e.x + e.width // 2
            if self.sweep_start_x <= enemy_center_x <= self.sweep_end_x:#用enemy中心點判定
                e.take_damage(self.damage, "physic")

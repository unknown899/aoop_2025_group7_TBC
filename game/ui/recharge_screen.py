import pygame

def draw_recharge_screen(
    screen,
    recharge_bg,
    recharge_modal
):
    """
    儲值頁面（獨立 state）
    - 畫背景
    - 更新並繪製 RechargeModal
    - 不處理事件、不切 state
    """

    # 1. 畫儲值頁背景
    screen.blit(recharge_bg, (0, 0))

    # 2. 更新 modal 狀態（游標、動畫）
    recharge_modal.update()

    # 3. 畫半透明 panel + 內容
    recharge_modal.draw(screen)

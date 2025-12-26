from .load_images import* 
import os

## constants.py
BOTTOM_Y = 490
smoke_images = load_smoke_images()
electric_images = load_electric_images()
gas_images = load_gas_images()
physic_images = load_physic_images()
csmoke_images1, csmoke_images2 = load_csmoke_images()
cannon_images = load_cannonskill_images(
    origin_scale=0.07,
    beam_scale=0.1,
    sweep_fx_scale=0.07,
    after_fx_scale1=0.5,
    after_fx_scale2=0.5, #offset=-40
    alpha=255
)

# 載入轉蛋背景，並強制縮放為螢幕大小
gacha_background = load_single_image(
    path="images/background/gacha_bg.jpeg", 
    size=(1280, 600),
    convert_alpha=False  # 背景通常不透明，False 可微幅提升效能
)
'''
# 載入轉蛋按鈕（如果有單獨圖片的話）
gacha_btn_img = load_single_image(
    path="assets/images/roll_btn.png",
    size=(200, 80),
    convert_alpha=True  # UI 按鈕通常需要去背透明
)
'''
ready, full, gray = load_cannonicon_image(scale=0.4)
icon_cfg = {
    'ready': [ready[0], ready[1]], # 動畫
    'full': full,             # 原圖
    'gray': gray,           # 你準備好的灰階圖
    'bounds': (701*0.4*1/9.25, 701*0.4*6.25/9.75)                  # 假設非透明區域在 Y=15~85 之間
}

# Gacha cost constants
GACHA_COST_GOLD = 500
GACHA_COST_SOULS = 5


# constants.py 的所在資料夾 → game/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# repo 根目錄
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

# data 資料夾
DATA_DIR = os.path.join(ROOT_DIR, "data")

# 檔案路徑
RESOURCE_FILE = os.path.join(DATA_DIR, "player_resources.json")
UNLOCKED_FILE = os.path.join(DATA_DIR, "player_unlocked_cats.json")

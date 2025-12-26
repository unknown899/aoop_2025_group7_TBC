from .load_images import* 

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
ready, full, gray = load_cannonicon_image(scale=0.4)
icon_cfg = {
    'ready': [ready[0], ready[1]], # 動畫
    'full': full,             # 原圖
    'gray': gray,           # 你準備好的灰階圖
    'bounds': (701*0.4*1/9.25, 701*0.4*6.25/9.75)                  # 假設非透明區域在 Y=15~85 之間
}

# Gacha cost constants
GACHA_COST_GOLD = 500
GACHA_COST_SOUL = 5
from .load_images import* 

## constants.py
BOTTOM_Y = 490
smoke_images = load_smoke_images()
electric_images = load_electric_images()
gas_images = load_gas_images()
physic_images = load_physic_images()
csmoke_images1, csmoke_images2 = load_csmoke_images()
cannon_images = load_cannonskill_images(
    origin_scale=1.0,
    beam_scale=1.0,
    sweep_fx_scale=1.0,
    after_fx_scale=1.0,
    alpha=255
)
ready, full, gray = load_cannonicon_image(scale=0.4)
icon_cfg = {
    'ready': [ready[0], ready[1]], # 動畫
    'full': full,             # 原圖
    'gray': gray,           # 你準備好的灰階圖
    'bounds': (701*0.4*1/9.25, 701*0.4*6.25/9.75)                  # 假設非透明區域在 Y=15~85 之間
}
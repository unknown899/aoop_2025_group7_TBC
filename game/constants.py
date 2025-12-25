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
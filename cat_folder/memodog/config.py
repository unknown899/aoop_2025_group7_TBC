cat_config = {
    "id":105,
    "hp": 12,
    "atk": 800,
    "speed": 1,
    "color": (0, 255, 255),
    "attack_range": 510,
    "is_aoe": True,
    "kb_limit": 5,
    "cooldown": 5000,
    "cost": 5100,
    "width":400,
    "height": 200,
    "windup_duration": 500,
    "attack_duration": 500,
    "recovery_duration": 50,
    "attack_interval": 10000,
    "idle_frames": [f"cat_folder/memodog/walking/77ebc47eae1738112a5d98548e866bdf.png" ],#900
    "move_frames": [f"cat_folder/memodog/walking/77ebc47eae1738112a5d98548e866bdf.png"]\
        ,
    
    "windup_frames": [f"cat_folder/memodog/attacking/frame_{i:03d}.png" for i in range(0, 1)] \
        ,
    "attack_frames": [f"cat_folder/memodog/attacking/frame_{i:03d}.png" for i in range(1, 10)], \

    "recovery_frames": [f"cat_folder/memodog/attacking/frame_{i:03d}.png" for i in range(10, 11)],
    
    "kb_frames": [f"cat_folder/memodog/walking/77ebc47eae1738112a5d98548e866bdf.png"],
    "delta_y": -52, # 微調 y 座標
    "ibtn_idle": "cat_folder/memodog/ibtn_idle.png",
    "ibtn_hover": "cat_folder/memodog/ibtn_hover.png",
    "ibtn_pressed": "cat_folder/memodog/ibtn_pressed.png",
    "attack_type": "physic",  # 攻擊類型
    "attack_type": "physic",  # 攻擊類型
    "cat_image": "cat_folder/memodog/cat_image.png",  # 放在levelselection的貓咪圖片
}
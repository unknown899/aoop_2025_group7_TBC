import json
import random
import os

from  .constants import GACHA_COST_GOLD, GACHA_COST_SOULS, RESOURCE_FILE, UNLOCKED_FILE

def perform_gacha():
    """
    執行轉蛋邏輯並更新 JSON
    返回: (是否成功, 抽中結果文字, 更新後的資料字典)
    """
    # 1. 讀取資源檔案
    if not os.path.exists(RESOURCE_FILE):
        return False, "Resource file missing!", {}
    
    with open(RESOURCE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. 檢查資源 (注意你的鍵名是 'souls' 有個 s)
    if data["gold"] < GACHA_COST_GOLD or data["souls"] < GACHA_COST_SOULS:
        return False, "Not enough Gold or Souls!", data

    # 3. 扣除資源
    data["gold"] -= GACHA_COST_GOLD
    data["souls"] -= GACHA_COST_SOULS

    # 4. 隨機抽取邏輯
    # 這裡放你所有的角色 ID（對應你角色清單的字串）
    all_cats = ["basic","speedy","eraser","mtank","tank", "kp"]
    
    # 30% 機率槓龜，70% 抽中
    if random.random() < 0.3:
        result_msg = "Nothing... Try again!"
        won_cat = None
    else:
        won_cat = random.choice(all_cats)
        result_msg = f"Obtained: {won_cat}!"

    # 5. 更新檔案：資源檔
    with open(RESOURCE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    # 6. 更新檔案：已解鎖角色檔 (如果有抽中)
    if won_cat:
        unlocked = []
        if os.path.exists(UNLOCKED_FILE):
            with open(UNLOCKED_FILE, "r", encoding="utf-8") as f:
                unlocked = json.load(f)
        
        if won_cat not in unlocked:
            unlocked.append(won_cat)
            with open(UNLOCKED_FILE, "w", encoding="utf-8") as f:
                json.dump(unlocked, f, indent=4)
        else:
            result_msg += " (Already owned)"

    return True, result_msg, data
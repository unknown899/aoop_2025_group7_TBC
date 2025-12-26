import json
import random
import os

GACHA_COST_GOLD = 500
GACHA_COST_SOUL = 5

def perform_gacha(current_gold, current_soul, unlocked_cats_file="player_unlocked_cat.json"):
    """
    執行轉蛋邏輯
    返回: (是否成功, 更新後的gold, 更新後的soul, 抽中結果文字)
    """
    # 1. 檢查資源
    if current_gold < GACHA_COST_GOLD or current_soul < GACHA_COST_SOUL:
        return False, current_gold, current_soul, "Not enough Gold or Soul!"

    # 2. 扣除資源
    new_gold = current_gold - GACHA_COST_GOLD
    new_soul = current_soul - GACHA_COST_SOUL

    # 3. 隨機抽取 (機率設定)
    # 假設目前遊戲中有的角色列表
    all_possible_cats = ["TankCat", "ArcherCat", "NinjaCat", "MageCat"]
    
    # 40% 機率沒抽中, 60% 抽中
    if random.random() < 0.4:
        return True, new_gold, new_soul, "Nothing... Try again!"

    won_cat = random.choice(all_possible_cats)

    # 4. 更新 JSON 檔案
    unlocked_list = []
    if os.path.exists(unlocked_cats_file):
        with open(unlocked_cats_file, "r") as f:
            unlocked_list = json.load(f)

    if won_cat not in unlocked_list:
        unlocked_list.append(won_cat)
        with open(unlocked_cats_file, "w") as f:
            json.dump(unlocked_list, f)
        result_msg = f"New Hero: {won_cat}!"
    else:
        result_msg = f"Got {won_cat} (Already owned)"

    return True, new_gold, new_soul, result_msg
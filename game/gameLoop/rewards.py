# game/gameLoop/rewards.py
from ..rewards import LEVEL_REWARDS

class RewardCalculator:
    def calculate(self, level_idx, clear_time, is_first):
        data = LEVEL_REWARDS.get(level_idx, {})
        rewards = []
        gold = data.get("base_gold", 100)
        souls = data.get("base_souls", 10)
        rewards.append(f"Stage Clear: {gold} Gold + {souls} Souls")

        speed = data.get("speed_bonus", {})
        if speed and clear_time <= speed["threshold"]:
            gold += speed["gold"]
            souls += speed["souls"]
            rewards.append(f"★ Speed Clear Bonus: +{speed['gold']} Gold + {speed['souls']} Souls")

        if is_first:
            first = data.get("first_clear", {})
            extra_gold = first.get("gold", 200)
            extra_souls = first.get("souls", 30)
            gold += extra_gold
            souls += extra_souls
            rewards.append(f"★ First Clear Bonus: +{extra_gold} Gold + {extra_souls} Souls")
            if "unlock_cat" in first:
                cat_name = first["unlock_cat"].replace('_', ' ').title()
                rewards.append(f"★ New Cat Unlocked: {cat_name}!")

        return rewards, gold, souls

    def draw(self, screen, rewards, total_gold, total_souls, end_font, select_font):
        if not rewards:
            return
        y = 280
        title = end_font.render("Rewards Earned!", True, (255, 255, 100))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, y))
        y += 100
        for text in rewards:
            surf = select_font.render(text, True, (255, 255, 200))
            screen.blit(surf, (screen.get_width() // 2 - surf.get_width() // 2, y))
            y += 60
        total = select_font.render(f"Total: {total_gold} Gold + {total_souls} Souls", True, (255, 255, 0))
        screen.blit(total, (screen.get_width() // 2 - total.get_width() // 2, y + 20))
# game/gameLoop/reward_system.py
from ..rewards import LEVEL_REWARDS

class RewardSystem:
    def calculate_rewards(self, level_idx, clear_time_seconds, is_first_completion):
        data = LEVEL_REWARDS.get(level_idx, {})
        earned = []
        gold = data.get("base_gold", 100)
        souls = data.get("base_souls", 10)
        earned.append(f"Stage Clear: {gold} Gold + {souls} Souls")

        speed_bonus = data.get("speed_bonus", {})
        if speed_bonus and clear_time_seconds <= speed_bonus["threshold"]:
            gold += speed_bonus["gold"]
            souls += speed_bonus["souls"]
            earned.append(f"★ Speed Clear Bonus: +{speed_bonus['gold']} Gold + {speed_bonus['souls']} Souls")

        if is_first_completion:
            first = data.get("first_clear", {})
            extra_gold = first.get("gold", 200)
            extra_souls = first.get("souls", 30)
            gold += extra_gold
            souls += extra_souls
            earned.append(f"★ First Clear Bonus: +{extra_gold} Gold + {extra_souls} Souls")
            if "unlock_cat" in first:
                cat_name = first["unlock_cat"].replace('_', ' ').title()
                earned.append(f"★ New Cat Unlocked: {cat_name}!")

        return earned, gold, souls

    def draw_rewards(self, screen, earned_rewards, total_gold, total_souls, end_font, select_font):
        if not earned_rewards:
            return
        y = 280
        title = end_font.render("Rewards Earned!", True, (255, 255, 100))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, y))
        y += 100
        for text in earned_rewards:
            surf = select_font.render(text, True, (255, 255, 200))
            screen.blit(surf, (screen.get_width() // 2 - surf.get_width() // 2, y))
            y += 60
        total = select_font.render(f"Total: {total_gold} Gold + {total_souls} Souls", True, (255, 255, 0))
        screen.blit(total, (screen.get_width() // 2 - total.get_width() // 2, y + 20))
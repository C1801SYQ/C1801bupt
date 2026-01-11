# core/save_manager.py
import json
import os

SAVE_FILE = "save_data.json"

# core/save_manager.py
def save_game(gold, potions):
    data = {
        "total_gold": gold,
        "potions": potions
    }
    with open("save_data.json", "w") as f:
        json.dump(data, f)

def load_game():
    default_data = {"total_gold": 0, "potions": 0}
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            try:
                data = json.load(f)
                # 使用 update 确保旧存档缺失的键会被补全
                default_data.update(data)
                return default_data
            except:
                return default_data
    return default_data
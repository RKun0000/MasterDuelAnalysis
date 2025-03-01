import json
import os
from tkinter import messagebox
from tools import my_deck_name, opp_deck_name, get_current_season

# 檔案讀寫


def load_data(filename="card_data.json"):

    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            my_decks = data.get("my_decks", [])
            opp_decks = data.get("opp_decks", [])
            records = data.get("records", [])
            current_season = data.get("current_season", [])
            if not my_decks:
                my_decks = my_deck_name()
            if not opp_decks:
                opp_decks = opp_deck_name()

            return my_decks, opp_decks, records, current_season
        except Exception as e:
            messagebox.showerror("錯誤", f"資料載入失敗: {e}")
            return None
    else:
        my_decks = my_deck_name()
        opp_decks = opp_deck_name()
        current_season = get_current_season()
        return my_decks, opp_decks, [], current_season


def save_data(my_decks, opp_decks, records, current_season, filename="card_data.json"):
    data = {
        "my_decks": my_decks,
        "opp_decks": opp_decks,
        "records": records,
        "current_season": current_season,
    }
    try:
        with open("card_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("錯誤", f"資料儲存失敗: {e}")

import json
import os
from tkinter import messagebox
from tools import my_deck_name, opp_deck_name, get_current_season, get_dc_season

DATA_VERSION = 1.1


def load_data(filename="card_data.json"):
    if os.path.exists(filename):
        if os.path.getsize(filename) == 0:
            # 檔案為空，直接回傳預設值，但不要寫入空資料
            return (
                my_deck_name(),
                opp_deck_name(),
                [],
                get_current_season(),
                [],
                get_dc_season(),
            )
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            version = data.get("version", 1)
            my_decks = data.get("my_decks", [])
            opp_decks = data.get("opp_decks", [])
            if not my_decks:
                my_decks = my_deck_name()
            if not opp_decks:
                opp_decks = opp_deck_name()
            if version >= 1.1:
                records_rank = data.get("records_rank", [])
                current_season = data.get("current_season", get_current_season())
                records_dc = data.get("records_dc", [])
                current_season_dc = data.get("current_season_dc", get_dc_season())
            else:
                records_rank = data.get("records", [])
                current_season = data.get("current_season", get_current_season())
                records_dc = []
                current_season_dc = get_dc_season()
            return (
                my_decks,
                opp_decks,
                records_rank,
                current_season,
                records_dc,
                current_season_dc,
            )
        except Exception as e:
            messagebox.showerror("錯誤", f"資料載入失敗: {e}")
            return None
    else:
        return (
            my_deck_name(),
            opp_deck_name(),
            [],
            get_current_season(),
            [],
            get_dc_season(),
        )


def save_data(
    my_decks,
    opp_decks,
    records_rank,
    current_season,
    records_dc,
    current_season_dc,
    filename="card_data.json",
):
    data = {
        "version": DATA_VERSION,
        "my_decks": my_decks,
        "opp_decks": opp_decks,
        "records_rank": records_rank,
        "current_season": current_season,
        "records_dc": records_dc,
        "current_season_dc": current_season_dc,
    }
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("錯誤", f"資料儲存失敗: {e}")

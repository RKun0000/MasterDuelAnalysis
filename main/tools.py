import sys, os
import matplotlib as mpl
import matplotlib.font_manager as fm
from datetime import datetime

DEFAULT_DC_SEASON = "March 2025"


def center_window(window, parent):
    window.update_idletasks()
    # 取得主視窗的位置與尺寸
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    # 取得跳出視窗的尺寸
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    # 計算新的 x, y 座標
    x = parent_x + (parent_width - window_width) // 2
    y = parent_y + (parent_height - window_height) // 2
    window.geometry(f"+{x}+{y}")


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_font():
    # 使用自訂字體
    font_path = resource_path("TaipeiSansTCBeta-Regular.ttf")
    fm.fontManager.addfont(font_path)
    custom_font = fm.FontProperties(fname=font_path).get_name()

    # 設定全域字體為自訂字體
    mpl.rcParams["font.sans-serif"] = [custom_font]
    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["axes.unicode_minus"] = False  # 避免負號顯示問題


# 初始賽季取得
def get_current_season():

    base_year = 2025
    base_month = 2
    base_season = 38
    now = datetime.now()
    delta_months = (now.year - base_year) * 12 + (now.month - base_month)
    season_num = base_season + delta_months
    return f"S{season_num}"


def get_dc_season():
    return DEFAULT_DC_SEASON


def compute_streaks(records):
    longest_win = 0
    longest_loss = 0
    current_win = 0
    current_loss = 0
    sorted_records = sorted(records, key=lambda r: r["id"])
    for rec in sorted_records:
        if rec.get("result") == "勝":
            current_win += 1
            current_loss = 0
        else:
            current_loss += 1
            current_win = 0
        longest_win = max(longest_win, current_win)
        longest_loss = max(longest_loss, current_loss)
    return longest_win, longest_loss


# 初始卡組名稱清單
def my_deck_name():
    my_decks = [
        "刻魔蛇眼",
        "刻魔尤貝爾",
        "刻魔白森聖徒",
        "刻魔珠淚",
        "肅聲",
        "天盃龍",
        "閃刀姬",
    ]
    return my_decks


def opp_deck_name():
    opp_decks = [
        "未知",
        "刻魔尤貝爾",
        "刻魔聖徒蛇眼",
        "刻魔白森聖徒",
        "刻魔珠淚",
        "60GS",
        "天盃龍",
        "反主流",
        "貼紙大法師",
        "烙印",
        "霸王幻奏",
        "白銀城",
        "旅鳥",
        "刻魔聖徒消防隊",
        "龍輝巧",
        "英雄",
        "魔式甜點",
        "肅聲",
        "百夫長" "六花",
        "魔術師",
        "人偶FTK",
        "荷魯斯強攻",
        "神碑",
        "雙子雷精靈",
        "光道FTK",
        "天威相劍",
    ]

    return opp_decks


def rank_list():
    rank = [
        "競等賽",
        "Master 1",
        "Master 2",
        "Master 3",
        "Master 4",
        "Master 5",
        "Diamond 1",
        "Diamond 2",
        "Diamond 3",
        "Diamond 4",
        "Diamond 5",
        "Platinum 1",
        "Platinum 2",
        "Platinum 3",
        "Platinum 4",
        "Platinum 5",
        "Gold 1",
        "Gold 2",
        "Gold 3",
        "Gold 4",
        "Gold 5",
        "Silver 1",
        "Silver 2",
        "Silver 3",
        "Silver 4",
        "Silver 5",
    ]

    return rank

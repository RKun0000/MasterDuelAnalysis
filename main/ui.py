import tkinter as tk
from tkinter import ttk, messagebox
from deck_management import DeckManagementWindow, SeasonManagementWindow
from record_modify import RecordModifyWindow
from data_manager import load_data, save_data
from tools import (
    get_current_season,
    get_dc_season,
    search_for_combobox,
    rank_list,
    hand_trap_list,
    compute_streaks,
    exclusive,
)
from charts import OpponentDeckPieChart, MyDeckPieChart
import sys


class CardRecordApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Master Duel Analysis")
        # init windows
        self.my_deck_window = None
        self.opp_deck_window = None
        self.season_window = None
        self.record_modify_window = None
        self.pie_chart_window = None
        self.my_pie_chart_window = None

        self.my_decks = []
        self.opp_decks = []
        self.record_id_counter = 0
        self.sort_descending = True

        self.records_rank = []
        self.current_season = get_current_season()

        self.records_dc = []
        self.current_season_dc = get_dc_season()

        self.stats_deck_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="全部")

        self.mode = "rank_mode"
        self.mode_var = tk.StringVar(value=self.mode)

        data = load_data()
        if data is not None:
            (
                self.my_decks,
                self.opp_decks,
                self.records_rank,
                self.current_season,
                self.records_dc,
                self.current_season_dc,
            ) = data
        else:
            # 若讀取失敗，不覆蓋原檔案
            messagebox.showwarning("資料載入失敗")
        self.create_top_menu()
        self.create_main_area()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.developer_label = tk.Label(
            self.root, text="Developer : RK", font=("Arial", 8), fg="gray"
        )
        self.developer_label.place(relx=1, rely=1, anchor="se", x=-5, y=-5)

    def create_top_menu(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        btn_my_deck = tk.Button(
            top_frame, text="我方卡組管理", command=self.manage_my_decks
        )
        btn_my_deck.pack(side=tk.LEFT, padx=5)
        btn_opp_deck = tk.Button(
            top_frame, text="對方卡組管理", command=self.manage_opp_decks
        )
        btn_opp_deck.pack(side=tk.LEFT, padx=5)
        btn_season = tk.Button(top_frame, text="賽季管理", command=self.manage_season)
        btn_season.pack(side=tk.LEFT, padx=5)

        tk.Label(top_frame, text="模式:").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(
            top_frame,
            text="天梯紀錄",
            variable=self.mode_var,
            value="rank_mode",
            command=self.on_mode_change,
        ).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(
            top_frame,
            text="DC盃紀錄",
            variable=self.mode_var,
            value="dc_mode",
            command=self.on_mode_change,
        ).pack(side=tk.LEFT, padx=5)

    def on_mode_change(self):
        self.sort_descending = True
        # 設定按鈕顯示「由舊至新」（點擊後會變成舊至新）
        self.sort_button.config(text="由舊至新")
        self.mode = self.mode_var.get()
        # 如果有賽季管理視窗存在，先關閉
        if self.season_window is not None and self.season_window.winfo_exists():
            self.season_window.destroy()
            self.season_window = None

        # 依據模式自動更新賽季
        if self.mode == "rank_mode":
            # 若有天梯記錄，取得最新的賽季（假設字串排序符合最新到最舊）
            if self.records_rank:
                # 例如：以排序取最後一個
                seasons = sorted(
                    {
                        rec.get("season", self.current_season)
                        for rec in self.records_rank
                    }
                )
                self.current_season = seasons[-1]
            else:
                self.current_season = get_current_season()
            self.season_label.config(text=self.current_season)
        else:
            if self.records_dc:
                seasons = sorted(
                    {
                        rec.get("season", self.current_season_dc)
                        for rec in self.records_dc
                    }
                )
                self.current_season_dc = seasons[-1]
            else:
                self.current_season_dc = get_dc_season()
            self.season_label.config(text=self.current_season_dc)

        # 重新建立新增紀錄面板與戰績列表
        self.create_record_form(self.left_frame)
        self.create_record_list(self.left_frame)

    def create_main_area(self):
        # 使用 grid 分左右兩個區域
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=0)

        # 左側區域：輸入表單
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.create_record_form(self.left_frame)
        # 右側區域：統計數據
        right_frame = tk.Frame(self.main_frame, width=350)
        right_frame.grid(row=0, column=1, sticky="n", padx=(10, 0))
        right_frame.grid_propagate(False)
        self.create_statistics_panel(right_frame)
        # 建立戰績列表
        self.create_record_list(self.left_frame)

    def create_record_form(self, parent):
        # 每次重建前，先清空原有元件（若存在）
        for widget in parent.winfo_children():
            widget.destroy()

        form_frame = tk.LabelFrame(parent, text="新增戰績紀錄")
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        deck_frame = tk.Frame(form_frame)
        deck_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=5)

        tk.Label(deck_frame, text="我方卡組：").pack(side=tk.LEFT, padx=2)
        self.my_deck_var_form = tk.StringVar()
        self.my_deck_option = ttk.Combobox(
            deck_frame,
            textvariable=self.my_deck_var_form,
            values=self.my_decks,
            state="readonly",
            width=15,
        )
        self.my_deck_option.pack(side=tk.LEFT, padx=(2, 5))

        tk.Label(deck_frame, text="對方卡組：").pack(side=tk.LEFT, padx=(30, 2))
        self.opp_deck_var_form = tk.StringVar()
        self.opp_deck_option = ttk.Combobox(
            deck_frame,
            textvariable=self.opp_deck_var_form,
            values=self.opp_decks,
            state="normal",
            width=15,
        )
        self.opp_deck_option.pack(side=tk.LEFT, padx=(2, 5))
        search_for_combobox(self.opp_deck_option, self.opp_decks)

        if self.mode == "rank_mode":
            tk.Label(deck_frame, text="段位：").pack(side=tk.LEFT, padx=(30, 2))
            self.rank_var = tk.StringVar(value="Diamond 5")
            rank_options = rank_list()
            self.rank_option = ttk.Combobox(
                deck_frame,
                textvariable=self.rank_var,
                values=rank_options,
                state="readonly",
                width=15,
            )
            self.rank_option.pack(side=tk.LEFT, padx=(5, 2))
        elif self.mode == "dc_mode":
            tk.Label(deck_frame, text="積分:").pack(side=tk.LEFT, padx=(30, 2))
            self.points_var = tk.StringVar(value="0")
            self.points_entry = tk.Entry(
                deck_frame, textvariable=self.points_var, width=15
            )
            self.points_entry.pack(side=tk.LEFT, padx=(5, 2))

        options_frame = tk.Frame(form_frame)
        options_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="w")

        tk.Label(options_frame, text="勝負：").grid(
            row=0, column=0, padx=5, pady=2, sticky="e"
        )
        self.result_win_var = tk.BooleanVar(value=True)
        self.result_loss_var = tk.BooleanVar(value=False)

        self.result_win_cb = tk.Checkbutton(
            options_frame,
            text="勝",
            variable=self.result_win_var,
            command=lambda: exclusive(self.result_win_var, self.result_loss_var),
        )

        self.result_loss_cb = tk.Checkbutton(
            options_frame,
            text="敗",
            variable=self.result_loss_var,
            command=lambda: exclusive(self.result_loss_var, self.result_win_var),
        )
        self.result_win_cb.grid(row=0, column=1, padx=0, pady=2, sticky="w")
        self.result_loss_cb.grid(row=0, column=2, padx=0, pady=2, sticky="w")

        tk.Label(options_frame, text="硬幣：").grid(
            row=0, column=3, padx=(45, 0), pady=2, sticky="e"
        )
        self.coin_heads_var = tk.BooleanVar(value=True)
        self.coin_tails_var = tk.BooleanVar(value=False)

        self.coin_heads_cb = tk.Checkbutton(
            options_frame,
            text="正面",
            variable=self.coin_heads_var,
            command=lambda: exclusive(self.coin_heads_var, self.coin_tails_var),
        )
        self.coin_tails_cb = tk.Checkbutton(
            options_frame,
            text="反面",
            variable=self.coin_tails_var,
            command=lambda: exclusive(self.coin_tails_var, self.coin_heads_var),
        )
        self.coin_heads_cb.grid(row=0, column=4, padx=0, pady=2, sticky="w")
        self.coin_tails_cb.grid(row=0, column=5, padx=0, pady=2, sticky="w")

        tk.Label(options_frame, text="先後手：").grid(
            row=0, column=6, padx=0, pady=2, sticky="e"
        )
        self.turn_first_var = tk.BooleanVar(value=True)
        self.turn_second_var = tk.BooleanVar(value=False)

        self.first_cb_mod = tk.Checkbutton(
            options_frame,
            text="先手",
            variable=self.turn_first_var,
            command=lambda: exclusive(self.turn_first_var, self.turn_second_var),
        )
        self.second_cb_mod = tk.Checkbutton(
            options_frame,
            text="後手",
            variable=self.turn_second_var,
            command=lambda: exclusive(self.turn_second_var, self.turn_first_var),
        )
        self.first_cb_mod.grid(row=0, column=7, padx=0, pady=2, sticky="w")
        self.second_cb_mod.grid(row=0, column=8, padx=0, pady=2, sticky="w")

        tk.Label(options_frame, text="對方G是否通過：").grid(
            row=1, column=0, padx=0, pady=2, sticky="w"
        )
        self.g_var = tk.BooleanVar()
        self.g_cb = tk.Checkbutton(options_frame, variable=self.g_var)
        self.g_cb.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        tk.Label(options_frame, text="是否卡手：").grid(
            row=1, column=3, padx=(20, 0), pady=2, sticky="e"
        )
        self.card_stuck_var = tk.BooleanVar()
        self.card_stuck_cb = tk.Checkbutton(options_frame, variable=self.card_stuck_var)
        self.card_stuck_cb.grid(row=1, column=4, padx=0, pady=2, sticky="w")

        tk.Label(options_frame, text="我方有無手坑：").grid(
            row=1, column=6, padx=(10, 0), pady=2, sticky="e"
        )
        self.my_hand_traps_var = tk.BooleanVar()
        self.my_hand_traps_cb = tk.Checkbutton(
            options_frame, variable=self.my_hand_traps_var
        )
        self.my_hand_traps_cb.grid(row=1, column=7, padx=0, pady=2, sticky="w")

        tk.Label(form_frame, text="中G以外手坑:").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        # 預設所有手坑皆記錄，例如預設值為一個列表
        hand_trap_frame = tk.Frame(form_frame)
        hand_trap_frame.grid(row=3, column=1, columnspan=4, padx=5, pady=5, sticky="w")

        self.hand_traps = hand_trap_list()
        self.hand_traps_vars = {}
        for trap in self.hand_traps:
            var = tk.BooleanVar(value=False)  # 可依需求預設為 True 或 False
            cb = tk.Checkbutton(hand_trap_frame, text=trap, variable=var)
            cb.pack(side=tk.LEFT, padx=3)
            self.hand_traps_vars[trap] = var

        tk.Label(form_frame, text="備註:").grid(
            row=5, column=0, padx=5, pady=5, sticky="e"
        )

        self.note_entry = tk.Entry(form_frame, width=50)
        self.note_entry.grid(row=5, column=1, columnspan=3, padx=5, pady=5, sticky="w")
        submit_btn = tk.Button(form_frame, text="新增紀錄", command=self.add_record)
        submit_btn.grid(row=6, column=0, columnspan=4, pady=10)

    def create_record_list(self, parent):
        list_frame = tk.LabelFrame(parent, text="戰績紀錄列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 將 list_frame 透過 grid 設定彈性佈局
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        top_list_frame = tk.Frame(list_frame)
        top_list_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(top_list_frame, text="賽季:").pack(side=tk.LEFT)
        if self.mode == "rank_mode":
            season_text = self.current_season
        else:
            season_text = self.current_season_dc
        self.season_label = tk.Label(
            top_list_frame, text=season_text, font=("Arial", 16, "bold"), fg="red"
        )
        self.season_label.pack(side=tk.LEFT, padx=5)

        tk.Label(top_list_frame, text="篩選(我方卡組):").pack(side=tk.LEFT, padx=10)
        self.filter_var.set("全部")
        filter_options = ["全部"] + self.my_decks
        self.filter_option = ttk.Combobox(
            top_list_frame,
            textvariable=self.filter_var,
            values=filter_options,
            state="readonly",
            width=15,
        )
        self.filter_option.pack(side=tk.LEFT, padx=5)
        self.filter_option.bind("<<ComboboxSelected>>", lambda e: self.filter_records())

        self.sort_button = tk.Button(
            top_list_frame,
            text="由舊至新" if self.sort_descending else "由新至舊",
            command=self.toggle_sort_order,
        )
        self.sort_button.pack(side=tk.LEFT, padx=5)

        if self.mode == "rank_mode":
            columns = (
                "my_deck",
                "opp_deck",
                "result",
                "turn",
                "rank",
                "coin",
                "forced_first",
                "g",
                "expanded",
                "card_stuck",
                "my_hand_traps",
                "note",
            )
        elif self.mode == "dc_mode":
            columns = (
                "my_deck",
                "opp_deck",
                "result",
                "turn",
                "points",
                "coin",
                "forced_first",
                "g",
                "expanded",
                "card_stuck",
                "my_hand_traps",
                "note",
            )

        screen_height = self.root.winfo_screenheight()
        # 螢幕解析度較小時顯示較少的筆數
        if screen_height < 800:
            tree_height = 10
        else:
            tree_height = 15

        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=tree_height,
        )
        self.tree.heading("my_deck", text="我方卡組", anchor="center")
        self.tree.heading("opp_deck", text="對方卡組", anchor="center")
        self.tree.heading("result", text="勝負", anchor="center")
        self.tree.heading("turn", text="先後手", anchor="center")
        if self.mode == "rank_mode":
            self.tree.heading("rank", text="段位", anchor="center")
        else:
            self.tree.heading("points", text="積分", anchor="center")
        self.tree.heading("coin", text="硬幣", anchor="center")
        self.tree.heading("forced_first", text="被讓先", anchor="center")
        self.tree.heading("g", text="對方G通過", anchor="center")
        self.tree.heading("expanded", text="中G以外手坑", anchor="center")
        self.tree.heading("card_stuck", text="是否卡手", anchor="center")
        self.tree.heading("my_hand_traps", text="我方手坑", anchor="center")
        self.tree.heading("note", text="備註", anchor="center")

        for col in columns:
            self.tree.column(col, anchor="center", width=90)
        self.tree.column("note", width=200)

        # 垂直滾輪
        v_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscroll=v_scrollbar.set)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # 水平滾輪
        h_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.HORIZONTAL, command=self.tree.xview
        )
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.pack(fill=tk.BOTH, expand=True)
        btn_frame = tk.Frame(list_frame)
        btn_frame.pack(pady=5)
        btn_modify = tk.Button(btn_frame, text="修改紀錄", command=self.modify_record)
        btn_modify.pack(side=tk.LEFT, padx=5)
        btn_delete = tk.Button(btn_frame, text="刪除紀錄", command=self.delete_record)
        btn_delete.pack(side=tk.LEFT, padx=5)
        btn_stat = tk.Button(
            btn_frame, text="本賽季對手卡組使用比例", command=self.show_opp_deck_pie
        )
        btn_stat.pack(side=tk.LEFT, padx=5)
        btn_my_deck_stat = tk.Button(
            btn_frame, text="本賽季我方卡組使用比例", command=self.show_my_deck_pie
        )
        btn_my_deck_stat.pack(side=tk.LEFT, padx=5)

        # 當 list_frame 的大小改變時，調整 Treeview 欄位寬度
        list_frame.bind("<Configure>", self.on_list_frame_resize)
        # 載入資料到 Treeview
        self.load_tree_records()
        self.refresh_tree_records()

    def on_list_frame_resize(self, event):
        total_width = event.width
        # 取得目前的欄位列表（不包含未顯示的隱藏欄位）
        cols = self.tree["columns"]

        small_widths = {
            "result": 50,
            "turn": 50,
            "coin": 50,
            "g": 70,
            "forced_first": 50,
            "expanded": 80,
            "card_stuck": 60,
            "my_hand_traps": 60,
        }
        # 為其他欄位設定預設最小寬度（note 除外）
        default_width = 90

        # 計算除了 note 欄位外所有欄位的總寬度
        total_fixed = 0
        for col in cols:
            if col == "note":
                continue
            if col in small_widths:
                w = small_widths[col]
            else:
                w = default_width
            total_fixed += w
            self.tree.column(col, width=w)

        # note 欄位獲得剩餘寬度（至少100）
        note_width = max(total_width - total_fixed, 100)
        self.tree.column("note", width=note_width)

    def toggle_sort_order(self):
        self.sort_descending = not self.sort_descending
        self.sort_button.config(text="由舊至新" if self.sort_descending else "由新至舊")
        self.filter_records()

    def refresh_tree_records(self):
        self.sort_descending = True
        # 清除 Treeview 資料，然後僅載入當前賽季的紀錄
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.load_tree_records()
        self.filter_records()

    def create_statistics_panel(self, parent):
        stats_frame = tk.LabelFrame(parent, text="統計數據", width=220, height=490)
        stats_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        stats_frame.pack_propagate(False)
        tk.Label(stats_frame, text="選擇卡組:").pack(padx=5, pady=5)
        all_options = ["全部"] + self.my_decks
        self.stats_deck_var.set("全部")
        self.stats_deck_option = ttk.Combobox(
            stats_frame,
            textvariable=self.stats_deck_var,
            values=all_options,
            state="readonly",
            width=15,
        )
        self.stats_deck_option.pack(padx=5, pady=5)
        self.stats_deck_option.bind(
            "<<ComboboxSelected>>", lambda e: self.update_statistics()
        )
        self.total_label = tk.Label(stats_frame, text="總場數: 0")
        self.total_label.pack(padx=5, pady=5)
        self.win_label = tk.Label(stats_frame, text="勝場數: 0")
        self.win_label.pack(padx=5, pady=5)
        self.win_rate_label = tk.Label(stats_frame, text="勝率: 0%")
        self.win_rate_label.pack(padx=5, pady=5)
        self.first_label = tk.Label(stats_frame, text="先手勝率: 0%")
        self.first_label.pack(padx=5, pady=5)
        self.second_label = tk.Label(stats_frame, text="後手勝率: 0%")
        self.second_label.pack(padx=5, pady=5)
        self.coin_heads_label = tk.Label(stats_frame, text="正面率: 0%")
        self.coin_heads_label.pack(padx=5, pady=5)
        self.coin_tails_label = tk.Label(stats_frame, text="反面率: 0%")
        self.coin_tails_label.pack(padx=5, pady=5)
        self.g_win_label = tk.Label(stats_frame, text="先攻中G勝率: 0%")
        self.g_win_label.pack(padx=5, pady=5)
        self.expanded_win_label = tk.Label(stats_frame, text="先攻中G以外手坑勝率: 0%")
        self.expanded_win_label.pack(padx=5, pady=5)
        self.second_traps_win_label = tk.Label(stats_frame, text="後攻有手坑勝率: 0%")
        self.second_traps_win_label.pack(padx=5, pady=5)
        self.card_stuck_rate_label = tk.Label(stats_frame, text="卡手率: 0%")
        self.card_stuck_rate_label.pack(padx=5, pady=5)
        # 最長連勝與連敗顯示
        self.longest_win_label = tk.Label(stats_frame, text="")
        self.longest_win_label.pack(padx=5, pady=5)
        self.longest_loss_label = tk.Label(stats_frame, text="")
        self.longest_loss_label.pack(padx=5, pady=5)

    def manage_my_decks(self):
        if self.my_deck_window is not None and self.my_deck_window.winfo_exists():
            self.my_deck_window.lift()
        else:
            self.my_deck_window = DeckManagementWindow(
                self, self.my_decks, "我方卡組", self.update_my_deck_name
            )

    def manage_opp_decks(self):
        if self.opp_deck_window is not None and self.opp_deck_window.winfo_exists():
            self.opp_deck_window.lift()
        else:
            self.opp_deck_window = DeckManagementWindow(
                self, self.opp_decks, "對方卡組", self.update_opp_deck_name
            )

    def manage_season(self):
        if (
            hasattr(self, "season_window")
            and self.season_window is not None
            and self.season_window.winfo_exists()
        ):
            self.season_window.lift()
        else:
            self.season_window = SeasonManagementWindow(self)

    def update_my_deck_name(self, current_name=None, new_name=None):
        # 更新所有紀錄中使用舊名稱的紀錄
        # 根據模式更新對應的記錄集合
        if self.mode == "rank_mode":
            if current_name is not None and new_name is not None:
                for rec in self.records_rank:
                    if rec.get("my_deck") == current_name:
                        rec["my_deck"] = new_name
                self.my_decks = [
                    new_name if deck == current_name else deck for deck in self.my_decks
                ]
        elif self.mode == "dc_mode":
            if current_name is not None and new_name is not None:
                for rec in self.records_dc:
                    if rec.get("my_deck") == current_name:
                        rec["my_deck"] = new_name
                self.my_decks = [
                    new_name if deck == current_name else deck for deck in self.my_decks
                ]

        # 檢查統計下拉式選單是否為被修改的名稱
        if self.stats_deck_var.get() == current_name:
            self.stats_deck_var.set("全部")
        self.sort_descending = True
        # 刷新統計下拉選單的選項
        all_options = ["全部"] + self.my_decks
        self.stats_deck_option["values"] = all_options
        self.filter_option["values"] = all_options
        self.refresh_tree_records()

    def update_my_deck_comboboxes(self):
        self.my_deck_option["values"] = self.my_decks
        all_options = ["全部"] + self.my_decks
        self.stats_deck_option["values"] = all_options
        self.filter_option["values"] = all_options

    def update_opp_deck_name(self, current_name=None, new_name=None):
        # 如果成功修改對方卡組名稱，更新所有紀錄中對方卡組名稱
        if self.mode == "rank_mode":
            if current_name is not None and new_name is not None:
                for rec in self.records_rank:
                    if rec.get("opp_deck") == current_name:
                        rec["opp_deck"] = new_name
                self.opp_decks = [
                    new_name if deck == current_name else deck
                    for deck in self.opp_decks
                ]
        elif self.mode == "dc_mode":
            if current_name is not None and new_name is not None:
                for rec in self.records_dc:
                    if rec.get("opp_deck") == current_name:
                        rec["opp_deck"] = new_name
                self.opp_decks = [
                    new_name if deck == current_name else deck
                    for deck in self.opp_decks
                ]

        # 不論有無修改，都更新下拉選單與戰績列表
        self.sort_descending = True
        self.update_opp_deck_comboboxes()
        self.refresh_tree_records()

    def update_opp_deck_comboboxes(self):
        self.opp_deck_option["values"] = self.opp_decks

    def add_record(self):
        opp_deck_input = self.opp_deck_var_form.get()
        if opp_deck_input not in self.opp_decks:
            messagebox.showerror("錯誤", "請選擇有效的對方卡組！")
            return

        my_deck = self.my_deck_var_form.get()
        opp_deck = self.opp_deck_var_form.get()
        result = "勝" if self.result_win_var.get() else "敗"
        turn = "先手" if self.turn_first_var.get() else "後手"
        coin = "正面" if self.coin_heads_var.get() else "反面"
        forced_first = "是" if (coin == "反面" and turn == "先手") else "否"
        g = "是" if self.g_var.get() else "否"
        card_stuck = "是" if self.card_stuck_var.get() else "否"
        my_hand_traps = "有" if self.my_hand_traps_var.get() else "無"
        note = self.note_entry.get()

        # 取得手坑勾選結果：僅記錄被勾選的手坑
        selected_hand_traps = [
            trap for trap, var in self.hand_traps_vars.items() if var.get()
        ]
        expanded = "是" if selected_hand_traps else "否"

        if not my_deck or not opp_deck:
            messagebox.showerror("錯誤", "請選擇我方和對方的卡組!")
            return

            # 根據模式選擇賽季
        if self.mode == "rank_mode":
            season = self.current_season
        else:
            season = self.current_season_dc

        record = {
            "id": self.record_id_counter,
            "my_deck": my_deck,
            "opp_deck": opp_deck,
            "result": result,
            "turn": turn,
            "coin": coin,
            "forced_first": forced_first,
            "g": g,
            "expanded": expanded,
            "card_stuck": card_stuck,
            "my_hand_traps": my_hand_traps,
            "note": note,
            "season": season,
            "hand_traps": selected_hand_traps,
        }

        if self.mode == "rank_mode":
            record["rank"] = self.rank_var.get()
        elif self.mode == "dc_mode":
            points_str = self.points_var.get()
            try:
                # 嘗試轉換成數字，這裡以整數為例
                points = int(points_str)
            except ValueError:
                messagebox.showerror("輸入錯誤", "請輸入有效的整數作為積分！")
                return
            record["points"] = str(points)

        self.record_id_counter += 1  # 保證下次不會重複使用相同 id
        # 根據模式將記錄存入正確的集合
        if self.mode == "rank_mode":
            self.records_rank.append(record)
        elif self.mode == "dc_mode":
            self.records_dc.append(record)

        note_display = note
        if selected_hand_traps:
            note_display += " 中" + ",".join(selected_hand_traps)

        if self.mode == "rank_mode":
            self.tree.insert(
                "",
                0,
                iid=str(record["id"]),
                values=(
                    record["my_deck"],
                    record["opp_deck"],
                    record["result"],
                    record["turn"],
                    record["rank"],
                    record["coin"],
                    record["forced_first"],
                    record["g"],
                    record["expanded"],
                    record["card_stuck"],
                    record["my_hand_traps"],
                    note_display,
                    record["season"],
                ),
            )
        elif self.mode == "dc_mode":
            self.tree.insert(
                "",
                0,
                iid=str(record["id"]),
                values=(
                    record["my_deck"],
                    record["opp_deck"],
                    record["result"],
                    record["turn"],
                    record["points"],
                    record["coin"],
                    record["forced_first"],
                    record["g"],
                    record["expanded"],
                    record["card_stuck"],
                    record["my_hand_traps"],
                    note_display,
                    record["season"],
                ),
            )
        self.note_entry.delete(0, tk.END)
        self.g_var.set(False)
        self.card_stuck_var.set(False)
        self.my_hand_traps_var.set(False)
        for var in self.hand_traps_vars.values():
            var.set(False)

        if self.mode == "dc_rank":
            self.points_var.set("0")
        self.update_statistics()

    def delete_record(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要刪除的紀錄!")
            return

        confirm = messagebox.askyesno("確認刪除", "確定要刪除此紀錄嗎？")
        if not confirm:
            return

        record_id = int(selection[0])

        # 根據模式選擇正確的記錄集合
        if self.mode == "rank_mode":
            records = self.records_rank
        else:
            records = self.records_dc

        for i, rec in enumerate(records):
            if rec.get("id") == record_id:
                del records[i]
                break
        self.tree.delete(selection[0])
        self.update_statistics()

    def modify_record(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要修改的紀錄!")
            return
        record_id = int(selection[0])
        if (
            self.record_modify_window is not None
            and self.record_modify_window.winfo_exists()
        ):
            self.record_modify_window.lift()
            self.record_modify_window.focus_force()
            return
            # 根據模式選擇正確的記錄集合
        if self.mode == "rank_mode":
            records = self.records_rank
        else:
            records = self.records_dc

        for rec in records:
            if rec.get("id") == record_id:
                self.record_modify_window = RecordModifyWindow(self, rec)
                break

    def update_statistics(self):

        if self.mode == "rank_mode":
            records = self.records_rank
            current_season = self.current_season
        else:
            records = self.records_dc
            current_season = self.current_season_dc

        selected_deck = self.stats_deck_var.get()
        if selected_deck == "全部":
            filtered = [r for r in records if r.get("season") == current_season]
        else:
            filtered = [
                r
                for r in records
                if r.get("season") == current_season
                and r.get("my_deck") == selected_deck
            ]
        # 統計列表數據計算
        total = len(filtered)
        wins = len([r for r in filtered if r.get("result") == "勝"])
        win_rate = (wins / total * 100) if total > 0 else 0

        first_games = [r for r in filtered if r.get("turn") == "先手"]
        first_wins = len([r for r in first_games if r.get("result") == "勝"])
        first_rate = (first_wins / len(first_games) * 100) if first_games else 0

        second_games = [r for r in filtered if r.get("turn") == "後手"]
        second_wins = len([r for r in second_games if r.get("result") == "勝"])
        second_rate = (second_wins / len(second_games) * 100) if second_games else 0

        coin_heads = len([r for r in filtered if r.get("coin", "正面") == "正面"])
        coin_tails = len([r for r in filtered if r.get("coin", "正面") == "反面"])
        coin_heads_rate = (coin_heads / total * 100) if total > 0 else 0
        coin_tails_rate = (coin_tails / total * 100) if total > 0 else 0

        g_recs = [r for r in filtered if r.get("turn") == "先手" and r.get("g") == "是"]
        g_wins = len([r for r in g_recs if r.get("result") == "勝"])
        g_win_rate = (g_wins / len(g_recs) * 100) if g_recs else 0

        expanded_recs = [
            r
            for r in filtered
            if r.get("expanded", "否") == "是" and r.get("turn") == "先手"
        ]
        expanded_wins = len([r for r in expanded_recs if r.get("result") == "勝"])
        expanded_win_rate = (
            (expanded_wins / len(expanded_recs) * 100) if expanded_recs else 0
        )
        second_trap = [
            r
            for r in filtered
            if r.get("turn") == "後手" and r.get("my_hand_traps") == "有"
        ]
        second_traps_win = len([r for r in second_trap if r.get("result") == "勝"])
        second_traps_rate = (
            (second_traps_win / len(second_trap) * 100) if second_trap else 0
        )

        card_stuck = len([r for r in filtered if r.get("card_stuck", "否") == "是"])
        card_stuck_rate = (card_stuck / total * 100) if total > 0 else 0

        self.total_label.config(text=f"總場數: {total}")
        self.win_label.config(text=f"勝場數: {wins}")
        self.win_rate_label.config(text=f"勝率: {win_rate:.1f}%")
        self.first_label.config(text=f"先手勝率: {first_rate:.1f}%")
        self.second_label.config(text=f"後手勝率: {second_rate:.1f}%")
        self.coin_heads_label.config(text=f"正面率: {coin_heads_rate:.1f}%")
        self.coin_tails_label.config(text=f"反面率: {coin_tails_rate:.1f}%")
        self.g_win_label.config(text=f"先攻中G勝率: {g_win_rate:.1f}%")
        self.expanded_win_label.config(
            text=f"先攻中G以外手坑勝率: {expanded_win_rate:.1f}%"
        )
        self.second_traps_win_label.config(
            text=f"後攻有手坑勝率:{second_traps_rate:.1f}%"
        )
        self.card_stuck_rate_label.config(text=f"卡手率: {card_stuck_rate:.1f}%")

        # 計算連勝與連敗(全部)
        if selected_deck == "全部":
            longest_win, longest_loss = compute_streaks(filtered)
            self.longest_win_label.config(text=f"最長連勝: {longest_win}")
            self.longest_loss_label.config(text=f"最長連敗: {longest_loss}")
        else:
            self.longest_win_label.config(text="")
            self.longest_loss_label.config(text="")

    def filter_records(self):
        filter_val = self.filter_var.get()
        # 先從當前賽季的紀錄中篩選出符合條件的紀錄
        if self.mode == "rank_mode":
            records = self.records_rank
            current_season = self.current_season
        else:
            records = self.records_dc
            current_season = self.current_season_dc
        filtered_records = [r for r in records if r.get("season") == current_season]
        if filter_val != "全部":
            filtered_records = [
                r for r in filtered_records if r.get("my_deck") == filter_val
            ]
        # 依據 sort_descending 進行排序: id 越大表示越新
        sorted_records = sorted(
            filtered_records, key=lambda r: r["id"], reverse=self.sort_descending
        )
        # 清空 Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 插入排序後的資料
        for record in sorted_records:
            note_display = record.get("note", "")
            if "hand_traps" in record and record["hand_traps"]:
                note_display += " 中" + ", ".join(record["hand_traps"])

            if self.mode == "rank_mode":
                self.tree.insert(
                    "",
                    tk.END,
                    iid=str(record["id"]),
                    values=(
                        record.get("my_deck"),
                        record.get("opp_deck"),
                        record.get("result"),
                        record.get("turn"),
                        record.get("rank", "Diamond 5"),
                        record.get("coin", "正面"),
                        record.get("forced_first"),
                        record.get("g"),
                        record.get("expanded", "否"),
                        record.get("card_stuck", "否"),
                        record.get("my_hand_traps", "無"),
                        note_display,
                    ),
                )
            else:
                self.tree.insert(
                    "",
                    tk.END,
                    iid=str(record["id"]),
                    values=(
                        record.get("my_deck"),
                        record.get("opp_deck"),
                        record.get("result"),
                        record.get("turn"),
                        record.get("points"),
                        record.get("coin", "正面"),
                        record.get("forced_first"),
                        record.get("g"),
                        record.get("expanded", "否"),
                        record.get("card_stuck", "否"),
                        record.get("my_hand_traps", "無"),
                        note_display,
                    ),
                )
        self.update_statistics()

    # record_id重複檢查
    def ensure_unique_ids(self):
        if self.mode == "rank_mode":
            records = self.records_rank
        else:
            records = self.records_dc
        # 先找出所有有效的ID ，並取得最大值
        max_id = -1
        for record in records:
            rec_id = record.get("id")
            if isinstance(rec_id, int):
                max_id = max(max_id, rec_id)
        # 如果沒有任何 ID，設定 max_id 為 -1
        if max_id < 0:
            max_id = -1

        # 建立一個集合來追蹤已使用的 ID
        seen = set()
        for record in records:
            rec_id = record.get("id")
            # 若沒有 id、非整數或已重複，則重新分配一個新的 ID
            if not isinstance(rec_id, int) or rec_id in seen:
                max_id += 1
                record["id"] = max_id
            seen.add(record["id"])
        # 更新 record_id_counter 為最大ID的下一個數字
        self.record_id_counter = max_id + 1

    def load_tree_records(self):
        self.sort_descending = True
        # 設定按鈕顯示「由舊至新」（點擊後會變成舊至新）
        self.sort_button.config(text="由舊至新")
        # 清除現有項目，避免重複插入
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.ensure_unique_ids()
        # 根據目前模式選擇資料來源
        if self.mode == "rank_mode":
            records = self.records_rank
            current_season = self.current_season

        else:  # DC盃紀錄
            records = self.records_dc
            current_season = self.current_season_dc

        # 篩選出當前賽季的紀錄
        filtered_records = [r for r in records if r.get("season") == current_season]
        # 根據ID排序
        sorted_records = sorted(
            filtered_records, key=lambda r: r["id"], reverse=self.sort_descending
        )
        # 插入資料到Treeview
        for record in sorted_records:
            if self.mode == "rank_mode":
                self.tree.insert(
                    "",
                    tk.END,
                    iid=str(record["id"]),
                    values=(
                        record.get("my_deck"),
                        record.get("opp_deck"),
                        record.get("result"),
                        record.get("turn"),
                        record.get("rank", "Diamond 5"),
                        record.get("coin", "正面"),
                        record.get("forced_first"),
                        record.get("g"),
                        record.get("expanded", "否"),
                        record.get("card_stuck", "否"),
                        record.get("my_hand_traps", "無"),
                        record.get("note"),
                    ),
                )
            else:  # DC盃紀錄
                self.tree.insert(
                    "",
                    tk.END,
                    iid=str(record["id"]),
                    values=(
                        record.get("my_deck"),
                        record.get("opp_deck"),
                        record.get("result"),
                        record.get("turn"),
                        record.get("points", "0"),
                        record.get("coin", "正面"),
                        record.get("forced_first"),
                        record.get("g"),
                        record.get("expanded", "否"),
                        record.get("card_stuck", "否"),
                        record.get("my_hand_traps", "無"),
                        record.get("note"),
                    ),
                )
        self.update_statistics()

    def refresh_tree_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.load_tree_records()
        self.filter_records()

    def show_opp_deck_pie(self):
        if self.mode == "rank_mode":
            season_records = [
                r for r in self.records_rank if r.get("season") == self.current_season
            ]
        else:
            season_records = [
                r for r in self.records_dc if r.get("season") == self.current_season_dc
            ]

        if not season_records:
            messagebox.showinfo("提示", "當前賽季尚無資料")
            return
        # 檢查是否已有餅圖視窗存在
        if self.pie_chart_window is not None and self.pie_chart_window.winfo_exists():
            self.pie_chart_window.lift()
            self.pie_chart_window.focus_force()
            return
        self.pie_chart_window = OpponentDeckPieChart(self, season_records)

    def show_my_deck_pie(self):
        # 篩選出當前賽季的所有紀錄
        if self.mode == "rank_mode":
            season_records = [
                r for r in self.records_rank if r.get("season") == self.current_season
            ]
        else:
            season_records = [
                r for r in self.records_dc if r.get("season") == self.current_season_dc
            ]
        if not season_records:
            messagebox.showinfo("提示", "當前賽季尚無資料")
            return
        if (
            self.my_pie_chart_window is not None
            and self.my_pie_chart_window.winfo_exists()
        ):
            self.my_pie_chart_window.lift()
            self.my_pie_chart_window.focus_force()
            return
        self.my_pie_chart_window = MyDeckPieChart(self, season_records)

    # 關閉app時確保正確退出
    def on_close(self):
        data = load_data()
        if data is not None:
            save_data(
                self.my_decks,
                self.opp_decks,
                self.records_rank,
                self.current_season,
                self.records_dc,
                self.current_season_dc,
            )
        self.root.destroy()

        sys.exit(0)

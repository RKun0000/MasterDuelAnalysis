import tkinter as tk
from tkinter import ttk, messagebox
from tools import (
    center_window,
    rank_list,
    search_for_combobox,
    exclusive,
)


class RecordModifyWindow(tk.Toplevel):
    def __init__(self, app, record):
        super().__init__(app.root)
        self.app = app
        self.parent = app.root
        self.record = record
        self.withdraw()
        self.title("修改紀錄")
        self.geometry("450x450")
        self.update_idletasks()
        self.create_widgets()
        center_window(self, app.root)
        self.transient(self.parent)
        self.deiconify()
        self.lift(self.parent)
        self.parent.attributes("-disabled", True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TLabel", padding=(0, 0, 0, 0))
        style.configure("TCheckbutton", padding=(0, 0, 0, 0))

        group1 = tk.Frame(self)
        group1.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        tk.Label(group1, text="我方卡組：").pack(side=tk.LEFT, padx=(5, 2))
        self.my_deck_var_mod = tk.StringVar(value=self.record["my_deck"])
        self.my_deck_option_mod = ttk.Combobox(
            group1,
            textvariable=self.my_deck_var_mod,
            values=self.app.my_decks,
            state="readonly",
            width=15,
        )
        self.my_deck_option_mod.pack(side=tk.LEFT, padx=2)
        tk.Label(group1, text="對方卡組：").pack(side=tk.LEFT, padx=(15, 2))
        self.opp_deck_var_mod = tk.StringVar(value=self.record["opp_deck"])
        self.opp_deck_option_mod = ttk.Combobox(
            group1,
            textvariable=self.opp_deck_var_mod,
            values=self.app.opp_decks,
            state="normal",
            width=15,
        )
        self.opp_deck_option_mod.pack(side=tk.LEFT, padx=2)
        search_for_combobox(self.opp_deck_option_mod, self.app.opp_decks)

        group2 = tk.Frame(self)
        group2.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        if self.app.mode == "rank_mode":
            tk.Label(group2, text="段位：").pack(side=tk.LEFT, padx=(28, 2))
            self.rank_var_mod = tk.StringVar(value=self.record.get("rank", "Diamond 5"))
            rank_options = rank_list()
            self.rank_option_mod = ttk.Combobox(
                group2,
                textvariable=self.rank_var_mod,
                values=rank_options,
                state="readonly",
                width=15,
            )
            self.rank_option_mod.pack(side=tk.LEFT, padx=2)
        else:
            tk.Label(group2, text="積分：").pack(side=tk.LEFT, padx=(5, 2))
            self.points_var_mod = tk.StringVar(value=self.record.get("points", "0"))
            self.points_entry_mod = ttk.Entry(
                group2, textvariable=self.points_var_mod, width=15
            )
            self.points_entry_mod.pack(side=tk.LEFT, padx=2)

        group3 = tk.Frame(self)
        group3.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        tk.Label(group3, text="勝負：").pack(side=tk.LEFT, padx=(5, 2))
        win_frame = tk.Frame(group3)
        win_frame.pack(side=tk.LEFT)
        win_value = self.record.get("result", "勝")
        self.win_var_mod = tk.BooleanVar(value=(win_value == "勝"))
        self.lose_var_mod = tk.BooleanVar(value=(win_value == "敗"))
        self.win_cb_mod = tk.Checkbutton(
            win_frame,
            text="勝",
            variable=self.win_var_mod,
            command=lambda: exclusive(self.win_var_mod, self.lose_var_mod),
        )
        self.lose_cb_mod = tk.Checkbutton(
            win_frame,
            text="敗",
            variable=self.lose_var_mod,
            command=lambda: exclusive(self.lose_var_mod, self.win_var_mod),
        )
        self.win_cb_mod.pack(side=tk.LEFT, padx=2)
        self.lose_cb_mod.pack(side=tk.LEFT, padx=2)

        group4 = tk.Frame(self)
        group4.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="w")

        tk.Label(group4, text="硬幣：").pack(side=tk.LEFT, padx=(5, 2))
        coin_frame = tk.Frame(group4)
        coin_frame.pack(side=tk.LEFT)
        coin_val = self.record.get("coin", "正面")
        self.coin_heads_var = tk.BooleanVar(value=(coin_val == "正面"))
        self.coin_tails_var = tk.BooleanVar(value=(coin_val == "反面"))
        self.coin_heads_cb = tk.Checkbutton(
            coin_frame,
            text="正面",
            variable=self.coin_heads_var,
            command=lambda: exclusive(self.coin_heads_var, self.coin_tails_var),
        )
        self.coin_tails_cb = tk.Checkbutton(
            coin_frame,
            text="反面",
            variable=self.coin_tails_var,
            command=lambda: exclusive(self.coin_tails_var, self.coin_heads_var),
        )
        self.coin_heads_cb.pack(side=tk.LEFT, padx=2)
        self.coin_tails_cb.pack(side=tk.LEFT, padx=2)

        tk.Label(group4, text="先後手：").pack(side=tk.LEFT, padx=(15, 2))
        turn_frame = tk.Frame(group4)
        turn_frame.pack(side=tk.LEFT)
        turn_value = self.record.get("turn", "先手")
        self.first_var_mod = tk.BooleanVar(value=(turn_value == "先手"))
        self.second_var_mod = tk.BooleanVar(value=(turn_value == "後手"))
        self.first_cb_mod = tk.Checkbutton(
            turn_frame,
            text="先手",
            variable=self.first_var_mod,
            command=lambda: exclusive(self.first_var_mod, self.second_var_mod),
        )
        self.second_cb_mod = tk.Checkbutton(
            turn_frame,
            text="後手",
            variable=self.second_var_mod,
            command=lambda: exclusive(self.second_var_mod, self.first_var_mod),
        )
        self.first_cb_mod.pack(side=tk.LEFT, padx=2)
        self.second_cb_mod.pack(side=tk.LEFT, padx=2)

        group5 = tk.Frame(self)
        group5.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        tk.Label(group5, text="是否中G:").pack(side=tk.LEFT, padx=(5, 2))
        self.g_var_mod = tk.BooleanVar(value=(self.record["g"] == "是"))
        self.g_cb_mod = tk.Checkbutton(group5, variable=self.g_var_mod)
        self.g_cb_mod.pack(side=tk.LEFT, padx=2)

        group6 = tk.Frame(self)
        group6.grid(row=5, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        tk.Label(group6, text="中G以外手坑:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )

        self.hand_trap_vars_mod = {}
        hand_trap_frame = tk.Frame(group6)
        hand_trap_frame.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="w")
        for i, trap in enumerate(self.app.hand_traps):
            var = tk.BooleanVar(value=False)
            if "hand_traps" in self.record and trap in self.record["hand_traps"]:
                var.set(True)
            self.hand_trap_vars_mod[trap] = var
            cb = tk.Checkbutton(hand_trap_frame, text=trap, variable=var)

            cb.grid(row=i // 4, column=i % 4, padx=3, pady=3, sticky="w")

        group7 = tk.Frame(self)
        group7.grid(row=6, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        tk.Label(group7, text="是否卡手:").pack(side=tk.LEFT, padx=(5, 2))
        self.card_stuck_var_mod = tk.BooleanVar(
            value=(self.record.get("card_stuck", "否") == "是")
        )
        self.card_stuck_cb_mod = tk.Checkbutton(
            group7, variable=self.card_stuck_var_mod
        )
        self.card_stuck_cb_mod.pack(side=tk.LEFT, padx=2)

        tk.Label(group7, text="我方有無手坑").pack(side=tk.LEFT, padx=(5, 2))
        self.my_hand_traps_var_mod = tk.BooleanVar(
            value=(self.record.get("my_hand_traps", "無") == "有")
        )
        self.my_hand_traps_cb_mod = tk.Checkbutton(
            group7, variable=self.my_hand_traps_var_mod
        )
        self.my_hand_traps_cb_mod.pack(side=tk.LEFT, padx=(5, 2))

        group8 = tk.Frame(self)
        group8.grid(row=7, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        tk.Label(group8, text="是否被讓先:").pack(side=tk.LEFT, padx=(5, 2))
        computed_forced = (
            "是"
            if (
                self.record.get("coin", "正面") == "反面"
                and self.record["turn"] == "先手"
            )
            else "否"
        )
        self.forced_first_label_mod = tk.Label(group8, text=computed_forced)
        self.forced_first_label_mod.pack(side=tk.LEFT, padx=2)

        group9 = tk.Frame(self)
        group9.grid(row=8, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        tk.Label(group9, text="備註:").pack(side=tk.LEFT, padx=(5, 2))
        self.note_entry_mod = tk.Entry(group9, width=50)
        self.note_entry_mod.insert(0, self.record["note"])
        self.note_entry_mod.pack(side=tk.LEFT, padx=2)

        btn_save = tk.Button(self, text="確認修改", command=self.save_changes)
        btn_save.grid(row=9, column=0, columnspan=4, pady=10)

    def save_changes(self):
        opp_deck_input = self.opp_deck_var_mod.get()
        if opp_deck_input not in self.app.opp_decks:
            messagebox.showerror("錯誤", "請選擇有效的對方卡組！")
            self.attributes("-topmost", True)
            self.after(100, lambda: self.attributes("-topmost", False))
            return
        self.record["my_deck"] = self.my_deck_var_mod.get()
        self.record["opp_deck"] = self.opp_deck_var_mod.get()
        self.record["result"] = "勝" if self.win_var_mod.get() else "敗"
        self.record["turn"] = "先手" if self.first_var_mod.get() else "後手"
        if self.coin_heads_var.get():
            self.record["coin"] = "正面"
        elif self.coin_tails_var.get():
            self.record["coin"] = "反面"
        else:
            self.record["coin"] = "正面"  # 預設

        if self.app.mode == "rank_mode":
            self.record["rank"] = self.rank_var_mod.get()
        else:
            points_str = self.points_var_mod.get()
            try:
                points = int(points_str)
            except ValueError:
                messagebox.showerror("輸入錯誤", "請輸入有效的整數作為積分！")
                return
            self.record["points"] = str(points)

        self.record["forced_first"] = (
            "是"
            if (self.record["coin"] == "反面" and self.record["turn"] == "先手")
            else "否"
        )

        selected_traps = [
            trap for trap, var in self.hand_trap_vars_mod.items() if var.get()
        ]
        # 無論有無選取，都更新 hand_traps 欄位
        self.record["hand_traps"] = selected_traps
        # 如果有選取任何手坑，則 expanded 為 "是"，否則為 "否"
        self.record["expanded"] = "是" if selected_traps else "否"

        self.record["card_stuck"] = "是" if self.card_stuck_var_mod.get() else "否"
        self.record["my_hand_traps"] = (
            "有" if self.my_hand_traps_var_mod.get() else "無"
        )
        self.record["note"] = self.note_entry_mod.get()

        note_display = self.record["note"]

        if selected_traps:
            note_display += " 中" + ", ".join(selected_traps)

        self.app.tree.item(
            str(self.record["id"]),
            values=(
                self.record["my_deck"],
                self.record["opp_deck"],
                self.record["result"],
                self.record["turn"],
                self.record.get("rank", self.record.get("points", "")),
                self.record["coin"],
                self.record["forced_first"],
                self.record["g"],
                self.record["expanded"],
                self.record.get("card_stuck", "否"),
                self.record.get("my_hand_traps", "無"),
                note_display,
                # self.record.get("season", self.app.current_season),
            ),
        )
        self.app.update_statistics()
        self.on_close()

    def on_close(self):
        self.parent.attributes("-disabled", False)
        self.destroy()

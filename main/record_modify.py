import tkinter as tk
from tkinter import ttk, messagebox
from tools import center_window, rank_list


class RecordModifyWindow(tk.Toplevel):
    def __init__(self, app, record):
        super().__init__(app.root)
        self.app = app
        self.withdraw()
        self.record = record
        self.title("修改紀錄")
        self.geometry("400x450")
        self.update_idletasks()
        self.create_widgets()
        center_window(self, app.root)
        self.deiconify()  # 顯示視窗
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        tk.Label(self, text="我方卡組:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.my_deck_var_mod = tk.StringVar(value=self.record["my_deck"])
        self.my_deck_option_mod = ttk.Combobox(
            self,
            textvariable=self.my_deck_var_mod,
            values=self.app.my_decks,
            state="readonly",
            width=15,
        )
        self.my_deck_option_mod.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="對方卡組:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.opp_deck_var_mod = tk.StringVar(value=self.record["opp_deck"])
        self.opp_deck_option_mod = ttk.Combobox(
            self,
            textvariable=self.opp_deck_var_mod,
            values=self.app.opp_decks,
            state="readonly",
            width=15,
        )
        self.opp_deck_option_mod.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self, text="勝負:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.result_var_mod = tk.StringVar(value=self.record["result"])
        self.result_option_mod = ttk.Combobox(
            self,
            textvariable=self.result_var_mod,
            values=["勝", "敗"],
            state="readonly",
            width=15,
        )
        self.result_option_mod.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self, text="先後手:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.turn_var_mod = tk.StringVar(value=self.record["turn"])
        self.turn_option_mod = ttk.Combobox(
            self,
            textvariable=self.turn_var_mod,
            values=["先手", "後手"],
            state="readonly",
            width=15,
        )
        self.turn_option_mod.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self, text="硬幣:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.coin_var_mod = tk.StringVar(value=self.record.get("coin", "正面"))
        self.coin_option_mod = ttk.Combobox(
            self,
            textvariable=self.coin_var_mod,
            values=["正面", "反面"],
            state="readonly",
            width=15,
        )
        self.coin_option_mod.grid(row=4, column=1, padx=5, pady=5)

        if self.app.mode == "rank_mode":
            tk.Label(self, text="段位:").grid(
                row=5, column=0, padx=5, pady=5, sticky="e"
            )
            self.rank_var_mod = tk.StringVar(value=self.record.get("rank", "Diamond 5"))
            rank_options = rank_list()
            self.rank_option_mod = ttk.Combobox(
                self,
                textvariable=self.rank_var_mod,
                values=rank_options,
                state="readonly",
                width=15,
            )
            self.rank_option_mod.grid(row=5, column=1, padx=5, pady=5)
        else:
            tk.Label(self, text="積分:").grid(
                row=5, column=0, padx=5, pady=5, sticky="e"
            )
            self.points_var_mod = tk.StringVar(value=self.record.get("points", "0"))
            self.points_entry_mod = ttk.Entry(
                self,
                textvariable=self.points_var_mod,
                width=15,
            )
            self.points_entry_mod.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(self, text="是否中G:").grid(
            row=6, column=0, padx=5, pady=5, sticky="e"
        )
        self.g_var_mod = tk.BooleanVar(value=(self.record["g"] == "是"))
        self.g_cb_mod = tk.Checkbutton(self, variable=self.g_var_mod)
        self.g_cb_mod.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self, text="展開是否中G以外手坑:").grid(
            row=7, column=0, padx=5, pady=5, sticky="e"
        )
        self.expanded_var_mod = tk.BooleanVar(
            value=(self.record.get("expanded", "否") == "是")
        )
        self.expanded_cb_mod = tk.Checkbutton(self, variable=self.expanded_var_mod)
        self.expanded_cb_mod.grid(row=7, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self, text="是否卡手:").grid(
            row=8, column=0, padx=5, pady=5, sticky="e"
        )
        self.card_stuck_var_mod = tk.BooleanVar(
            value=(self.record.get("card_stuck", "否") == "是")
        )
        self.card_stuck_cb_mod = tk.Checkbutton(self, variable=self.card_stuck_var_mod)
        self.card_stuck_cb_mod.grid(row=8, column=1, padx=5, pady=5, sticky="w")

        # 自動計算是否被讓先
        computed_forced = (
            "是"
            if (
                self.record.get("coin", "正面") == "反面"
                and self.record["turn"] == "先手"
            )
            else "否"
        )
        tk.Label(self, text="是否被讓先:").grid(
            row=9, column=0, padx=5, pady=5, sticky="e"
        )
        self.forced_first_label_mod = tk.Label(self, text=computed_forced)
        self.forced_first_label_mod.grid(row=9, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self, text="備註:").grid(row=10, column=0, padx=5, pady=5, sticky="e")
        self.note_entry_mod = tk.Entry(self, width=30)
        self.note_entry_mod.insert(0, self.record["note"])
        self.note_entry_mod.grid(row=10, column=1, padx=5, pady=5)

        btn_save = tk.Button(self, text="確認修改", command=self.save_changes)
        btn_save.grid(row=11, column=0, columnspan=2, pady=10)

    def save_changes(self):
        self.record["my_deck"] = self.my_deck_var_mod.get()
        self.record["opp_deck"] = self.opp_deck_var_mod.get()
        self.record["result"] = self.result_var_mod.get()
        self.record["turn"] = self.turn_var_mod.get()
        self.record["coin"] = self.coin_var_mod.get()
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
        self.record["g"] = "是" if self.g_var_mod.get() else "否"
        self.record["expanded"] = "是" if self.expanded_var_mod.get() else "否"
        self.record["card_stuck"] = "是" if self.card_stuck_var_mod.get() else "否"
        self.record["note"] = self.note_entry_mod.get()
        if self.app.mode == "rank_mode":
            new_values = (
                self.record["my_deck"],
                self.record["opp_deck"],
                self.record["result"],
                self.record["turn"],
                self.record["rank"],
                self.record["coin"],
                self.record["forced_first"],
                self.record["g"],
                self.record["expanded"],
                self.record["card_stuck"],
                self.record["note"],
                self.record.get("season", self.app.current_season),
            )
        else:
            new_values = (
                self.record["my_deck"],
                self.record["opp_deck"],
                self.record["result"],
                self.record["turn"],
                self.record["points"],
                self.record["coin"],
                self.record["forced_first"],
                self.record["g"],
                self.record["expanded"],
                self.record["card_stuck"],
                self.record["note"],
                self.record.get("season", self.app.current_season_dc),
            )

        self.app.tree.item(str(self.record["id"]), values=new_values)
        self.app.update_statistics()
        self.destroy()

    def on_close(self):
        self.destroy()
        self.app.record_modify_window = None

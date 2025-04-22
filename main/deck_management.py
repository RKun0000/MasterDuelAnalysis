import tkinter as tk
from tkinter import messagebox, simpledialog
from tools import center_window
from edit_window import EditNameWindow


class DeckManagementWindow(tk.Toplevel):
    def __init__(self, app, deck_list, deck_type, update_callback):
        super().__init__(app.root)
        self.app = app
        self.parent = app.root
        self.withdraw()
        self.title(f"{deck_type}管理")
        self.deck_list = deck_list
        self.deck_type = deck_type
        self.update_callback = update_callback
        self.geometry("300x300")
        self.update_idletasks()
        self.create_widgets()
        center_window(self, app.root)
        self.transient(self.parent)
        self.deiconify()
        self.lift(self.parent)
        self.parent.attributes("-disabled", True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        for deck in self.deck_list:
            self.listbox.insert(tk.END, deck)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="新增", command=self.add_deck).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="修改", command=self.modify_deck).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="刪除", command=self.delete_deck).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="關閉", command=self.on_close).pack(
            side=tk.LEFT, padx=5
        )

    def add_deck(self):
        new_name_window = EditNameWindow(self, "新增卡組")
        new_deck = new_name_window.new_name
        if not new_deck:
            return
        if new_deck in self.deck_list:
            messagebox.showinfo("提示", "該卡組已存在!")
            self.lift()
            self.focus_force()
            return

        self.deck_list.append(new_deck)
        self.listbox.insert(tk.END, new_deck)
        self.update_callback()
        self.lift()
        self.focus_force()

    def modify_deck(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要修改的卡組!")
            self.attributes("-topmost", True)
            self.after(100, lambda: self.attributes("-topmost", False))
            return
        index = selection[0]
        current_name = self.deck_list[index]
        new_name_window = EditNameWindow(self, "修改卡組名稱", current_name)
        new_name = new_name_window.new_name
        if not new_name:
            return
        if new_name in self.deck_list:
            self.lift()
            self.focus_force()
            return
        self.deck_list[index] = new_name
        self.listbox.delete(index)
        self.listbox.insert(index, new_name)
        self.update_callback(current_name, new_name)
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

    def delete_deck(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要刪除的卡組!")
            return
        index = selection[0]
        deck_to_delete = self.deck_list[index]
        if self.deck_type == "我方卡組":
            used = any(
                rec.get("my_deck") == deck_to_delete for rec in self.app.records_rank
            ) or any(
                rec.get("my_deck") == deck_to_delete for rec in self.app.records_dc
            )
        else:
            used = any(
                rec.get("opp_deck") == deck_to_delete for rec in self.app.records_rank
            ) or any(
                rec.get("opp_deck") == deck_to_delete for rec in self.app.records_dc
            )
        if used:
            confirm = messagebox.askyesno(
                "確認刪除",
                f"該卡組 '{deck_to_delete}' 已在戰績紀錄中使用，確定要刪除嗎？\n（刪除後，該卡組相關的紀錄會被清除）",
            )
            if not confirm:
                self.attributes("-topmost", True)
                self.after(100, lambda: self.attributes("-topmost", False))
                return
        if self.deck_type == "我方卡組":
            self.app.records_rank = [
                r for r in self.app.records_rank if r.get("my_deck") != deck_to_delete
            ]
            self.app.records_dc = [
                r for r in self.app.records_dc if r.get("my_deck") != deck_to_delete
            ]
        else:
            self.app.records_rank = [
                r for r in self.app.records_rank if r.get("opp_deck") != deck_to_delete
            ]
            self.app.records_dc = [
                r for r in self.app.records_dc if r.get("opp_deck") != deck_to_delete
            ]

        # 若確認刪除，則從列表中刪除
        self.deck_list.pop(index)
        self.listbox.delete(index)
        self.update_callback(deck_to_delete, None)
        self.lift()
        self.focus_force()

    def on_close(self):
        self.parent.attributes("-disabled", False)
        self.destroy()


class SeasonManagementWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.parent = app.root
        self.withdraw()
        self.title("賽季管理")
        self.geometry("300x300")
        self.create_widgets()
        self.update_idletasks()
        center_window(self, app.root)
        self.transient(self.parent)
        self.deiconify()
        self.lift(self.parent)
        self.parent.attributes("-disabled", True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_current_data(self):
        """
        根據當前模式返回一個三元素元組：(records, current_season, set_current_season_function)
        若模式為 "rank_mode"，返回天梯資料；若為 "dc_mode"，返回 DC 盃資料。
        """
        if self.app.mode == "rank_mode":
            return (
                self.app.records_rank,
                self.app.current_season,
                self.set_current_season_rank,
            )
        else:
            return (
                self.app.records_dc,
                self.app.current_season_dc,
                self.set_current_season_dc,
            )

    def set_current_season_rank(self, new_season):
        self.app.current_season = new_season

    def set_current_season_dc(self, new_season):
        self.app.current_season_dc = new_season

    def create_widgets(self):
        tk.Label(self, text="賽季列表:").pack(pady=5)
        self.season_listbox = tk.Listbox(self)
        self.season_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.refresh_season_list()

        # 第一行：載入賽季與新增賽季
        btn_frame1 = tk.Frame(self)
        btn_frame1.pack(pady=5)
        tk.Button(btn_frame1, text="載入賽季", command=self.load_season).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame1, text="新增賽季", command=self.add_season).pack(
            side=tk.LEFT, padx=5
        )

        # 第二行：修改賽季名稱、刪除賽季資料、關閉視窗
        btn_frame2 = tk.Frame(self)
        btn_frame2.pack(pady=5)
        tk.Button(btn_frame2, text="修改賽季名稱", command=self.modify_season).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame2, text="刪除賽季資料", command=self.delete_season).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame2, text="關閉", command=self.on_close).pack(
            side=tk.LEFT, padx=5
        )

    def refresh_season_list(self):
        # 根據目前模式選擇對應的記錄與當前賽季
        records, current_season, _ = self.get_current_data()

        seasons = set()
        for rec in records:
            seasons.add(rec.get("season", current_season))
        seasons.add(current_season)
        seasons = sorted(list(seasons))
        self.season_listbox.delete(0, tk.END)
        for s in seasons:
            self.season_listbox.insert(tk.END, s)

        mode_str = "天梯" if self.app.mode == "rank_mode" else "DC盃"
        self.title(f"賽季管理 ({mode_str})")

    def modify_season(self):
        selection = self.season_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要修改的賽季！")
            self.attributes("-topmost", True)
            self.after(100, lambda: self.attributes("-topmost", False))
            return
        old_season = self.season_listbox.get(selection[0])
        new_season = simpledialog.askstring(
            "修改賽季名稱", "請輸入新的賽季名稱：", parent=self
        )
        if not new_season:
            return
        new_season = new_season.strip()
        # 取得目前模式下的資料
        records, current_season, set_current = self.get_current_data()
        # 檢查新名稱是否已存在
        existing = {rec.get("season", current_season) for rec in records}
        existing.add(current_season)
        if new_season in existing:
            messagebox.showinfo("提示", "該賽季已存在！")
            self.attributes("-topmost", True)
            self.after(100, lambda: self.attributes("-topmost", False))
            return
        # 更新所有紀錄中該賽季的名稱
        for rec in records:
            if rec.get("season") == old_season:
                rec["season"] = new_season
        # 如果目前載入的賽季就是被修改的，則更新
        if current_season == old_season:
            set_current(new_season)
            self.app.season_label.config(text=new_season)
        self.refresh_season_list()
        self.app.refresh_tree_records()
        messagebox.showinfo("提示", f"已將賽季名稱修改為 {new_season}")
        self.lift()

    def add_season(self):
        if self.app.mode == "rank_mode":
            prompt = "新增天梯賽季"
        else:
            prompt = "新增DC盃賽季"
        new_season = simpledialog.askstring(prompt, "請輸入新賽季名稱：", parent=self)
        if new_season:
            new_season = new_season.strip()
            records, current_season, set_current = self.get_current_data()
            # 取得所有現有的賽季
            existing_seasons = {rec.get("season", current_season) for rec in records}
            existing_seasons.add(current_season)
            if new_season in existing_seasons:
                messagebox.showinfo("提示", "該賽季已存在！")
                self.attributes("-topmost", True)
                self.after(100, lambda: self.attributes("-topmost", False))
                return
            else:
                # 新增賽季後，直接切換至該賽季
                set_current(new_season)
                if self.app.mode == "rank_mode":
                    self.app.season_label.config(text=new_season)
                else:
                    self.app.season_label.config(text=new_season)
                self.app.refresh_tree_records()
                self.refresh_season_list()
                messagebox.showinfo("提示", f"已新增並切換到賽季 {new_season}")
                self.lift()

    def load_season(self):
        selection = self.season_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要載入的賽季!")
            self.attributes("-topmost", True)
            self.after(100, lambda: self.attributes("-topmost", False))
            return
        season = self.season_listbox.get(selection[0])
        _, _, set_current = self.get_current_data()
        set_current(season)
        self.app.season_label.config(text=season)
        self.app.refresh_tree_records()
        messagebox.showinfo("提示", f"已載入賽季 {season}")
        self.lift()

    def delete_season(self):
        selection = self.season_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要刪除的賽季!")
            self.attributes("-topmost", True)
            self.after(100, lambda: self.attributes("-topmost", False))
            return

        season = self.season_listbox.get(selection[0])
        _, current_season, _ = self.get_current_data()

        if season == current_season:
            messagebox.showwarning("警告", "不能刪除目前載入的賽季!")
            self.attributes("-topmost", True)
            self.after(100, lambda: self.attributes("-topmost", False))
            return
        if messagebox.askyesno("確認", f"確定要刪除賽季 {season} 的所有資料嗎？"):
            if self.app.mode == "rank_mode":
                self.app.records_rank = [
                    r for r in self.app.records_rank if r.get("season") != season
                ]
            else:
                self.app.records_dc = [
                    r for r in self.app.records_dc if r.get("season") != season
                ]
            self.app.refresh_tree_records()
            self.refresh_season_list()
            messagebox.showinfo("提示", f"已刪除賽季 {season} 的資料")
            self.attributes("-topmost", True)
            self.after(100, lambda: self.attributes("-topmost", False))
        self.lift()

    # 關閉視窗時清除
    def on_close(self):
        self.parent.attributes("-disabled", False)
        self.destroy()

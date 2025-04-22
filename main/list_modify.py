from tkinter import messagebox, ttk
import tkinter as tk
import tkinter.font as tkFont
from edit_window import EditNameWindow
from tools import center_window


class TrapSettingWindow(tk.Toplevel):
    def __init__(self, app, hand_traps, update_callback):
        super().__init__(app.root)
        self.app = app
        self.hand_traps = hand_traps  # 手坑清單 (列表)
        self.update_callback = update_callback  # 更新主視窗手坑勾選框的回呼
        self.title("設定手坑")
        self.geometry("300x300")
        self.transient(app.root)
        app.root.attributes("-disabled", True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.hand_traps_listbox = tk.Listbox(self)
        self.hand_traps_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for trap in self.hand_traps:
            self.hand_traps_listbox.insert(tk.END, trap)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="新增", command=self.add_trap).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="修改", command=self.modify_trap).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="刪除", command=self.delete_trap).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="關閉", command=self.on_close).pack(
            side=tk.LEFT, padx=5
        )

        center_window(self, app.root)

    def add_trap(self):
        new_trap = EditNameWindow(self, "新增手坑").new_name
        if new_trap:
            if new_trap in self.hand_traps:
                messagebox.showinfo("提示", "該手坑已存在！")
                self.attributes("-topmost", True)
                self.after(100, lambda: self.attributes("-topmost", False))
                return
            self.hand_traps.append(new_trap)
            self.hand_traps_listbox.insert(tk.END, new_trap)
            self.update_callback()

    def modify_trap(self):
        selection = self.hand_traps_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要修改的手坑")
            self.attributes("-topmost", True)
            self.after(100, lambda: self.attributes("-topmost", False))
            return
        index = selection[0]
        current_trap = self.hand_traps[index]
        new_trap = EditNameWindow(self, "修改手坑", current_trap).new_name
        if new_trap:
            self.hand_traps[index] = new_trap
            self.hand_traps_listbox.delete(index)
            self.hand_traps_listbox.insert(index, new_trap)
            self.update_callback()

    def delete_trap(self):
        selection = self.hand_traps_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "請選擇要刪除的手坑")
            self.attributes("-topmost", True)
            self.after(100, lambda: self.attributes("-topmost", False))
            return
        index = selection[0]
        self.hand_traps.pop(index)
        self.hand_traps_listbox.delete(index)
        self.update_callback()

    def on_close(self):
        self.app.root.attributes("-disabled", False)
        self.destroy()


class TrapNoteWindow(tk.Toplevel):

    def __init__(self, app, records, decks):
        super().__init__(app.root)
        self.app = app
        self.records = records  # 當前賽季所有戰績記錄
        self.decks = decks  # 我方卡組清單
        self.title("本賽季吃坑札記")
        self.geometry("250x400")
        self.transient(app.root)
        self.grab_set()
        app.root.attributes("-disabled", True)
        self.create_widgets()
        center_window(self, app.root)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        self.custom_font = tkFont.Font(family="TaipeiSansTCBeta", size=12)

        used_decks = sorted(
            {rec.get("my_deck", "") for rec in self.records if rec.get("my_deck", "")}
        )
        deck_options = ["全部"] + used_decks
        tk.Label(self, text="選擇卡組：", font=self.custom_font).pack(padx=5, pady=5)
        self.deck_var = tk.StringVar(value="全部")
        self.deck_combo = ttk.Combobox(
            self,
            textvariable=self.deck_var,
            values=deck_options,
            state="readonly",
            font=self.custom_font,
        )
        self.deck_combo.pack(padx=5, pady=5)
        # 綁定下拉選單事件，當使用者選擇新項目時立即刷新
        self.deck_combo.bind("<<ComboboxSelected>>", lambda e: self.update_statistics())

        # 建立唯讀的多行文字區
        self.text = tk.Text(
            self, width=50, height=10, font=self.custom_font, state="disabled"
        )
        self.text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # 設定 tag 樣式
        self.text.tag_configure("trap", foreground="blue")
        self.text.tag_configure("win_rate", foreground="red")
        self.text.tag_configure("normal", foreground="black")

        # 初始更新統計資料
        self.update_statistics()

    def update_statistics(self):
        # 解除唯讀狀態以便更新
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)

        filtered = []
        selected_deck = self.deck_var.get()
        if selected_deck == "全部":
            filtered = self.records
        else:
            filtered = [r for r in self.records if r.get("my_deck") == selected_deck]

        games_num = len(filtered)
        games_win = len([r for r in filtered if r.get("result") == "勝"])
        games_win_rate = games_win / games_num * 100
        self.text.insert(tk.END, f"場次: {games_num},  勝率: {games_win_rate:.1f}%\n")

        traps = self.app.hand_traps

        # 逐一計算每個手坑的統計資訊
        for trap in traps:
            games = [r for r in filtered if trap in r.get("hand_traps", [])]
            count = len(games)
            if count > 0:
                wins = sum(1 for r in games if r.get("result") == "勝")
                win_rate = wins / count * 100
            else:
                win_rate = 0

            # 插入手坑名稱 (藍色)
            self.text.insert(tk.END, trap, "trap")
            # 插入冒號及空格 (預設黑色)
            self.text.insert(tk.END, ": ", "normal")
            # 插入場次資訊 (預設)
            self.text.insert(tk.END, f"{count} 場, 勝率 ", "normal")
            # 插入勝率 (紅色)
            self.text.insert(tk.END, f"{win_rate:.1f}%", "win_rate")
            self.text.insert(tk.END, "\n", "normal")

        # 更新完畢後重新設定唯讀
        self.text.config(state="disabled")

    def on_close(self):
        # 在關閉視窗前，先釋放主視窗的禁用狀態
        self.app.root.attributes("-disabled", False)
        self.destroy()

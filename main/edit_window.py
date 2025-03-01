import tkinter as tk
from tkinter import ttk, messagebox
from tools import center_window


class EditNameWindow(tk.Toplevel):
    def __init__(self, parent, title, current_name=""):
        super().__init__(parent)
        self.withdraw()  # 先隱藏視窗
        self.title(title)
        self.geometry("300x100")
        self.resizable(False, False)
        self.new_name = None  # 修改後的新名稱
        self.transient(parent)
        self.create_widgets(current_name)
        # 呼叫 update_idletasks() 以確保尺寸資訊已更新
        self.update_idletasks()
        center_window(self, parent)  # 置中視窗
        self.deiconify()  # 顯示視窗
        self.grab_set()  # 設置模態
        self.wait_window()

    def create_widgets(self, current_name):
        tk.Label(self, text="請輸入新的名稱：").pack(padx=10, pady=5)
        self.entry = tk.Entry(self)
        self.entry.pack(padx=10, pady=5, fill=tk.X)
        self.entry.insert(0, current_name)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="確定", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", command=self.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def on_ok(self):
        name = self.entry.get().strip()
        if not name:
            messagebox.showwarning("提示", "名稱不能為空")
        else:
            self.new_name = name
            self.destroy()

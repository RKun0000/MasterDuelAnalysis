import tkinter as tk
from tkinter import ttk, messagebox
from tools import center_window


class EditNameWindow(tk.Toplevel):
    def __init__(self, app, title, current_name=""):
        super().__init__(app)
        self.app = app
        self.withdraw()  # 先隱藏視窗
        self.title(title)
        self.geometry("300x100")
        self.resizable(False, False)
        self.new_name = None
        self.transient(app)
        app.attributes("-disabled", True)
        self.create_widgets(current_name)

        self.update_idletasks()
        center_window(self, app)  # 置中視窗
        self.deiconify()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.wait_window(self)

    def create_widgets(self, current_name):
        tk.Label(self, text="請輸入新的名稱：").pack(padx=10, pady=5)
        self.entry = tk.Entry(self)
        self.entry.pack(padx=10, pady=5, fill=tk.X)
        self.entry.insert(0, current_name)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="確定", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", command=self.on_close).pack(
            side=tk.LEFT, padx=5
        )

    def on_ok(self):
        name = self.entry.get().strip()
        if not name:
            messagebox.showwarning("提示", "名稱不能為空")
        else:
            self.new_name = name
            self.on_close()

    def on_close(self):
        self.app.attributes("-disabled", False)
        self.destroy()

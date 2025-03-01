import tkinter as tk
from ui import CardRecordApp

def get_initial_geometry(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # 自訂閾值，低解析度則使用固定尺寸
    if screen_width < 1200 or screen_height < 800:
        return "1024x720"
    else:
        # 較大解析度時最大化
        return None


if __name__ == "__main__":
    root = tk.Tk()
    init_geom = get_initial_geometry(root)
    if init_geom:
        root.geometry(init_geom)
    else:
        root.geometry("1300x800")
    root.resizable(True, True)

    app = CardRecordApp(root)
    root.mainloop()

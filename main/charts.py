import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tools import load_font
from tools import center_window, display_width, pad_to_width


class OpponentDeckPieChart(tk.Toplevel):
    def __init__(self, app, records):
        super().__init__(app.root)
        self.app = app
        self.parent = app.root
        self.withdraw()
        if app.mode == "rank_mode":
            self.title("本賽季對手卡組使用比例 (天梯)")
        else:
            self.title("本賽季對手卡組使用比例 (DC盃)")
        self.geometry("700x550")
        self.records = records  # 從主程式傳入當前賽季戰績紀錄
        self.current_filter = "全部"  # 預設下拉選單選項
        load_font()
        self.create_widgets()
        self.update_chart()
        center_window(self, app.root)
        self.transient(self.parent)
        self.deiconify()
        self.lift(self.parent)
        self.parent.attributes("-disabled", True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        # 上方區域：下拉選單與統計資訊
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        if self.app.mode == "rank_mode":
            tk.Label(top_frame, text="選擇段位:").pack(side=tk.LEFT)
            self.rank_filter_var = tk.StringVar(value="全部")
            self.rank_filter_option = ttk.Combobox(
                top_frame,
                textvariable=self.rank_filter_var,
                values=[
                    "全部",
                    "競等賽",
                    "Master",
                    "Diamond",
                    "Platinum",
                    "Gold",
                    "Silver",
                ],
                state="readonly",
                width=10,
            )
            self.rank_filter_option.pack(side=tk.LEFT, padx=5)
            self.rank_filter_option.bind(
                "<<ComboboxSelected>>", lambda e: self.on_filter_change()
            )
        # 若DC模式則不顯示下拉選單，所有紀錄皆統計
        self.stats_label = tk.Label(top_frame, text="")
        self.stats_label.pack(side=tk.LEFT, padx=10)
        # 圖形區域
        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

    def on_filter_change(self):
        self.current_filter = self.rank_filter_var.get()
        self.update_chart()

    def update_chart(self):
        # 篩選紀錄：依段位篩選
        if self.current_filter == "全部":
            filtered = self.records
        else:
            filtered = [
                r
                for r in self.records
                if r.get("rank", "").startswith(self.current_filter)
            ]
        # 統計資訊更新
        total = len(filtered)
        wins = len([r for r in filtered if r.get("result") == "勝"])
        win_rate = (wins / total * 100) if total > 0 else 0
        self.stats_label.config(text=f"場數: {total} 勝率: {win_rate:.1f}%")

        # 計算對手卡組出現次數
        opp_deck_counts = {}
        for r in filtered:
            deck = r.get("opp_deck", "未知")
            opp_deck_counts[deck] = opp_deck_counts.get(deck, 0) + 1

        # 依數值由大到小排序，並讓"未知"排在最後
        sorted_items = sorted(
            opp_deck_counts.items(),
            key=lambda x: (x[0] == "未知", -x[1] if x[0] != "未知" else 0),
        )
        # 如果存在"未知"，取出並暫存；剩下的項目另處理
        unknown = None
        items = []
        for item in sorted_items:
            if item[0] == "未知":
                unknown = item
            else:
                items.append(item)
        # 設定主要項目的數量上限，剩餘的卡組合併為"其他"
        THRESHOLD = 12
        if len(items) > THRESHOLD:
            main_items = items[:THRESHOLD]
            others_items = items[THRESHOLD:]
            others_count = sum(count for name, count in others_items)
            # 其他項目的圖表隱藏資訊：列出每個被合併項目的名稱與場次
            others_details = "\n".join(
                f"{name}: {count}" for name, count in others_items
            )

            main_items.append(("其他", others_count))
        else:
            main_items = items

        # 如果 "未知" 存在，則放在最後
        final_items = main_items[:]
        if unknown is not None:
            final_items.append(unknown)

        self.labels = [name for name, count in final_items]
        self.sizes = [count for name, count in final_items]
        # 如果有"其他" 項目，將其詳細資料存入一個屬性
        self.others_details = others_details if len(items) > THRESHOLD else None

        # 清除先前的餅圖
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()

        # 建立互動式餅圖
        self.fig, self.ax = plt.subplots()

        self.wedges, self.texts, self.autotexts = self.ax.pie(
            self.sizes,
            labels=self.labels,
            autopct="%1.1f%%",
            startangle=90,
            counterclock=False,
        )
        self.ax.axis("equal")
        # 為每個 wedge 設定 picker 支援
        for w in self.wedges:
            w.set_picker(5)
        # 建立隱藏的註解
        self.ann = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
        )
        self.ann.set_visible(False)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_move)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def on_move(self, event):
        if event.inaxes != self.ax:
            self.ann.set_visible(False)
            self.fig.canvas.draw_idle()
            return
        found = False
        # 遍歷每個 wedge
        for wedge, label, size in zip(self.wedges, self.labels, self.sizes):
            contains, _ = wedge.contains(event)
            if contains:
                # 如果這個 wedge 是 "其他"，顯示包含的卡組名稱與場次
                if label == "其他" and self.others_details:
                    data = [line.strip() for line in self.others_details.splitlines()]

                    # 2. 依每 3 筆一組分列（可依需求修改分組數）
                    rows = [data[i : i + 3] for i in range(0, len(data), 3)]
                    ncols = 3

                    # 3. 計算每一欄的最大顯示寬度
                    col_widths = [0] * ncols
                    for row in rows:
                        for i, item in enumerate(row):
                            col_widths[i] = max(col_widths[i], display_width(item))

                    # 如需額外間隔，可在每個欄位寬度上加上額外的寬度（例如加 5）
                    col_widths = [w + 5 for w in col_widths]

                    # 4. 使用 pad_to_width 依照各欄最大寬度對齊每一列
                    formatted_rows = []
                    for row in rows:
                        formatted_items = []
                        for i, item in enumerate(row):
                            formatted_items.append(pad_to_width(item, col_widths[i]))
                        formatted_rows.append("".join(formatted_items).rstrip())

                    # 5. 組合最終結果並加上標題 "其他:"
                    format_text = "其他:\n" + "\n".join(formatted_rows)
                    self.ann.set_text(format_text)
                else:
                    self.ann.set_text(f"{label}: {size} 場")
                self.ann.xy = (event.xdata, event.ydata)
                self.ann.set_visible(True)
                found = True
                break
        if not found:
            self.ann.set_visible(False)
        self.fig.canvas.draw_idle()

    # 關閉視窗時清除
    def on_close(self):
        self.parent.attributes("-disabled", False)
        self.destroy()


class MyDeckPieChart(tk.Toplevel):
    def __init__(self, app, records):
        super().__init__(app.root)
        self.app = app
        self.parent = app.root
        self.withdraw()
        if app.mode == "rank_mode":
            self.title("本賽季我方卡組使用比例 (天梯)")
        else:
            self.title("本賽季我方卡組使用比例 (DC盃)")
        self.geometry("700x550")
        self.records = records
        load_font()
        self.create_chart()
        center_window(self, app.root)
        self.transient(self.parent)
        self.deiconify()
        self.lift(self.parent)
        self.parent.attributes("-disabled", True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_chart(self):
        # 計算每個我方卡組的出場次數以及勝場數
        deck_counts = {}
        deck_wins = {}
        for rec in self.records:
            deck = rec.get("my_deck", "未知")
            deck_counts[deck] = deck_counts.get(deck, 0) + 1
            if rec.get("result") == "勝":
                deck_wins[deck] = deck_wins.get(deck, 0) + 1
            else:
                deck_wins.setdefault(deck, 0)
        # 儲存勝率資料供互動式餅圖使用
        self.deck_wins = deck_wins

        sorted_items = sorted(deck_counts.items(), key=lambda x: x[1], reverse=False)
        self.labels = [item[0] for item in sorted_items]
        self.sizes = [item[1] for item in sorted_items]

        total = sum(self.sizes)
        # 餅圖顯示內容
        display_labels = [
            f"{label} \n({(size/total*100):.1f}%)"
            for label, size in zip(self.labels, self.sizes)
        ]

        self.fig, self.ax = plt.subplots()
        # 建立互動式餅圖
        self.wedges, self.texts = self.ax.pie(
            self.sizes, labels=display_labels, startangle=90
        )
        self.ax.axis("equal")

        # 建立隱藏的標籤，用於顯示滑鼠提示資訊
        self.ann = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
        )
        self.ann.set_visible(False)

        self.fig.canvas.mpl_connect("motion_notify_event", self.on_move)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def on_move(self, event):
        if event.inaxes != self.ax:
            self.ann.set_visible(False)
            self.fig.canvas.draw_idle()
            return
        found = False
        # 遍歷每個 wedge，看游標是否位於其中
        for wedge, label, size in zip(self.wedges, self.labels, self.sizes):
            contains, _ = wedge.contains(event)
            if contains:
                # 從 self.deck_wins 取出該卡組的勝場數
                wins = self.deck_wins.get(label, 0)
                total_games = size
                win_rate = (wins / total_games * 100) if total_games > 0 else 0
                self.ann.set_text(
                    f"{label}\n場次: {total_games}\n勝率: {win_rate:.1f}%"
                )
                self.ann.xy = (event.xdata, event.ydata)
                self.ann.set_visible(True)
                found = True
                break
        if not found:
            self.ann.set_visible(False)
        self.fig.canvas.draw_idle()

    # 關閉視窗時清除
    def on_close(self):
        self.parent.attributes("-disabled", False)
        self.destroy()

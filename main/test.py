list1 = "apple:10\nbanana:5\ncherry:12\ndragonfruit:16\ngrape:136\nmango:78\ntie:12"
# 假設原始字串存放在 self.others_details
data = list1.splitlines()
lines = [line.strip() for line in data]

# 將資料以每 3 個為一組分組（不足 3 個也沒關係）
groups = [lines[i : i + 3] for i in range(0, len(lines), 3)]

# 計算各欄位的最大長度
num_columns = max(len(group) for group in groups)
col_widths = [0] * num_columns
for group in groups:
    for idx, item in enumerate(group):
        col_widths[idx] = max(col_widths[idx], len(item))

# 設定一個最小間隔（例如 5 個空白），這裡只作用於非最後一欄
min_gap = 5

# 根據各欄位的最大長度與最小間隔動態格式化每一列
formatted_rows = []
for group in groups:
    row_items = []
    for idx, item in enumerate(group):
        # 若非最後一欄則在原欄位寬度上加上最小間隔
        if idx < len(group) - 1:
            row_items.append(item.ljust(col_widths[idx] + min_gap))
        else:
            row_items.append(item)
    formatted_rows.append("".join(row_items))

# 最後組合成最終字串並存入變數，前面加上標題 "其他:"
format_text = "其他:\n" + "\n".join(formatted_rows)
print(format_text)

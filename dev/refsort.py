import tkinter as tk
from tkinter import scrolledtext, messagebox
import re


def sort_references():
    """按参考文献的序号进行数字排序"""
    input_text = text_input.get("1.0", tk.END).strip()

    if not input_text:
        messagebox.showwarning("警告", "请输入参考文献条目")
        return

    # 按行分割，并过滤空行
    lines = [line.strip() for line in input_text.split('\n') if line.strip()]

    if not lines:
        messagebox.showwarning("警告", "没有有效的参考文献条目")
        return

    # 提取序号函数
    def extract_number(line):
        match = re.search(r'\[(\d+)\]', line)
        if match:
            return int(match.group(1))
        return float('inf')  # 没有序号的排到最后

    # 按数字序号排序
    sorted_lines = sorted(lines, key=extract_number)

    # 更新输出区域
    text_output.delete("1.0", tk.END)
    text_output.insert("1.0", '\n'.join(sorted_lines))

    # 显示统计信息
    label_info.config(text=f"共 {len(sorted_lines)} 条参考文献")


def clear_all():
    """清空所有文本框"""
    text_input.delete("1.0", tk.END)
    text_output.delete("1.0", tk.END)
    label_info.config(text="")


# 创建主窗口
root = tk.Tk()
root.title("参考文献排序工具 - 按序号排序")
root.geometry("700x500")

# 设置字体
font_style = ("微软雅黑", 10)

# 输入区域标签
label_input = tk.Label(root, text="输入参考文献（每行一条，格式如 [1] 内容）：", font=font_style)
label_input.pack(pady=(10, 5))

# 输入文本框
text_input = scrolledtext.ScrolledText(root, height=10, font=font_style)
text_input.pack(fill=tk.BOTH, padx=10, pady=(0, 10), expand=True)

# 按钮框架
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

# 排序按钮
btn_sort = tk.Button(button_frame, text="排序", command=sort_references,
                     bg="#4CAF50", fg="white", font=font_style, width=10)
btn_sort.pack(side=tk.LEFT, padx=5)

# 清空按钮
btn_clear = tk.Button(button_frame, text="清空", command=clear_all,
                      bg="#f44336", fg="white", font=font_style, width=10)
btn_clear.pack(side=tk.LEFT, padx=5)

# 输出区域标签
label_output = tk.Label(root, text="排序结果：", font=font_style)
label_output.pack(pady=(10, 5))

# 输出文本框（只读）
text_output = scrolledtext.ScrolledText(root, height=10, font=font_style,
                                        fg="#2E7D32", bg="#F5F5F5")
text_output.pack(fill=tk.BOTH, padx=10, pady=(0, 10), expand=True)

# 信息标签
label_info = tk.Label(root, text="", font=("微软雅黑", 9), fg="blue")
label_info.pack(pady=5)

# 运行主循环
root.mainloop()
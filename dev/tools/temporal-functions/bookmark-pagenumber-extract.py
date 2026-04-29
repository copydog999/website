#!/usr/bin/env python3
"""
PDF书签提取工具 - 带图形界面
提取PDF文件的顶层书签和对应页码
"""

import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import csv
from datetime import datetime


class PDFBookmarkExtractor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF书签提取工具 v1.0")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # 设置图标（如果有的话）
        try:
            self.root.iconbitmap('bookmark.ico')
        except:
            pass

        self.setup_ui()
        self.pdf_path = None

    def setup_ui(self):
        """设置用户界面"""
        # 顶部框架 - 文件选择
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="PDF文件:").pack(side=tk.LEFT)

        self.file_label = ttk.Label(top_frame, text="未选择文件", foreground="gray", width=50)
        self.file_label.pack(side=tk.LEFT, padx=10)

        ttk.Button(top_frame, text="选择文件", command=self.select_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="刷新", command=self.refresh_file).pack(side=tk.LEFT)

        # 信息显示框架
        info_frame = ttk.Frame(self.root, padding="5")
        info_frame.pack(fill=tk.X)

        self.info_label = ttk.Label(info_frame, text="")
        self.info_label.pack()

        # 结果显示区域
        result_frame = ttk.LabelFrame(self.root, text="书签列表", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建带滚动条的文本框
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            height=20
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # 底部按钮框架
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="导出到CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="导出到TXT", command=self.export_txt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="复制到剪贴板", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空结果", command=self.clear_results).pack(side=tk.LEFT, padx=5)

        # 状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 右键菜单
        self.create_context_menu()

    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="复制选中内容", command=self.copy_selected)
        self.context_menu.add_command(label="全选", command=self.select_all)

        # 绑定右键事件
        self.text_area.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """显示右键菜单"""
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def select_file(self):
        """选择PDF文件"""
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[
                ("PDF文件", "*.pdf"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.pdf_path = file_path
            self.file_label.config(
                text=os.path.basename(file_path),
                foreground="black"
            )
            self.extract_bookmarks()

    def refresh_file(self):
        """刷新当前文件"""
        if self.pdf_path and os.path.exists(self.pdf_path):
            self.extract_bookmarks()
        else:
            messagebox.showwarning("警告", "文件不存在或未选择文件")

    def extract_bookmarks(self):
        """提取书签"""
        if not self.pdf_path:
            return

        try:
            self.status_bar.config(text="正在提取书签...")
            self.root.update()

            doc = fitz.open(self.pdf_path)
            toc = doc.get_toc()  # 获取目录

            # 筛选顶层书签（层级为1）
            top_level_bookmarks = [item for item in toc if item[0] == 1]

            if not top_level_bookmarks:
                messagebox.showinfo("提示", "未找到顶层书签")
                self.info_label.config(text="未找到书签")
                self.text_area.delete(1.0, tk.END)
                return

            # 显示信息
            total_pages = doc.page_count
            self.info_label.config(
                text=f"文件: {os.path.basename(self.pdf_path)} | "
                     f"总页数: {total_pages} | "
                     f"顶层书签数: {len(top_level_bookmarks)}"
            )

            # 在文本区域显示结果
            self.text_area.delete(1.0, tk.END)

            # 添加标题
            title = f"PDF书签提取结果\n"
            title += f"文件: {os.path.basename(self.pdf_path)}\n"
            title += f"提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            title += f"总页数: {total_pages} | 顶层书签数: {len(top_level_bookmarks)}\n"
            title += "=" * 60 + "\n\n"

            self.text_area.insert(tk.END, title)

            # 添加书签列表
            result_text = f"{'序号':<6} {'页码':<8} {'书签名'}\n"
            result_text += "-" * 80 + "\n"

            for i, item in enumerate(top_level_bookmarks, 1):
                level, name, page = item
                # 页码在PyMuPDF中是从1开始的逻辑页码
                result_text += f"{i:<6} {page:<8} {name}\n"

            self.text_area.insert(tk.END, result_text)

            # 保存数据供导出使用
            self.bookmarks_data = top_level_bookmarks

            doc.close()

            self.status_bar.config(text=f"成功提取 {len(top_level_bookmarks)} 个书签")

        except Exception as e:
            messagebox.showerror("错误", f"提取书签时出错:\n{str(e)}")
            self.status_bar.config(text="提取失败")

    def export_csv(self):
        """导出到CSV文件"""
        if not hasattr(self, 'bookmarks_data') or not self.bookmarks_data:
            messagebox.showwarning("警告", "没有可导出的数据")
            return

        file_path = filedialog.asksaveasfilename(
            title="保存CSV文件",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(['序号', '层级', '书签名', '页码'])

                    for i, item in enumerate(self.bookmarks_data, 1):
                        level, name, page = item
                        writer.writerow([i, level, name, page])

                messagebox.showinfo("成功", f"已导出到:\n{file_path}")
                self.status_bar.config(text=f"已导出到 {os.path.basename(file_path)}")

            except Exception as e:
                messagebox.showerror("错误", f"导出CSV时出错:\n{str(e)}")

    def export_txt(self):
        """导出到文本文件"""
        if not hasattr(self, 'bookmarks_data') or not self.bookmarks_data:
            messagebox.showwarning("警告", "没有可导出的数据")
            return

        file_path = filedialog.asksaveasfilename(
            title="保存文本文件",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_area.get(1.0, tk.END))

                messagebox.showinfo("成功", f"已导出到:\n{file_path}")
                self.status_bar.config(text=f"已导出到 {os.path.basename(file_path)}")

            except Exception as e:
                messagebox.showerror("错误", f"导出TXT时出错:\n{str(e)}")

    def copy_to_clipboard(self):
        """复制到剪贴板"""
        try:
            text = self.text_area.get(1.0, tk.END)
            if text.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(text.strip())
                self.status_bar.config(text="已复制到剪贴板")
            else:
                messagebox.showwarning("警告", "没有内容可复制")
        except Exception as e:
            messagebox.showerror("错误", f"复制时出错:\n{str(e)}")

    def copy_selected(self):
        """复制选中内容"""
        try:
            selected = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected)
        except:
            pass

    def select_all(self):
        """全选"""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)

    def clear_results(self):
        """清空结果"""
        self.text_area.delete(1.0, tk.END)
        self.info_label.config(text="")
        self.status_bar.config(text="已清空")

    def run(self):
        """运行应用程序"""
        self.root.mainloop()


def main():
    """主函数"""
    app = PDFBookmarkExtractor()
    app.run()


if __name__ == "__main__":
    # 检查依赖
    try:
        import fitz
    except ImportError:
        print("错误: 需要安装 PyMuPDF 库")
        print("请运行: pip install PyMuPDF")
        input("按回车键退出...")
        exit(1)

    main()
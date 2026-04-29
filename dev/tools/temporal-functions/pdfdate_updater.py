#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF文件日期更新工具 - GUI版本
扫描articles文件夹下的PDF文件，提取最后修改日期，
匹配nowbase.json中的记录，并提供GUI界面进行更新确认。
"""

import os
import json
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
from pathlib import Path
from difflib import SequenceMatcher
import re
import shutil
from tkinter import filedialog

# 配置路径
BASE_DIR = Path(__file__).parent.parent  # 项目根目录
ARTICLES_DIR = BASE_DIR / "articles"
NOWBASE_PATH = BASE_DIR / "database" / "data" / "nowbase.json"


class PDFDateUpdaterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF文件日期更新工具")
        self.root.geometry("1000x700")

        # 设置样式
        self.root.configure(bg='#f0f0f0')

        # 数据变量
        self.nowbase_data = None
        self.pdf_files = []
        self.current_index = 0
        self.current_pdf = None
        self.current_match = None
        self.updated_count = 0
        self.skipped_count = 0
        self.not_found_count = 0

        # 创建UI
        self.create_widgets()

        # 初始化数据
        self.load_data()

    def create_widgets(self):
        """创建界面组件"""

        # 顶部标题
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="📄 PDF文件日期更新工具",
            font=('微软雅黑', 16, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=15)

        # 主内容区域
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 左侧面板 - 文件列表
        left_frame = tk.Frame(main_frame, bg='white', relief=tk.GROOVE, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        left_header = tk.Label(
            left_frame,
            text="📋 PDF文件列表",
            font=('微软雅黑', 12, 'bold'),
            bg='#3498db',
            fg='white',
            pady=5
        )
        left_header.pack(fill=tk.X)

        # 文件列表
        list_frame = tk.Frame(left_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建带滚动条的列表
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=('微软雅黑', 9),
            selectmode=tk.SINGLE,
            bg='#f8f9fa',
            relief=tk.FLAT
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.file_listbox.yview)

        # 绑定选择事件
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)

        # 右侧面板 - 详细信息
        right_frame = tk.Frame(main_frame, bg='white', relief=tk.GROOVE, bd=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        right_header = tk.Label(
            right_frame,
            text="🔍 详细信息",
            font=('微软雅黑', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            pady=5
        )
        right_header.pack(fill=tk.X)

        # 信息显示区域
        info_frame = tk.Frame(right_frame, bg='white')
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # PDF信息
        pdf_frame = tk.LabelFrame(info_frame, text="📄 PDF文件信息", font=('微软雅黑', 10, 'bold'), bg='white')
        pdf_frame.pack(fill=tk.X, pady=(0, 10))

        self.pdf_info_text = scrolledtext.ScrolledText(
            pdf_frame,
            height=6,
            font=('微软雅黑', 9),
            wrap=tk.WORD,
            bg='#f8f9fa',
            relief=tk.FLAT
        )
        self.pdf_info_text.pack(fill=tk.X, padx=5, pady=5)

        # JSON信息
        json_frame = tk.LabelFrame(info_frame, text="📚 JSON对象信息", font=('微软雅黑', 10, 'bold'), bg='white')
        json_frame.pack(fill=tk.X, pady=(0, 10))

        self.json_info_text = scrolledtext.ScrolledText(
            json_frame,
            height=10,
            font=('微软雅黑', 9),
            wrap=tk.WORD,
            bg='#f8f9fa',
            relief=tk.FLAT
        )
        self.json_info_text.pack(fill=tk.X, padx=5, pady=5)

        # 操作按钮
        button_frame = tk.Frame(info_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=10)

        self.btn_update = tk.Button(
            button_frame,
            text="✅ 更新日期",
            command=self.update_date,
            bg='#27ae60',
            fg='white',
            font=('微软雅黑', 10, 'bold'),
            padx=20,
            pady=5,
            state=tk.DISABLED
        )
        self.btn_update.pack(side=tk.LEFT, padx=5)

        self.btn_skip = tk.Button(
            button_frame,
            text="⏭️ 跳过",
            command=self.skip_file,
            bg='#f39c12',
            fg='white',
            font=('微软雅黑', 10, 'bold'),
            padx=20,
            pady=5,
            state=tk.DISABLED
        )
        self.btn_skip.pack(side=tk.LEFT, padx=5)

        self.btn_next = tk.Button(
            button_frame,
            text="⏩ 下一个",
            command=self.next_file,
            bg='#3498db',
            fg='white',
            font=('微软雅黑', 10, 'bold'),
            padx=20,
            pady=5,
            state=tk.DISABLED
        )
        self.btn_next.pack(side=tk.LEFT, padx=5)

        # 底部状态栏
        status_frame = tk.Frame(self.root, bg='#34495e', height=40)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text="就绪",
            font=('微软雅黑', 10),
            fg='white',
            bg='#34495e'
        )
        self.status_label.pack(side=tk.LEFT, padx=20, pady=10)

        self.stats_label = tk.Label(
            status_frame,
            text="已更新: 0 | 已跳过: 0 | 未匹配: 0",
            font=('微软雅黑', 10),
            fg='white',
            bg='#34495e'
        )
        self.stats_label.pack(side=tk.RIGHT, padx=20, pady=10)

    def load_data(self):
        """加载数据"""
        self.status_label.config(text="正在加载数据...")
        self.root.update()

        # 加载nowbase.json
        self.nowbase_data = self.load_nowbase()
        if self.nowbase_data is None:
            return

        # 获取所有PDF文件
        self.pdf_files = self.get_pdf_files()

        # 更新文件列表
        self.update_file_list()

        self.status_label.config(text=f"已加载 {len(self.pdf_files)} 个PDF文件")

    def load_nowbase(self):
        """加载nowbase.json文件"""
        if not NOWBASE_PATH.exists():
            messagebox.showerror("错误", f"找不到文件：{NOWBASE_PATH}")
            return None

        try:
            with open(NOWBASE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"加载JSON文件失败：{e}")
            return None

    def get_pdf_files(self):
        """递归扫描articles目录下的所有PDF文件"""
        pdf_files = []
        if not ARTICLES_DIR.exists():
            messagebox.showerror("错误", f"找不到目录：{ARTICLES_DIR}")
            return pdf_files

        for root, dirs, files in os.walk(ARTICLES_DIR):
            for file in files:
                if file.lower().endswith('.pdf'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, ARTICLES_DIR)

                    # 获取文件修改日期
                    file_date = self.get_file_modify_date(full_path)

                    pdf_files.append({
                        'path': full_path,
                        'filename': file,
                        'rel_path': rel_path,
                        'date_info': file_date
                    })

        return pdf_files

    def get_file_modify_date(self, file_path):
        """获取文件的最后修改日期"""
        timestamp = os.path.getmtime(file_path)
        modify_date = datetime.datetime.fromtimestamp(timestamp)
        return {
            'timestamp': timestamp,
            'date_str': modify_date.strftime('%Y-%m-%d %H:%M:%S'),
            'iso_date': modify_date.isoformat()
        }

    def update_file_list(self):
        """更新文件列表"""
        self.file_listbox.delete(0, tk.END)
        for pdf in self.pdf_files:
            display_text = f"{pdf['filename']}"
            self.file_listbox.insert(tk.END, display_text)

    def on_file_select(self, event):
        """文件选择事件"""
        selection = self.file_listbox.curselection()
        if selection:
            self.current_index = selection[0]
            self.display_file_info(self.current_index)

    def display_file_info(self, index):
        """显示文件信息"""
        self.current_pdf = self.pdf_files[index]

        # 查找匹配的JSON对象
        self.current_match = self.find_matching_article(
            self.current_pdf['filename'],
            self.nowbase_data
        )

        # 显示PDF信息
        pdf_info = f"文件名：{self.current_pdf['filename']}\n"
        pdf_info += f"路径：{self.current_pdf['rel_path']}\n"
        pdf_info += f"最后修改：{self.current_pdf['date_info']['date_str']}\n"

        self.pdf_info_text.delete(1.0, tk.END)
        self.pdf_info_text.insert(1.0, pdf_info)

        # 显示JSON信息
        if self.current_match:
            article = self.current_match['article']
            json_info = f"标题：{article.get('title', 'N/A')}\n"
            json_info += f"作者：{', '.join(article.get('authors', ['N/A']))}\n"
            json_info += f"期刊：{article.get('issue', 'N/A')}\n"
            json_info += f"DOI：{article.get('nowbasedoi', 'N/A')}\n"
            json_info += f"匹配度：{self.current_match['similarity']:.2%}\n"

            if 'published' in article:
                json_info += f"现有发布日期：{article['published']}\n"

            self.json_info_text.delete(1.0, tk.END)
            self.json_info_text.insert(1.0, json_info)

            # 启用按钮
            self.btn_update.config(state=tk.NORMAL)
            self.btn_skip.config(state=tk.NORMAL)
            self.btn_next.config(state=tk.NORMAL)
        else:
            self.json_info_text.delete(1.0, tk.END)
            self.json_info_text.insert(1.0, "⚠️ 未找到匹配的JSON对象")

            # 只启用跳过和下一个按钮
            self.btn_update.config(state=tk.DISABLED)
            self.btn_skip.config(state=tk.NORMAL)
            self.btn_next.config(state=tk.NORMAL)

            self.not_found_count += 1
            self.update_stats()

    def normalize_filename(self, filename):
        """标准化文件名，用于模糊匹配"""
        # 移除.pdf后缀
        name = filename[:-4] if filename.lower().endswith('.pdf') else filename

        # 移除常见的特殊字符
        name = re.sub(r'[：:：:：\s\-_]+', ' ', name)

        # 移除空格
        name = name.strip()

        return name

    def calculate_similarity(self, str1, str2):
        """计算两个字符串的相似度"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def find_matching_article(self, pdf_filename, nowbase_data):
        """根据PDF文件名匹配nowbase中的记录"""
        pdf_norm = self.normalize_filename(pdf_filename)
        matches = []

        for article in nowbase_data:
            title = article.get('title', '')
            if not title:
                continue

            # 计算相似度
            similarity = self.calculate_similarity(pdf_norm, title)

            # 如果标题包含文件名或文件名包含标题
            if similarity > 0.6:  # 相似度阈值
                matches.append({
                    'article': article,
                    'similarity': similarity,
                    'title': title
                })

        # 按相似度排序
        matches.sort(key=lambda x: x['similarity'], reverse=True)

        return matches[0] if matches else None

    def update_date(self):
        """更新日期"""
        if not self.current_match:
            return

        article = self.current_match['article']
        article['published'] = self.current_pdf['date_info']['iso_date']

        self.updated_count += 1
        self.update_stats()

        messagebox.showinfo("成功", f"已更新发布日期：{article['published']}")

        # 重新显示信息
        self.display_file_info(self.current_index)

    def skip_file(self):
        """跳过当前文件"""
        self.skipped_count += 1
        self.update_stats()
        self.next_file()

    def next_file(self):
        """下一个文件"""
        if self.current_index < len(self.pdf_files) - 1:
            self.current_index += 1
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(self.current_index)
            self.file_listbox.see(self.current_index)
            self.display_file_info(self.current_index)
        else:
            # 所有文件处理完成
            self.show_completion()

    def update_stats(self):
        """更新统计信息"""
        self.stats_label.config(
            text=f"已更新: {self.updated_count} | 已跳过: {self.skipped_count} | 未匹配: {self.not_found_count}"
        )

    def show_completion(self):
        """显示完成信息"""
        # 询问是否保存
        if messagebox.askyesno("完成",
                               f"所有文件处理完成！\n\n已更新：{self.updated_count}\n已跳过：{self.skipped_count}\n未匹配：{self.not_found_count}\n\n是否保存修改？"):
            self.save_nowbase()

        self.status_label.config(text="处理完成")

    def save_nowbase(self):
        """保存nowbase.json文件"""
        try:
            # 创建备份
            backup_path = NOWBASE_PATH.with_suffix('.json.bak')
            shutil.copy2(NOWBASE_PATH, backup_path)

            # 保存新文件
            with open(NOWBASE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.nowbase_data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("成功", f"已保存到：{NOWBASE_PATH}\n备份已创建：{backup_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{e}")


def main():
    root = tk.Tk()
    app = PDFDateUpdaterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
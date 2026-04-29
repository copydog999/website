#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电子游戏科学与技术期刊 - 通知公告页面更新工具
用于自动更新 database/notification.json 文件中的通知公告信息
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import re
from datetime import datetime
from pathlib import Path
import json


class NotificationUpdaterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JOEST 通知公告更新工具")
        self.root.geometry("1200x700")
        
        # JSON文件路径 - 从 tools 目录向上两级到项目根目录
        script_dir = Path(__file__).parent
        self.json_file_path = str(script_dir.parent.parent / "database" / "data" / "notification.json")
        
        # 当前选中的通知ID
        self.current_notification_id = None
        
        # 创建界面
        self.create_widgets()
        self.load_notifications_list()
        
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(11, weight=1)  # 日志区域权重
        
        # 标题
        title_label = ttk.Label(main_frame, text="通知公告更新工具", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=6, pady=(0, 20))
        
        # 通知列表
        ttk.Label(main_frame, text="通知列表:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.notifications_listbox = tk.Listbox(main_frame, height=10)
        self.notifications_listbox.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        self.notifications_listbox.bind('<<ListboxSelect>>', self.on_notification_select)
        
        # 滚动条
        list_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.notifications_listbox.yview)
        list_scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S))
        self.notifications_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # 通知标题
        ttk.Label(main_frame, text="通知标题:").grid(row=1, column=3, sticky=tk.W, pady=5)
        self.notice_title_var = tk.StringVar()
        self.notice_title_entry = ttk.Entry(main_frame, textvariable=self.notice_title_var, width=60)
        self.notice_title_entry.grid(row=1, column=4, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 发布者
        ttk.Label(main_frame, text="发布者:").grid(row=2, column=3, sticky=tk.W, pady=5)
        self.author_var = tk.StringVar()
        self.author_entry = ttk.Entry(main_frame, textvariable=self.author_var, width=60)
        self.author_entry.grid(row=2, column=4, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 通知内容
        ttk.Label(main_frame, text="通知内容:").grid(row=3, column=3, sticky=(tk.W, tk.N), pady=5)
        self.content_text = scrolledtext.ScrolledText(main_frame, height=10, width=60)
        self.content_text.grid(row=4, column=3, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=6, pady=20)
        
        # 添加通知按钮
        self.add_notice_button = ttk.Button(button_frame, text="添加通知", command=self.add_notification)
        self.add_notice_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 修改通知按钮
        self.update_notice_button = ttk.Button(button_frame, text="修改通知", command=self.update_notification)
        self.update_notice_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 删除通知按钮
        self.delete_notice_button = ttk.Button(button_frame, text="删除通知", command=self.delete_notification)
        self.delete_notice_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空表单按钮
        self.clear_button = ttk.Button(button_frame, text="清空表单", command=self.clear_fields)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 刷新列表按钮
        self.refresh_button = ttk.Button(button_frame, text="刷新列表", command=self.load_notifications_list)
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 备份按钮
        self.backup_button = ttk.Button(button_frame, text="备份文件", command=self.backup_file)
        self.backup_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 预览按钮
        self.preview_button = ttk.Button(button_frame, text="预览JSON", command=self.preview_json)
        self.preview_button.pack(side=tk.LEFT)
        
        # 日志文本框
        ttk.Label(main_frame, text="操作日志:").grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.N), pady=(10, 5))
        self.log_text = tk.Text(main_frame, height=8, width=60)
        self.log_text.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 滚动条
        log_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=7, column=3, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # 配置行权重
        main_frame.rowconfigure(2, weight=1)  # 通知列表
        main_frame.rowconfigure(7, weight=1)  # 日志区域
        
    def load_notifications_list(self):
        """加载通知列表到列表框"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                notifications = json.load(f)
            
            self.notifications_listbox.delete(0, tk.END)
            for i, notification in enumerate(notifications):
                display_text = f"[{notification['id']}] {notification['title']} ({notification['date']})"
                self.notifications_listbox.insert(tk.END, display_text)
                
            self.log(f"已加载 {len(notifications)} 条通知")
        except FileNotFoundError:
            self.log(f"错误: 找不到文件 {self.json_file_path}")
            messagebox.showerror("错误", f"找不到文件 {self.json_file_path}")
        except json.JSONDecodeError:
            self.log(f"错误: JSON文件格式错误 {self.json_file_path}")
            messagebox.showerror("错误", f"JSON文件格式错误 {self.json_file_path}")
    
    def on_notification_select(self, event):
        """当选择通知列表中的项目时"""
        if not self.notifications_listbox.curselection():
            return
            
        index = self.notifications_listbox.curselection()[0]
        
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                notifications = json.load(f)
            
            if 0 <= index < len(notifications):
                selected_notification = notifications[index]
                
                # 填充表单字段
                self.current_notification_id = selected_notification['id']
                self.notice_title_var.set(selected_notification['title'])
                self.author_var.set(selected_notification['author'])
                
                # 清空并设置内容
                self.content_text.delete(1.0, tk.END)
                # 移除<p></p>标签并设置内容
                content = selected_notification['content'].replace('<p></p>\n', '\n').replace('<p></p>', '')
                self.content_text.insert(tk.END, content)
        except Exception as e:
            self.log(f"加载通知详情失败: {str(e)}")
    
    def log(self, message):
        """添加日志信息"""
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.update()
        
    def backup_file(self):
        """备份原文件"""
        if os.path.exists(self.json_file_path):
            backup_path = f"{self.json_file_path}.backup"
            try:
                with open(self.json_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"已备份原文件至: {backup_path}")
                messagebox.showinfo("成功", f"已备份原文件至: {backup_path}")
            except Exception as e:
                self.log(f"备份失败: {str(e)}")
                messagebox.showerror("错误", f"备份失败: {str(e)}")
        else:
            self.log("错误: 找不到文件进行备份")
            messagebox.showerror("错误", "找不到文件进行备份")
            
    def read_json_file(self):
        """读取JSON文件内容"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.log(f"错误: 找不到文件 {self.json_file_path}")
            messagebox.showerror("错误", f"找不到文件 {self.json_file_path}")
            return None
        except json.JSONDecodeError:
            self.log(f"错误: JSON文件格式错误 {self.json_file_path}")
            messagebox.showerror("错误", f"JSON文件格式错误 {self.json_file_path}")
            return None
            
    def write_json_file(self, data):
        """写入JSON文件内容"""
        try:
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.log(f"已更新文件: {self.json_file_path}")
        except Exception as e:
            self.log(f"写入文件失败: {str(e)}")
            messagebox.showerror("错误", f"写入文件失败: {str(e)}")
            
    def add_notification(self):
        """添加通知到JSON文件"""
        # 获取输入值
        notice_title = self.notice_title_var.get().strip()
        author = self.author_var.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        
        # 验证必填字段
        if not all([notice_title, author, content]):
            self.log("错误: 请完整填写通知信息")
            messagebox.showerror("错误", "请完整填写通知信息")
            return
            
        notifications = self.read_json_file()
        if notifications is None:
            return
            
        # 生成通知ID（基于当前时间戳）
        notice_id = int(datetime.now().timestamp())
        
        # 处理内容中的换行符
        content_lines = content.split('\n')
        formatted_content = ""
        for line in content_lines:
            if line.strip():  # 忽略空行
                formatted_content += f"{line.strip()}<p></p>\n"
        
        # 构造通知对象
        new_notification = {
            "id": notice_id,
            "title": notice_title,
            "date": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "author": author,
            "content": formatted_content.rstrip('<p></p>\n')  # 移除最后的<p></p>
        }
        
        # 添加到列表开头（最新通知在前）
        notifications.insert(0, new_notification)
        
        # 保存更新后的内容
        self.write_json_file(notifications)
        self.log(f"成功添加通知: {notice_title}")
        messagebox.showinfo("成功", f"成功添加通知: {notice_title}")
        
        # 刷新列表并清空表单
        self.load_notifications_list()
        self.clear_fields()
        
    def update_notification(self):
        """修改现有的通知"""
        if self.current_notification_id is None:
            self.log("错误: 请选择要修改的通知")
            messagebox.showerror("错误", "请先从列表中选择要修改的通知")
            return
            
        # 获取输入值
        notice_title = self.notice_title_var.get().strip()
        author = self.author_var.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        
        # 验证必填字段
        if not all([notice_title, author, content]):
            self.log("错误: 请完整填写通知信息")
            messagebox.showerror("错误", "请完整填写通知信息")
            return
            
        notifications = self.read_json_file()
        if notifications is None:
            return
            
        # 查找要修改的通知
        notification_found = False
        for i, notification in enumerate(notifications):
            if notification['id'] == self.current_notification_id:
                # 处理内容中的换行符
                content_lines = content.split('\n')
                formatted_content = ""
                for line in content_lines:
                    if line.strip():  # 忽略空行
                        formatted_content += f"{line.strip()}<p></p>\n"
                
                # 更新通知信息
                notifications[i] = {
                    "id": self.current_notification_id,
                    "title": notice_title,
                    "date": notification['date'],  # 保持原日期
                    "author": author,
                    "content": formatted_content.rstrip('<p></p>\n')  # 移除最后的<p></p>
                }
                notification_found = True
                break
        
        if not notification_found:
            self.log(f"错误: 未找到ID为 {self.current_notification_id} 的通知")
            messagebox.showerror("错误", f"未找到ID为 {self.current_notification_id} 的通知")
            return
            
        # 保存更新后的内容
        self.write_json_file(notifications)
        self.log(f"成功修改通知: {notice_title}")
        messagebox.showinfo("成功", f"成功修改通知: {notice_title}")
        
        # 刷新列表并保持选中状态
        self.load_notifications_list()
        # 重新选中刚修改的通知
        for i, item in enumerate(self.notifications_listbox.get(0, tk.END)):
            if str(self.current_notification_id) in item:
                self.notifications_listbox.selection_set(i)
                self.notifications_listbox.see(i)
                break
        
    def delete_notification(self):
        """删除选中的通知"""
        if self.current_notification_id is None:
            self.log("错误: 请选择要删除的通知")
            messagebox.showerror("错误", "请先从列表中选择要删除的通知")
            return
            
        result = messagebox.askyesno("确认删除", f"确定要删除通知 '{self.notice_title_var.get()}' 吗？\n此操作不可撤销！")
        if not result:
            return
            
        notifications = self.read_json_file()
        if notifications is None:
            return
            
        # 过滤掉要删除的通知
        notifications = [n for n in notifications if n['id'] != self.current_notification_id]
        
        # 保存更新后的内容
        self.write_json_file(notifications)
        self.log(f"成功删除通知: {self.current_notification_id}")
        messagebox.showinfo("成功", f"成功删除通知")
        
        # 刷新列表并清空表单
        self.load_notifications_list()
        self.clear_fields()
        
    def preview_json(self):
        """预览生成的JSON"""
        notice_title = self.notice_title_var.get().strip()
        author = self.author_var.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        
        if not all([notice_title, author, content]):
            self.log("错误: 请完整填写通知信息以进行预览")
            messagebox.showerror("错误", "请完整填写通知信息以进行预览")
            return
            
        # 生成通知ID（基于当前时间戳）
        notice_id = int(datetime.now().timestamp())
        
        # 处理内容中的换行符
        content_lines = content.split('\n')
        formatted_content = ""
        for line in content_lines:
            if line.strip():  # 忽略空行
                formatted_content += f"{line.strip()}<p></p>\n"
        
        # 构造通知对象
        notification_obj = {
            "id": notice_id,
            "title": notice_title,
            "date": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "author": author,
            "content": formatted_content.rstrip('<p></p>\n')  # 移除最后的<p></p>
        }
        
        # 生成JSON预览
        json_preview = json.dumps([notification_obj], ensure_ascii=False, indent=2)
        
        # 在新窗口中显示预览
        preview_window = tk.Toplevel(self.root)
        preview_window.title("JSON 预览")
        preview_window.geometry("700x400")
        
        text_widget = tk.Text(preview_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, json_preview)
        text_widget.config(state=tk.DISABLED)
        
    def clear_fields(self):
        """清空输入字段"""
        self.current_notification_id = None
        self.notice_title_var.set("")
        self.author_var.set("")
        self.content_text.delete("1.0", tk.END)


def main():
    """主函数"""
    root = tk.Tk()
    app = NotificationUpdaterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
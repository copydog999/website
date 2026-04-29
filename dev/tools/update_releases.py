#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电子游戏科学与技术期刊 - 发布页面更新工具
用于自动更新 database/nowbase.json 文件中的论文发布信息
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from datetime import datetime
from pathlib import Path
import json
import hashlib

# 导入文档文本提取模块
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'ocr'))


class ReleaseUpdaterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JOEST 发布页面更新工具")
        self.root.geometry("1200x750")  # 增加高度以容纳新控件
        
        # JSON文件路径 - 从 tools 目录向上两级到项目根目录
        script_dir = Path(__file__).parent
        self.json_file_path = str(script_dir.parent.parent / "database" / "data" / "nowbase.json")
        # 备份文件夹路径 - 相对于项目根目录
        self.backup_folder_path = str(script_dir.parent.parent / "dev" / "backup")
        
        # 当前选中的论文ID
        self.current_paper_id = None
        
        # 确保备份文件夹存在
        if not os.path.exists(self.backup_folder_path):
            os.makedirs(self.backup_folder_path)
        
        # 创建界面
        self.create_widgets()
        self.load_papers_list()
        
    def create_widgets(self):
        """创建界面控件"""
        # 初始化控件变量，确保在刷新期刊期数列表之前已存在
        self.add_existing_section_var = tk.StringVar()
        self.add_new_section_var = tk.StringVar()
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=2)  # 左侧列权重
        main_frame.columnconfigure(1, weight=1)  # 右侧列权重
        
        # 标题
        title_label = ttk.Label(main_frame, text="发布页面更新工具", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 创建左侧主内容区域
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 创建右侧摘要和日志区域
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建分页控件
        notebook = ttk.Notebook(left_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加分页
        self.add_frame = ttk.Frame(notebook, padding="10")
        self.update_frame = ttk.Frame(notebook, padding="10")
        self.delete_frame = ttk.Frame(notebook, padding="10")
        
        notebook.add(self.add_frame, text="添加论文")
        notebook.add(self.update_frame, text="修改论文")
        notebook.add(self.delete_frame, text="删除论文")
        
        # 配置分页的权重
        for frame in [self.add_frame, self.update_frame, self.delete_frame]:
            frame.columnconfigure(1, weight=1)
        
        # 添加分页界面
        self.create_add_tab()
        
        # 修改分页界面
        self.create_update_tab()
        
        # 删除分页界面
        self.create_delete_tab()
        
        # 右侧区域：摘要和操作日志
        # 摘要区域
        ttk.Label(right_frame, text="摘要:").grid(row=0, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        self.add_abstract_text = tk.Text(right_frame, width=40, height=8)
        self.add_abstract_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 摘要滚动条
        abstract_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.add_abstract_text.yview)
        abstract_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S), pady=(0, 10))
        self.add_abstract_text.configure(yscrollcommand=abstract_scrollbar.set)
        
        # 操作日志区域
        ttk.Label(right_frame, text="操作日志:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(10, 5))
        self.log_text = tk.Text(right_frame, height=12, width=40)
        self.log_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志滚动条
        log_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=3, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # 备份按钮
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=1, column=0, pady=10)
        self.backup_button = ttk.Button(button_frame, text="备份文件", command=self.backup_file)
        self.backup_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 刷新列表按钮
        self.refresh_button = ttk.Button(button_frame, text="刷新列表", command=self.load_papers_list)
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 已删除复制URL前缀按钮
        
        # 配置主框架的行权重
        main_frame.rowconfigure(1, weight=1)  # 内容区域
        
        # 配置左右框架的权重
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)  # 分页控件
        
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)  # 摘要区域
        right_frame.rowconfigure(3, weight=1)  # 日志区域
    
    def create_add_tab(self):
        """创建添加分页"""
        # 期刊期数选择模式
        ttk.Label(self.add_frame, text="选择模式:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.add_mode_var = tk.StringVar(value="existing")
        mode_frame = ttk.Frame(self.add_frame)
        mode_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        existing_radio = ttk.Radiobutton(mode_frame, text="已有期刊期数", variable=self.add_mode_var, value="existing", command=self.on_add_mode_change)
        existing_radio.grid(row=0, column=0, padx=(0, 10))
        new_radio = ttk.Radiobutton(mode_frame, text="新建期刊期数", variable=self.add_mode_var, value="new", command=self.on_add_mode_change)
        new_radio.grid(row=0, column=1, padx=(0, 10))
        
        # 期刊期数下拉框和输入框
        ttk.Label(self.add_frame, text="期刊期数:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.add_section_title_frame = ttk.Frame(self.add_frame)
        self.add_section_title_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 已有期刊期数下拉框
        self.add_existing_section_var = tk.StringVar()
        self.add_existing_section_combo = ttk.Combobox(self.add_section_title_frame, textvariable=self.add_existing_section_var, width=47, state="readonly")
        self.add_existing_section_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.add_existing_section_var.trace('w', self.on_section_change)
        
        # 新建期刊期数输入框
        self.add_new_section_var = tk.StringVar()
        self.add_new_section_entry = ttk.Entry(self.add_section_title_frame, textvariable=self.add_new_section_var, width=50)
        self.add_new_section_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.add_new_section_entry.grid_remove()  # 初始隐藏
        
        # DOI生成功能区域框架
        self.doi_frame = ttk.LabelFrame(self.add_frame, text="DOI生成设置", padding="10")
        self.doi_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 初始化DOI控件变量
        self.setup_doi_controls()
        
        # 创建DOI控件
        self.create_doi_controls()
        
        # 添加按钮
        self.add_paper_button = ttk.Button(self.add_frame, text="添加论文", command=self.add_paper)
        self.add_paper_button.grid(row=12, column=1, pady=20)
        
        # 预览按钮
        self.add_preview_button = ttk.Button(self.add_frame, text="预览JSON", command=self.add_preview_json)
        self.add_preview_button.grid(row=12, column=2, padx=(10, 0), pady=20)
        
        # 标题（移到文件路径上方）
        ttk.Label(self.add_frame, text="论文标题:").grid(row=3, column=0, sticky=tk.W, pady=5)
        title_frame = ttk.Frame(self.add_frame)
        title_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.add_title_var = tk.StringVar()
        self.add_title_entry = ttk.Entry(title_frame, textvariable=self.add_title_var, width=40)
        self.add_title_entry.pack(side=tk.LEFT)
        self.add_title_entry.bind('<KeyRelease>', self.on_title_change)
        
        # 警告标签（初始隐藏）
        self.title_warning_label = ttk.Label(title_frame, text="", foreground="red", font=("Arial", 9))
        self.title_warning_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 配置列权重
        title_frame.columnconfigure(0, weight=1)
        
        # 文件路径（分块填入制）
        ttk.Label(self.add_frame, text="文件路径:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # 创建文件路径框架
        file_path_frame = ttk.Frame(self.add_frame)
        file_path_frame.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 第一块：固定前缀
        prefix_label = ttk.Label(file_path_frame, text="https://gitee.com/copycat666/articles/raw/master/")
        prefix_label.pack(side=tk.LEFT)
        
        # 第二块：可编辑的中间部分
        self.file_path_middle_var = tk.StringVar(value="volume1")
        middle_entry = ttk.Entry(file_path_frame, textvariable=self.file_path_middle_var, width=15)
        middle_entry.pack(side=tk.LEFT, padx=(2, 2))
        
        # 斜杠分隔符
        slash_label = ttk.Label(file_path_frame, text="/", foreground="gray")
        slash_label.pack(side=tk.LEFT)
        
        # 第三块：文件名（通过按钮选择文件自动填充）
        self.file_path_filename_var = tk.StringVar()
        filename_entry = ttk.Entry(file_path_frame, textvariable=self.file_path_filename_var, width=20, state='readonly')
        filename_entry.pack(side=tk.LEFT, padx=(2, 2))
        
        # 选择文件按钮
        select_file_button = ttk.Button(file_path_frame, text="选择文件", command=self.select_file_for_path)
        select_file_button.pack(side=tk.LEFT, padx=(2, 2))
        
        # 打开链接按钮
        open_link_button = ttk.Button(file_path_frame, text="打开链接", command=self.open_file_link)
        open_link_button.pack(side=tk.LEFT, padx=(2, 0))
        
        # 完整路径显示（只读）
        self.add_file_path_var = tk.StringVar()
        self.add_file_path_entry = ttk.Entry(self.add_frame, textvariable=self.add_file_path_var, width=50, state='readonly')
        self.add_file_path_entry.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 绑定中间部分变化事件
        self.file_path_middle_var.trace('w', self.update_full_file_path)
        
        # 绑定卷号变化事件
        self.volume_number_var.trace('w', self.update_file_path_with_volume_new)
        
        # 作者信息（支持多种分隔符）
        ttk.Label(self.add_frame, text="作者信息:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.add_authors_var = tk.StringVar()
        self.add_authors_entry = ttk.Entry(self.add_frame, textvariable=self.add_authors_var, width=50)
        self.add_authors_entry.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.add_authors_entry.bind('<FocusOut>', self.parse_authors_input)
        
        # 关键词（支持多种分隔符）
        ttk.Label(self.add_frame, text="关键词:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.add_keywords_var = tk.StringVar()
        self.add_keywords_entry = ttk.Entry(self.add_frame, textvariable=self.add_keywords_var, width=50)
        self.add_keywords_entry.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.add_keywords_entry.bind('<FocusOut>', self.parse_keywords_input)
        
        # 等级
        ttk.Label(self.add_frame, text="等级:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.add_level_var = tk.StringVar()
        level_frame = ttk.Frame(self.add_frame)
        level_frame.grid(row=7, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        levels = ["", "【1级】", "【2级】", "【3级】"]
        for i, level in enumerate(levels):
            ttk.Radiobutton(level_frame, text=level if level else "无", variable=self.add_level_var, 
                           value=level).grid(row=0, column=i, padx=(0, 10))
        
        # 特殊说明
        ttk.Label(self.add_frame, text="特殊说明:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.add_special_note_var = tk.StringVar()
        self.add_special_note_entry = ttk.Entry(self.add_frame, textvariable=self.add_special_note_var, width=50)
        self.add_special_note_entry.grid(row=8, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # DOI功能区已包含DOI显示和生成按钮，此处无需重复
        
        # 摘要已移至右侧主界面
        
        # 初始化期刊期数列表
        self.refresh_section_list()
    
    def create_update_tab(self):
        """创建修改分页"""
        # 数据库
        ttk.Label(self.update_frame, text="数据库:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.update_papers_listbox = tk.Listbox(self.update_frame, height=8, selectmode=tk.SINGLE)  # 改为单选
        self.update_papers_listbox.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        self.update_papers_listbox.bind('<<ListboxSelect>>', self.on_update_paper_select)
        
        # 滚动条
        update_list_scrollbar = ttk.Scrollbar(self.update_frame, orient=tk.VERTICAL, command=self.update_papers_listbox.yview)
        update_list_scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.update_papers_listbox.configure(yscrollcommand=update_list_scrollbar.set)
        
        # JSON编辑区域
        ttk.Label(self.update_frame, text="JSON 编辑:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.update_json_text = tk.Text(self.update_frame, width=80, height=15)
        self.update_json_text.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # JSON编辑滚动条
        update_json_scrollbar = ttk.Scrollbar(self.update_frame, orient=tk.VERTICAL, command=self.update_json_text.yview)
        update_json_scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
        self.update_json_text.configure(yscrollcommand=update_json_scrollbar.set)
        
        # 保存按钮
        self.save_updated_paper_button = ttk.Button(self.update_frame, text="保存修改", command=self.save_updated_paper)
        self.save_updated_paper_button.grid(row=4, column=0, pady=20)
        
        # 配置行权重
        self.update_frame.rowconfigure(3, weight=1)
    
    def create_delete_tab(self):
        """创建删除分页"""
        # 数据库
        ttk.Label(self.delete_frame, text="数据库:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.delete_papers_listbox = tk.Listbox(self.delete_frame, height=15, selectmode=tk.SINGLE)  # 改为单选
        self.delete_papers_listbox.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        self.delete_papers_listbox.bind('<<ListboxSelect>>', self.on_delete_paper_select)
        
        # 滚动条
        delete_list_scrollbar = ttk.Scrollbar(self.delete_frame, orient=tk.VERTICAL, command=self.delete_papers_listbox.yview)
        delete_list_scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.delete_papers_listbox.configure(yscrollcommand=delete_list_scrollbar.set)
        
        # 选中的论文信息显示
        self.delete_selected_info = tk.Text(self.delete_frame, width=60, height=5)
        self.delete_selected_info.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        self.delete_selected_info.config(state=tk.DISABLED)
        
        # 删除按钮
        self.delete_paper_button = ttk.Button(self.delete_frame, text="删除论文", command=self.delete_paper)
        self.delete_paper_button.grid(row=3, column=0, pady=20)
        
        # 清空选择按钮
        self.delete_clear_button = ttk.Button(self.delete_frame, text="清空选择", command=self.clear_delete_selection)
        self.delete_clear_button.grid(row=3, column=1, padx=(10, 0), pady=20)
    
    def check_doi_uniqueness(self, papers, new_doi, new_title):
        """检查DOI唯一性并处理冲突
        
        Args:
            papers: 现有论文列表
            new_doi: 新生成的DOI
            new_title: 新论文标题
            
        Returns:
            str: 唯一的DOI
        """
        # 检查DOI唯一性
        existing_dois = {paper.get('nowbasedoi', '') for paper in papers}
        
        if new_doi not in existing_dois:
            return new_doi
        
        # DOI重复，按16进制递增处理
        current_doi = new_doi
        increment = 1
        max_attempts = 1000  # 防止无限循环
        
        while current_doi in existing_dois and increment <= max_attempts:
            try:
                # 将DOI作为16进制数处理
                doi_int = int(current_doi, 16)
                doi_int += 1
                # 转换回16进制字符串，保持10位长度
                current_doi = format(doi_int, '010X')
                increment += 1
            except ValueError:
                # 如果转换失败，简单地在末尾添加数字
                current_doi = new_doi[:-1] + str(increment % 10)
                increment += 1
        
        if increment > max_attempts:
            # 如果尝试次数过多，生成随机后缀
            import random
            random_suffix = format(random.randint(0, 0xFFFF), '04X')
            current_doi = new_doi[:6] + random_suffix
            self.log(f"警告：DOI冲突次数过多，使用随机后缀: {current_doi}")
        
        self.log(f"DOI冲突解决：{new_doi} -> {current_doi}")
        return current_doi
    
    def generate_new_doi(self):
        """生成新的DOI格式：版号-卷号-索引-年份-分类码"""
        # 验证必填字段
        if not self.index_var.get().strip():
            self.log("错误: 请输入索引")
            messagebox.showerror("错误", "请输入索引")
            return
            
        # 获取DOI生成所需的各个部分
        edition = self.edition_var.get().strip()
        volume = self.volume_number_var.get().strip()
        index = self.index_var.get().strip()
        year = self.year_var.get().strip()
        category = self.doc_category_var.get().strip()
        
        # 验证索引是否为数字
        if not index.isdigit():
            self.log("错误: 索引必须是数字")
            messagebox.showerror("错误", "索引必须是数字")
            return
        
        # 生成DOI
        new_doi = f"{edition}-{volume}-{index}-{year}-{category}"
        
        # 检查DOI唯一性
        papers = self.read_json_file()
        if papers is None:
            return
            
        final_doi = self.check_doi_uniqueness(papers, new_doi, "")
        
        # 显示最终DOI
        self.add_doi_var.set(final_doi)
        self.log(f"DOI生成完成: {final_doi}")
        
        # 保存生成的DOI供添加论文时使用
        self.generated_doi = final_doi
        
        # 文件路径会自动更新，无需额外操作
    
    def setup_doi_controls(self):
        """初始化DOI控件变量"""
        self.doc_category_var = tk.StringVar(value="R")
        self.edition_var = tk.StringVar(value="PS")
        self.volume_number_var = tk.StringVar(value="1")
        self.index_var = tk.StringVar()
        current_year = str(datetime.now().year)
        self.year_var = tk.StringVar(value=current_year)
        self.add_doi_var = tk.StringVar()
        
        # 会议论文特有变量
        self.ICEST_index_var = tk.StringVar()
    
    def create_doi_controls(self):
        """创建DOI控件（根据期刊期数类型动态创建）"""
        # 先清除现有控件
        for widget in self.doi_frame.winfo_children():
            widget.destroy()
        
        # 获取当前期刊期数
        current_section = self.add_existing_section_var.get().strip()
        is_ICEST = "ICEST" in current_section.upper()
        
        if is_ICEST:
            self.create_ICEST_doi_controls()
        else:
            self.create_regular_doi_controls()
    
    def create_regular_doi_controls(self):
        """创建常规DOI控件"""
        # 文献分类码
        ttk.Label(self.doi_frame, text="文献分类码:").grid(row=0, column=0, sticky=tk.W, pady=2)
        category_frame = ttk.Frame(self.doi_frame)
        category_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        categories = [("R", "普"), ("N", "社"), ("D", "数"), ("S", "源"), ("M", "媒"), ("L", "评"),("W", "白")]
        for i, (code, name) in enumerate(categories):
            ttk.Radiobutton(category_frame, text=f"{code}({name})", variable=self.doc_category_var, 
                           value=code).grid(row=0, column=i, padx=(0, 10))
        
        # 版号
        ttk.Label(self.doi_frame, text="版号:").grid(row=1, column=0, sticky=tk.W, pady=2)
        edition_frame = ttk.Frame(self.doi_frame)
        edition_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        editions = ["PS", "BS", "ET", "SS", "HS", "EDU", "HM", "YSA", "TM", "WP"]
        edition_combo = ttk.Combobox(edition_frame, textvariable=self.edition_var, values=editions, width=10, state="readonly")
        edition_combo.grid(row=0, column=0)
        
        # 卷号
        ttk.Label(self.doi_frame, text="卷号:").grid(row=2, column=0, sticky=tk.W, pady=2)
        volume_spinbox = ttk.Spinbox(self.doi_frame, from_=1, to=999, textvariable=self.volume_number_var, width=10)
        volume_spinbox.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 索引
        ttk.Label(self.doi_frame, text="索引:").grid(row=3, column=0, sticky=tk.W, pady=2)
        index_frame = ttk.Frame(self.doi_frame)
        index_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        index_entry = ttk.Entry(index_frame, textvariable=self.index_var, width=10)
        index_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # 自动计算索引按钮
        self.calculate_index_button = ttk.Button(index_frame, text="自动计算", command=self.calculate_next_index)
        self.calculate_index_button.pack(side=tk.LEFT)
        
        # 年份
        ttk.Label(self.doi_frame, text="年份:").grid(row=4, column=0, sticky=tk.W, pady=2)
        year_entry = ttk.Entry(self.doi_frame, textvariable=self.year_var, width=10, state='readonly')
        year_entry.grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # DOI显示和生成按钮
        ttk.Label(self.doi_frame, text="DOI:").grid(row=5, column=0, sticky=tk.W, pady=2)
        doi_display_frame = ttk.Frame(self.doi_frame)
        doi_display_frame.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=2)
        
        self.add_doi_entry = ttk.Entry(doi_display_frame, textvariable=self.add_doi_var, width=30)
        self.add_doi_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.generate_doi_button = ttk.Button(doi_display_frame, text="生成DOI", command=self.generate_new_doi)
        self.generate_doi_button.pack(side=tk.LEFT)
    
    def create_ICEST_doi_controls(self):
        """创建会议论文DOI控件"""
        # 文献分类码
        ttk.Label(self.doi_frame, text="文献分类码:").grid(row=0, column=0, sticky=tk.W, pady=2)
        category_frame = ttk.Frame(self.doi_frame)
        category_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        categories = [("R", "普"), ("N", "社"), ("D", "数"), ("S", "源"), ("M", "媒"), ("L", "评")]
        for i, (code, name) in enumerate(categories):
            ttk.Radiobutton(category_frame, text=f"{code}({name})", variable=self.doc_category_var, 
                           value=code).grid(row=0, column=i, padx=(0, 10))
        
        # 索引（会议论文用）
        ttk.Label(self.doi_frame, text="索引:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ICEST_index_frame = ttk.Frame(self.doi_frame)
        ICEST_index_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ICEST_index_entry = ttk.Entry(ICEST_index_frame, textvariable=self.ICEST_index_var, width=10)
        ICEST_index_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # 自动计算索引按钮
        self.calculate_ICEST_index_button = ttk.Button(ICEST_index_frame, text="自动计算", command=self.calculate_ICEST_next_index)
        self.calculate_ICEST_index_button.pack(side=tk.LEFT)
        
        # 年份
        ttk.Label(self.doi_frame, text="年份:").grid(row=2, column=0, sticky=tk.W, pady=2)
        year_entry = ttk.Entry(self.doi_frame, textvariable=self.year_var, width=10, state='readonly')
        year_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # DOI显示和生成按钮
        ttk.Label(self.doi_frame, text="DOI:").grid(row=3, column=0, sticky=tk.W, pady=2)
        doi_display_frame = ttk.Frame(self.doi_frame)
        doi_display_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        self.add_doi_entry = ttk.Entry(doi_display_frame, textvariable=self.add_doi_var, width=30)
        self.add_doi_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.generate_ICEST_doi_button = ttk.Button(doi_display_frame, text="生成DOI", command=self.generate_ICEST_doi)
        self.generate_ICEST_doi_button.pack(side=tk.LEFT)
    
    def on_section_change(self, *args):
        """当期刊期数改变时的处理"""
        self.create_doi_controls()
    
    def calculate_next_index(self):
        """计算当前版号 + 卷号的下一个可用索引"""
        try:
            # 获取当前选择的版号和卷号
            current_edition = self.edition_var.get().strip()
            current_volume = self.volume_number_var.get().strip()
                
            if not current_edition:
                self.log("错误：请先选择版号")
                messagebox.showerror("错误", "请先选择版号")
                return
                
            if not current_volume.isdigit():
                self.log("错误：卷号格式不正确")
                messagebox.showerror("错误", "卷号格式不正确")
                return
                
            # 读取现有论文数据
            papers = self.read_json_file()
            if papers is None:
                return
                
            # 找出当前版号 + 卷号的最大索引
            max_index = 0
            for paper in papers:
                if (paper.get('edition') == current_edition and 
                    paper.get('volume') == int(current_volume) and
                    paper.get('index') and 
                    str(paper.get('index')).isdigit()):
                    index_value = int(paper.get('index'))
                    if index_value > max_index:
                        max_index = index_value
                            
            # 下一个可用索引
            next_index = max_index + 1
            self.index_var.set(str(next_index))
            self.log(f"版号 {current_edition} 卷号 {current_volume} 的下一个可用索引：{next_index}")
                
        except Exception as e:
            self.log(f"计算索引时出错：{str(e)}")
            messagebox.showerror("错误", f"计算索引时出错：{str(e)}")
    
    def calculate_ICEST_next_index(self):
        """计算会议论文的下一个可用索引"""
        try:
            # 获取当前期刊期数
            current_section = self.add_existing_section_var.get().strip()
            if not current_section:
                self.log("错误: 请先选择期刊期数")
                messagebox.showerror("错误", "请先选择期刊期数")
                return
            
            # 读取现有论文数据
            papers = self.read_json_file()
            if papers is None:
                return
            
            # 找出当前期刊期数中会议论文的最大索引
            max_index = 0
            for paper in papers:
                if (paper.get('issue') == current_section and 
                    'ICEST' in paper.get('issue', '').upper() and
                    paper.get('index') and 
                    str(paper.get('index')).isdigit()):
                    index_value = int(paper.get('index'))
                    if index_value > max_index:
                        max_index = index_value
            
            # 下一个可用索引
            next_index = max_index + 1
            self.ICEST_index_var.set(str(next_index))
            self.log(f"会议论文 {current_section} 的下一个可用索引: {next_index}")
            
        except Exception as e:
            self.log(f"计算会议论文索引时出错: {str(e)}")
            messagebox.showerror("错误", f"计算会议论文索引时出错: {str(e)}")
    
    def generate_ICEST_doi(self):
        """生成会议论文DOI格式：ICEST-年份-索引-分类码"""
        # 验证必填字段
        if not self.ICEST_index_var.get().strip():
            self.log("错误: 请输入索引")
            messagebox.showerror("错误", "请输入索引")
            return
            
        # 获取DOI生成所需的各个部分
        year = self.year_var.get().strip()
        index = self.ICEST_index_var.get().strip()
        category = self.doc_category_var.get().strip()
        
        # 验证索引是否为数字
        if not index.isdigit():
            self.log("错误: 索引必须是数字")
            messagebox.showerror("错误", "索引必须是数字")
            return
        
        # 生成DOI
        new_doi = f"ICEST-{year}-{index}-{category}"
        
        # 检查DOI唯一性
        papers = self.read_json_file()
        if papers is None:
            return
            
        final_doi = self.check_doi_uniqueness(papers, new_doi, "")
        
        # 显示最终DOI
        self.add_doi_var.set(final_doi)
        self.log(f"会议论文DOI生成完成: {final_doi}")
        
        # 保存生成的DOI供添加论文时使用
        self.generated_doi = final_doi
    
    def update_file_path_with_volume_new(self, *args):
        """当新的卷号改变时更新文件路径"""
        volume_num = self.volume_number_var.get().strip()
        if volume_num.isdigit():
            self.file_path_middle_var.set(f"volume{volume_num}")
        else:
            self.file_path_middle_var.set("volume1")
    
    def select_file_for_path(self):
        """选择文件并提取文件名用于文件路径"""
        file_path = filedialog.askopenfilename(
            title="选择论文文件",
            filetypes=[
                ("PDF文件", "*.pdf"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            # 提取文件名（包含扩展名）
            filename = os.path.basename(file_path)
            self.file_path_filename_var.set(filename)
            self.update_full_file_path()
            self.log(f"已选择文件: {filename}")
    
    def update_full_file_path(self, *args):
        """更新完整的文件路径显示"""
        middle_part = self.file_path_middle_var.get().strip()
        filename_part = self.file_path_filename_var.get().strip()
        
        if middle_part and filename_part:
            full_path = f"https://gitee.com/copycat666/articles/raw/master/{middle_part}/{filename_part}"
            self.add_file_path_var.set(full_path)
        else:
            self.add_file_path_var.set("")
    
    def open_file_link(self):
        """在浏览器中打开文件链接"""
        file_path = self.add_file_path_var.get().strip()
        if not file_path:
            messagebox.showwarning("警告", "请先生成完整的文件路径")
            return
        
        try:
            import webbrowser
            webbrowser.open(file_path)
            self.log(f"已在浏览器中打开链接: {file_path}")
        except Exception as e:
            self.log(f"打开链接时出错: {str(e)}")
            messagebox.showerror("错误", f"无法打开链接: {str(e)}")
    
    def generate_and_check_doi(self):
        """生成并检查DOI唯一性"""
        # 获取所有必填信息
        section_title = self.add_existing_section_var.get().strip() if self.add_mode_var.get() == "existing" else self.add_new_section_var.get().strip()
        file_path = self.add_file_path_var.get().strip()
        title = self.add_title_var.get().strip()
        level = self.add_level_var.get().strip()
        
        # 获取解析后的作者和关键词
        if not hasattr(self, 'parsed_authors') or not self.parsed_authors:
            self.log("错误: 请填写作者信息并离开输入框以触发解析")
            messagebox.showerror("错误", "请填写作者信息并离开输入框以触发解析")
            return
            
        if not hasattr(self, 'parsed_keywords') or not self.parsed_keywords:
            self.log("错误: 请填写关键词并离开输入框以触发解析")
            messagebox.showerror("错误", "请填写关键词并离开输入框以触发解析")
            return
            
        authors_array = self.parsed_authors
        keywords_array = self.parsed_keywords
        
        # 验证必填字段
        if not all([section_title, file_path, title]):
            self.log("错误: 请完整填写必填信息后再生成DOI")
            messagebox.showerror("错误", "请完整填写期刊期数、文件路径、论文标题后再生成DOI")
            return
            
        # 获取其他信息
        special_note = self.add_special_note_var.get().strip()
        abstract = self.add_abstract_text.get(1.0, tk.END).strip()
        volume_num = self.add_volume_number_var.get().strip()
        if not volume_num.isdigit():
            volume_num = "1"
        volume_field = f"volume{volume_num}"
        
        # 生成初始DOI（不包含特殊说明）
        authors_str = ''.join(authors_array)
        keywords_str = ','.join(keywords_array)
        
        initial_doi = self.generate_doi(
            title=title,
            authors=authors_str,
            issue=section_title,
            keywords=keywords_str,
            file_path=file_path,
            special_note="",  # 不包含特殊说明
            abstract=abstract,
            volume=volume_field
        )
        
        # 检查DOI唯一性
        papers = self.read_json_file()
        if papers is None:
            return
            
        final_doi = self.check_doi_uniqueness(papers, initial_doi, title)
        
        # 显示最终DOI
        self.add_doi_var.set(final_doi)
        self.log(f"DOI生成完成: {final_doi}")
        
        # 保存生成的DOI供添加论文时使用
        self.generated_doi = final_doi
    
    def generate_doi(self, title, authors, issue, keywords, file_path, special_note, abstract, volume):
        """根据所有论文属性生成10位字符串DOI
        
        Args:
            所有论文相关属性
            
        Returns:
            str: 10位DOI字符串
        """
        # 将所有属性拼接成一个大字符串
        all_data = f"{title}{authors}{issue}{keywords}{file_path}{special_note}{abstract}{volume}"
        
        # 编码为字节
        input_bytes = all_data.encode('utf-8')
        
        # 初始哈希
        hash_obj = hashlib.sha256(input_bytes)
        hash_result = hash_obj.digest()
        
        # 循环运算直到得到10位结果
        target_length = 10
        max_iterations = 1000  # 防止无限循环
        iteration = 0
        
        while iteration < max_iterations:
            # 将当前哈希结果转换为16进制字符串
            hex_string = hash_result.hex()
            
            if len(hex_string) >= target_length:
                # 如果长度足够，取前10位
                doi = hex_string[:target_length].upper()
                break
            else:
                # 长度不够，继续运算
                # 方法1：将当前结果与原始数据结合重新哈希
                combined_data = input_bytes + hash_result
                hash_obj = hashlib.sha256(combined_data)
                hash_result = hash_obj.digest()
                
                # 方法2：添加迭代次数作为盐值
                salted_data = combined_data + str(iteration).encode('utf-8')
                hash_obj = hashlib.sha256(salted_data)
                hash_result = hash_obj.digest()
                
                iteration += 1
        
        # 如果达到最大迭代次数仍未获得足够长度，使用备用方案
        if iteration >= max_iterations:
            # 使用更复杂的组合方式
            complex_input = f"{title[::-1]}{authors}{issue[::-1]}{keywords}{file_path}{volume}"
            final_hash = hashlib.md5(complex_input.encode('utf-8')).hexdigest()
            doi = (final_hash * 2)[:target_length].upper()  # 重复确保长度
            
        self.log(f"DOI生成完成，迭代次数: {iteration}, 结果: {doi}")
        return doi
    
    def on_title_change(self, event=None):
        """当标题发生变化时的处理"""
        title = self.add_title_var.get().strip()
        if title:
            # 检查标题重复
            self.check_title_duplicate(title)
        else:
            # 清空警告
            self.hide_title_warning()
    
    def check_title_duplicate(self, title):
        """检查标题是否重复"""
        try:
            papers = self.read_json_file()
            if papers is None:
                return
                
            # 检查是否有相同标题
            for paper in papers:
                if paper.get('title', '').strip() == title.strip():
                    self.show_title_warning("⚠ 标题已存在！")
                    return
            
            # 如果没有重复，隐藏警告
            self.hide_title_warning()
            
        except Exception as e:
            self.log(f"检查标题重复时出错: {str(e)}")
    
    def show_title_warning(self, message):
        """显示标题警告"""
        self.title_warning_label.config(text=message)
        self.title_warning_label.pack(side=tk.LEFT, padx=(10, 0))  # 确保显示
    
    def hide_title_warning(self):
        """隐藏标题警告"""
        self.title_warning_label.config(text="")
        self.title_warning_label.pack_forget()
    
    # 移除了原有的 auto_generate_file_path 方法，因为现在使用分块填入制
    
    def update_file_path_with_volume(self, *args):
        """当volume编号改变时更新文件路径"""
        if self.add_title_var.get().strip():
            self.auto_generate_file_path()
    
    def parse_authors_input(self, event=None):
        """解析作者输入，支持中英文逗号分隔"""
        authors_input = self.add_authors_var.get().strip()
        if not authors_input:
            return
            
        # 使用正则表达式分割中英文逗号
        authors_list = re.split(r'[，,]\s*', authors_input)
        # 清理每个作者名称（去除首尾空格）
        authors_list = [author.strip() for author in authors_list if author.strip()]
        
        # 更新显示（保持原始输入格式，但内部已解析）
        self.log(f"解析出 {len(authors_list)} 位作者: {', '.join(authors_list)}")
        
        # 存储解析后的作者数组
        self.parsed_authors = authors_list
    
    def parse_keywords_input(self, event=None):
        """解析关键词输入，支持中英文逗号、分号分隔"""
        keywords_input = self.add_keywords_var.get().strip()
        if not keywords_input:
            return
            
        # 使用正则表达式分割中英文逗号和分号
        keywords_list = re.split(r'[，,；;]\s*', keywords_input)
        # 清理每个关键词（去除首尾空格）
        keywords_list = [keyword.strip() for keyword in keywords_list if keyword.strip()]
        
        # 更新显示
        self.log(f"解析出 {len(keywords_list)} 个关键词: {', '.join(keywords_list)}")
        
        # 存储解析后的关键词数组
        self.parsed_keywords = keywords_list
    
    def load_papers_list(self):
        """加载论文列表到列表框"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                papers = json.load(f)
            
            # 更新添加分页的列表（虽然添加分页不需要列表，但用于刷新期刊期数）
            self.refresh_section_list()
            
            # 更新修改分页的列表
            self.update_papers_listbox.delete(0, tk.END)
            for i, paper in enumerate(papers):
                display_text = f"[{paper['id']}] {paper['title']} ({paper['issue']})"
                self.update_papers_listbox.insert(tk.END, display_text)
                
            # 更新删除分页的列表
            self.delete_papers_listbox.delete(0, tk.END)
            for i, paper in enumerate(papers):
                display_text = f"[{paper['id']}] {paper['title']} ({paper['issue']})"
                self.delete_papers_listbox.insert(tk.END, display_text)
                
            self.log(f"已加载 {len(papers)} 篇论文")
        except FileNotFoundError:
            self.log(f"错误: 找不到文件 {self.json_file_path}")
            messagebox.showerror("错误", f"找不到文件 {self.json_file_path}")
        except json.JSONDecodeError:
            self.log(f"错误: JSON文件格式错误 {self.json_file_path}")
            messagebox.showerror("错误", f"JSON文件格式错误 {self.json_file_path}")
    
    def on_add_mode_change(self):
        """当添加模式改变时，切换显示的控件"""
        if self.add_mode_var.get() == "existing":
            self.add_existing_section_combo.grid()
            self.add_new_section_entry.grid_remove()
        else:
            self.add_existing_section_combo.grid_remove()
            self.add_new_section_entry.grid()
    
    def on_update_paper_select(self, event):
        """当选择修改分页中的论文时"""
        # 获取选中的索引
        selected_index = self.update_papers_listbox.curselection()
        
        if not selected_index:
            return
            
        index = selected_index[0]
        
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                papers = json.load(f)
            
            if 0 <= index < len(papers):
                selected_paper = papers[index]
                
                # 设置当前论文ID
                self.current_paper_id = selected_paper['id']
                
                # 显示论文的JSON内容
                self.update_json_text.delete(1.0, tk.END)
                json_str = json.dumps(selected_paper, ensure_ascii=False, indent=2)
                self.update_json_text.insert(tk.END, json_str)
        except Exception as e:
            self.log(f"加载论文详情失败: {str(e)}")
    
    def on_delete_paper_select(self, event):
        """当选择删除分页中的论文时"""
        # 获取选中的索引
        selected_index = self.delete_papers_listbox.curselection()
        
        if not selected_index:
            return
            
        index = selected_index[0]
        
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                papers = json.load(f)
            
            if 0 <= index < len(papers):
                selected_paper = papers[index]
                
                # 显示选中论文的详细信息
                self.delete_selected_info.config(state=tk.NORMAL)
                self.delete_selected_info.delete(1.0, tk.END)
                
                info = f"ID: {selected_paper['id']}\n"
                info += f"标题: {selected_paper['title']}\n"
                info += f"作者: {selected_paper['authors']}\n"
                info += f"期刊期数: {selected_paper['issue']}\n"
                info += f"等级：{selected_paper.get('level', '') if selected_paper.get('level') else '无'}\n"
                info += f"关键词: {selected_paper['keywords']}\n"
                info += f"文件路径: {selected_paper['filePath']}\n"
                info += f"特殊说明：{selected_paper.get('specialNote', '') if selected_paper.get('specialNote') else '无'}\n"
                info += f"摘要：{selected_paper.get('abstract', '')[:100] if selected_paper.get('abstract') else '无'}..."  # 只显示前 100 个字符
                
                self.delete_selected_info.insert(tk.END, info)
                self.delete_selected_info.config(state=tk.DISABLED)
                
        except Exception as e:
            self.log(f"加载论文详情失败: {str(e)}")
    
    def refresh_section_list(self):
        """刷新期刊期数列表"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                papers = json.load(f)
            
            # 提取所有唯一的期刊期数
            issues = list(set([paper.get('issue', '') for paper in papers if paper.get('issue')]))
            issues.sort()  # 排序
            
            # 更新添加分页的期刊期数列表（如果控件存在）
            if hasattr(self, 'add_existing_section_combo'):
                self.add_existing_section_combo['values'] = issues
                if issues:
                    # 默认选择ID最大的论文对应的期刊期数
                    max_id_paper = max(papers, key=lambda x: x.get('id', 0))
                    default_issue = max_id_paper.get('issue', issues[0])
                    self.add_existing_section_combo.set(default_issue)
                else:
                    self.add_existing_section_combo.set("")
            
            # 更新修改分页的期刊期数列表（如果控件存在）
            # if hasattr(self, 'update_existing_section_combo'):
            #     self.update_existing_section_combo['values'] = issues
            #     if issues:
            #         self.update_existing_section_combo.set(issues[0] if issues else "")
            #     else:
            #         self.update_existing_section_combo.set("")
                
            self.log("期刊期数列表已刷新")
        except FileNotFoundError:
            self.log(f"错误: 找不到文件 {self.json_file_path}")
            if hasattr(self, 'add_existing_section_combo'):
                self.add_existing_section_combo['values'] = []
            # if hasattr(self, 'update_existing_section_combo'):
            #     self.update_existing_section_combo['values'] = []
        except json.JSONDecodeError:
            self.log(f"错误: JSON文件格式错误 {self.json_file_path}")
            if hasattr(self, 'add_existing_section_combo'):
                self.add_existing_section_combo['values'] = []
            # if hasattr(self, 'update_existing_section_combo'):
            #     self.update_existing_section_combo['values'] = []
    
    def browse_file_add(self):
        """浏览文件（添加分页）"""
        filename = filedialog.askopenfilename(
            title="选择论文文件",
            filetypes=[("PDF files", "*.pdf"), ("Word files", "*.doc"), ("Word files", "*.docx"), ("All files", "*.*")]
        )
        if filename:
            # 尝试将路径转换为相对路径
            try:
                rel_path = os.path.relpath(filename, os.path.dirname(os.path.abspath(self.json_file_path)))
                # 将反斜杠替换为正斜杠
                rel_path = rel_path.replace("\\", "/")
                self.add_file_path_var.set(rel_path)
            except:
                # 将反斜杠替换为正斜杠
                filename = filename.replace("\\", "/")
                self.add_file_path_var.set(filename)
                
            # 文件选择后自动提取摘要和关键词
            self.extract_info_from_file_add()

    def extract_info_from_file_add(self):
        """从文件中提取摘要和关键词（添加分页）"""
        file_path = self.add_file_path_var.get().strip()
        if not file_path:
            return  # 如果没有文件路径，直接返回
            
        # 如果是相对路径，尝试从项目根目录开始查找
        project_root = os.path.join(os.path.dirname(__file__), "..")
        full_path = os.path.join(project_root, file_path)
        if not os.path.exists(full_path):
            full_path = file_path  # 如果相对路径不存在，使用原路径
            
        if not os.path.exists(full_path):
            self.log(f"警告: 找不到文件: {full_path}")
            return
        
        try:
            # 提取文档信息
            text, abstract, keywords = extract_document_info(full_path)
            
            # 更新GUI中的摘要和关键词字段
            # 进一步处理摘要，确保删除换行符和多余空格
            abstract = re.sub(r"\n+", " ", abstract)
            abstract = re.sub(r"\s+", " ", abstract).strip()
            
            self.add_abstract_text.delete(1.0, tk.END)
            self.add_abstract_text.insert(tk.END, abstract)
            
            # 填入提取的关键词，如果当前关键词字段为空
            if not self.add_keywords_var.get().strip():
                self.add_keywords_var.set(keywords)
            else:
                # 如果已有关键词，询问用户是否替换
                result = messagebox.askyesno("关键词已存在", "关键词字段已有内容，是否用提取的关键词替换？")
                if result:
                    self.add_keywords_var.set(keywords)
            
            self.log(f"成功从文件中提取摘要和关键词: {os.path.basename(full_path)}")
            
        except ImportError as e:
            messagebox.showerror("错误", str(e))
        except Exception as e:
            self.log(f"提取文档信息时出错: {str(e)}")
    
    def log(self, message):
        """添加日志信息"""
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
            self.log_text.see(tk.END)
            self.log_text.update()
        
    def backup_file(self):
        """备份原文件"""
        if os.path.exists(self.json_file_path):
            # 使用时间戳作为备份文件名的一部分
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"nowbase_backup_{timestamp}.json"
            backup_path = os.path.join(self.backup_folder_path, backup_filename)
            
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
            
    def add_paper(self):
        """添加论文到JSON文件"""
        # 获取输入值
        if self.add_mode_var.get() == "existing":
            section_title = self.add_existing_section_var.get().strip()
        else:
            section_title = self.add_new_section_var.get().strip()
        
        file_path = self.add_file_path_var.get().strip()
        title = self.add_title_var.get().strip()
        level = self.add_level_var.get().strip()
        special_note = self.add_special_note_var.get().strip()
        
        # 获取摘要内容并清理换行符
        abstract = self.add_abstract_text.get(1.0, tk.END).strip()
        # 自动去除所有换行符和多余空格
        abstract = re.sub(r'\n+', ' ', abstract)
        abstract = re.sub(r'\s+', ' ', abstract).strip()
        
        # 验证必填字段
        if not all([section_title, file_path, title]):
            self.log("错误: 请完整填写论文信息")
            messagebox.showerror("错误", "请完整填写论文信息")
            return
            
        # 检查作者和关键词是否已解析
        if not hasattr(self, 'parsed_authors') or not self.parsed_authors:
            self.log("错误: 请填写作者信息并离开输入框以触发解析")
            messagebox.showerror("错误", "请填写作者信息并离开输入框以触发解析")
            return
            
        if not hasattr(self, 'parsed_keywords') or not self.parsed_keywords:
            self.log("错误: 请填写关键词并离开输入框以触发解析")
            messagebox.showerror("错误", "请填写关键词并离开输入框以触发解析")
            return
            
        # 检查DOI是否已生成
        if not hasattr(self, 'generated_doi') or not self.generated_doi:
            self.log("错误: 请先点击'生成DOI'按钮生成DOI")
            messagebox.showerror("错误", "请先点击'生成DOI'按钮生成DOI")
            return
            
        # 获取解析后的作者和关键词数组
        authors_array = self.parsed_authors
        keywords_array = self.parsed_keywords
        final_doi = self.generated_doi
        
        papers = self.read_json_file()
        if papers is None:
            return
            
        # 获取当前最大ID并加1作为新ID
        max_id = 0
        if papers:
            max_id = max([paper.get('id', 0) for paper in papers])
        
        # 获取卷号编号（如果是会议论文则不存储卷号）
        current_section = self.add_existing_section_var.get().strip()
        is_ICEST = "ICEST" in current_section.upper()
        
        if is_ICEST:
            volume_field = None  # 会议论文不存储卷号
            index_value = self.ICEST_index_var.get().strip()
            # 将索引存储为数字类型
            if index_value.isdigit():
                index_value = int(index_value)
            else:
                index_value = 1  # 默认值
        else:
            volume_num = self.volume_number_var.get().strip()
            if not volume_num.isdigit():
                volume_num = "1"
            # 存储为纯数字而不是字符串
            volume_field = int(volume_num)
            index_value = self.index_var.get().strip()
            # 将索引存储为数字类型
            if index_value.isdigit():
                index_value = int(index_value)
            else:
                index_value = 1  # 默认值
        
        # 构造论文信息对象 - 使用数组格式存储作者和关键词
        paper_info = {
            "id": max_id + 1,
            "title": title,
            "authors": authors_array,  # 数组格式
            "issue": section_title,
            "keywords": keywords_array,  # 数组格式
            "filePath": file_path,
            "specialNote": special_note if special_note else None,
            "abstract": abstract if abstract else None,
            "nowbasedoi": final_doi,  # 使用预先生成并检查过的 DOI
            "doc_category": self.doc_category_var.get(),  # 文献分类码
            "year": self.year_var.get(),  # 年份
            "index": index_value,  # 索引
            "published": datetime.now().isoformat()  # 添加发布日期字段
        }
        
        # 根据是否为会议论文添加不同的字段
        if is_ICEST:
            # 会议论文不添加版号和卷号
            pass
        else:
            # 常规论文添加版号和卷号
            paper_info["edition"] = self.edition_var.get()  # 版号
            paper_info["volume"] = volume_field  # 卷号
        
        # 添加到列表
        papers.append(paper_info)
        
        # 保存更新后的内容
        self.write_json_file(papers)
        self.log(f"成功添加论文: {title}")
        messagebox.showinfo("成功", f"成功添加论文: {title}")
        
        # 刷新列表并清空输入字段（保留期刊期数）
        self.load_papers_list()
        self.add_file_path_var.set("")
        self.add_title_var.set("")
        self.add_authors_var.set("")
        self.add_keywords_var.set("")
        self.add_special_note_var.set("")
        self.add_abstract_text.delete(1.0, tk.END)
        self.volume_number_var.set("1")
        self.index_var.set("")
        self.ICEST_index_var.set("")
        self.add_doi_var.set("")  # 清空 DOI 显示
        
        # 清除解析缓存和生成的DOI
        if hasattr(self, 'parsed_authors'):
            delattr(self, 'parsed_authors')
        if hasattr(self, 'parsed_keywords'):
            delattr(self, 'parsed_keywords')
        if hasattr(self, 'generated_doi'):
            delattr(self, 'generated_doi')
        
        # 如果是新建期刊期数，添加到下拉列表中
        if self.add_mode_var.get() == "new":
            current_values = list(self.add_existing_section_combo['values'])
            if section_title not in current_values:
                current_values.append(section_title)
                current_values.sort()
                self.add_existing_section_combo['values'] = current_values
                self.add_existing_section_combo.set(section_title)
    
    def update_paper(self):
        """修改现有的论文"""
        if self.current_paper_id is None:
            self.log("错误: 请选择要修改的论文")
            messagebox.showerror("错误", "请先从列表中选择要修改的论文")
            return
            
        # 获取输入值
        if self.update_mode_var.get() == "existing":
            section_title = self.update_existing_section_var.get().strip()
        else:
            section_title = self.update_new_section_var.get().strip()
        
        file_path = self.update_file_path_var.get().strip()
        authors = self.update_authors_var.get().strip()
        title = self.update_title_var.get().strip()
        keywords = self.update_keywords_var.get().strip()
        level = self.update_level_var.get().strip()
        special_note = self.update_special_note_var.get().strip()
        
        # 获取摘要内容
        abstract = self.update_abstract_text.get(1.0, tk.END).strip()
        
        # 验证必填字段
        if not all([section_title, file_path, authors, title, keywords]):
            self.log("错误: 请完整填写论文信息")
            messagebox.showerror("错误", "请完整填写论文信息")
            return
            
        # 将文件路径中的反斜杠替换为正斜杠
        file_path = file_path.replace("\\", "/")
            
        papers = self.read_json_file()
        if papers is None:
            return
            
        # 查找要修改的论文
        paper_found = False
        for i, paper in enumerate(papers):
            if paper['id'] == self.current_paper_id:
                # 生成新的DOI
                doi = self.generate_doi(title, authors, level)
                
                # 更新论文信息 - 添加abstract和nowbasedoi字段
                papers[i] = {
                    "id": self.current_paper_id,
                    "title": title,
                    "authors": authors,
                    "level": level if level else None,
                    "issue": section_title,
                    "keywords": keywords,
                    "filePath": file_path,
                    "specialNote": special_note if special_note else None,
                    "abstract": abstract if abstract else None,  # 添加摘要字段
                    "nowbasedoi": doi  # 添加DOI字段
                }
                paper_found = True
                break
        
        if not paper_found:
            self.log(f"错误: 未找到ID为 {self.current_paper_id} 的论文")
            messagebox.showerror("错误", f"未找到ID为 {self.current_paper_id} 的论文")
            return
            
        # 保存更新后的内容
        self.write_json_file(papers)
        self.log(f"成功修改论文: {title}")
        messagebox.showinfo("成功", f"成功修改论文: {title}")
        
        # 刷新列表并保持选中状态
        self.load_papers_list()
        # 重新选中刚修改的论文
        for i, item in enumerate(self.update_papers_listbox.get(0, tk.END)):
            if str(self.current_paper_id) in item:
                self.update_papers_listbox.selection_set(i)
                self.update_papers_listbox.see(i)
                break
    
    def save_updated_paper(self):
        """保存修改后的论文"""
        if self.current_paper_id is None:
            self.log("错误: 请选择要修改的论文")
            messagebox.showerror("错误", "请先从列表中选择要修改的论文")
            return
            
        # 获取文本框中的JSON内容
        json_str = self.update_json_text.get(1.0, tk.END).strip()
        
        if not json_str:
            self.log("错误: JSON内容不能为空")
            messagebox.showerror("错误", "JSON内容不能为空")
            return
            
        try:
            # 解析JSON内容
            updated_paper = json.loads(json_str)
            
            # 将文件路径中的反斜杠替换为正斜杠
            if "filePath" in updated_paper:
                updated_paper["filePath"] = updated_paper["filePath"].replace("\\", "/")
            
            # 验证必要的字段是否存在
            required_fields = ['id', 'title', 'authors', 'issue', 'keywords', 'filePath', 'nowbasedoi']
            for field in required_fields:
                if field not in updated_paper:
                    self.log(f"错误: 缺少必要字段 {field}")
                    messagebox.showerror("错误", f"缺少必要字段 {field}")
                    return
                    
            # 读取现有数据
            papers = self.read_json_file()
            if papers is None:
                return
                
            # 查找要修改的论文位置
            paper_index = None
            for i, paper in enumerate(papers):
                if paper['id'] == self.current_paper_id:
                    paper_index = i
                    break
                    
            if paper_index is None:
                self.log(f"错误: 未找到ID为 {self.current_paper_id} 的论文")
                messagebox.showerror("错误", f"未找到ID为 {self.current_paper_id} 的论文")
                return
                
            # 更新论文信息
            papers[paper_index] = updated_paper
            
            # 保存更新后的内容
            self.write_json_file(papers)
            self.log(f"成功更新论文: {updated_paper['title']}")
            messagebox.showinfo("成功", f"成功更新论文: {updated_paper['title']}")
            
            # 刷新列表并保持选中状态
            self.load_papers_list()
            # 重新选中刚修改的论文
            for i, item in enumerate(self.update_papers_listbox.get(0, tk.END)):
                if str(self.current_paper_id) in item:
                    self.update_papers_listbox.selection_set(i)
                    self.update_papers_listbox.see(i)
                    break
                    
        except json.JSONDecodeError as e:
            self.log(f"错误: JSON格式无效 - {str(e)}")
            messagebox.showerror("错误", f"JSON格式无效:\n{str(e)}")
        except Exception as e:
            self.log(f"保存论文时出错: {str(e)}")
            messagebox.showerror("错误", f"保存论文时出错: {str(e)}")
            
    def delete_paper(self):
        """删除选中的论文"""
        selected_indices = self.delete_papers_listbox.curselection()
        if not selected_indices:
            self.log("错误: 请选择要删除的论文")
            messagebox.showerror("错误", "请先从列表中选择要删除的论文")
            return
            
        # 获取要删除的论文ID
        papers_to_delete = []
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                papers = json.load(f)
            
            for index in sorted(selected_indices, reverse=True):  # 从后往前删除，避免索引变化
                if 0 <= index < len(papers):
                    papers_to_delete.append(papers[index]['title'])
            
            # 确认删除
            if len(papers_to_delete) == 1:
                message = f"确定要删除论文 '{papers_to_delete[0]}' 吗？\n此操作不可撤销！"
            else:
                message = f"确定要删除选中的 {len(papers_to_delete)} 篇论文吗？\n此操作不可撤销！"
            
            result = messagebox.askyesno("确认删除", message)
            if not result:
                return
            
            # 删除论文
            for index in sorted(selected_indices, reverse=True):
                if 0 <= index < len(papers):
                    papers.pop(index)
            
            # 保存更新后的内容
            self.write_json_file(papers)
            self.log(f"成功删除 {len(papers_to_delete)} 篇论文")
            messagebox.showinfo("成功", f"成功删除 {len(papers_to_delete)} 篇论文")
            
            # 刷新列表并清空表单
            self.load_papers_list()
            self.clear_delete_selection()
            
        except Exception as e:
            self.log(f"删除论文时出错: {str(e)}")
            messagebox.showerror("错误", f"删除论文时出错: {str(e)}")
    
    def clear_update_fields(self):
        """清空修改分页的输入字段"""
        self.current_paper_id = None
        self.update_existing_section_var.set("")
        self.update_new_section_var.set("")
        self.update_file_path_var.set("")
        self.update_authors_var.set("")
        self.update_title_var.set("")
        self.update_keywords_var.set("")
        self.update_level_var.set("")
        self.update_special_note_var.set("")
        self.update_abstract_text.delete(1.0, tk.END)
    
    def clear_delete_selection(self):
        """清空删除分页的选择"""
        self.delete_papers_listbox.selection_clear(0, tk.END)
        self.delete_selected_info.config(state=tk.NORMAL)
        self.delete_selected_info.delete(1.0, tk.END)
        self.delete_selected_info.config(state=tk.DISABLED)
        
    def add_preview_json(self):
        """预览生成的JSON（添加分页）"""
        # 获取输入值
        if self.add_mode_var.get() == "existing":
            section_title = self.add_existing_section_var.get().strip()
        else:
            section_title = self.add_new_section_var.get().strip()
        
        file_path = self.add_file_path_var.get().strip()
        title = self.add_title_var.get().strip()
        level = self.add_level_var.get().strip()
        special_note = self.add_special_note_var.get().strip()
        
        # 获取摘要内容
        abstract = self.add_abstract_text.get(1.0, tk.END).strip()
        
        if not all([section_title, file_path, title]):
            self.log("错误: 请完整填写论文信息以进行预览")
            messagebox.showerror("错误", "请完整填写论文信息以进行预览")
            return
            
        # 检查作者和关键词是否已解析
        if not hasattr(self, 'parsed_authors') or not self.parsed_authors:
            self.log("错误: 请填写作者信息并离开输入框以触发解析")
            messagebox.showerror("错误", "请填写作者信息并离开输入框以触发解析")
            return
            
        if not hasattr(self, 'parsed_keywords') or not self.parsed_keywords:
            self.log("错误: 请填写关键词并离开输入框以触发解析")
            messagebox.showerror("错误", "请填写关键词并离开输入框以触发解析")
            return
            
        # 获取解析后的作者和关键词数组
        authors_array = self.parsed_authors
        keywords_array = self.parsed_keywords
        
        # 获取当前最大ID并加1作为新ID
        try:
            papers = self.read_json_file()
            max_id = 0
            if papers:
                max_id = max([paper.get('id', 0) for paper in papers])
        except:
            max_id = 0
        
        # 生成 DOI
        authors_str = ''.join(authors_array)  # 将作者数组合并为字符串用于 DOI 生成
        doi = self.generate_doi(title, authors_str, section_title, keywords_str, file_path, special_note, abstract, volume_field)
        
        # 获取卷号编号
        volume_num = self.add_volume_number_var.get().strip()
        if not volume_num.isdigit():
            volume_num = "1"
        # 存储为纯数字而不是字符串
        volume_field = int(volume_num)
        
        # 构造论文信息对象 - 使用数组格式存储作者和关键词
        paper_info = {
            "id": max_id + 1,
            "title": title,
            "authors": authors_array,  # 数组格式
            "issue": section_title,
            "keywords": keywords_array,  # 数组格式
            "filePath": file_path,
            "specialNote": special_note if special_note else None,
            "abstract": abstract if abstract else None,
            "nowbasedoi": doi,
            "doc_category": self.doc_category_var.get(),  # 文献分类码
            "edition": self.edition_var.get(),  # 版号
            "volume": volume_field,  # 卷号
            "year": self.year_var.get(),  # 年份
            "index": self.index_var.get()  # 索引
        }
        
        # 生成JSON预览
        json_preview = json.dumps([paper_info], ensure_ascii=False, indent=2)
        
        # 在新窗口中显示预览
        preview_window = tk.Toplevel(self.root)
        preview_window.title("JSON 预览")
        preview_window.geometry("600x300")
        
        text_widget = tk.Text(preview_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, json_preview)
        text_widget.config(state=tk.DISABLED)

    # 已删除 copy_gitee_url_prefix 方法


def main():
    """主函数"""
    root = tk.Tk()
    app = ReleaseUpdaterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
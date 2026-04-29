#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编辑部成员数据管理工具 - 图形界面版本
提供可视化的增删改查功能
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import sys
import urllib.request
import urllib.parse


class EditorManagerGUI:
    """编辑部成员管理图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("编辑部成员数据管理工具")
        self.root.geometry("1200x800")
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 数据文件路径 - 从 tools 目录向上两级到项目根目录
        script_dir = Path(__file__).parent
        self.json_file = script_dir.parent.parent / "database" / "data" / "nowledge.json"
        self.data = self._load_data()
        
        # 创建界面
        self._create_widgets()
        self._refresh_list()
    
    def _load_data(self):
        """加载 JSON 数据"""
        if not self.json_file.exists():
            messagebox.showwarning("警告", f"文件 {self.json_file} 不存在，将创建新文件")
            return []
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON 格式错误: {e}")
            return []
    
    def _save_data(self):
        """保存数据到 JSON 文件"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"✓ 已保存 ({len(self.data)} 条记录)")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # === 顶部工具栏 ===
        toolbar = ttk.Frame(main_frame)
        toolbar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(toolbar, text="刷新", command=self._refresh_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="新增成员", command=self._add_member_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="编辑选中", command=self._edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="删除选中", command=self._delete_selected).pack(side=tk.LEFT, padx=5)
        
        # 搜索框
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # === 左侧列表 ===
        list_frame = ttk.LabelFrame(main_frame, text="成员列表", padding="5")
        list_frame.grid(row=1, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 创建表格
        columns = ('ID', '姓名', '职位', '机构', 'h-index', '论文数')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        # 设置列
        self.tree.heading('ID', text='ID')
        self.tree.heading('姓名', text='姓名')
        self.tree.heading('职位', text='职位')
        self.tree.heading('机构', text='机构')
        self.tree.heading('h-index', text='h-index')
        self.tree.heading('论文数', text='论文数')
        
        self.tree.column('ID', width=50, anchor=tk.CENTER)
        self.tree.column('姓名', width=100, anchor=tk.W)
        self.tree.column('职位', width=150, anchor=tk.W)
        self.tree.column('机构', width=150, anchor=tk.W)
        self.tree.column('h-index', width=60, anchor=tk.CENTER)
        self.tree.column('论文数', width=60, anchor=tk.CENTER)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', lambda e: self._view_details())
        
        # === 右侧详情面板 ===
        detail_frame = ttk.LabelFrame(main_frame, text="详细信息", padding="10")
        detail_frame.grid(row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        
        # 详情文本框
        self.detail_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD, width=60, height=30,
                                                      font=('Microsoft YaHei', 10))
        self.detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # === 底部状态栏 ===
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _refresh_list(self):
        """刷新列表"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加数据
        for member in self.data:
            papers_count = len(member.get('papers', []))
            h_index = member.get('h-index', 'N/A')
            
            self.tree.insert('', tk.END, values=(
                member['id'],
                member['name'],
                member['position'],
                member['institution'],
                h_index,
                papers_count
            ))
        
        self.status_var.set(f"已加载 {len(self.data)} 条记录")
    
    def _on_search(self, *args):
        """搜索过滤"""
        keyword = self.search_var.get().lower()
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 过滤并显示
        for member in self.data:
            if keyword in member['name'].lower():
                papers_count = len(member.get('papers', []))
                h_index = member.get('h-index', 'N/A')
                
                self.tree.insert('', tk.END, values=(
                    member['id'],
                    member['name'],
                    member['position'],
                    member['institution'],
                    h_index,
                    papers_count
                ))
    
    def _get_selected_member(self):
        """获取选中的成员"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个成员")
            return None
        
        item = self.tree.item(selected[0])
        member_id = item['values'][0]
        
        for member in self.data:
            if member['id'] == member_id:
                return member
        
        return None
    
    def _view_details(self):
        """查看详细信息"""
        member = self._get_selected_member()
        if not member:
            return
        
        # 构建详情文本
        detail = f"{'='*60}\n"
        detail += f"成员详细信息\n"
        detail += f"{'='*60}\n\n"
        detail += f"ID: {member['id']}\n"
        detail += f"姓名: {member['name']}\n"
        detail += f"职位: {member['position']}\n"
        detail += f"机构: {member['institution']}\n"
        detail += f"头衔: {member.get('title', 'N/A')}\n"
        detail += f"h-index: {member.get('h-index', 'N/A')}\n\n"
        
        detail += f"研究方向:\n"
        for field in member.get('resfield', []):
            detail += f"  • {field}\n"
        
        detail += f"\n个人简介:\n  {member.get('bio', 'N/A')}\n"
        
        papers = member.get('papers', [])
        detail += f"\n学术论文 (共 {len(papers)} 篇):\n"
        for i, paper in enumerate(papers, 1):
            venue = paper.get('journal') or paper.get('conference', 'N/A')
            venue_type = "期刊" if paper.get('journal') else "会议"
            detail += f"  {i}. {paper['title']}\n"
            detail += f"     {venue_type}: {venue}, {paper.get('year', 'N/A')}\n"
            detail += f"     DOI: {paper.get('doi', 'N/A')}\n\n"
        
        detail += f"\n头像: {member.get('avatar_url', 'N/A')}\n"
        detail += f"背景: {member.get('backgound_url', member.get('background_url', 'N/A'))}\n"
        detail += f"{'='*60}"
        
        # 显示详情
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(tk.END, detail)
    
    def _add_member_dialog(self):
        """添加成员对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加新成员")
        dialog.geometry("600x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 表单框架
        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 自动计算新 ID
        max_id = max([m['id'] for m in self.data], default=0)
        new_id = max_id + 1
        
        fields = [
            ("ID:", str(new_id), True),
            ("姓名:", "", False),
            ("职位:", "", False),
            ("所属机构:", "", False),
            ("学术头衔:", "", False),
            ("研究方向:", "", False),
            ("个人简介:", "", False),
            ("头像 URL:", "", False),
            ("背景 URL:", "", False),
            ("h-index:", "0", False),
        ]
        
        entries = {}
        for i, (label, default, disabled) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(form_frame, width=40)
            entry.insert(0, default)
            if disabled:
                entry.config(state='disabled')
            entry.grid(row=i, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))
            entries[label] = entry
        
        form_frame.columnconfigure(1, weight=1)
        
        # DOI 批量导入区域
        doi_frame = ttk.LabelFrame(form_frame, text="批量导入论文（通过 DOI）", padding="10")
        doi_frame.grid(row=len(fields), column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        doi_frame.columnconfigure(0, weight=1)
        
        ttk.Label(doi_frame, text="输入多个 DOI，用分号隔开:", font=('Microsoft YaHei', 9)).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        doi_text = scrolledtext.ScrolledText(doi_frame, height=6, width=50, 
                                             font=('Consolas', 9), wrap=tk.WORD)
        doi_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 临时存储解析的论文
        parsed_papers = []
        
        def parse_dois():
            """批量解析 DOI"""
            doi_input = doi_text.get(1.0, tk.END).strip()
            if not doi_input:
                messagebox.showwarning("提示", "请输入 DOI")
                return
            
            # 分割 DOI（支持中英文分号、逗号、换行）
            import re
            dois = re.split(r'[;；,，\n]', doi_input)
            dois = [d.strip() for d in dois if d.strip()]
            
            if not dois:
                messagebox.showwarning("提示", "未找到有效的 DOI")
                return
            
            # 创建进度对话框
            progress_dialog = tk.Toplevel(dialog)
            progress_dialog.title("正在解析 DOI")
            progress_dialog.geometry("400x300")
            progress_dialog.transient(dialog)
            progress_dialog.grab_set()
            
            prog_frame = ttk.Frame(progress_dialog, padding="10")
            prog_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(prog_frame, text=f"正在解析 {len(dois)} 个 DOI...", 
                     font=('Microsoft YaHei', 10)).pack(pady=10)
            
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(prog_frame, variable=progress_var, 
                                         maximum=len(dois), length=300)
            progress_bar.pack(pady=10)
            
            status_label = ttk.Label(prog_frame, text="", font=('Microsoft YaHei', 9))
            status_label.pack(pady=5)
            
            log_text = scrolledtext.ScrolledText(prog_frame, height=8, width=45,
                                                font=('Consolas', 8), wrap=tk.WORD)
            log_text.pack(pady=5, fill=tk.BOTH, expand=True)
            
            success_count = 0
            fail_count = 0
            
            for i, doi in enumerate(dois, 1):
                # 清理 DOI
                clean_doi = doi.replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
                
                try:
                    # 调用 CrossRef API
                    url = f"https://api.crossref.org/works/{urllib.parse.quote(clean_doi)}"
                    req = urllib.request.Request(url)
                    req.add_header('User-Agent', 'EditorManager/1.0')
                    
                    with urllib.request.urlopen(req, timeout=10) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        work = data['message']
                        
                        # 提取信息
                        title = work.get('title', [''])[0]
                        
                        year = None
                        if 'published-print' in work:
                            year = work['published-print'].get('date-parts', [[None]])[0][0]
                        elif 'published-online' in work:
                            year = work['published-online'].get('date-parts', [[None]])[0][0]
                        elif 'created' in work:
                            year = work['created'].get('date-parts', [[None]])[0][0]
                        
                        container_title = work.get('container-title', [''])[0]
                        type_value = work.get('type', '')
                        
                        paper_data = {
                            "title": title,
                            "year": year if year else 2024,
                            "doi": clean_doi
                        }
                        
                        if type_value in ['journal-article', 'article']:
                            paper_data["journal"] = container_title
                        else:
                            paper_data["conference"] = container_title
                        
                        parsed_papers.append(paper_data)
                        success_count += 1
                        
                        log_text.insert(tk.END, f"✓ [{i}/{len(dois)}] {clean_doi}\n")
                        log_text.see(tk.END)
                        
                except Exception as e:
                    fail_count += 1
                    log_text.insert(tk.END, f"✗ [{i}/{len(dois)}] {clean_doi}: {str(e)[:50]}\n")
                    log_text.see(tk.END)
                
                # 更新进度
                progress_var.set(i)
                status_label.config(text=f"成功: {success_count}, 失败: {fail_count}")
                progress_dialog.update()
            
            # 完成
            ttk.Button(prog_frame, text="关闭", command=progress_dialog.destroy).pack(pady=10)
            status_label.config(text=f"解析完成！成功: {success_count}, 失败: {fail_count}")
            
            # 刷新论文列表显示
            refresh_paper_list()
        
        def refresh_paper_list():
            """刷新论文列表显示"""
            paper_listbox.delete(0, tk.END)
            for paper in parsed_papers:
                venue = paper.get('journal') or paper.get('conference', 'N/A')
                display_text = f"{paper['title']} ({venue}, {paper.get('year', 'N/A')})"
                paper_listbox.insert(tk.END, display_text)
        
        btn_row = ttk.Frame(doi_frame)
        btn_row.grid(row=2, column=0, pady=5)
        ttk.Button(btn_row, text="开始解析", command=parse_dois, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="清空", command=lambda: doi_text.delete(1.0, tk.END), width=10).pack(side=tk.LEFT, padx=5)
        
        # 论文管理区域
        paper_frame = ttk.LabelFrame(form_frame, text="已解析的论文", padding="5")
        paper_frame.grid(row=len(fields)+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        paper_frame.columnconfigure(0, weight=1)
        
        # 论文列表
        paper_listbox = tk.Listbox(paper_frame, height=6, width=50, font=('Microsoft YaHei', 9))
        paper_listbox.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 临时存储论文数据
        temp_papers = []
        
        def add_paper():
            """添加论文对话框"""
            paper_dialog = tk.Toplevel(dialog)
            paper_dialog.title("添加论文")
            paper_dialog.geometry("500x400")
            paper_dialog.transient(dialog)
            paper_dialog.grab_set()
            
            p_form = ttk.Frame(paper_dialog, padding="10")
            p_form.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(p_form, text="论文标题:").grid(row=0, column=0, sticky=tk.W, pady=5)
            p_title = ttk.Entry(p_form, width=40)
            p_title.grid(row=0, column=1, padx=10, pady=5)
            
            ttk.Label(p_form, text="类型:").grid(row=1, column=0, sticky=tk.W, pady=5)
            p_type_var = tk.StringVar(value="conference")
            ttk.Radiobutton(p_form, text="会议", variable=p_type_var, value="conference").grid(row=1, column=1, sticky=tk.W, padx=10)
            ttk.Radiobutton(p_form, text="期刊", variable=p_type_var, value="journal").grid(row=1, column=1, sticky=tk.E, padx=10)
            
            ttk.Label(p_form, text="会议/期刊名称:").grid(row=2, column=0, sticky=tk.W, pady=5)
            p_venue = ttk.Entry(p_form, width=40)
            p_venue.grid(row=2, column=1, padx=10, pady=5)
            
            ttk.Label(p_form, text="年份:").grid(row=3, column=0, sticky=tk.W, pady=5)
            p_year = ttk.Entry(p_form, width=40)
            p_year.insert(0, "2024")
            p_year.grid(row=3, column=1, padx=10, pady=5)
            
            ttk.Label(p_form, text="DOI:").grid(row=4, column=0, sticky=tk.W, pady=5)
            p_doi = ttk.Entry(p_form, width=40)
            p_doi.grid(row=4, column=1, padx=10, pady=5)
            
            def fetch_doi_info():
                """从 DOI 获取论文信息"""
                doi = p_doi.get().strip()
                if not doi:
                    messagebox.showwarning("提示", "请先输入 DOI")
                    return
                
                # 清理 DOI（移除 URL 前缀）
                doi = doi.replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
                
                try:
                    paper_dialog.config(cursor='watch')
                    paper_dialog.update()
                    
                    # 使用 CrossRef API
                    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
                    req = urllib.request.Request(url)
                    req.add_header('User-Agent', 'EditorManager/1.0')
                    
                    with urllib.request.urlopen(req, timeout=10) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        work = data['message']
                        
                        # 提取标题
                        title = work.get('title', [''])[0]
                        if title:
                            p_title.delete(0, tk.END)
                            p_title.insert(0, title)
                        
                        # 提取年份
                        year = None
                        if 'published-print' in work:
                            year = work['published-print'].get('date-parts', [[None]])[0][0]
                        elif 'published-online' in work:
                            year = work['published-online'].get('date-parts', [[None]])[0][0]
                        elif 'created' in work:
                            year = work['created'].get('date-parts', [[None]])[0][0]
                        
                        if year:
                            p_year.delete(0, tk.END)
                            p_year.insert(0, str(year))
                        
                        # 提取期刊或会议名称
                        container_title = work.get('container-title', [''])[0]
                        if container_title:
                            p_venue.delete(0, tk.END)
                            p_venue.insert(0, container_title)
                            
                            # 根据类型设置单选按钮
                            type_value = work.get('type', '')
                            if type_value in ['journal-article', 'article']:
                                p_type_var.set('journal')
                            else:
                                p_type_var.set('conference')
                        
                        paper_dialog.config(cursor='')
                        messagebox.showinfo("成功", "DOI 解析成功！")
                        
                except Exception as e:
                    paper_dialog.config(cursor='')
                    messagebox.showerror("错误", f"DOI 解析失败: {str(e)}\n\n请手动填写论文信息")
            
            # DOI 自动解析按钮
            doi_frame = ttk.Frame(p_form)
            doi_frame.grid(row=4, column=2, padx=5)
            ttk.Button(doi_frame, text="自动解析", command=fetch_doi_info, width=10).pack()
            
            def save_paper():
                title = p_title.get()
                venue = p_venue.get()
                year = p_year.get()
                doi = p_doi.get()
                
                if not title or not venue:
                    messagebox.showerror("错误", "标题和会议/期刊名称不能为空")
                    return
                
                paper_data = {
                    "title": title,
                    "year": int(year) if year else 2024,
                    "doi": doi if doi else "N/A"
                }
                
                if p_type_var.get() == "journal":
                    paper_data["journal"] = venue
                else:
                    paper_data["conference"] = venue
                
                temp_papers.append(paper_data)
                
                # 更新列表显示
                display_text = f"{title} ({venue}, {year})"
                paper_listbox.insert(tk.END, display_text)
                
                paper_dialog.destroy()
            
            p_btn_frame = ttk.Frame(p_form)
            p_btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
            ttk.Button(p_btn_frame, text="保存", command=save_paper).pack(side=tk.LEFT, padx=5)
            ttk.Button(p_btn_frame, text="取消", command=paper_dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        def delete_paper():
            """删除选中的论文"""
            selection = paper_listbox.curselection()
            if not selection:
                messagebox.showwarning("提示", "请先选择要删除的论文")
                return
            
            index = selection[0]
            confirm = messagebox.askyesno("确认删除", "确定要删除这篇论文吗？")
            if confirm:
                temp_papers.pop(index)
                paper_listbox.delete(index)
        
        paper_btn_frame = ttk.Frame(paper_frame)
        paper_btn_frame.grid(row=1, column=0, columnspan=3, pady=5)
        ttk.Button(paper_btn_frame, text="添加论文", command=add_paper).pack(side=tk.LEFT, padx=5)
        ttk.Button(paper_btn_frame, text="删除选中", command=delete_paper).pack(side=tk.LEFT, padx=5)
        
        # 按钮
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        def save_member():
            try:
                member = {
                    "id": new_id,
                    "name": entries["姓名:"].get(),
                    "position": entries["职位:"].get(),
                    "institution": entries["所属机构:"].get(),
                    "title": entries["学术头衔:"].get(),
                    "resfield": [f.strip() for f in entries["研究方向:"].get().split(',') if f.strip()],
                    "bio": entries["个人简介:"].get(),
                    "papers": parsed_papers.copy(),  # 使用解析后的论文列表
                    "avatar_url": entries["头像 URL:"].get(),
                    "backgound_url": entries["背景 URL:"].get(),
                    "h-index": int(entries["h-index:"].get() or 0)
                }
                
                if not member['name']:
                    messagebox.showerror("错误", "姓名不能为空")
                    return
                
                self.data.append(member)
                self._save_data()
                self._refresh_list()
                dialog.destroy()
                messagebox.showinfo("成功", f"已添加成员: {member['name']}\n论文数: {len(parsed_papers)}")
                
            except Exception as e:
                messagebox.showerror("错误", f"添加失败: {e}")
        
        ttk.Button(btn_frame, text="保存", command=save_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _edit_selected(self):
        """编辑选中的成员"""
        member = self._get_selected_member()
        if not member:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"编辑成员: {member['name']}")
        dialog.geometry("600x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ("姓名:", member['name']),
            ("职位:", member['position']),
            ("所属机构:", member['institution']),
            ("学术头衔:", member.get('title', '')),
            ("研究方向:", ', '.join(member.get('resfield', []))),
            ("个人简介:", member.get('bio', '')),
            ("头像 URL:", member.get('avatar_url', '')),
            ("背景 URL:", member.get('backgound_url', '')),
            ("h-index:", str(member.get('h-index', 0))),
        ]
        
        entries = {}
        for i, (label, default) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(form_frame, width=40)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))
            entries[label] = entry
        
        form_frame.columnconfigure(1, weight=1)
        
        # 论文管理区域
        paper_frame = ttk.LabelFrame(form_frame, text="论文管理", padding="5")
        paper_frame.grid(row=len(fields), column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        paper_frame.columnconfigure(0, weight=1)
        
        # 论文列表
        paper_listbox = tk.Listbox(paper_frame, height=6, width=50, font=('Microsoft YaHei', 9))
        paper_listbox.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 加载现有论文
        for paper in member.get('papers', []):
            venue = paper.get('journal') or paper.get('conference', 'N/A')
            display_text = f"{paper['title']} ({venue}, {paper.get('year', 'N/A')})"
            paper_listbox.insert(tk.END, display_text)
        
        def add_paper():
            """添加论文对话框"""
            paper_dialog = tk.Toplevel(dialog)
            paper_dialog.title("添加论文")
            paper_dialog.geometry("500x400")
            paper_dialog.transient(dialog)
            paper_dialog.grab_set()
            
            p_form = ttk.Frame(paper_dialog, padding="10")
            p_form.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(p_form, text="论文标题:").grid(row=0, column=0, sticky=tk.W, pady=5)
            p_title = ttk.Entry(p_form, width=40)
            p_title.grid(row=0, column=1, padx=10, pady=5)
            
            ttk.Label(p_form, text="类型:").grid(row=1, column=0, sticky=tk.W, pady=5)
            p_type_var = tk.StringVar(value="conference")
            ttk.Radiobutton(p_form, text="会议", variable=p_type_var, value="conference").grid(row=1, column=1, sticky=tk.W, padx=10)
            ttk.Radiobutton(p_form, text="期刊", variable=p_type_var, value="journal").grid(row=1, column=1, sticky=tk.E, padx=10)
            
            ttk.Label(p_form, text="会议/期刊名称:").grid(row=2, column=0, sticky=tk.W, pady=5)
            p_venue = ttk.Entry(p_form, width=40)
            p_venue.grid(row=2, column=1, padx=10, pady=5)
            
            ttk.Label(p_form, text="年份:").grid(row=3, column=0, sticky=tk.W, pady=5)
            p_year = ttk.Entry(p_form, width=40)
            p_year.insert(0, "2024")
            p_year.grid(row=3, column=1, padx=10, pady=5)
            
            ttk.Label(p_form, text="DOI:").grid(row=4, column=0, sticky=tk.W, pady=5)
            p_doi = ttk.Entry(p_form, width=40)
            p_doi.grid(row=4, column=1, padx=10, pady=5)
            
            def save_paper():
                title = p_title.get()
                venue = p_venue.get()
                year = p_year.get()
                doi = p_doi.get()
                
                if not title or not venue:
                    messagebox.showerror("错误", "标题和会议/期刊名称不能为空")
                    return
                
                paper_data = {
                    "title": title,
                    "year": int(year) if year else 2024,
                    "doi": doi if doi else "N/A"
                }
                
                if p_type_var.get() == "journal":
                    paper_data["journal"] = venue
                else:
                    paper_data["conference"] = venue
                
                member.setdefault('papers', []).append(paper_data)
                
                # 更新列表显示
                display_text = f"{title} ({venue}, {year})"
                paper_listbox.insert(tk.END, display_text)
                
                paper_dialog.destroy()
            
            p_btn_frame = ttk.Frame(p_form)
            p_btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
            ttk.Button(p_btn_frame, text="保存", command=save_paper).pack(side=tk.LEFT, padx=5)
            ttk.Button(p_btn_frame, text="取消", command=paper_dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        def delete_paper():
            """删除选中的论文"""
            selection = paper_listbox.curselection()
            if not selection:
                messagebox.showwarning("提示", "请先选择要删除的论文")
                return
            
            index = selection[0]
            confirm = messagebox.askyesno("确认删除", "确定要删除这篇论文吗？")
            if confirm:
                if 'papers' in member:
                    member['papers'].pop(index)
                paper_listbox.delete(index)
        
        paper_btn_frame = ttk.Frame(paper_frame)
        paper_btn_frame.grid(row=1, column=0, columnspan=3, pady=5)
        ttk.Button(paper_btn_frame, text="添加论文", command=add_paper).pack(side=tk.LEFT, padx=5)
        ttk.Button(paper_btn_frame, text="删除选中", command=delete_paper).pack(side=tk.LEFT, padx=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        def update_member():
            try:
                updates = {
                    'name': entries["姓名:"].get(),
                    'position': entries["职位:"].get(),
                    'institution': entries["所属机构:"].get(),
                    'title': entries["学术头衔:"].get(),
                    'resfield': [f.strip() for f in entries["研究方向:"].get().split(',') if f.strip()],
                    'bio': entries["个人简介:"].get(),
                    'avatar_url': entries["头像 URL:"].get(),
                    'backgound_url': entries["背景 URL:"].get(),
                    'h-index': int(entries["h-index:"].get() or 0)
                }
                
                for key, value in updates.items():
                    member[key] = value
                
                self._save_data()
                self._refresh_list()
                dialog.destroy()
                messagebox.showinfo("成功", "更新成功")
                
            except Exception as e:
                messagebox.showerror("错误", f"更新失败: {e}")
        
        ttk.Button(btn_frame, text="保存", command=update_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _delete_selected(self):
        """删除选中的成员"""
        member = self._get_selected_member()
        if not member:
            return
        
        confirm = messagebox.askyesno("确认删除", 
                                     f"确定要删除成员 '{member['name']}' (ID: {member['id']}) 吗？\n此操作不可恢复！")
        if confirm:
            self.data = [m for m in self.data if m['id'] != member['id']]
            self._save_data()
            self._refresh_list()
            self.detail_text.delete(1.0, tk.END)
            messagebox.showinfo("成功", "删除成功")


def main():
    """主函数"""
    root = tk.Tk()
    app = EditorManagerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

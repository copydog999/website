#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOI 解析演示工具 - 图形界面版本
输入 DOI，实时显示解析结果的 JSON 格式
"""

import json
import tkinter as tk
from tkinter import ttk, scrolledtext
import urllib.request
import urllib.parse


class DOIParserDemo:
    """DOI 解析演示工具"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DOI 解析演示工具")
        self.root.geometry("900x700")
        
        # 创建界面
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="DOI 解析演示工具", 
                               font=('Microsoft YaHei', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # 输入区域
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="输入 DOI:", font=('Microsoft YaHei', 10)).grid(
            row=0, column=0, padx=(0, 10))
        
        self.doi_var = tk.StringVar()
        doi_entry = ttk.Entry(input_frame, textvariable=self.doi_var, 
                             font=('Microsoft YaHei', 10), width=50)
        doi_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        doi_entry.bind('<Return>', lambda e: self.parse_doi())
        
        parse_btn = ttk.Button(input_frame, text="解析", command=self.parse_doi, 
                              width=10)
        parse_btn.grid(row=0, column=2)
        
        # 示例 DOI 按钮
        example_frame = ttk.Frame(main_frame)
        example_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(example_frame, text="示例 DOI:", font=('Microsoft YaHei', 9)).pack(
            side=tk.LEFT, padx=(0, 5))
        
        examples = [
            "10.20965/jaciii.2025.p1283",
            "10.1007/978-981-95-8411-6_44",
            "10.1109/TG.2023.3456789"
        ]
        
        for doi in examples:
            btn = ttk.Button(example_frame, text=doi[:30] + "...", 
                           command=lambda d=doi: self.set_doi(d), width=25)
            btn.pack(side=tk.LEFT, padx=2)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="解析结果 (JSON 格式)", 
                                     padding="10")
        result_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # JSON 显示文本框
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, 
                                                     font=('Consolas', 10),
                                                     bg='#1e1e1e', fg='#d4d4d4',
                                                     insertbackground='white')
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪 | 输入 DOI 后点击解析或按回车")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, font=('Microsoft YaHei', 9))
        status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def set_doi(self, doi):
        """设置示例 DOI"""
        self.doi_var.set(doi)
        self.parse_doi()
    
    def parse_doi(self):
        """解析 DOI"""
        doi = self.doi_var.get().strip()
        
        if not doi:
            self.status_var.set("错误: 请输入 DOI")
            self._show_error("请输入 DOI")
            return
        
        # 清理 DOI
        clean_doi = doi.replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
        
        self.status_var.set(f"正在解析: {clean_doi}...")
        self.root.config(cursor='watch')
        self.root.update()
        
        try:
            # 调用 CrossRef API
            url = f"https://api.crossref.org/works/{urllib.parse.quote(clean_doi)}"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'DOIParserDemo/1.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                work = data['message']
                
                # 提取关键信息
                result = {
                    "doi": clean_doi,
                    "title": work.get('title', [''])[0] if work.get('title') else "",
                    "authors": self._extract_authors(work),
                    "type": work.get('type', 'unknown'),
                    "venue_type": "journal" if work.get('type') in ['journal-article', 'article'] else "conference",
                    "venue": work.get('container-title', [''])[0] if work.get('container-title') else "",
                    "year": self._extract_year(work),
                    "publisher": work.get('publisher', ''),
                    "url": work.get('URL', ''),
                    "cited_by_count": work.get('is-referenced-by-count', 0),
                    "raw_data": work  # 保留原始数据
                }
                
                # 格式化 JSON 显示
                json_str = json.dumps(result, ensure_ascii=False, indent=2)
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, json_str)
                
                self.status_var.set(f"✓ 解析成功 | DOI: {clean_doi}")
                
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP 错误 {e.code}"
            if e.code == 404:
                error_msg += " - DOI 不存在"
            elif e.code == 429:
                error_msg += " - 请求过于频繁"
            self.status_var.set(f"✗ {error_msg}")
            self._show_error(error_msg)
            
        except Exception as e:
            error_msg = f"解析失败: {str(e)}"
            self.status_var.set(f"✗ {error_msg}")
            self._show_error(error_msg)
        
        finally:
            self.root.config(cursor='')
    
    def _extract_authors(self, work):
        """提取作者信息"""
        authors = work.get('author', [])
        result = []
        for author in authors:
            given = author.get('given', '')
            family = author.get('family', '')
            name = f"{given} {family}".strip()
            if name:
                result.append(name)
        return result
    
    def _extract_year(self, work):
        """提取年份"""
        if 'published-print' in work:
            return work['published-print'].get('date-parts', [[None]])[0][0]
        elif 'published-online' in work:
            return work['published-online'].get('date-parts', [[None]])[0][0]
        elif 'created' in work:
            return work['created'].get('date-parts', [[None]])[0][0]
        return None
    
    def _show_error(self, message):
        """显示错误信息"""
        self.result_text.delete(1.0, tk.END)
        error_json = {
            "error": True,
            "message": message,
            "hint": "请检查 DOI 是否正确，或稍后重试"
        }
        json_str = json.dumps(error_json, ensure_ascii=False, indent=2)
        self.result_text.insert(tk.END, json_str)


def main():
    """主函数"""
    root = tk.Tk()
    app = DOIParserDemo(root)
    root.mainloop()


if __name__ == '__main__':
    main()

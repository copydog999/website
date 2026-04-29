#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown参考文献引用转换工具
将[author-year]格式的引用转换为数字编号[1][2][3]格式
"""

import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


def select_md_file():
    """让用户选择MD文件"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    file_path = filedialog.askopenfilename(
        title="选择Markdown文件",
        filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
    )
    
    return file_path


def extract_references_order(content):
    """从参考文献部分提取引用顺序"""
    # 查找参考文献部分
    ref_pattern = r'##\s*参考文献[\s\S]*?(?=##|$)'
    ref_match = re.search(ref_pattern, content)
    
    if not ref_match:
        return [], None
    
    ref_section = ref_match.group(0)
    
    # 匹配多种格式的参考文献条目：
    # 1. [author-year] 开头
    # 2. 数字. [author-year]
    # 3. - [author-year]
    # 4. * [author-year]
    citation_pattern = r'(?:^|\n)\s*(?:\d+[\.、]\s*|-\s*|\*\s*)?\[([^\]]+)\]'
    citations = re.findall(citation_pattern, ref_section)
    
    # 过滤出看起来像 author-year 格式的引用
    author_year_citations = []
    seen = set()  # 用于去重
    for citation in citations:
        # 检查是否包含年份（通常是4位数字）
        if re.search(r'\d{4}', citation):
            # 去重，保持首次出现的顺序
            if citation not in seen:
                author_year_citations.append(citation)
                seen.add(citation)
    
    return author_year_citations, ref_match


def find_all_citations_in_text(content):
    """查找全文中所有的[author-year]格式引用及其位置"""
    # 匹配所有 [content] 格式，但排除纯数字的引用如[1][2]
    pattern = r'\[([^\]]+)\]'
    citations_with_pos = []
    
    for match in re.finditer(pattern, content):
        inner_content = match.group(1)
        # 检查是否是author-year格式（包含年份）
        if re.search(r'\d{4}', inner_content) and not inner_content.isdigit():
            citations_with_pos.append({
                'citation': inner_content,
                'position': match.start(),
                'match': match.group(0)
            })
    
    return citations_with_pos


def check_missing_citations(text_citations, ref_citations):
    """检查文中有引用但参考文献列表中没有的条目"""
    text_citation_set = set([c['citation'] for c in text_citations])
    ref_citation_set = set(ref_citations)
    
    missing = text_citation_set - ref_citation_set
    return list(missing)


def reorder_references_by_appearance(text_citations, ref_citations):
    """根据全文首次出现位置对参考文献重排序"""
    # 获取每个引用首次出现的位置
    first_appearance = {}
    for item in text_citations:
        citation = item['citation']
        if citation not in first_appearance:
            first_appearance[citation] = item['position']
    
    # 只保留在参考文献列表中存在的引用
    valid_citations = [c for c in ref_citations if c in first_appearance]
    
    # 按首次出现位置排序
    sorted_citations = sorted(valid_citations, key=lambda x: first_appearance[x])
    
    return sorted_citations


def convert_citations(content, citation_order):
    """将[author-year]格式的引用转换为数字编号"""
    if not citation_order:
        return content
    
    # 创建映射表：author-year -> 数字编号
    citation_map = {}
    for i, citation in enumerate(citation_order, 1):
        citation_map[citation] = str(i)
    
    # 定义替换函数
    def replace_citation(match):
        full_match = match.group(0)  # 包括方括号
        inner_content = match.group(1)  # 方括号内的内容
        
        if inner_content in citation_map:
            return f"[{citation_map[inner_content]}]"
        else:
            return full_match  # 如果不在映射中，保持原样
    
    # 替换所有 [content] 格式的文本
    pattern = r'\[([^\]]+)\]'
    converted_content = re.sub(pattern, replace_citation, content)
    
    return converted_content


def process_md_file(file_path):
    """处理MD文件的主函数"""
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"正在处理文件: {file_path}")
        
        # 提取参考文献顺序
        ref_citations, ref_match = extract_references_order(content)
        
        if not ref_citations:
            print("未找到参考文献部分或没有找到有效的引用")
            return False
        
        print(f"\n参考文献列表中找到 {len(ref_citations)} 个引用:")
        for i, citation in enumerate(ref_citations, 1):
            print(f"  [{i}] {citation}")
        
        # 查找全文中所有的引用及其位置
        text_citations = find_all_citations_in_text(content)
        print(f"\n全文中共找到 {len(text_citations)} 处引用")
        
        # 检查缺失的引用
        missing_citations = check_missing_citations(text_citations, ref_citations)
        if missing_citations:
            print(f"\n警告: 发现 {len(missing_citations)} 个在文中引用但未在参考文献列表中出现的条目:")
            for i, citation in enumerate(missing_citations, 1):
                print(f"  {i}. [{citation}]")
            
            # 询问用户是否继续
            root = tk.Tk()
            root.withdraw()
            result = messagebox.askyesno(
                "发现缺失引用",
                f"发现 {len(missing_citations)} 个在文中引用但未在参考文献列表中出现的条目。\n\n"
                f"是否继续处理？（建议先补充参考文献列表）"
            )
            root.destroy()
            
            if not result:
                print("用户取消了操作")
                return False
        else:
            print("\n检查通过: 所有文中引用都在参考文献列表中存在")
        
        # 根据全文首次出现位置重排序参考文献
        print("\n正在根据全文首次出现位置重排序参考文献...")
        sorted_citations = reorder_references_by_appearance(text_citations, ref_citations)
        
        print(f"\n重排序后的参考文献顺序 (共 {len(sorted_citations)} 个):")
        for i, citation in enumerate(sorted_citations, 1):
            # 找到该引用的首次出现位置（用于显示）
            first_pos = next((item['position'] for item in text_citations if item['citation'] == citation), 0)
            print(f"  [{i}] {citation} (首次出现在位置 {first_pos})")
        
        # 转换引用格式
        converted_content = convert_citations(content, sorted_citations)
        
        # 备份原文件
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n已创建备份文件: {backup_path}")
        
        # 写入转换后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(converted_content)
        
        print(f"\n文件转换完成: {file_path}")
        return True
        
    except Exception as e:
        print(f"处理文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


class CitationConverterApp:
    """参考文献转换工具的GUI应用"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown参考文献引用转换工具")
        self.root.geometry("800x600")
        
        self.file_path = None
        self.content = None
        self.ref_citations = []
        self.text_citations = []
        self.missing_citations = []
        self.sorted_citations = []
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建GUI组件"""
        # 顶部按钮区域
        top_frame = tk.Frame(self.root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)
        
        select_btn = tk.Button(top_frame, text="选择MD文件", command=self.select_file, 
                               font=("微软雅黑", 10), bg="#4CAF50", fg="white", padx=20)
        select_btn.pack(side=tk.LEFT, padx=5)
        
        self.file_label = tk.Label(top_frame, text="未选择文件", font=("微软雅黑", 9))
        self.file_label.pack(side=tk.LEFT, padx=10)
        
        # 文本显示区域
        text_frame = tk.Frame(self.root, padx=10, pady=5)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                    font=("Consolas", 10),
                                                    state=tk.DISABLED)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # 底部按钮区域
        bottom_frame = tk.Frame(self.root, padx=10, pady=10)
        bottom_frame.pack(fill=tk.X)
        
        self.step1_btn = tk.Button(bottom_frame, text="步骤1: 分析引用", 
                                   command=self.step1_analyze,
                                   font=("微软雅黑", 10), state=tk.DISABLED, padx=15)
        self.step1_btn.pack(side=tk.LEFT, padx=5)
        
        self.step2_btn = tk.Button(bottom_frame, text="步骤2: 检查缺失", 
                                   command=self.step2_check_missing,
                                   font=("微软雅黑", 10), state=tk.DISABLED, padx=15)
        self.step2_btn.pack(side=tk.LEFT, padx=5)
        
        self.step3_btn = tk.Button(bottom_frame, text="步骤3: 重排序", 
                                   command=self.step3_reorder,
                                   font=("微软雅黑", 10), state=tk.DISABLED, padx=15)
        self.step3_btn.pack(side=tk.LEFT, padx=5)
        
        self.step4_btn = tk.Button(bottom_frame, text="步骤4: 执行转换", 
                                   command=self.step4_convert,
                                   font=("微软雅黑", 10), state=tk.DISABLED, 
                                   bg="#FF9800", fg="white", padx=15)
        self.step4_btn.pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value="请选择MD文件开始")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor=tk.W, font=("微软雅黑", 9))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def append_text(self, text):
        """向文本区域追加内容"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
    
    def clear_text(self):
        """清空文本区域"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)
    
    def select_file(self):
        """选择MD文件"""
        file_path = filedialog.askopenfilename(
            title="选择Markdown文件",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.content = f.read()
                
                self.clear_text()
                self.append_text(f"已加载文件: {file_path}")
                self.append_text(f"文件大小: {len(self.content)} 字符")
                self.append_text("\n点击'步骤1: 分析引用'继续...")
                
                self.step1_btn.config(state=tk.NORMAL)
                self.step2_btn.config(state=tk.DISABLED)
                self.step3_btn.config(state=tk.DISABLED)
                self.step4_btn.config(state=tk.DISABLED)
                self.update_status("文件加载成功")
                
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败: {e}")
                self.update_status("文件读取失败")
    
    def step1_analyze(self):
        """步骤1: 分析引用"""
        if not self.content:
            return
        
        self.clear_text()
        self.append_text("=" * 60)
        self.append_text("步骤1: 分析引用")
        self.append_text("=" * 60)
        
        # 提取参考文献顺序
        self.ref_citations, ref_match = extract_references_order(self.content)
        
        if not self.ref_citations:
            self.append_text("\n错误: 未找到参考文献部分或没有找到有效的引用")
            self.update_status("分析失败")
            return
        
        self.append_text(f"\n参考文献列表中找到 {len(self.ref_citations)} 个引用:\n")
        for i, citation in enumerate(self.ref_citations, 1):
            self.append_text(f"  [{i}] {citation}")
        
        # 查找全文中所有的引用及其位置
        self.text_citations = find_all_citations_in_text(self.content)
        self.append_text(f"\n全文中共找到 {len(self.text_citations)} 处引用")
        
        self.append_text("\n分析完成！点击'步骤2: 检查缺失'继续...")
        self.step2_btn.config(state=tk.NORMAL)
        self.update_status("步骤1完成")
    
    def step2_check_missing(self):
        """步骤2: 检查缺失引用"""
        self.clear_text()
        self.append_text("=" * 60)
        self.append_text("步骤2: 检查缺失引用")
        self.append_text("=" * 60)
        
        # 检查缺失的引用
        self.missing_citations = check_missing_citations(self.text_citations, self.ref_citations)
        
        if self.missing_citations:
            self.append_text(f"\n警告: 发现 {len(self.missing_citations)} 个在文中引用但未在参考文献列表中出现的条目:\n")
            for i, citation in enumerate(self.missing_citations, 1):
                self.append_text(f"  {i}. [{citation}]")
            
            self.append_text("\n建议: 请先补充参考文献列表中的缺失条目")
            self.append_text("\n是否继续处理？")
            
            # 创建确认按钮
            btn_frame = tk.Frame(self.root)
            btn_frame.pack(pady=10)
            
            def on_continue():
                btn_frame.destroy()
                self.step3_btn.config(state=tk.NORMAL)
                self.update_status("步骤2完成 - 发现缺失但用户选择继续")
                self.append_text("\n用户选择继续处理...")
                self.append_text("点击'步骤3: 重排序'继续...")
            
            def on_cancel():
                btn_frame.destroy()
                self.update_status("步骤2取消")
                self.append_text("\n用户取消了操作")
            
            continue_btn = tk.Button(btn_frame, text="继续处理", command=on_continue,
                                    font=("微软雅黑", 10), bg="#4CAF50", fg="white", padx=20)
            continue_btn.pack(side=tk.LEFT, padx=10)
            
            cancel_btn = tk.Button(btn_frame, text="取消", command=on_cancel,
                                  font=("微软雅黑", 10), bg="#f44336", fg="white", padx=20)
            cancel_btn.pack(side=tk.LEFT, padx=10)
            
        else:
            self.append_text("\n检查通过: 所有文中引用都在参考文献列表中存在")
            self.append_text("\n点击'步骤3: 重排序'继续...")
            self.step3_btn.config(state=tk.NORMAL)
            self.update_status("步骤2完成 - 无缺失引用")
    
    def step3_reorder(self):
        """步骤3: 重排序参考文献"""
        self.clear_text()
        self.append_text("=" * 60)
        self.append_text("步骤3: 重排序参考文献")
        self.append_text("=" * 60)
        
        self.append_text("\n正在根据全文首次出现位置重排序参考文献...\n")
        self.sorted_citations = reorder_references_by_appearance(self.text_citations, self.ref_citations)
        
        self.append_text(f"重排序后的参考文献顺序 (共 {len(self.sorted_citations)} 个):\n")
        for i, citation in enumerate(self.sorted_citations, 1):
            # 找到该引用的首次出现位置（用于显示）
            first_pos = next((item['position'] for item in self.text_citations if item['citation'] == citation), 0)
            self.append_text(f"  [{i}] {citation} (首次出现在位置 {first_pos})")
        
        self.append_text("\n是否按此顺序执行转换？")
        
        # 创建确认按钮
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        def on_confirm():
            btn_frame.destroy()
            self.step4_btn.config(state=tk.NORMAL)
            self.update_status("步骤3完成")
            self.append_text("\n用户确认了排序结果")
            self.append_text("点击'步骤4: 执行转换'开始转换...")
        
        def on_modify():
            btn_frame.destroy()
            self.update_status("步骤3取消")
            self.append_text("\n用户取消了操作，请手动调整参考文献顺序后重试")
        
        confirm_btn = tk.Button(btn_frame, text="确认并继续", command=on_confirm,
                               font=("微软雅黑", 10), bg="#4CAF50", fg="white", padx=20)
        confirm_btn.pack(side=tk.LEFT, padx=10)
        
        modify_btn = tk.Button(btn_frame, text="取消", command=on_modify,
                              font=("微软雅黑", 10), bg="#f44336", fg="white", padx=20)
        modify_btn.pack(side=tk.LEFT, padx=10)
    
    def step4_convert(self):
        """步骤4: 执行转换"""
        if not self.sorted_citations:
            messagebox.showwarning("警告", "请先完成步骤3")
            return
        
        self.clear_text()
        self.append_text("=" * 60)
        self.append_text("步骤4: 执行转换")
        self.append_text("=" * 60)
        
        try:
            # 转换引用格式
            converted_content = convert_citations(self.content, self.sorted_citations)
            
            # 备份原文件
            backup_path = self.file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
            self.append_text(f"\n已创建备份文件: {backup_path}")
            
            # 写入转换后的内容
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(converted_content)
            
            self.append_text(f"\n文件转换完成: {self.file_path}")
            self.append_text("\n转换成功！")
            
            messagebox.showinfo("成功", "参考文献引用转换完成！")
            self.update_status("转换完成")
            
        except Exception as e:
            self.append_text(f"\n错误: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("错误", f"转换失败: {e}")
            self.update_status("转换失败")


def main():
    """主函数"""
    root = tk.Tk()
    app = CitationConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF转HTML代码转换器
支持将PDF文件转换为HTML代码片段
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import re
import tempfile
import webbrowser


class PDFToHTMLConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF转HTML代码转换器")
        self.root.geometry("1000x700")
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="PDF转HTML代码转换器", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 文件选择按钮
        self.select_button = ttk.Button(
            main_frame, 
            text="选择PDF文件", 
            command=self.select_pdf_file
        )
        self.select_button.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # 文件路径显示
        self.file_path_label = ttk.Label(main_frame, text="未选择文件", foreground="gray")
        self.file_path_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 转换选项
        options_frame = ttk.LabelFrame(main_frame, text="转换选项", padding="5")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 是否保留格式
        self.preserve_format_var = tk.BooleanVar(value=True)
        format_check = ttk.Checkbutton(options_frame, text="保留基本格式", variable=self.preserve_format_var)
        format_check.grid(row=0, column=0, padx=(0, 20))
        
        # 是否包含标题
        self.include_title_var = tk.BooleanVar(value=True)
        title_check = ttk.Checkbutton(options_frame, text="包含文件标题", variable=self.include_title_var)
        title_check.grid(row=0, column=1, padx=(0, 20))
        
        # 输出类型选择
        ttk.Label(options_frame, text="输出类型:").grid(row=0, column=2, padx=(0, 5))
        self.output_type = tk.StringVar(value="html")
        output_combo = ttk.Combobox(options_frame, textvariable=self.output_type, values=["html", "div_only"], state="readonly", width=15)
        output_combo.grid(row=0, column=3)
        
        # HTML内容显示区域
        ttk.Label(main_frame, text="转换后的HTML代码:").grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        self.html_area = scrolledtext.ScrolledText(
            main_frame, 
            wrap=tk.WORD, 
            width=100, 
            height=20,
            font=("Consolas", 10)
        )
        self.html_area.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        
        # 复制按钮
        self.copy_button = ttk.Button(
            button_frame, 
            text="复制HTML代码", 
            command=self.copy_html_to_clipboard
        )
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 预览按钮
        self.preview_button = ttk.Button(
            button_frame, 
            text="预览HTML", 
            command=self.preview_html
        )
        self.preview_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存按钮
        self.save_button = ttk.Button(
            button_frame, 
            text="保存为HTML文件", 
            command=self.save_html_to_file
        )
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空按钮
        self.clear_button = ttk.Button(
            button_frame, 
            text="清空内容", 
            command=self.clear_content
        )
        self.clear_button.pack(side=tk.LEFT)
        
    def select_pdf_file(self):
        """选择PDF文件"""
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[
                ("PDF文件", "*.pdf"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.file_path_label.config(text=f"文件: {os.path.basename(file_path)}")
            self.convert_pdf_to_html(file_path)
    
    def convert_pdf_to_html(self, file_path):
        """将PDF文件转换为HTML代码"""
        try:
            # 导入PyPDF2
            import PyPDF2
        except ImportError:
            messagebox.showerror(
                "错误", 
                "缺少PyPDF2库，请安装: pip install PyPDF2"
            )
            return
        
        try:
            # 使用PyPDF2提取文本
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            # 转换文本为HTML
            html_content = self.text_to_html(text)
            
            # 显示HTML内容
            self.html_area.delete(1.0, tk.END)
            self.html_area.insert(tk.END, html_content)
            
            messagebox.showinfo("成功", "PDF已成功转换为HTML代码！")
            
        except Exception as e:
            messagebox.showerror("错误", f"转换PDF文件时出错: {str(e)}")
    
    def text_to_html(self, text):
        """将文本转换为HTML格式"""
        # 处理换行
        paragraphs = text.split('\n')
        
        # 过滤掉空段落并去除每段开头和结尾的空白
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # 根据选项决定输出格式
        if self.output_type.get() == "html":
            # 完整的HTML结构
            html_parts = []
            
            if self.include_title_var.get():
                file_name = os.path.basename(getattr(self, 'current_file_path', 'Converted PDF'))
                html_parts.append(f'<h1>{self.escape_html(file_name)}</h1>')
            
            for para in paragraphs:
                if para.strip():  # 只处理非空段落
                    escaped_para = self.escape_html(para)
                    if self.preserve_format_var.get():
                        # 保留基本格式，将多个空格替换为&nbsp;
                        formatted_para = re.sub(r' {2,}', lambda m: '&nbsp;' * len(m.group()), escaped_para)
                        html_parts.append(f'<p>{formatted_para}</p>')
                    else:
                        html_parts.append(f'<p>{escaped_para}</p>')
            
            html_parts.append('</body>')
            html_parts.append('</html>')
            return '\n'.join(html_parts)
        else:
            # 仅输出div内容
            html_parts = ['<div class="pdf-content" style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;">']
            
            for para in paragraphs:
                if para.strip():  # 只处理非空段落
                    escaped_para = self.escape_html(para)
                    if self.preserve_format_var.get():
                        # 保留基本格式，将多个空格替换为&nbsp;
                        formatted_para = re.sub(r' {2,}', lambda m: '&nbsp;' * len(m.group()), escaped_para)
                        html_parts.append(f'<p style="margin: 10px 0;">{formatted_para}</p>')
                    else:
                        html_parts.append(f'<p style="margin: 10px 0;">{escaped_para}</p>')
            
            html_parts.append('</div>')
            return '\n'.join(html_parts)
    
    def escape_html(self, text):
        """转义HTML特殊字符"""
        if text is None:
            return ""
        return (text.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace('"', "&quot;")
                   .replace("'", "&#x27;"))
    
    def copy_html_to_clipboard(self):
        """复制HTML代码到剪贴板"""
        html_content = self.html_area.get(1.0, tk.END).strip()
        if html_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(html_content)
            messagebox.showinfo("成功", "HTML代码已复制到剪贴板！")
        else:
            messagebox.showwarning("警告", "没有可复制的HTML代码！")
    
    def preview_html(self):
        """预览HTML内容"""
        html_content = self.html_area.get(1.0, tk.END).strip()
        if not html_content:
            messagebox.showwarning("警告", "没有可预览的HTML内容！")
            return
        
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(html_content)
                temp_file_path = temp_file.name
            
            # 在浏览器中打开临时文件
            webbrowser.open('file://' + os.path.realpath(temp_file_path))
            
            messagebox.showinfo("预览", "HTML已在浏览器中打开预览！")
        except Exception as e:
            messagebox.showerror("错误", f"预览HTML时出错: {str(e)}")
    
    def save_html_to_file(self):
        """保存HTML代码到文件"""
        html_content = self.html_area.get(1.0, tk.END).strip()
        if not html_content:
            messagebox.showwarning("警告", "没有可保存的HTML代码！")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存HTML文件",
            defaultextension=".html",
            filetypes=[
                ("HTML文件", "*.html"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                messagebox.showinfo("成功", f"HTML文件已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件时出错: {str(e)}")
    
    def clear_content(self):
        """清空内容"""
        self.html_area.delete(1.0, tk.END)
        self.file_path_label.config(text="未选择文件")


def main():
    """主函数"""
    root = tk.Tk()
    app = PDFToHTMLConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
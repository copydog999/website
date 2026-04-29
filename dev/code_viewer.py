import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
import glob
from pathlib import Path


class CodeViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("代码查看器 - JOEST 项目")
        self.root.geometry("1000x700")
        
        # 创建文本框用于显示代码
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 10))
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建按钮框架
        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 加载代码按钮
        load_button = tk.Button(button_frame, text="加载代码", command=self.load_code)
        load_button.pack(side=tk.LEFT, padx=5)
        
        # 复制全部按钮
        copy_button = tk.Button(button_frame, text="复制全部", command=self.copy_all)
        copy_button.pack(side=tk.LEFT, padx=5)
        
        # 清空按钮
        clear_button = tk.Button(button_frame, text="清空", command=self.clear_text)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        self.status_label = tk.Label(root, text="就绪", anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=10, pady=5)
        
        # 存储所有代码内容
        self.all_code_content = ""
        
    def get_project_files(self):
        """获取项目中的所有文件并分类"""
        project_root = os.path.dirname(os.path.abspath(__file__))
        
        # 定义要搜索的文件扩展名及类别
        code_extensions = {
            '.html': '前端代码 (HTML)',
            '.css': '前端代码 (CSS)', 
            '.js': '前端代码 (JavaScript)',
            '.py': 'Python代码'
        }
        
        all_files = []
        
        # 遍历项目目录查找所有文件
        for root, dirs, files in os.walk(project_root):
            # 排除隐藏目录和某些特定目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', '.idea', 'node_modules']]
            
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                if ext in code_extensions:
                    category = code_extensions[ext]
                    all_files.append((file_path, category, 'code'))
                else:
                    # 其他文件类型，标记为非代码文件
                    all_files.append((file_path, f'其他文件 ({ext or "无扩展名"})', 'non-code'))
        
        return sorted(all_files, key=lambda x: x[0])  # 按路径排序
    
    def generate_file_tree(self, files):
        """生成文件树结构"""
        tree_lines = []
        tree_lines.append("=" * 60)
        tree_lines.append("项目文件树结构")
        tree_lines.append("=" * 60)
        
        # 构建目录树结构
        dir_structure = {}
        for file_path, category, file_type in files:
            rel_path = os.path.relpath(file_path, os.path.dirname(os.path.abspath(__file__)))
            parts = rel_path.split(os.sep)
            
            current_level = dir_structure
            for part in parts[:-1]:  # 处理目录部分
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            
            # 添加文件到对应目录
            if parts[-1] not in current_level:
                current_level[parts[-1]] = None  # None 表示这是文件而非目录
        
        def build_tree_str(structure, prefix="", is_last=True):
            result = []
            items = list(structure.items())
            
            for i, (name, children) in enumerate(items):
                is_last_item = (i == len(items) - 1)
                connector = "└── " if is_last_item else "├── "
                
                if children is None:  # 这是一个文件
                    result.append(f"{prefix}{connector}{name}")
                else:  # 这是一个目录
                    result.append(f"{prefix}{connector}{name}/")
                    extension = "    " if is_last_item else "│   "
                    result.extend(build_tree_str(children, prefix + extension, is_last_item))
            
            return result
        
        tree_content = build_tree_str(dir_structure)
        tree_lines.extend(tree_content)
        tree_lines.append("")  # 空行分隔
        
        return "\n".join(tree_lines)
    
    def load_code(self):
        """加载并显示所有代码"""
        try:
            self.text_area.delete(1.0, tk.END)
            self.all_code_content = ""
            
            files = self.get_project_files()
            
            if not files:
                messagebox.showinfo("提示", "未找到任何文件")
                return
            
            total_files = len(files)
            processed_files = 0
            
            # 首先生成并显示文件树
            file_tree = self.generate_file_tree(files)
            self.text_area.insert(tk.END, file_tree + "\n")
            self.all_code_content += file_tree + "\n"
            
            # 然后逐个处理文件内容
            for file_path, category, file_type in files:
                try:
                    relative_path = os.path.relpath(file_path, os.path.dirname(os.path.abspath(__file__)))
                    header = f"\n{'='*60}\n文件名：{relative_path}\n类别：{category}\n{'='*60}\n\n"
                    
                    if file_type == 'code':
                        # 读取代码文件内容
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        self.text_area.insert(tk.END, header)
                        self.text_area.insert(tk.END, content)
                        self.text_area.insert(tk.END, "\n")
                        
                        self.all_code_content += header + content + "\n"
                    else:
                        # 非代码文件，只显示占位信息
                        placeholder = f"[非代码文件，大小为 {os.path.getsize(file_path)} 字节]\n"
                        self.text_area.insert(tk.END, header)
                        self.text_area.insert(tk.END, placeholder)
                        self.text_area.insert(tk.END, "\n")
                        
                        self.all_code_content += header + placeholder + "\n"
                    
                    processed_files += 1
                    self.status_label.config(text=f"正在处理: {processed_files}/{total_files}")
                    self.root.update_idletasks()
                    
                except Exception as e:
                    error_msg = f"\n{'='*60}\n文件名：{file_path}\n错误：读取文件时出错 - {str(e)}\n{'='*60}\n\n"
                    self.text_area.insert(tk.END, error_msg)
                    self.all_code_content += error_msg
                    
            self.status_label.config(text=f"完成！共处理 {processed_files} 个文件")
            messagebox.showinfo("完成", f"成功加载 {processed_files} 个文件")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载代码时发生错误：{str(e)}")
            self.status_label.config(text="加载失败")
    
    def copy_all(self):
        """复制所有内容到剪贴板"""
        if not self.all_code_content:
            messagebox.showwarning("警告", "没有可复制的内容，请先加载代码")
            return
        
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.all_code_content)
            self.status_label.config(text="内容已复制到剪贴板")
            messagebox.showinfo("成功", "所有内容已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制到剪贴板失败：{str(e)}")
    
    def clear_text(self):
        """清空文本区域"""
        self.text_area.delete(1.0, tk.END)
        self.all_code_content = ""
        self.status_label.config(text="内容已清空")


def main():
    root = tk.Tk()
    app = CodeViewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
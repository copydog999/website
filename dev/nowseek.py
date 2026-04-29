#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JOEST 编辑部数据处理工具箱
统一的图形界面工具,集成所有编辑部数据处理功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


class JOESTDataToolsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NowSeek编辑部管理系统")
        self.root.geometry("1400x900")
        
        # 项目根目录
        self.project_root = Path(__file__).parent.parent
        self.dev_dir = Path(__file__).parent
        self.tools_dir = self.dev_dir / "tools"
        
        # 创建界面
        self.create_widgets()
        self.load_tools_info()
        
    def create_widgets(self):
        """创建主界面"""
        # 设置全局样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义颜色配置
        style.configure('Title.TLabel', 
                       font=('Microsoft YaHei', 16, 'bold'),
                       foreground='#2c3e50')
        style.configure('Subtitle.TLabel',
                       font=('Microsoft YaHei', 9),
                       foreground='#7f8c8d')
        style.configure('ToolName.TLabel',
                       font=('Microsoft YaHei', 11, 'bold'),
                       foreground='#34495e')
        style.configure('Accent.TButton',
                       font=('Microsoft YaHei', 10, 'bold'),
                       padding=10,
                       background='#3498db',
                       foreground='white')
        style.map('Accent.TButton',
                 background=[('active', '#2980b9'), ('pressed', '#21618c')])
        style.configure('Secondary.TButton',
                       font=('Microsoft YaHei', 9),
                       padding=8)
        
        # 主框架 - 增加边距
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 标题区域 - 使用Frame包裹,居中显示
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(header_frame, text="《电游科技》编辑部数据处理工作流",                               style='Title.TLabel')
        title_label.pack(anchor=tk.CENTER)
        
        subtitle_label = ttk.Label(header_frame, text="NowSeeker 编辑部管理系统 | 集成所有核心功能的统一工具平台",
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.CENTER, pady=(5, 0))
        
        # 左侧:工具列表 - 优化边框和间距
        tools_frame = ttk.LabelFrame(main_frame, text="  可用工具  ", padding="8")
        tools_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 12))
        tools_frame.columnconfigure(0, weight=1)
        tools_frame.rowconfigure(1, weight=1)
        
        # 工具列表框 - 美化
        self.tools_listbox = tk.Listbox(tools_frame, height=18, width=45,
                                       font=("Microsoft YaHei", 10),
                                       selectbackground='#3498db',
                                       selectforeground='white',
                                       activestyle='none',
                                       borderwidth=1,
                                       relief='flat')
        self.tools_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tools_listbox.bind('<<ListboxSelect>>', self.on_tool_select)
        
        # 滚动条
        tools_scrollbar = ttk.Scrollbar(tools_frame, orient=tk.VERTICAL, 
                                       command=self.tools_listbox.yview)
        tools_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tools_listbox.configure(yscrollcommand=tools_scrollbar.set)
        
        # 右侧:工具详情和操作区
        detail_frame = ttk.Frame(main_frame)
        detail_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(2, weight=1)
        
        # 工具信息面板 - 优化
        info_frame = ttk.LabelFrame(detail_frame, text="  工具信息  ", padding="12")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(0, weight=1)
        
        # 工具名称
        self.tool_name_var = tk.StringVar(value="请选择一个工具")
        name_label = ttk.Label(info_frame, textvariable=self.tool_name_var,
                              style='ToolName.TLabel')
        name_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        # 工具描述 - 优化背景色
        self.tool_desc_text = tk.Text(info_frame, height=4, width=60, 
                                     wrap=tk.WORD, font=("Microsoft YaHei", 9),
                                     state=tk.DISABLED, bg="#ecf0f1",
                                     borderwidth=0, relief='flat',
                                     padx=8, pady=8)
        self.tool_desc_text.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 工具参数配置区
        params_frame = ttk.LabelFrame(detail_frame, text="  参数配置  ", padding="12")
        params_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        params_frame.columnconfigure(0, weight=1)
        
        self.params_container = ttk.Frame(params_frame)
        self.params_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 操作按钮区 - 优化布局
        button_frame = ttk.Frame(detail_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        
        self.run_button = ttk.Button(button_frame, text="▶ 运行工具", 
                                    command=self.run_selected_tool,
                                    style="Accent.TButton")
        self.run_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.open_script_button = ttk.Button(button_frame, text="📁 打开脚本",
                                            command=self.open_script_location,
                                            style='Secondary.TButton')
        self.open_script_button.pack(side=tk.LEFT, padx=(0, 8))
        
        help_button = ttk.Button(button_frame, text="❓ 查看帮助",
                                command=self.show_tool_help,
                                style='Secondary.TButton')
        help_button.pack(side=tk.LEFT)
        
        # 日志输出区 - 优化
        log_frame = ttk.LabelFrame(detail_frame, text="  执行日志  ", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=14, width=80,
                                                 font=("Consolas", 9),
                                                 state=tk.DISABLED,
                                                 bg="#2c3e50",
                                                 fg="#ecf0f1",
                                                 insertbackground='white',
                                                 borderwidth=0,
                                                 relief='flat',
                                                 padx=10,
                                                 pady=8)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志控制按钮
        log_btn_frame = ttk.Frame(log_frame)
        log_btn_frame.grid(row=1, column=0, sticky=tk.E, pady=(5, 0))
        
        clear_log_btn = ttk.Button(log_btn_frame, text="清空日志",
                                  command=self.clear_log)
        clear_log_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        save_log_btn = ttk.Button(log_btn_frame, text="保存日志",
                                 command=self.save_log)
        save_log_btn.pack(side=tk.LEFT)
        
    def load_tools_info(self):
        """加载工具信息 - 仅显示核心常驻功能"""
        self.tools = [
            {
                "name": "通知公告管理",
                "script": "update_notifications.py",
                "description": "可视化管理通知公告数据,支持添加、修改、删除通知内容,自动更新 notification.json 文件。提供实时预览和备份功能。",
                "category": "内容管理",
                "params": []
            },
            {
                "name": "期刊发布更新",
                "script": "update_releases.py",
                "description": "更新期刊发布页面数据,整合最新论文信息,生成期刊阅览页面内容。功能强大的综合更新工具。",
                "category": "内容管理",
                "params": []
            },
            {
                "name": "编辑人员管理",
                "script": "manage_editors.py",
                "description": "管理编辑部人员信息,支持添加、修改、删除编辑人员,管理权限和角色分配。维护 nowledge.json 数据库。",
                "category": "团队管理",
                "params": []
            },
            {
                "name": "Gameme因子优化器",
                "script": "gmmf_optimizr.py",
                "description": "计算和优化 Gameme Factor,提供作者贡献度评估和学术影响力分析。",
                "category": "数据分析",
                "params": []
            },
            {
                "name": "本地Web服务器",
                "script": "local_webserver.py",
                "description": "启动本地HTTP服务器,用于预览和测试网站效果,支持JSON文件加载和CORS。",
                "category": "开发工具",
                "params": [
                    {"name": "port", "type": "number", "label": "端口号", 
                     "default": "8000", "required": False}
                ]
            },
            {
                "name": "部署工具",
                "script": "deploy.py",
                "description": "自动化部署工具,打包必要文件,准备上传到 Netlify 或其他托管平台。",
                "category": "部署工具",
                "params": []
            }
        ]
        
        # 填充工具列表
        for tool in self.tools:
            display_text = f"[{tool['category']}] {tool['name']}"
            self.tools_listbox.insert(tk.END, display_text)
            
    def on_tool_select(self, event):
        """工具选择事件"""
        if not self.tools_listbox.curselection():
            return
            
        index = self.tools_listbox.curselection()[0]
        tool = self.tools[index]
        
        # 更新工具信息
        self.tool_name_var.set(tool['name'])
        
        # 更新描述
        self.tool_desc_text.config(state=tk.NORMAL)
        self.tool_desc_text.delete(1.0, tk.END)
        self.tool_desc_text.insert(tk.END, tool['description'])
        self.tool_desc_text.config(state=tk.DISABLED)
        
        # 更新参数配置区
        self.update_params_area(tool)
        
        # 记录日志
        self.log(f"已选择工具: {tool['name']}")
        
    def update_params_area(self, tool):
        """更新参数配置区域"""
        # 清空现有参数控件
        for widget in self.params_container.winfo_children():
            widget.destroy()
        
        # 如果没有参数,显示提示
        if not tool.get('params'):
            label = ttk.Label(self.params_container, 
                            text="此工具无需额外参数,点击'运行工具'即可执行",
                            font=("Microsoft YaHei", 9), foreground="#666")
            label.grid(row=0, column=0, sticky=tk.W, pady=5)
            return
        
        # 创建参数输入控件
        self.param_vars = {}
        for i, param in enumerate(tool['params']):
            # 标签
            label = ttk.Label(self.params_container, text=f"{param['label']}:")
            label.grid(row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            
            # 根据类型创建不同的输入控件
            if param['type'] == 'directory':
                var = tk.StringVar(value=param.get('default', ''))
                self.param_vars[param['name']] = var
                
                frame = ttk.Frame(self.params_container)
                frame.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5)
                
                entry = ttk.Entry(frame, textvariable=var, width=40)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
                
                browse_btn = ttk.Button(frame, text="浏览...",
                                       command=lambda v=var: self.browse_directory(v))
                browse_btn.pack(side=tk.LEFT)
                
            elif param['type'] == 'file':
                var = tk.StringVar(value=param.get('default', ''))
                self.param_vars[param['name']] = var
                
                frame = ttk.Frame(self.params_container)
                frame.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5)
                
                entry = ttk.Entry(frame, textvariable=var, width=40)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
                
                browse_btn = ttk.Button(frame, text="浏览...",
                                       command=lambda v=var: self.browse_file(v))
                browse_btn.pack(side=tk.LEFT)
                
            else:  # text, number 等
                var = tk.StringVar(value=param.get('default', ''))
                self.param_vars[param['name']] = var
                
                entry = ttk.Entry(self.params_container, textvariable=var, width=40)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5)
        
    def browse_directory(self, var):
        """浏览选择目录"""
        directory = filedialog.askdirectory(initialdir=self.project_root)
        if directory:
            var.set(directory)
            
    def browse_file(self, var):
        """浏览选择文件"""
        file_path = filedialog.askopenfilename(initialdir=self.project_root)
        if file_path:
            var.set(file_path)
            
    def run_selected_tool(self):
        """运行选中的工具"""
        if not self.tools_listbox.curselection():
            messagebox.showwarning("警告", "请先选择一个工具")
            return
            
        index = self.tools_listbox.curselection()[0]
        tool = self.tools[index]
        
        # 构建命令 - 脚本在 tools 子目录中
        script_path = self.tools_dir / tool['script']
        
        if not script_path.exists():
            self.log(f"错误: 脚本文件不存在 - {script_path}")
            messagebox.showerror("错误", f"脚本文件不存在:\n{script_path}")
            return
        
        # 构建命令行参数
        cmd = [sys.executable, str(script_path)]
        
        # 添加用户输入的参数
        if hasattr(self, 'param_vars'):
            for param_name, var in self.param_vars.items():
                value = var.get().strip()
                if value:
                    cmd.append(value)
        
        # 记录执行的命令
        self.log("=" * 80)
        self.log(f"开始执行: {tool['name']}")
        self.log(f"脚本路径: {script_path}")
        self.log(f"命令: {' '.join(cmd)}")
        self.log("-" * 80)
        
        # 禁用运行按钮
        self.run_button.config(state=tk.DISABLED)
        
        # 在后台线程执行
        self.root.after(100, lambda: self.execute_command(cmd, tool['name']))
        
    def execute_command(self, cmd, tool_name):
        """执行命令并捕获输出"""
        try:
            # 本地Web服务器特殊处理 - 不等待完成
            if 'local_webserver' in cmd[1]:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    cwd=str(self.tools_dir),
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
                )
                self.log("-" * 80)
                self.log(f"✓ {tool_name} 已在新窗口启动")
                self.log(f"进程ID: {process.pid}")
                self.log("提示: 请在新打开的命令行窗口中查看服务器日志")
                self.run_button.config(state=tk.NORMAL)
                return
            
            # 其他工具正常执行
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                cwd=str(self.tools_dir)
            )
            
            # 实时读取输出
            for line in process.stdout:
                self.log(line.rstrip())
            
            # 等待进程完成
            process.wait()
            
            if process.returncode == 0:
                self.log("-" * 80)
                self.log(f"✓ {tool_name} 执行成功")
            else:
                self.log("-" * 80)
                self.log(f"✗ {tool_name} 执行失败 (返回码: {process.returncode})")
                messagebox.showerror("错误", f"{tool_name} 执行失败,请查看日志")
                
        except Exception as e:
            self.log(f"执行异常: {str(e)}")
            messagebox.showerror("错误", f"执行失败:\n{str(e)}")
        finally:
            # 恢复运行按钮(非服务器工具)
            if 'local_webserver' not in str(cmd):
                self.run_button.config(state=tk.NORMAL)
            
    def open_script_location(self):
        """打开脚本所在目录"""
        if not self.tools_listbox.curselection():
            messagebox.showwarning("警告", "请先选择一个工具")
            return
            
        index = self.tools_listbox.curselection()[0]
        tool = self.tools[index]
        
        script_path = self.tools_dir / tool['script']
        
        if script_path.exists():
            # Windows下用explorer打开
            if sys.platform == 'win32':
                os.startfile(str(self.tools_dir))
            else:
                subprocess.Popen(['open', str(self.dev_dir)])
        else:
            messagebox.showerror("错误", f"脚本文件不存在:\n{script_path}")
            
    def show_tool_help(self):
        """显示工具帮助信息"""
        if not self.tools_listbox.curselection():
            messagebox.showwarning("警告", "请先选择一个工具")
            return
            
        index = self.tools_listbox.curselection()[0]
        tool = self.tools[index]
        
        help_text = f"""
工具名称: {tool['name']}
分类: {tool['category']}
脚本: {tool['script']}

功能说明:
{tool['description']}

使用方法:
1. 在左侧列表中选择此工具
2. 如有需要,在右侧配置参数
3. 点击"运行工具"按钮执行
4. 在下方的日志区域查看执行结果

注意事项:
- 运行前建议先备份相关数据
- 某些工具可能需要较长时间执行
- 如遇问题,请查看详细日志输出
        """
        
        messagebox.showinfo(f"帮助 - {tool['name']}", help_text)
        
    def log(self, message):
        """添加日志"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log_text.update()
        
    def clear_log(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def save_log(self):
        """保存日志到文件"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=f"joest_tool_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("成功", f"日志已保存到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败:\n{str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置样式
    style = ttk.Style()
    style.theme_use('clam')
    
    # 配置自定义样式
    style.configure('Accent.TButton', 
                   font=('Microsoft YaHei', 10, 'bold'),
                   padding=10)
    
    app = JOESTDataToolsGUI(root)
    
    # 居中窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()

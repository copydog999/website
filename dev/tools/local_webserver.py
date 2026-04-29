#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地Web服务器
用于启动本地HTTP服务器，支持JSON文件的本地加载
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from urllib.parse import urlparse
import mimetypes
import subprocess


class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """支持CORS的请求处理器"""
    
    def end_headers(self):
        # 添加禁用缓存的头部
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def guess_type(self, path):
        """为JSON文件设置正确的MIME类型"""
        if path.endswith('.json'):
            return 'application/json'
        return super().guess_type(path)


def kill_existing_server(port=8000):
    """关闭占用端口的进程"""
    try:
        if sys.platform == 'win32':
            # Windows: 查找并关闭占用端口的进程
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            subprocess.run(['taskkill', '/F', '/PID', pid], 
                                         capture_output=True)
                            print(f"已关闭占用端口 {port} 的进程 (PID: {pid})")
                        except:
                            pass
    except Exception as e:
        print(f"关闭旧进程时出错: {e}")


def start_server(port=8000, directory="."):
    """启动本地HTTP服务器"""
    # 切换到指定目录
    os.chdir(directory)
    
    # 创建服务器
    with socketserver.TCPServer(("", port), CORSRequestHandler) as httpd:
        print(f"服务器启动在 http://localhost:{port}")
        print(f"目录: {os.path.abspath('.')}")
        print("按 Ctrl+C 停止服务器")
        
        # 打开浏览器
        webbrowser.open(f"http://localhost:{port}/index.html")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")


if __name__ == "__main__":
    # 获取项目根目录 - 从 tools 目录向上两级
    project_root = os.path.join(os.path.dirname(__file__), "..", "..")
    project_root = os.path.abspath(project_root)
    
    print("启动本地Web服务器...")
    print(f"项目根目录: {project_root}")
    
    port = 8000
    # 启动前先关闭已有服务器
    kill_existing_server(port)
    
    # 启动服务器
    start_server(port=port, directory=project_root)
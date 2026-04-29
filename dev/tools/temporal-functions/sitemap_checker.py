#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sitemap 验证爬虫
检查 sitemap.xml 中的所有 URL 是否可访问
"""

import xml.etree.ElementTree as ET
import requests
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style


def check_sitemap_urls(sitemap_path=None, generate_html_report=True):
    """
    检查 sitemap 中的所有 URL 是否可访问
    
    Args:
        sitemap_path: sitemap.xml 文件路径，默认为项目根目录
        generate_html_report: 是否生成 HTML 报告
    """
    # 初始化 colorama
    init()
    
    # 获取 sitemap 文件路径
    if sitemap_path is None:
        sitemap_path = Path(__file__).parent.parent / "sitemap.xml"
    
    # HTML 报告输出路径
    report_dir = Path(__file__).parent
    report_filename = f"sitemap_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    report_path = report_dir / report_filename
    
    if not sitemap_path.exists():
        print(f"{Fore.RED}✗ 错误：找不到 sitemap.xml 文件{Style.RESET_ALL}")
        return
    
    print(f"\n正在检查：{sitemap_path}")
    print("=" * 60)
    
    # 解析 sitemap.xml
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        
        # 处理 XML 命名空间
        ns = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        url_elements = root.findall('sitemap:url', ns)
        
        if not url_elements:
            # 尝试不带命名空间
            url_elements = root.findall('.//url')
        
        total_urls = len(url_elements)
        print(f"\n共发现 {total_urls} 个 URL\n")
        
    except Exception as e:
        print(f"{Fore.RED}✗ 解析 sitemap.xml 失败：{e}{Style.RESET_ALL}")
        return
    
    # 统计信息
    success_count = 0
    error_count = 0
    redirect_count = 0
    results = []
    
    # 逐个检查 URL
    for i, url_elem in enumerate(url_elements, 1):
        # 获取 URL loc
        loc_elem = url_elem.find('sitemap:loc', ns)
        if loc_elem is None:
            loc_elem = url_elem.find('loc')
        
        if loc_elem is None or not loc_elem.text:
            continue
        
        url = loc_elem.text.strip()
        
        # 显示进度
        print(f"[{i}/{total_urls}] 检查：{url}")
        
        try:
            # 发送 HTTP 请求
            response = requests.get(url, timeout=10, allow_redirects=True)
            
            status_code = response.status_code
            
            if status_code == 200:
                print(f"  {Fore.GREEN}✓ 正常 (200 OK){Style.RESET_ALL}")
                success_count += 1
                results.append((url, "OK", status_code))
                
            elif 300 <= status_code < 400:
                print(f"  {Fore.YELLOW}⚠ 重定向 ({status_code}){Style.RESET_ALL}")
                redirect_count += 1
                results.append((url, "Redirect", status_code, response.url if response.url != url else None))
                
            else:
                print(f"  {Fore.RED}✗ 错误 ({status_code}){Style.RESET_ALL}")
                error_count += 1
                results.append((url, "Error", status_code, None))
                
        except requests.exceptions.Timeout:
            print(f"  {Fore.RED}✗ 超时 (Timeout){Style.RESET_ALL}")
            error_count += 1
            results.append((url, "Timeout", 0, None))
            
        except requests.exceptions.ConnectionError:
            print(f"  {Fore.RED}✗ 连接失败 (Connection Error){Style.RESET_ALL}")
            error_count += 1
            results.append((url, "ConnectionError", 0, None))
            
        except Exception as e:
            print(f"  {Fore.RED}✗ 未知错误：{e}{Style.RESET_ALL}")
            error_count += 1
            results.append((url, "Error", str(e), None))
        
        print()
    
    # 输出总结报告
    print("\n" + "=" * 60)
    print("检查报告")
    print("=" * 60)
    print(f"总 URL 数：{total_urls}")
    print(f"{Fore.GREEN}正常访问：{success_count}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}重定向：{redirect_count}{Style.RESET_ALL}")
    print(f"{Fore.RED}错误：{error_count}{Style.RESET_ALL}")
    print(f"成功率：{(success_count/total_urls*100):.1f}%")
    print("=" * 60)
    
    # 如果有错误，列出详细信息
    if error_count > 0:
        print(f"\n{Fore.RED}问题 URL 列表:{Style.RESET_ALL}")
        for url, status, code in results:
            if status in ["Error", "Timeout", "ConnectionError"]:
                print(f"  {Fore.RED}✗ {url} - {status}: {code}{Style.RESET_ALL}")
    
    print()
    
    # 生成 HTML 报告
    if generate_html_report:
        generate_html_report_func(results, report_path, total_urls, success_count, redirect_count, error_count)
    
    return results


def generate_html_report_func(results, report_path, total_urls, success_count, redirect_count, error_count):
    """
    生成 HTML 格式的sitemap检查报告
    
    Args:
        results: 检查结果列表
        report_path: 报告文件路径
        total_urls: 总URL数
        success_count: 成功数量
        redirect_count: 重定向数量
        error_count: 错误数量
    """
    # 计算成功率
    success_rate = (success_count / total_urls * 100) if total_urls > 0 else 0
    
    # 生成检查时间
    check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 构建 HTML 内容
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sitemap 检查报告 - {check_time}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.95em;
        }}
        
        .stat-success .stat-number {{ color: #10b981; }}
        .stat-redirect .stat-number {{ color: #f59e0b; }}
        .stat-error .stat-number {{ color: #ef4444; }}
        .stat-rate .stat-number {{ color: #3b82f6; }}
        
        .content {{
            padding: 30px;
        }}
        
        .content h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .status-ok {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .status-redirect {{
            background: #fef3c7;
            color: #92400e;
        }}
        
        .status-error {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .url-link {{
            color: #667eea;
            text-decoration: none;
            word-break: break-all;
        }}
        
        .url-link:hover {{
            text-decoration: underline;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}
            
            table {{
                font-size: 0.9em;
            }}
            
            th, td {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Sitemap 检查报告</h1>
            <p>检查时间：{check_time}</p>
        </div>
        
        <div class="summary">
            <div class="stat-card stat-total">
                <div class="stat-number">{total_urls}</div>
                <div class="stat-label">总 URL 数</div>
            </div>
            <div class="stat-card stat-success">
                <div class="stat-number">{success_count}</div>
                <div class="stat-label">正常访问</div>
            </div>
            <div class="stat-card stat-redirect">
                <div class="stat-number">{redirect_count}</div>
                <div class="stat-label">重定向</div>
            </div>
            <div class="stat-card stat-error">
                <div class="stat-number">{error_count}</div>
                <div class="stat-label">错误</div>
            </div>
            <div class="stat-card stat-rate">
                <div class="stat-number">{success_rate:.1f}%</div>
                <div class="stat-label">成功率</div>
            </div>
        </div>
        
        <div class="content">
            <h2>详细检查结果</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>URL</th>
                        <th>状态</th>
                        <th>HTTP 代码</th>
                        <th>最终地址</th>
                    </tr>
                </thead>
                <tbody>
'''
    
    # 添加每一行数据
    for i, result in enumerate(results, 1):
        url = result[0]
        status = result[1]
        code = result[2]
        final_url = result[3] if len(result) > 3 else None
        
        # 确定状态样式
        if status == "OK":
            status_text = "✓ 正常"
            status_class = "status-ok"
        elif status == "Redirect":
            status_text = "⚠ 重定向"
            status_class = "status-redirect"
        else:
            status_text = "✗ 错误"
            status_class = "status-error"
        
        # 处理最终地址
        final_url_display = "-"
        if final_url and final_url != url:
            final_url_display = f'<a href="{final_url}" class="url-link" target="_blank">{final_url}</a>'
        elif status == "Redirect":
            final_url_display = "未检测到变化"
        
        html_content += f'''                    <tr>
                        <td>{i}</td>
                        <td><a href="{url}" class="url-link" target="_blank">{url}</a></td>
                        <td><span class="status-badge {status_class}">{status_text}</span></td>
                        <td>{code}</td>
                        <td>{final_url_display}</td>
                    </tr>
'''
    
    # 关闭 HTML 标签
    html_content += '''                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>由 Sitemap Checker 自动生成 | JOEST Project</p>
        </div>
    </div>
</body>
</html>
'''
    
    # 写入文件
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n{Fore.GREEN}✓ HTML 报告已生成：{report_path}{Style.RESET_ALL}")


if __name__ == "__main__":
    check_sitemap_urls()

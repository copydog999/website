#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sitemap 生成器
为 JOEST 网站生成 XML sitemap 文件
"""

import os
from datetime import datetime
from pathlib import Path


def generate_sitemap(base_url="https://journalofest.netlify.app", output_dir=None):
    """
    生成网站的 sitemap.xml 文件
    
    Args:
        base_url: 网站的基础 URL
        output_dir: 输出目录,默认为项目根目录
    """
    # 获取项目根目录
    if output_dir is None:
        output_dir = Path(__file__).parent.parent
    
    # 需要包含的文件扩展名
    include_extensions = {".html"}
    
    # 需要排除的目录
    exclude_dirs = {"dev", "articles", ".idea", "node_modules", "__pycache__", ".git"}
    
    # 需要排除的文件名
    exclude_files = {"sitemap.xml"}
    
    # 获取当前日期（ISO 8601 格式）
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 构建 XML 内容
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    
    # 收集所有符合条件的文件
    all_files = []
    
    for root, dirs, files in os.walk(output_dir):
        # 过滤排除的目录（原地修改，避免进入这些目录）
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(output_dir)
            
            # 检查文件扩展名
            if file_path.suffix.lower() not in include_extensions:
                continue
            
            # 检查是否在排除文件列表中
            if file in exclude_files:
                continue
            
            all_files.append(relative_path)
    
    # 按路径排序
    all_files.sort()
    
    url_count = 0
    
    # 添加首页（优先级最高）
    index_path = Path("index.html")
    if index_path in all_files:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{base_url}/</loc>")
        xml_lines.append(f"    <lastmod>{today}</lastmod>")
        xml_lines.append("    <changefreq>daily</changefreq>")
        xml_lines.append("    <priority>1.0</priority>")
        xml_lines.append("  </url>")
        url_count += 1
    
    # 添加其他文件
    for relative_path in all_files:
        # 跳过 index.html，因为已经作为首页处理
        if relative_path == Path("index.html"):
            continue
        
        file_path = output_dir / relative_path
        
        # 获取文件的最后修改时间
        lastmod = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d")
        
        # 根据文件类型设置优先级和更新频率
        suffix = relative_path.suffix.lower()
        filename = relative_path.name
        
        if suffix == ".html":
            # HTML 页面：根据文件名动态判断重要性
            if filename in ["notifications.html", "releases.html"]:
                priority = "1.0"
                changefreq = "daily"
            elif filename == "report.html":
                priority = "1.0"
                changefreq = "monthly"
            else:
                priority = "1.0"
                changefreq = "weekly"
        elif suffix in [".js", ".css"]:
            # JS 和 CSS 文件
            priority = "0.6"
            changefreq = "monthly"
        elif suffix == ".json":
            # JSON 数据文件
            priority = "0.7"
            changefreq = "weekly"
        elif suffix == ".xml":
            # XML 文件
            priority = "0.7"
            changefreq = "monthly"
        elif suffix == ".md":
            # Markdown 文件
            priority = "0.6"
            changefreq = "monthly"
        else:
            priority = "0.5"
            changefreq = "monthly"
        
        # 构建 URL 路径（统一使用正斜杠）
        url_path = str(relative_path).replace("\\", "/")
        
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{base_url}/{url_path}</loc>")
        xml_lines.append(f"    <lastmod>{lastmod}</lastmod>")
        xml_lines.append(f"    <changefreq>{changefreq}</changefreq>")
        xml_lines.append(f"    <priority>{priority}</priority>")
        xml_lines.append("  </url>")
        url_count += 1
    
    # 关闭 urlset
    xml_lines.append("</urlset>")
    
    # 写入文件
    output_path = output_dir / "sitemap.xml"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines))
    
    print(f"✓ Sitemap 已生成：{output_path}")
    print(f"  共包含 {url_count} 个 URL")
    
    return output_path


if __name__ == "__main__":
    generate_sitemap()

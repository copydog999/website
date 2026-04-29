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
        output_dir: 输出目录，默认为项目根目录
    """
    # 获取项目根目录
    if output_dir is None:
        output_dir = Path(__file__).parent.parent
    
    # 需要包含的 HTML 页面
    html_files = [
        "index.html",
        "releases.html",
        "nowbase.html",
        "notifications.html",
        "infos.html",
        "opensource.html",
        "editorial.html",
        "report.html",
    ]
    
    # 特殊页面（在 database 子目录下）
    special_pages = [
        "database/nowgraph.html",
        "database/stat.html",
    ]
    
    # 需要排除的目录
    exclude_dirs = ["dev", "articles"]
    
    # 获取当前日期（ISO 8601 格式）
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 构建 XML 内容
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    
    # 添加首页（优先级最高）
    xml_lines.append("  <url>")
    xml_lines.append(f"    <loc>{base_url}/</loc>")
    xml_lines.append(f"    <lastmod>{today}</lastmod>")
    xml_lines.append("    <changefreq>daily</changefreq>")
    xml_lines.append("    <priority>1.0</priority>")
    xml_lines.append("  </url>")
    
    # 添加其他 HTML 页面
    for html_file in html_files:
        file_path = output_dir / html_file
        if file_path.exists():
            # 检查是否在排除目录中
            if any(exclude_dir in str(file_path.relative_to(output_dir)) for exclude_dir in exclude_dirs):
                continue
                
            # 获取文件的最后修改时间
            lastmod = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d")
            
            # 设置优先级和更新频率
            priority = "0.8"
            changefreq = "weekly"
            
            # 特殊页面特殊处理
            if html_file in ["notifications.html", "releases.html"]:
                priority = "0.9"
                changefreq = "daily"
            elif html_file in ["report.html"]:
                priority = "0.5"
                changefreq = "monthly"
            
            xml_lines.append("  <url>")
            xml_lines.append(f"    <loc>{base_url}/{html_file}</loc>")
            xml_lines.append(f"    <lastmod>{lastmod}</lastmod>")
            xml_lines.append(f"    <changefreq>{changefreq}</changefreq>")
            xml_lines.append(f"    <priority>{priority}</priority>")
            xml_lines.append("  </url>")
    
    # 添加特殊页面
    for page in special_pages:
        file_path = output_dir / page
        if file_path.exists():
            # 检查是否在排除目录中
            if any(exclude_dir in str(file_path.relative_to(output_dir)) for exclude_dir in exclude_dirs):
                continue
                
            lastmod = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d")
            
            xml_lines.append("  <url>")
            xml_lines.append(f"    <loc>{base_url}/{page}</loc>")
            xml_lines.append(f"    <lastmod>{lastmod}</lastmod>")
            xml_lines.append("    <changefreq>weekly</changefreq>")
            xml_lines.append("    <priority>0.7</priority>")
            xml_lines.append("  </url>")
    
    # 关闭 urlset
    xml_lines.append("</urlset>")
    
    # 写入文件
    output_path = output_dir / "sitemap.xml"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines))
    
    print(f"✓ Sitemap 已生成：{output_path}")
    print(f"  共包含 {len(html_files) + len(special_pages) + 1} 个 URL")
    
    return output_path


if __name__ == "__main__":
    generate_sitemap()

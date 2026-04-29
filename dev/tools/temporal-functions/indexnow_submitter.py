#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexNow 提交工具
向 Bing 等搜索引擎主动推送新 URL
"""

import requests
from pathlib import Path


def submit_to_indexnow(urls, api_key=None):
    """
    使用 IndexNow 协议向 Bing 提交 URL
    
    Args:
        urls: URL 列表或单个 URL 字符串
        api_key: API 密钥（可选，不提供则自动生成）
    """
    # 如果是单个 URL，转为列表
    if isinstance(urls, str):
        urls = [urls]
    
    # 生成 API Key（基于主机名的哈希）
    if not api_key:
        import hashlib
        # 从第一个 URL 提取主机名
        from urllib.parse import urlparse
        hostname = urlparse(urls[0]).hostname
        api_key = hashlib.sha256(hostname.encode()).hexdigest()
    
    # IndexNow API 端点
    endpoint = "https://api.indexnow.org/indexnow"
    
    # 请求数据
    payload = {
        "host": "journalofest.netlify.app",
        "key": api_key,
        "keyLocation": f"https://journalofest.netlify.app/{api_key}.txt",
        "urlList": urls
    }
    
    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        
        if response.status_code in [200, 202]:
            print(f"✓ 成功提交 {len(urls)} 个 URL 到 IndexNow")
            print(f"  HTTP 状态码：{response.status_code}")
            print(f"  API Key: {api_key[:16]}...")
            return True
        else:
            print(f"✗ 提交失败：{response.status_code}")
            print(f"  响应：{response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 提交出错：{e}")
        return False


def generate_key_file(output_dir=None):
    """
    生成 API Key 文件（用于验证）
    
    Args:
        output_dir: 输出目录，默认为项目根目录
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent
    
    import hashlib
    hostname = "journalofest.netlify.app"
    api_key = hashlib.sha256(hostname.encode()).hexdigest()
    
    # 创建 key 文件
    key_file_path = output_dir / f"{api_key}.txt"
    
    with open(key_file_path, 'w', encoding='utf-8') as f:
        f.write(api_key)
    
    print(f"✓ API Key 文件已生成：{key_file_path}")
    print(f"  Key: {api_key}")
    
    return api_key


if __name__ == "__main__":
    # 示例：提交所有 sitemap 中的 URL
    import xml.etree.ElementTree as ET
    
    sitemap_path = Path(__file__).parent.parent / "sitemap.xml"
    
    if sitemap_path.exists():
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        
        ns = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        url_elements = root.findall('sitemap:url', ns)
        
        if not url_elements:
            url_elements = root.findall('.//url')
        
        urls = []
        for url_elem in url_elements:
            loc_elem = url_elem.find('sitemap:loc', ns)
            if loc_elem is None:
                loc_elem = url_elem.find('loc')
            
            if loc_elem is not None and loc_elem.text:
                urls.append(loc_elem.text.strip())
        
        if urls:
            print(f"\n准备提交 {len(urls)} 个 URL 到 IndexNow...\n")
            
            # 生成 key 文件
            generate_key_file()
            
            # 分批提交（每次最多 10000 个）
            batch_size = 100
            for i in range(0, len(urls), batch_size):
                batch = urls[i:i + batch_size]
                print(f"\n提交批次 {i//batch_size + 1}...")
                submit_to_indexnow(batch)
        else:
            print("✗ 未找到 URL")
    else:
        print("✗ 找不到 sitemap.xml 文件")

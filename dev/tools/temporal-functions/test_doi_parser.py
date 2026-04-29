#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOI 解析测试脚本
用于测试 CrossRef API 的论文信息获取功能
"""

import json
import urllib.request
import urllib.parse


def fetch_paper_by_doi(doi):
    """
    根据 DOI 获取论文信息
    
    Args:
        doi: DOI 字符串
        
    Returns:
        dict: 包含标题、年份、期刊/会议名称等信息的字典
    """
    # 清理 DOI（移除 URL 前缀）
    doi = doi.replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
    
    print(f"正在查询 DOI: {doi}")
    print("-" * 60)
    
    try:
        # 使用 CrossRef API
        url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'DOITestScript/1.0')
        
        print(f"请求 URL: {url}\n")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            work = data['message']
            
            # 提取标题
            title = work.get('title', [''])[0]
            
            # 提取年份
            year = None
            if 'published-print' in work:
                year = work['published-print'].get('date-parts', [[None]])[0][0]
            elif 'published-online' in work:
                year = work['published-online'].get('date-parts', [[None]])[0][0]
            elif 'created' in work:
                year = work['created'].get('date-parts', [[None]])[0][0]
            
            # 提取期刊或会议名称
            container_title = work.get('container-title', [''])[0]
            
            # 提取类型
            type_value = work.get('type', 'unknown')
            venue_type = "期刊" if type_value in ['journal-article', 'article'] else "会议"
            
            # 提取作者
            authors = work.get('author', [])
            author_names = []
            for author in authors[:3]:  # 只显示前3个作者
                given = author.get('given', '')
                family = author.get('family', '')
                author_names.append(f"{given} {family}")
            if len(authors) > 3:
                author_names.append("等")
            
            # 输出结果
            print("✓ 解析成功！\n")
            print(f"标题: {title}")
            print(f"作者: {', '.join(author_names)}")
            print(f"类型: {venue_type}")
            print(f"期刊/会议: {container_title}")
            print(f"年份: {year}")
            print(f"DOI: {doi}")
            
            return {
                "title": title,
                "year": year,
                "venue": container_title,
                "venue_type": venue_type,
                "doi": doi
            }
            
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP 错误: {e.code}")
        if e.code == 404:
            print("  DOI 不存在或无法找到")
        elif e.code == 429:
            print("  请求过于频繁，请稍后再试")
        else:
            print(f"  错误详情: {e.reason}")
        return None
        
    except urllib.error.URLError as e:
        print(f"✗ 网络错误: {e.reason}")
        print("  请检查网络连接")
        return None
        
    except Exception as e:
        print(f"✗ 解析失败: {str(e)}")
        return None


def main():
    """主函数 - 测试多个 DOI"""
    
    # 测试用例
    test_dois = [
        "10.20965/jaciii.2025.p1283",  # 期刊论文
        "10.1007/978-981-95-8411-6_44",  # 会议论文
        "10.1109/TG.2023.3456789",  # IEEE 期刊
    ]
    
    print("=" * 60)
    print("DOI 解析测试工具")
    print("=" * 60)
    print()
    
    for i, doi in enumerate(test_dois, 1):
        print(f"\n【测试 {i}/{len(test_dois)}】")
        result = fetch_paper_by_doi(doi)
        print("\n" + "=" * 60)
        
        if i < len(test_dois):
            input("\n按回车继续下一个测试...")
    
    # 交互式测试
    print("\n\n=== 交互式测试 ===")
    print("输入 DOI 进行解析（输入 q 退出）\n")
    
    while True:
        doi = input("请输入 DOI: ").strip()
        if doi.lower() == 'q':
            break
        if doi:
            fetch_paper_by_doi(doi)
            print()


if __name__ == '__main__':
    main()

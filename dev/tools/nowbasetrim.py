#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NowBase数据清理工具 - 清除第三卷论文摘要字段中的空格
"""

import json
from pathlib import Path


def trim_volume3_abstracts():
    """清除第三卷论文摘要字段中的所有空格"""
    
    # 数据文件路径
    script_dir = Path(__file__).parent
    data_file = script_dir.parent.parent / "database" / "data" / "nowbase.json"
    
    if not data_file.exists():
        print(f"错误: 文件 {data_file} 不存在")
        return
    
    # 加载数据
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"错误: JSON格式错误 - {e}")
        return
    
    # 统计信息
    total_papers = len(data)
    volume3_papers = [p for p in data if p.get('volume') == 3]
    modified_count = 0
    
    print(f"总论文数: {total_papers}")
    print(f"第三卷论文数: {len(volume3_papers)}")
    print("-" * 60)
    
    # 处理第三卷论文
    for paper in volume3_papers:
        if 'abstract' in paper and paper['abstract']:
            original_abstract = paper['abstract']
            # 移除所有空格（包括普通空格、全角空格等）
            trimmed_abstract = original_abstract.replace(' ', '').replace(' ', '')
            
            if original_abstract != trimmed_abstract:
                paper['abstract'] = trimmed_abstract
                modified_count += 1
                print(f"ID {paper['id']}: {paper['title'][:40]}...")
                print(f"  原始长度: {len(original_abstract)}")
                print(f"  清理后长度: {len(trimmed_abstract)}")
                print(f"  移除空格数: {len(original_abstract) - len(trimmed_abstract)}")
    
    print("-" * 60)
    print(f"共修改 {modified_count} 篇论文的摘要")
    
    # 保存数据
    try:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ 数据已保存到 {data_file}")
    except Exception as e:
        print(f"错误: 保存失败 - {e}")
        return
    
    print("✓ 处理完成")


if __name__ == '__main__':
    trim_volume3_abstracts()

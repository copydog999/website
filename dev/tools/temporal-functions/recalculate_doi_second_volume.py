#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新计算"电子游戏科学与技术 第二卷"所有论文的DOI并检查冲突
"""

import json
import os
import hashlib
from datetime import datetime

def generate_doi_from_paper(paper):
    """根据新标准生成DOI: 版号-卷号-索引-年份-分类码"""
    # 获取DOI生成所需的各个部分
    edition = paper.get('edition', 'PS')  # 版号，默认PS
    volume = paper.get('volume', 1)       # 卷号
    index = paper.get('index', '')        # 索引
    year = paper.get('year', '2026')      # 年份
    category = paper.get('doc_category', 'R')  # 分类码，默认R
    
    # 验证必需字段
    if not index:
        print(f"警告: 论文 '{paper.get('title', 'Unknown')}' 缺少索引字段")
        # 如果没有索引，使用ID作为替代
        index = str(paper.get('id', '0'))
    
    # 生成DOI
    new_doi = f"{edition}-{volume}-{index}-{year}-{category}"
    
    return new_doi

def check_doi_conflicts(papers):
    """检查DOI冲突"""
    doi_count = {}
    conflicts = []
    
    for paper in papers:
        doi = paper.get('nowbasedoi', '')
        if doi:
            if doi in doi_count:
                doi_count[doi].append(paper['id'])
                if doi not in conflicts:
                    conflicts.append(doi)
            else:
                doi_count[doi] = [paper['id']]
    
    return conflicts, doi_count

def recalculate_second_volume_dois():
    """重新计算第二卷论文的DOI"""
    json_file_path = "../database/data/nowbase.json"
    
    # 读取JSON文件
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            papers = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {json_file_path}")
        return
    except json.JSONDecodeError:
        print(f"错误: JSON文件格式错误 {json_file_path}")
        return
    
    # 筛选出第二卷的论文
    second_volume_papers = []
    other_papers = []
    
    for paper in papers:
        if paper.get('issue') == "电子游戏科学与技术 第二卷":
            second_volume_papers.append(paper)
        else:
            other_papers.append(paper)
    
    print(f"找到第二卷论文 {len(second_volume_papers)} 篇")
    print(f"其他卷论文 {len(other_papers)} 篇")
    
    if not second_volume_papers:
        print("未找到第二卷的论文")
        return
    
    # 检查原始DOI冲突
    all_conflicts_before, _ = check_doi_conflicts(papers)
    second_volume_conflicts_before = [conflict for conflict in all_conflicts_before 
                                    if any(paper.get('nowbasedoi') == conflict 
                                         for paper in second_volume_papers)]
    
    print(f"\n重新计算前的DOI冲突:")
    if second_volume_conflicts_before:
        for conflict in second_volume_conflicts_before:
            conflict_papers = [p for p in second_volume_papers if p.get('nowbasedoi') == conflict]
            print(f"  DOI {conflict}: {[p['title'] for p in conflict_papers]}")
    else:
        print("  无冲突")
    
    # 重新计算第二卷论文的DOI
    print(f"\n开始重新计算第二卷论文的DOI...")
    recalculated_count = 0
    
    for paper in second_volume_papers:
        old_doi = paper.get('nowbasedoi', '无')
        new_doi = generate_doi_from_paper(paper)
        paper['nowbasedoi'] = new_doi
        recalculated_count += 1
        print(f"  [{paper['id']}] {paper['title'][:30]}...: {old_doi} -> {new_doi}")
    
    # 合并所有论文
    updated_papers = other_papers + second_volume_papers
    
    # 检查重新计算后的DOI冲突
    all_conflicts_after, doi_count = check_doi_conflicts(updated_papers)
    second_volume_conflicts_after = [conflict for conflict in all_conflicts_after 
                                   if any(paper.get('nowbasedoi') == conflict 
                                        for paper in second_volume_papers)]
    
    print(f"\n重新计算后的DOI冲突检查:")
    if second_volume_conflicts_after:
        print("  第二卷内冲突:")
        for conflict in second_volume_conflicts_after:
            conflict_papers = [p for p in second_volume_papers if p.get('nowbasedoi') == conflict]
            print(f"    DOI {conflict}: {[p['title'] for p in conflict_papers]}")
    else:
        print("  第二卷内无冲突")
    
    # 检查第二卷与其他卷的冲突
    cross_volume_conflicts = []
    for doi in second_volume_papers:
        paper_doi = doi.get('nowbasedoi')
        if paper_doi in [p.get('nowbasedoi') for p in other_papers]:
            cross_volume_conflicts.append({
                'doi': paper_doi,
                'second_volume_paper': doi['title'],
                'other_paper': [p['title'] for p in other_papers if p.get('nowbasedoi') == paper_doi][0]
            })
    
    if cross_volume_conflicts:
        print("  跨卷冲突:")
        for conflict in cross_volume_conflicts:
            print(f"    DOI {conflict['doi']}:")
            print(f"      第二卷: {conflict['second_volume_paper']}")
            print(f"      其他卷: {conflict['other_paper']}")
    else:
        print("  无跨卷冲突")
    
    # 询问是否保存更改
    print(f"\n总共重新计算了 {recalculated_count} 篇论文的DOI")
    
    if not second_volume_conflicts_after and not cross_volume_conflicts:
        response = input("\n没有发现冲突，是否保存更改到文件? (y/n): ")
        if response.lower() == 'y':
            try:
                # 备份原文件
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"../database/nowbase_backup_{timestamp}.json"
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                print(f"原文件已备份至: {backup_path}")
                
                # 保存更新后的文件
                with open(json_file_path, 'w', encoding='utf-8') as f:
                    json.dump(updated_papers, f, ensure_ascii=False, indent=2)
                print("文件已成功更新")
                
            except Exception as e:
                print(f"保存文件时出错: {str(e)}")
        else:
            print("取消保存，更改未应用")
    else:
        print("\n发现DOI冲突，建议手动处理后再运行此脚本")

if __name__ == "__main__":
    recalculate_second_volume_dois()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分阶段搜索最优 Gameme Factor 计算参数
第1阶段：粗粒度（步长0.5）- 快速定位大致范围
第2阶段：中等粒度（步长0.1）- 围绕最优解缩小范围
第3阶段：精细搜索（步长0.01）- 最终精确优化
"""

import json
import math
import numpy as np
from pathlib import Path
from collections import defaultdict


def load_nowbase_data(file_path):
    """加载 nowbase.json 数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_gameme_factor_raw(author_name, papers, r=0.7, award_weight=0.92, 
                                 abstract_weight=0.05, keyword_weight=0.03):
    """计算作者的原始 Gameme Factor（未归一化）"""
    if not papers:
        return 0.0
    
    g_raw = 0.0
    
    for paper in papers:
        authors = paper.get('authors', [])
        if not authors:
            continue
        
        try:
            position = authors.index(author_name)
        except ValueError:
            continue
        
        k = position + 1
        award = 1 if paper.get('bestpaperaward', False) else 0
        
        abstract = paper.get('abstract', '')
        abstract_length = len(abstract) if abstract else 100
        
        keywords = paper.get('keywords', [])
        keyword_count = len(keywords) if isinstance(keywords, list) else 3
        
        award_factor = 1 + award_weight * award
        abstract_factor = 1 + abstract_weight * math.log(abstract_length)
        keyword_factor = 1 + keyword_weight * keyword_count
        
        contribution = (r ** (k - 1)) * award_factor * abstract_factor * keyword_factor
        g_raw += contribution
    
    g = math.log(1 + g_raw) * 10
    return g


def normalize_sigmoid(g, center=0, scale=8, offset=4, min_val=1):
    """Sigmoid 归一化"""
    normalized_full = 10 / (1 + math.exp(-(g - center) / scale))
    normalized = max(min_val, normalized_full - offset)
    return normalized


def calculate_statistics(values):
    """计算统计指标"""
    n = len(values)
    if n == 0:
        return None
    
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n
    std_dev = math.sqrt(variance)
    
    if std_dev == 0:
        return {'mean': mean, 'std': 0, 'skewness': 0, 'kurtosis': 0}
    
    standardized = [(x - mean) / std_dev for x in values]
    skewness = sum(z ** 3 for z in standardized) / n
    kurtosis = sum(z ** 4 for z in standardized) / n - 3
    
    return {
        'mean': mean,
        'std': std_dev,
        'skewness': skewness,
        'kurtosis': kurtosis
    }


def ks_test_statistic(values):
    """计算 K-S 检验统计量"""
    from math import erf, sqrt
    
    def normal_cdf(x):
        return 0.5 * (1 + erf(x / sqrt(2)))
    
    n = len(values)
    if n == 0:
        return float('inf')
    
    mean = sum(values) / n
    std = math.sqrt(sum((x - mean) ** 2 for x in values) / n)
    
    if std == 0:
        return float('inf')
    
    standardized = sorted([(x - mean) / std for x in values])
    
    max_diff = 0
    for i, x in enumerate(standardized):
        empirical_cdf = (i + 1) / n
        theoretical_cdf = normal_cdf(x)
        diff = abs(empirical_cdf - theoretical_cdf)
        max_diff = max(max_diff, diff)
    
    return max_diff


def evaluate_distribution(values):
    """评估分布与标准正态分布的接近程度"""
    stats = calculate_statistics(values)
    if not stats:
        return float('inf')
    
    ks_stat = ks_test_statistic(values)
    score = ks_stat + abs(stats['skewness']) + abs(stats['kurtosis'])
    
    return score, stats, ks_stat


def _expand_range(center, radius, min_val, max_val):
    """扩展搜索范围，确保不越界"""
    low = max(min_val, center - radius)
    high = min(max_val, center + radius)
    return (low, high)


def _search_phase(papers, author_papers, param_ranges, phase_name, 
                  current_best_score, current_best_params, current_best_results):
    """执行单个阶段的搜索"""
    total_combinations = (len(param_ranges['center']) * 
                         len(param_ranges['scale']) * 
                         len(param_ranges['offset']) * 
                         len(param_ranges['min_val']))
    
    print(f"搜索空间: {total_combinations:,} 种组合")
    print(f"Center: {len(param_ranges['center'])} 个值")
    print(f"Scale: {len(param_ranges['scale'])} 个值")
    print(f"Offset: {len(param_ranges['offset'])} 个值")
    print(f"Min_val: {len(param_ranges['min_val'])} 个值")
    print()
    
    best_score = current_best_score
    best_params = current_best_params
    best_results = current_best_results
    
    count = 0
    last_print = 0
    no_improvement_count = 0  # 未改进计数器
    EARLY_STOP_THRESHOLD = 200000  # 早停阈值：20万次
    
    for center in param_ranges['center']:
        for scale in param_ranges['scale']:
            for offset in param_ranges['offset']:
                for min_val in param_ranges['min_val']:
                    count += 1
                    
                    values = []
                    for author_name, author_paper_list in author_papers.items():
                        g_raw = calculate_gameme_factor_raw(author_name, author_paper_list)
                        g_normalized = normalize_sigmoid(g_raw, center, scale, offset, min_val)
                        values.append(g_normalized)
                    
                    score, stats, ks_stat = evaluate_distribution(values)
                    
                    if score < best_score:
                        improvement = best_score - score
                        best_score = score
                        best_params = {
                            'center': round(center, 4),
                            'scale': round(scale, 4),
                            'offset': round(offset, 4),
                            'min_val': round(min_val, 4)
                        }
                        best_results = {
                            'values': values,
                            'stats': stats,
                            'ks_stat': ks_stat
                        }
                        no_improvement_count = 0  # 重置计数器
                        
                        if improvement > 0.001:  # 显著改进时打印
                            print(f"  [改进] 评分: {best_score:.6f} (提升 {improvement:.6f})")
                    else:
                        no_improvement_count += 1
                    
                    # 每 1% 打印进度
                    progress = count / total_combinations * 100
                    if progress - last_print >= 1:
                        last_print = progress
                        print(f"进度: {progress:.1f}% ({count}/{total_combinations}), "
                              f"当前最优评分: {best_score:.6f}, "
                              f"未改进计数: {no_improvement_count:,}")
                    
                    # 早停检查
                    if no_improvement_count >= EARLY_STOP_THRESHOLD:
                        print(f"\n触发早停机制！")
                        print(f"已连续 {no_improvement_count:,} 次迭代未找到更优解")
                        print(f"提前终止搜索，节省约 {(total_combinations - count):,} 次计算")
                        print(f"最终测试组合数: {count:,} / {total_combinations:,} ({count/total_combinations*100:.2f}%)")
                        print(f"\n搜索完成！最优评分: {best_score:.6f}\n")
                        return best_params, best_results, best_score
    
    print(f"\n搜索完成！共测试 {count:,} 种参数组合\n")
    
    return best_params, best_results, best_score


def search_optimal_parameters(papers, author_papers):
    """分阶段搜索最优参数组合"""
    print("开始分阶段参数搜索...")
    print("=" * 100)
    
    best_score = float('inf')
    best_params = None
    best_results = None
    
    # 第一阶段：粗粒度搜索（步长0.5-1.0）
    print("\n【第1阶段】粗粒度搜索")
    print("-" * 100)
    param_ranges_1 = {
        'center': np.arange(0, 5.5, 0.5).tolist(),
        'scale': np.arange(2, 21, 1).tolist(),
        'offset': np.arange(0, 8.5, 0.5).tolist(),
        'min_val': [0, 0.5, 1, 1.5, 2]
    }
    
    best_params, best_results, best_score = _search_phase(papers, author_papers, param_ranges_1, 
                                                           "第1阶段", best_score, best_params, best_results)
    
    # 第二阶段：中等粒度搜索（步长0.1），围绕最优解±1.0范围
    print("\n【第2阶段】中等粒度搜索（步长0.1）")
    print("-" * 100)
    
    center_range = _expand_range(best_params['center'], 1.0, 0, 5)
    scale_range = _expand_range(best_params['scale'], 2.0, 2, 20)
    offset_range = _expand_range(best_params['offset'], 1.0, 0, 8)
    min_val_range = _expand_range(best_params['min_val'], 0.5, 0, 2)
    
    param_ranges_2 = {
        'center': np.arange(center_range[0], center_range[1] + 0.1, 0.1).tolist(),
        'scale': np.arange(scale_range[0], scale_range[1] + 0.1, 0.1).tolist(),
        'offset': np.arange(offset_range[0], offset_range[1] + 0.1, 0.1).tolist(),
        'min_val': np.arange(min_val_range[0], min_val_range[1] + 0.1, 0.1).tolist()
    }
    
    best_params, best_results, best_score = _search_phase(papers, author_papers, param_ranges_2,
                                                           "第2阶段", best_score, best_params, best_results)
    
    # 第三阶段：精细搜索（步长0.01），进一步缩小到±0.2范围
    print("\n【第3阶段】精细搜索（步长0.01）")
    print("-" * 100)
    
    center_range = _expand_range(best_params['center'], 0.2, 0, 5)
    scale_range = _expand_range(best_params['scale'], 0.5, 2, 20)
    offset_range = _expand_range(best_params['offset'], 0.2, 0, 8)
    min_val_range = _expand_range(best_params['min_val'], 0.1, 0, 2)
    
    param_ranges_3 = {
        'center': np.arange(center_range[0], center_range[1] + 0.01, 0.01).tolist(),
        'scale': np.arange(scale_range[0], scale_range[1] + 0.01, 0.01).tolist(),
        'offset': np.arange(offset_range[0], offset_range[1] + 0.01, 0.01).tolist(),
        'min_val': np.arange(min_val_range[0], min_val_range[1] + 0.01, 0.01).tolist()
    }
    
    best_params, best_results, best_score = _search_phase(papers, author_papers, param_ranges_3,
                                                           "第3阶段", best_score, best_params, best_results)
    
    print(f"\n{'='*100}")
    print(f"搜索完成！最终最优评分: {best_score:.6f}\n")
    
    return best_params, best_results, best_score


def print_results(params, results, score):
    """打印最优结果"""
    print("=" * 100)
    print("最优参数配置")
    print("=" * 100)
    print(f"Center (中心点):     {params['center']:.4f}")
    print(f"Scale (缩放系数):    {params['scale']:.4f}")
    print(f"Offset (偏移量):     {params['offset']:.4f}")
    print(f"Min Value (最小值):  {params['min_val']:.4f}")
    print()
    
    print("=" * 100)
    print("分布统计信息")
    print("=" * 100)
    stats = results['stats']
    values = results['values']
    
    print(f"作者数量:            {len(values)}")
    print(f"平均值:              {stats['mean']:.4f}")
    print(f"标准差:              {stats['std']:.4f}")
    print(f"偏度:                {stats['skewness']:.4f} (理想值: 0)")
    print(f"峰度:                {stats['kurtosis']:.4f} (理想值: 0)")
    print(f"K-S 统计量:          {results['ks_stat']:.4f} (越小越好)")
    print(f"综合评分:            {score:.6f} (越低越好)")
    print()
    
    print("=" * 100)
    print("数值范围")
    print("=" * 100)
    print(f"最小值:              {min(values):.4f}")
    print(f"最大值:              {max(values):.4f}")
    print(f"中位数:              {sorted(values)[len(values)//2]:.4f}")
    print()
    
    print("=" * 100)
    print("Top 10 作者")
    print("=" * 100)
    sorted_indices = sorted(range(len(values)), key=lambda i: values[i], reverse=True)
    for i, idx in enumerate(sorted_indices[:10], 1):
        author_name = list(author_papers.keys())[idx]
        print(f"{i:2d}. {author_name:<25} {values[idx]:.4f}")


def update_stat_js(params):
    """自动更新 stat.js 文件中的归一化参数"""
    import os
    
    stat_js_path = os.path.join(os.path.dirname(__file__), '..', 'script', 'stat.js')
    
    if not os.path.exists(stat_js_path):
        print(f"警告: 找不到 stat.js 文件: {stat_js_path}")
        return False
    
    try:
        with open(stat_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换归一化代码
        old_pattern = r'// 归一化.*?\n.*?const normalized_full = .*?;\n.*?const normalized = .*?;'
        new_code = f"""    // 归一化（使用最优参数：center={params['center']:.4f}, scale={params['scale']:.4f}, offset={params['offset']:.4f}, min={params['min_val']:.4f}）
    const normalized_full = 10 / (1 + Math.exp(-(g - {params['center']:.4f}) / {params['scale']:.4f}));
    const normalized = Math.max({params['min_val']:.4f}, normalized_full - {params['offset']:.4f});"""
        
        import re
        updated_content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)
        
        if updated_content == content:
            print("警告: 未找到需要替换的代码模式")
            return False
        
        with open(stat_js_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✓ 已自动更新 stat.js 文件")
        print(f"  文件路径: {stat_js_path}")
        return True
        
    except Exception as e:
        print(f"错误: 更新 stat.js 失败 - {e}")
        return False


def generate_code_snippet(params):
    """生成代码片段"""
    print("\n" + "=" * 100)
    print("JavaScript 代码片段")
    print("=" * 100)
    code = f"""
// 归一化（最优参数）
const normalized_full = 10 / (1 + Math.exp(-(g - {params['center']:.4f}) / {params['scale']:.4f}));
const normalized = Math.max({params['min_val']:.4f}, normalized_full - {params['offset']:.4f});
"""
    print(code)
    
    print("\n" + "=" * 100)
    print("Python 代码片段")
    print("=" * 100)
    py_code = f"""
# 归一化（最优参数）
g_normalized_full = 10 / (1 + math.exp(-(g - {params['center']:.4f}) / {params['scale']:.4f}))
g_normalized = max({params['min_val']:.4f}, g_normalized_full - {params['offset']:.4f})
"""
    print(py_code)


if __name__ == '__main__':
    # 从 tools 目录向上两级到项目根目录
    script_dir = Path(__file__).parent
    data_file = script_dir.parent.parent / "database" / "data" / "nowbase.json"
    
    print(f"正在加载 {data_file}...")
    papers = load_nowbase_data(str(data_file))
    print(f"共加载 {len(papers)} 篇论文\n")
    
    author_papers = defaultdict(list)
    for paper in papers:
        authors = paper.get('authors', [])
        for author in authors:
            author_papers[author].append(paper)
    
    print(f"共 {len(author_papers)} 位作者\n")
    
    best_params, best_results, best_score = search_optimal_parameters(papers, author_papers)
    
    print_results(best_params, best_results, best_score)
    
    # 自动生成代码片段
    generate_code_snippet(best_params)
    
    # 自动更新 stat.js 文件
    print("\n" + "=" * 100)
    print("自动更新 stat.js")
    print("=" * 100)
    update_stat_js(best_params)

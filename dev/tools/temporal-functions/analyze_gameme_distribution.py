#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gameme Factor 完整分析报告
- 使用原始公式（包含 bestpaperaward、摘要、关键词）
- 输出所有作者评分
- 计算各项统计量
- 拟合多种分布并找出最接近的分布类型
"""

import json
import math
import numpy as np
from collections import defaultdict
from scipy import stats


def load_nowbase_data(file_path):
    """加载 nowbase.json 数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_gameme_factor_raw(author_name, papers):
    """
    计算作者的原始 Gameme Factor
    
    G_raw = Σ [ r^(k-1) × (1 + 0.92 × award) × (1 + 0.05 × log(abstract_length)) × (1 + 0.03 × keyword_count) ]
    G = ln(1 + G_raw) × 10
    """
    if not papers:
        return 0.0
    
    g_raw = 0.0
    r = 0.7
    
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
        
        award_factor = 1 + 0.92 * award
        abstract_factor = 1 + 0.05 * math.log(abstract_length)
        keyword_factor = 1 + 0.03 * keyword_count
        
        contribution = (r ** (k - 1)) * award_factor * abstract_factor * keyword_factor
        g_raw += contribution
    
    g = math.log(1 + g_raw) * 10
    return round(g, 4)


def fit_distributions(data):
    """
    拟合多种常见分布，返回拟合效果最好的分布
    """
    distributions = {
        '正态分布 (Normal)': stats.norm,
        '对数正态分布 (Log-normal)': stats.lognorm,
        '伽马分布 (Gamma)': stats.gamma,
        '威布尔分布 (Weibull)': stats.weibull_min,
        '贝塔分布 (Beta)': stats.beta,
        '指数分布 (Exponential)': stats.expon,
        '逻辑分布 (Logistic)': stats.logistic,
        't分布 (Student-t)': stats.t,
        '卡方分布 (Chi-square)': stats.chi2,
        'F分布 (F-distribution)': stats.f,
    }
    
    results = []
    
    for name, dist in distributions.items():
        try:
            # 拟合分布参数
            params = dist.fit(data)
            
            # 计算 K-S 检验
            ks_stat, p_value = stats.kstest(data, dist.cdf, args=params)
            
            # 计算 AIC (Akaike Information Criterion)
            log_likelihood = np.sum(dist.logpdf(data, *params))
            num_params = len(params)
            n = len(data)
            aic = 2 * num_params - 2 * log_likelihood
            
            # 计算 BIC (Bayesian Information Criterion)
            bic = num_params * math.log(n) - 2 * log_likelihood
            
            results.append({
                'name': name,
                'params': params,
                'ks_statistic': ks_stat,
                'p_value': p_value,
                'aic': aic,
                'bic': bic,
                'log_likelihood': log_likelihood
            })
        except Exception as e:
            print(f"  警告: {name} 拟合失败 - {e}")
            continue
    
    # 按 K-S 统计量排序（越小越好）
    results.sort(key=lambda x: x['ks_statistic'])
    
    return results


def calculate_comprehensive_statistics(values):
    """计算全面的统计指标"""
    n = len(values)
    if n == 0:
        return None
    
    sorted_values = sorted(values)
    
    # 基础统计
    mean = np.mean(values)
    median = np.median(values)
    std = np.std(values, ddof=0)  # 总体标准差
    variance = np.var(values, ddof=0)
    
    # 百分位数
    percentiles = {
        'min': sorted_values[0],
        'Q1': np.percentile(values, 25),
        'median': median,
        'Q3': np.percentile(values, 75),
        'max': sorted_values[-1],
        'P10': np.percentile(values, 10),
        'P90': np.percentile(values, 90),
    }
    
    # 离散程度
    range_val = percentiles['max'] - percentiles['min']
    iqr = percentiles['Q3'] - percentiles['Q1']
    cv = std / mean if mean != 0 else 0  # 变异系数
    
    # 高阶矩
    skewness = stats.skew(values)
    kurtosis = stats.kurtosis(values, fisher=True)  # 超额峰度
    
    # K-S 检验（与正态分布）
    ks_stat, ks_pvalue = stats.kstest(values, 'norm', args=(mean, std))
    
    # Shapiro-Wilk 检验（正态性检验，适用于小样本）
    if n <= 5000:
        sw_stat, sw_pvalue = stats.shapiro(values)
    else:
        sw_stat, sw_pvalue = None, None
    
    # Anderson-Darling 检验
    ad_result = stats.anderson(values, dist='norm')
    
    return {
        'count': n,
        'mean': mean,
        'median': median,
        'std': std,
        'variance': variance,
        'percentiles': percentiles,
        'range': range_val,
        'iqr': iqr,
        'cv': cv,
        'skewness': skewness,
        'kurtosis': kurtosis,
        'ks_test': {'statistic': ks_stat, 'p_value': ks_pvalue},
        'shapiro_wilk': {'statistic': sw_stat, 'p_value': sw_pvalue},
        'anderson_darling': ad_result
    }


def main():
    print("=" * 100)
    print("Gameme Factor 完整分析报告")
    print("=" * 100)
    print()
    
    # 加载数据
    print("正在加载 nowbase.json...")
    papers = load_nowbase_data('../database/data/nowbase.json')
    print(f"共加载 {len(papers)} 篇论文\n")
    
    # 收集所有作者及其论文
    author_papers = defaultdict(list)
    for paper in papers:
        authors = paper.get('authors', [])
        for author in authors:
            author_papers[author].append(paper)
    
    print(f"共 {len(author_papers)} 位作者\n")
    
    # 计算每位作者的 Gameme Factor（原始值，未归一化）
    print("=" * 100)
    print("所有作者 Gameme Factor 评分（原始值）")
    print("=" * 100)
    print(f"{'排名':<6} {'作者姓名':<25} {'论文数':<10} {'G_raw':<15} {'G (ln变换)':<15}")
    print("-" * 100)
    
    results = []
    for author_name, author_paper_list in author_papers.items():
        g_raw = calculate_gameme_factor_raw(author_name, author_paper_list)
        paper_count = len(author_paper_list)
        results.append({
            'name': author_name,
            'paper_count': paper_count,
            'g_raw': g_raw
        })
    
    # 按 G_raw 降序排序
    results.sort(key=lambda x: x['g_raw'], reverse=True)
    
    # 打印结果
    for rank, result in enumerate(results, 1):
        g = math.log(1 + result['g_raw']) * 10
        print(f"{rank:<6} {result['name']:<25} {result['paper_count']:<10} "
              f"{result['g_raw']:<15.4f} {g:<15.4f}")
    
    print("=" * 100)
    print()
    
    # 提取 G 值（对数变换后）
    g_values = [math.log(1 + r['g_raw']) * 10 for r in results]
    
    # 计算统计量
    print("=" * 100)
    print("综合统计指标")
    print("=" * 100)
    
    stats_result = calculate_comprehensive_statistics(g_values)
    
    print(f"\n【基础统计】")
    print(f"  作者数量:           {stats_result['count']}")
    print(f"  平均值 (Mean):      {stats_result['mean']:.4f}")
    print(f"  中位数 (Median):    {stats_result['median']:.4f}")
    print(f"  标准差 (Std):       {stats_result['std']:.4f}")
    print(f"  方差 (Variance):    {stats_result['variance']:.4f}")
    
    print(f"\n【百分位数】")
    for key, value in stats_result['percentiles'].items():
        print(f"  {key:<8}: {value:.4f}")
    
    print(f"\n【离散程度】")
    print(f"  极差 (Range):       {stats_result['range']:.4f}")
    print(f"  四分位距 (IQR):     {stats_result['iqr']:.4f}")
    print(f"  变异系数 (CV):      {stats_result['cv']:.4f}")
    
    print(f"\n【分布形态】")
    print(f"  偏度 (Skewness):    {stats_result['skewness']:.4f} "
          f"{'(对称)' if abs(stats_result['skewness']) < 0.5 else '(偏斜)'}")
    print(f"  峰度 (Kurtosis):    {stats_result['kurtosis']:.4f} "
          f"{'(正态)' if abs(stats_result['kurtosis']) < 0.5 else '(非正态)'}")
    
    print(f"\n【正态性检验】")
    print(f"  K-S 检验:")
    print(f"    统计量: {stats_result['ks_test']['statistic']:.4f}")
    print(f"    p值:    {stats_result['ks_test']['p_value']:.4f} "
          f"{'✓ 不能拒绝正态分布' if stats_result['ks_test']['p_value'] > 0.05 else '✗ 拒绝正态分布'}")
    
    if stats_result['shapiro_wilk']['statistic'] is not None:
        print(f"  Shapiro-Wilk 检验:")
        print(f"    统计量: {stats_result['shapiro_wilk']['statistic']:.4f}")
        print(f"    p值:    {stats_result['shapiro_wilk']['p_value']:.4f} "
              f"{'✓ 不能拒绝正态分布' if stats_result['shapiro_wilk']['p_value'] > 0.05 else '✗ 拒绝正态分布'}")
    
    print(f"  Anderson-Darling 检验:")
    print(f"    统计量: {stats_result['anderson_darling'].statistic:.4f}")
    print(f"    临界值 (5%): {stats_result['anderson_darling'].critical_values[2]:.4f}")
    print(f"    结论: {'✓ 不能拒绝正态分布' if stats_result['anderson_darling'].statistic < stats_result['anderson_darling'].critical_values[2] else '✗ 拒绝正态分布'}")
    
    print()
    
    # 分布拟合
    print("=" * 100)
    print("分布拟合分析")
    print("=" * 100)
    print("\n正在拟合多种分布...\n")
    
    fit_results = fit_distributions(g_values)
    
    print(f"{'排名':<6} {'分布名称':<30} {'K-S 统计量':<15} {'p值':<15} {'AIC':<15} {'BIC':<15}")
    print("-" * 100)
    
    for rank, result in enumerate(fit_results[:10], 1):  # 显示前10名
        print(f"{rank:<6} {result['name']:<30} {result['ks_statistic']:<15.4f} "
              f"{result['p_value']:<15.4f} {result['aic']:<15.2f} {result['bic']:<15.2f}")
    
    print()
    
    # 最佳分布
    best_fit = fit_results[0]
    print("=" * 100)
    print(f"最接近的分布: {best_fit['name']}")
    print("=" * 100)
    print(f"  K-S 统计量:  {best_fit['ks_statistic']:.4f}")
    print(f"  p值:         {best_fit['p_value']:.4f}")
    print(f"  AIC:         {best_fit['aic']:.2f}")
    print(f"  BIC:         {best_fit['bic']:.2f}")
    print(f"  对数似然:    {best_fit['log_likelihood']:.2f}")
    print(f"  分布参数:    {best_fit['params']}")
    print()
    
    # 对比正态分布
    normal_fit = next((r for r in fit_results if '正态分布' in r['name']), None)
    if normal_fit:
        print("=" * 100)
        print("与正态分布对比")
        print("=" * 100)
        print(f"  正态分布排名: 第 {fit_results.index(normal_fit) + 1} 名")
        print(f"  K-S 统计量:  {normal_fit['ks_statistic']:.4f}")
        print(f"  p值:         {normal_fit['p_value']:.4f}")
        
        improvement = ((best_fit['ks_statistic'] - normal_fit['ks_statistic']) / 
                      normal_fit['ks_statistic'] * 100)
        if improvement > 0:
            print(f"  改进幅度:    {improvement:.2f}% (K-S 统计量降低)")
        else:
            print(f"  说明:        正态分布已是最优或接近最优")
        print()
    
    # 建议
    print("=" * 100)
    print("分析与建议")
    print("=" * 100)
    
    if normal_fit and normal_fit['p_value'] > 0.05:
        print("✓ 数据符合正态分布，可以使用基于正态分布的统计方法")
    else:
        print(f"✗ 数据不符合正态分布，建议使用 {best_fit['name']}")
        print(f"  该分布在理论分析和实际应用中同样有效")
    
    print()
    print("【关键发现】")
    print(f"  1. 评分范围: [{stats_result['percentiles']['min']:.2f}, "
          f"{stats_result['percentiles']['max']:.2f}]")
    print(f"  2. 集中趋势: 均值={stats_result['mean']:.2f}, "
          f"中位数={stats_result['median']:.2f}")
    print(f"  3. 离散程度: 标准差={stats_result['std']:.2f}, "
          f"变异系数={stats_result['cv']:.2%}")
    print(f"  4. 分布形态: 偏度={stats_result['skewness']:.2f}, "
          f"峰度={stats_result['kurtosis']:.2f}")
    print()


if __name__ == '__main__':
    main()

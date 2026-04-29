/**
 * 作者统计页面脚本 - 搜索模式
 * 支持模糊匹配作者，显示论文列表和 Gameme Factor
 */

// 数据文件路径
const NOWBASE_FILE = 'database/data/nowbase.json';

// 存储全局数据
let nowbaseData = [];
let allAuthors = [];
let selectedAuthor = null;
let isAdminMode = false; // 管理员模式标志
let authorsData = []; // 统计数据
let currentMetric = 'gamemeFactor'; // 当前指标
let currentSortOrder = 'desc'; // 当前排序方式

/**
 * 检查是否为管理员模式
 */
function checkAdminMode() {
    const urlParams = new URLSearchParams(window.location.search);
    const password = urlParams.get('password');
    return password === 'wangzy20011115';
}

/**
 * 加载 JSON 数据
 */
async function loadJSONData(filePath) {
    try {
        const response = await fetch(filePath);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`加载 ${filePath} 失败:`, error);
        return null;
    }
}

/**
 * 计算作者的 Gameme Factor
 * G_raw = Σ [ r^(k-1) * (1 + 0.92 * award) * (1 + 0.05 * log(abstract_length)) * (1 + 0.03 * keyword_count) ]
 * 其中：r = 0.7，k 为作者顺位，award 为布尔值（获奖=1，未获奖=0）
 *       abstract_length 为摘要字数，keyword_count 为关键词数量
 * G = ln(1 + G_raw) * 10
 * 最终进行归一化到 0-10 范围（调整 sigmoid 参数以增加区分度）
 */
function calculateGamemeFactor(authorName, papers) {
    if (!papers || !Array.isArray(papers)) return 0;
    
    let gRaw = 0;
    const r = 0.7;
    
    // 遍历所有论文
    papers.forEach(paper => {
        if (!paper.authors || !Array.isArray(paper.authors)) return;
        
        // 找到该作者在这篇论文中的位置（从1开始）
        const position = paper.authors.findIndex(author => author === authorName);
        
        if (position !== -1) {
            const k = position + 1; // 作者顺位（第1作者=1）
            const award = paper.bestpaperaward ? 1 : 0; // 是否获得最佳论文奖
            
            // 获取摘要字数（如果没有则默认为100）
            const abstractLength = paper.abstract && paper.abstract.length > 0 ? paper.abstract.length : 100;
            
            // 获取关键词数量（如果没有则默认为3）
            const keywordCount = paper.keywords && Array.isArray(paper.keywords) ? paper.keywords.length : 3;
            
            // 计算该论文的贡献分
            const awardFactor = (1 + 0.92 * award);
            const abstractFactor = (1 + 0.05 * Math.log(abstractLength));
            const keywordFactor = (1 + 0.03 * keywordCount);
            
            const contribution = Math.pow(r, k - 1) * awardFactor * abstractFactor * keywordFactor;
            gRaw += contribution;
        }
    });
    
    // 计算原始的 Gameme Factor
    const g = Math.log(1 + gRaw) * 10;
    
                                                        // 归一化（使用最优参数：center=0.3000, scale=12.6000, offset=0.0900, min=0.0000）
    const normalized_full = 10 / (1 + Math.exp(-(g - 0.3000) / 12.6000));
    const normalized = Math.max(0.0000, normalized_full - 0.0900);
    
    return parseFloat(normalized.toFixed(4));
}

/**
 * 计算作者在 NowBase 中的论文数量
 */
function countAuthorPapers(authorName, papers) {
    if (!papers || !Array.isArray(papers)) return 0;
    
    return papers.filter(paper => {
        if (!paper.authors || !Array.isArray(paper.authors)) return false;
        return paper.authors.some(author => author === authorName);
    }).length;
}

/**
 * 收集 nowbase.json 中的所有唯一作者
 */
function extractAllAuthors(papers) {
    const authorSet = new Set();
    
    if (!papers || !Array.isArray(papers)) return [];
    
    papers.forEach(paper => {
        if (paper.authors && Array.isArray(paper.authors)) {
            paper.authors.forEach(author => {
                authorSet.add(author);
            });
        }
    });
    
    return Array.from(authorSet).sort();
}

/**
 * 计算所有作者的统计数据
 */
function calculateAuthorStats(papers) {
    // 提取所有唯一作者
    const allAuthors = extractAllAuthors(papers);
    
    const stats = allAuthors.map(authorName => {
        const paperCount = countAuthorPapers(authorName, papers);
        const gamemeFactor = calculateGamemeFactor(authorName, papers);
        
        return {
            name: authorName,
            paperCount: paperCount,
            gamemeFactor: gamemeFactor
        };
    });
    
    return stats;
}

/**
 * 获取作者的论文列表
 */
function getAuthorPapers(authorName, papers) {
    if (!papers || !Array.isArray(papers)) return [];
    
    return papers.filter(paper => {
        if (!paper.authors || !Array.isArray(paper.authors)) return false;
        return paper.authors.some(author => author === authorName);
    });
}

/**
 * 模糊搜索作者
 */
function searchAuthors(query) {
    if (!query || query.trim() === '') return [];
    
    const lowerQuery = query.toLowerCase().trim();
    
    return allAuthors.filter(author => 
        author.toLowerCase().includes(lowerQuery)
    ).slice(0, 10); // 最多显示10个建议
}

/**
 * 显示作者建议列表
 */
function showSuggestions(suggestions) {
    const suggestionsList = document.getElementById('authorSuggestions');
    
    if (suggestions.length === 0) {
        suggestionsList.classList.remove('visible');
        return;
    }
    
    suggestionsList.innerHTML = '';
    
    suggestions.forEach((author, index) => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        if (index === 0) item.classList.add('selected');
        item.textContent = author;
        item.dataset.author = author;
        
        item.addEventListener('click', () => {
            selectAuthor(author);
        });
        
        suggestionsList.appendChild(item);
    });
    
    suggestionsList.classList.add('visible');
}

/**
 * 隐藏建议列表
 */
function hideSuggestions() {
    const suggestionsList = document.getElementById('authorSuggestions');
    suggestionsList.classList.remove('visible');
}

/**
 * 选择作者
 */
function selectAuthor(authorName) {
    const searchInput = document.getElementById('authorSearch');
    searchInput.value = authorName;
    selectedAuthor = authorName;
    
    hideSuggestions();
    displayAuthorInfo(authorName);
}

/**
 * 显示作者信息
 */
function displayAuthorInfo(authorName) {
    const authorResult = document.getElementById('authorResult');
    const resultAuthorName = document.getElementById('resultAuthorName');
    const resultGamemeFactor = document.getElementById('resultGamemeFactor');
    const resultPaperCount = document.getElementById('resultPaperCount');
    const resultPapersList = document.getElementById('resultPapersList');
    
    // 计算 Gameme Factor
    const gamemeFactor = calculateGamemeFactor(authorName, nowbaseData);
    
    // 获取论文列表
    const papers = getAuthorPapers(authorName, nowbaseData);
    
    // 更新头部信息
    resultAuthorName.textContent = authorName;
    resultGamemeFactor.textContent = gamemeFactor.toFixed(4);
    resultPaperCount.textContent = papers.length;
    
    // 渲染论文列表
    resultPapersList.innerHTML = '';
    
    if (papers.length === 0) {
        resultPapersList.innerHTML = '<li class="paper-item"><p>暂无发表论文</p></li>';
    } else {
        papers.forEach(paper => {
            const li = document.createElement('li');
            li.className = 'paper-item';
            
            const titleDiv = document.createElement('div');
            titleDiv.className = 'paper-title';
            titleDiv.textContent = paper.title;
            li.appendChild(titleDiv);
            
            const authorsDiv = document.createElement('div');
            authorsDiv.className = 'paper-authors';
            authorsDiv.textContent = paper.authors.join(', ');
            li.appendChild(authorsDiv);
            
            const metaDiv = document.createElement('div');
            metaDiv.className = 'paper-meta';
            const venue = paper.issue || '未知出版物';
            const year = paper.year || new Date(paper.published).getFullYear();
            metaDiv.textContent = `${venue}, ${year}`;
            li.appendChild(metaDiv);
            
            if (paper.nowbasedoi) {
                const doiDiv = document.createElement('div');
                doiDiv.className = 'paper-doi';
                const doiLink = document.createElement('a');
                doiLink.href = `nowbase.html?doi=${encodeURIComponent(paper.nowbasedoi)}`;
                doiLink.target = '_blank';
                doiLink.textContent = paper.nowbasedoi;
                doiDiv.innerHTML = 'NowBase DOI: ';
                doiDiv.appendChild(doiLink);
                li.appendChild(doiDiv);
            }
            
            resultPapersList.appendChild(li);
        });
    }
    
    // 显示结果
    authorResult.style.display = 'block';
}

/**
 * 显示错误信息
 */
function showError(message) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.innerHTML = `
            <div class="error-state">
                <h3>⚠ 错误</h3>
                <p>${message}</p>
            </div>
        `;
    }
}

/**
 * 隐藏加载状态
 */
function hideLoading() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
}

/**
 * 显示搜索框
 */
function showSearchUI() {
    document.getElementById('searchContainer').style.display = 'block';
}

/**
 * 显示 Gameme Factor 分布图
 */
function showDistributionChart(authorsStats) {
    const chartContainer = document.getElementById('distributionChart');
    const canvas = document.getElementById('gamemeCanvas');
    
    if (!canvas) return;
    
    chartContainer.style.display = 'block';
    
    // 提取所有 Gameme Factor 值
    const values = authorsStats.map(stat => stat.gamemeFactor).sort((a, b) => a - b);
    
    if (values.length === 0) return;
    
    // 仅在管理员模式下计算并显示统计指标
    if (isAdminMode) {
        displayStatistics(values, authorsStats.length);
    }
    
    // 初始化 ECharts
    const dpr = window.devicePixelRatio || 1;
    const containerWidth = chartContainer.clientWidth - 60; // 减去padding
    
    const chart = echarts.init(canvas, null, {
        renderer: 'canvas',
        devicePixelRatio: dpr,
        width: containerWidth,
        height: 500
    });
    
    // 计算直方图数据
    const binCount = 50;
    const minVal = values[0];
    const maxVal = values[values.length - 1];
    const binWidth = (maxVal - minVal) / binCount;
    
    const bins = new Array(binCount).fill(0);
    const binLabels = [];
    values.forEach(val => {
        const binIndex = Math.min(Math.floor((val - minVal) / binWidth), binCount - 1);
        bins[binIndex]++;
    });
    
    // 生成 X 轴标签
    for (let i = 0; i < binCount; i++) {
        const label = (minVal + i * binWidth).toFixed(1);
        binLabels.push(label);
    }
    
    // 计算 KDE 曲线
    const kdeData = calculateKDECurve(values, minVal, maxVal, binCount);
    
    // ECharts 配置
    const option = {
        animation: true,
        animationDuration: 800,
        animationEasing: 'cubicOut',
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            },
            formatter: function(params) {
                let result = `区间: ${params[0].name}<br/>`;
                params.forEach(item => {
                    result += `${item.seriesName}: ${item.value.toFixed(2)}<br/>`;
                });
                return result;
            }
        },
        grid: {
            left: '60',
            right: '30',
            bottom: '50',
            top: '30',
            containLabel: false
        },
        xAxis: {
            type: 'category',
            data: binLabels,
            name: 'Gameme Factor',
            nameLocation: 'middle',
            nameGap: 35,
            nameTextStyle: {
                fontSize: 12
            },
            axisLabel: {
                interval: Math.floor(binCount / 10),
                rotate: 45,
                fontSize: 9
            },
            axisLine: {
                lineStyle: {
                    color: '#333'
                }
            }
        },
        yAxis: [
            {
                type: 'value',
                name: '频数',
                position: 'left',
                nameTextStyle: {
                    fontSize: 12
                },
                axisLabel: {
                    fontSize: 10
                },
                axisLine: {
                    lineStyle: {
                        color: '#333'
                    }
                },
                splitLine: {
                    lineStyle: {
                        color: '#eee'
                    }
                }
            },
            {
                type: 'value',
                name: '密度',
                position: 'right',
                nameTextStyle: {
                    fontSize: 12
                },
                axisLabel: {
                    fontSize: 10
                },
                axisLine: {
                    lineStyle: {
                        color: '#D36A00'
                    }
                },
                splitLine: {
                    show: false
                }
            }
        ],
        series: [
            {
                name: '频数',
                type: 'bar',
                data: bins,
                yAxisIndex: 0,
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#00629B' },
                        { offset: 1, color: '#003C6B' }
                    ]),
                    borderRadius: [2, 2, 0, 0]
                },
                emphasis: {
                    itemStyle: {
                        color: '#D36A00'
                    }
                }
            },
            {
                name: 'KDE拟合',
                type: 'line',
                data: kdeData,
                yAxisIndex: 1,
                smooth: true,
                symbol: 'none',
                lineStyle: {
                    color: '#D36A00',
                    width: 3
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(211, 106, 0, 0.3)' },
                        { offset: 1, color: 'rgba(211, 106, 0, 0.05)' }
                    ])
                }
            }
        ]
    };
    
    chart.setOption(option);
    
    // 响应式调整
    window.addEventListener('resize', function() {
        chart.resize();
    });
}

/**
 * 显示统计指标
 */
function displayStatistics(values, totalAuthors) {
    // 显示统计指标容器
    document.getElementById('statisticsSummary').style.display = 'grid';
    
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const median = calculateMedian(values);
    const stdDev = standardDeviation(values);
    const min = values[0];
    const max = values[values.length - 1];
    const q1 = calculatePercentile(values, 25);
    const q3 = calculatePercentile(values, 75);
    const iqr = q3 - q1;
    const range = max - min;
    const cv = (stdDev / mean) * 100; // 变异系数（百分比）
    const skewness = calculateSkewness(values, mean, stdDev);
    const kurtosis = calculateKurtosis(values, mean, stdDev);
    
    // K-S 检验
    const ksResult = kolmogorovSmirnovTest(values, mean, stdDev);
    
    document.getElementById('statTotalAuthors').textContent = totalAuthors;
    document.getElementById('statMean').textContent = mean.toFixed(4);
    document.getElementById('statMedian').textContent = median.toFixed(4);
    document.getElementById('statStdDev').textContent = stdDev.toFixed(4);
    document.getElementById('statMin').textContent = min.toFixed(4);
    document.getElementById('statMax').textContent = max.toFixed(4);
    document.getElementById('statQ1').textContent = q1.toFixed(4);
    document.getElementById('statQ3').textContent = q3.toFixed(4);
    document.getElementById('statIQR').textContent = iqr.toFixed(4);
    document.getElementById('statRange').textContent = range.toFixed(4);
    document.getElementById('statCV').textContent = cv.toFixed(2) + '%';
    document.getElementById('statSkewness').textContent = skewness.toFixed(4);
    document.getElementById('statKurtosis').textContent = kurtosis.toFixed(4);
    document.getElementById('statKSStat').textContent = ksResult.statistic.toFixed(4);
    document.getElementById('statKSPValue').textContent = ksResult.pValue.toFixed(4);
    
    // 设置颜色标识
    setColorIndicator('statSkewness', Math.abs(skewness), 0.5, 'lower');
    setColorIndicator('statKurtosis', Math.abs(kurtosis), 1.0, 'lower');
    setColorIndicator('statKSPValue', ksResult.pValue, 0.05, 'higher');
}

/**
 * 计算中位数
 */
function calculateMedian(sortedValues) {
    const mid = Math.floor(sortedValues.length / 2);
    if (sortedValues.length % 2 === 0) {
        return (sortedValues[mid - 1] + sortedValues[mid]) / 2;
    } else {
        return sortedValues[mid];
    }
}

/**
 * 计算百分位数
 */
function calculatePercentile(sortedValues, percentile) {
    const index = (percentile / 100) * (sortedValues.length - 1);
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    const weight = index - lower;
    
    if (upper >= sortedValues.length) return sortedValues[lower];
    return sortedValues[lower] * (1 - weight) + sortedValues[upper] * weight;
}

/**
 * 计算偏度
 */
function calculateSkewness(values, mean, stdDev) {
    const n = values.length;
    if (n < 3 || stdDev === 0) return 0;
    
    const sum = values.reduce((acc, val) => {
        return acc + Math.pow((val - mean) / stdDev, 3);
    }, 0);
    
    return (n / ((n - 1) * (n - 2))) * sum;
}

/**
 * 计算峰度
 */
function calculateKurtosis(values, mean, stdDev) {
    const n = values.length;
    if (n < 4 || stdDev === 0) return 0;
    
    const sum = values.reduce((acc, val) => {
        return acc + Math.pow((val - mean) / stdDev, 4);
    }, 0);
    
    // 超额峰度（减去3，使正态分布的峰度为0）
    const kurtosis = ((n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))) * sum - 
                     (3 * Math.pow(n - 1, 2)) / ((n - 2) * (n - 3));
    
    return kurtosis;
}

/**
 * K-S 检验（单样本，检验是否服从正态分布）
 */
function kolmogorovSmirnovTest(data, mean, stdDev) {
    const n = data.length;
    const sortedData = [...data].sort((a, b) => a - b);
    
    // 计算经验分布函数与理论正态分布CDF的最大差值
    let maxDiff = 0;
    
    for (let i = 0; i < n; i++) {
        // 经验分布函数
        const empiricalCDF = (i + 1) / n;
        
        // 理论正态分布 CDF
        const theoreticalCDF = normalCDF(sortedData[i], mean, stdDev);
        
        // 计算差值
        const diff1 = Math.abs(empiricalCDF - theoreticalCDF);
        const diff2 = Math.abs((i / n) - theoreticalCDF);
        
        maxDiff = Math.max(maxDiff, diff1, diff2);
    }
    
    // 计算 p 值（近似）
    const lambda = maxDiff * (Math.sqrt(n) + 0.12 + 0.11 / Math.sqrt(n));
    const pValue = kspValue(lambda);
    
    return {
        statistic: maxDiff,
        pValue: pValue
    };
}

/**
 * 标准正态分布 CDF
 */
function normalCDF(x, mean, stdDev) {
    const z = (x - mean) / stdDev;
    return 0.5 * (1 + erf(z / Math.sqrt(2)));
}

/**
 * 误差函数 erf(x) 的近似计算
 */
function erf(x) {
    const sign = x >= 0 ? 1 : -1;
    x = Math.abs(x);
    
    const a1 = 0.254829592;
    const a2 = -0.284496736;
    const a3 = 1.421413741;
    const a4 = -1.453152027;
    const a5 = 1.061405429;
    const p = 0.3275911;
    
    const t = 1.0 / (1.0 + p * x);
    const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
    
    return sign * y;
}

/**
 * K-S 检验 p 值计算（基于渐近分布）
 */
function kspValue(lambda) {
    if (lambda <= 0) return 1;
    if (lambda > 3) return 0;
    
    // 使用级数展开近似
    let sum = 0;
    const terms = 100;
    
    for (let j = 1; j <= terms; j++) {
        const term = Math.pow(-1, j - 1) * Math.exp(-2 * j * j * lambda * lambda);
        sum += term;
    }
    
    return 2 * sum;
}

/**
 * 设置统计指标的颜色标识
 * @param {string} elementId - 元素ID
 * @param {number} value - 当前值
 * @param {number} threshold - 阈值
 * @param {string} type - 'lower'表示越小越好，'higher'表示越大越好
 */
function setColorIndicator(elementId, value, threshold, type) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    let isNormal = false;
    
    if (type === 'lower') {
        // 越小越好（如偏度、峰度接近0）
        isNormal = value <= threshold;
    } else if (type === 'higher') {
        // 越大越好（如p值大于0.05）
        isNormal = value >= threshold;
    }
    
    if (isNormal) {
        element.classList.add('normal');
        element.classList.remove('warning');
    } else {
        element.classList.add('warning');
        element.classList.remove('normal');
    }
}

/**
 * 绘制 KDE 拟合曲线
 */
/**
 * 计算 KDE 曲线数据（用于 ECharts）
 */
function calculateKDECurve(data, minVal, maxVal, numPoints) {
    const bandwidth = calculateBandwidth(data);
    const kdeData = [];
    
    for (let i = 0; i <= numPoints; i++) {
        const x = minVal + (maxVal - minVal) * (i / numPoints);
        const density = kdeEstimate(x, data, bandwidth);
        kdeData.push(density);
    }
    
    return kdeData;
}

/**
 * 绘制 KDE 拟合曲线（Canvas 版本，保留兼容）
 */
function drawKDECurve(ctx, data, minVal, maxVal, padding, chartWidth, chartHeight, height, maxBinCount) {
    const numPoints = 200;
    const bandwidth = calculateBandwidth(data);
    
    // 生成曲线点
    const points = [];
    let maxDensity = 0;
    
    for (let i = 0; i <= numPoints; i++) {
        const x = minVal + (maxVal - minVal) * (i / numPoints);
        const density = kdeEstimate(x, data, bandwidth);
        points.push({ x, density });
        if (density > maxDensity) maxDensity = density;
    }
    
    // 归一化密度值以匹配直方图高度
    const normalizationFactor = (data.length * (maxVal - minVal)) / maxBinCount;
    
    // 绘制曲线
    ctx.strokeStyle = '#D36A00';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    points.forEach((point, i) => {
        const x = padding + ((point.x - minVal) / (maxVal - minVal)) * chartWidth;
        const normalizedDensity = point.density * normalizationFactor;
        const y = height - padding - (normalizedDensity / maxBinCount) * chartHeight;
        
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
    
    // 添加图例
    ctx.fillStyle = '#D36A00';
    ctx.font = 'bold 12px Microsoft YaHei';
    ctx.textAlign = 'left';
    ctx.fillText('— KDE 拟合曲线', padding + 10, padding + 20);
}

/**
 * 计算最优带宽（Silverman's rule of thumb）
 */
function calculateBandwidth(data) {
    const n = data.length;
    const std = standardDeviation(data);
    const iqr = interquartileRange(data);
    
    // 使用较小的那个
    const sigma = Math.min(std, iqr / 1.34);
    
    return 0.9 * sigma * Math.pow(n, -0.2);
}

/**
 * KDE 估计
 */
function kdeEstimate(x, data, bandwidth) {
    const n = data.length;
    let sum = 0;
    
    data.forEach(xi => {
        const u = (x - xi) / bandwidth;
        sum += gaussianKernel(u);
    });
    
    return sum / (n * bandwidth);
}

/**
 * 高斯核函数
 */
function gaussianKernel(u) {
    return (1 / Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * u * u);
}

/**
 * 计算标准差
 */
function standardDeviation(data) {
    const mean = data.reduce((sum, val) => sum + val, 0) / data.length;
    const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length;
    return Math.sqrt(variance);
}

/**
 * 计算四分位距
 */
function interquartileRange(data) {
    const sorted = [...data].sort((a, b) => a - b);
    const q1 = sorted[Math.floor(sorted.length * 0.25)];
    const q3 = sorted[Math.floor(sorted.length * 0.75)];
    return q3 - q1;
}

/**
 * 显示统计表格（管理员模式）
 */
function showStatsTable() {
    document.getElementById('statsControls').style.display = 'flex';
    document.getElementById('statsTableContainer').style.display = 'block';
}

/**
 * 渲染统计表格
 */
function renderStatsTable(sortedStats) {
    const tbody = document.getElementById('statsTableBody');
    tbody.innerHTML = '';
    
    sortedStats.forEach((stat, index) => {
        const row = document.createElement('tr');
        
        // 排名
        const rankCell = document.createElement('td');
        rankCell.className = `rank-cell ${getRankClass(index)}`;
        rankCell.textContent = index + 1;
        row.appendChild(rankCell);
        
        // 作者姓名
        const nameCell = document.createElement('td');
        nameCell.className = 'author-name-cell';
        nameCell.textContent = stat.name;
        row.appendChild(nameCell);
        
        // 发表论文数
        const paperCountCell = document.createElement('td');
        paperCountCell.textContent = stat.paperCount;
        row.appendChild(paperCountCell);
        
        // Gameme Factor
        const gamemeFactorCell = document.createElement('td');
        gamemeFactorCell.className = 'gameme-factor-cell';
        gamemeFactorCell.textContent = stat.gamemeFactor.toFixed(4);
        row.appendChild(gamemeFactorCell);
        
        // 查看详情链接（跳转到 nowbase.html 搜索该作者）
        const detailCell = document.createElement('td');
        const link = document.createElement('a');
        link.href = `nowbase.html?author=${encodeURIComponent(stat.name)}`;
        link.className = 'detail-link';
        link.textContent = '查看论文';
        link.target = '_blank';
        detailCell.appendChild(link);
        row.appendChild(detailCell);
        
        tbody.appendChild(row);
    });
}

/**
 * 根据指标和排序方式排序
 */
function sortAuthors(stats, metric, order) {
    return [...stats].sort((a, b) => {
        let valueA = a[metric];
        let valueB = b[metric];
        
        if (order === 'asc') {
            return valueA - valueB;
        } else {
            return valueB - valueA;
        }
    });
}

/**
 * 获取排名徽章类名
 */
function getRankClass(index) {
    if (index === 0) return 'rank-1';
    if (index === 1) return 'rank-2';
    if (index === 2) return 'rank-3';
    return '';
}

/**
 * 更新统计显示
 */
function updateStatsDisplay() {
    const sortedStats = sortAuthors(authorsData, currentMetric, currentSortOrder);
    renderStatsTable(sortedStats);
}

/**
 * 初始化事件监听
 */
function initEventListeners() {
    // 如果是管理员模式，初始化排序控件
    if (isAdminMode) {
        // 指标选择
        document.getElementById('metricSelect').addEventListener('change', function(e) {
            currentMetric = e.target.value;
            updateStatsDisplay();
        });
        
        // 排序方式选择
        document.getElementById('sortOrder').addEventListener('change', function(e) {
            currentSortOrder = e.target.value;
            updateStatsDisplay();
        });
        
        // 初始渲染表格
        updateStatsDisplay();
    }
    
    // 搜索框事件（始终可用）
    const searchInput = document.getElementById('authorSearch');
    let selectedIndex = 0;
    
    // 输入事件
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value;
        const suggestions = searchAuthors(query);
        selectedIndex = 0;
        showSuggestions(suggestions);
    });
    
    // 键盘事件
    searchInput.addEventListener('keydown', function(e) {
        const suggestionsList = document.getElementById('authorSuggestions');
        const items = suggestionsList.querySelectorAll('.suggestion-item');
        
        if (!suggestionsList.classList.contains('visible') || items.length === 0) {
            if (e.key === 'Enter' && selectedAuthor) {
                displayAuthorInfo(selectedAuthor);
            }
            return;
        }
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = (selectedIndex + 1) % items.length;
            updateSelectedSuggestion(items, selectedIndex);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = (selectedIndex - 1 + items.length) % items.length;
            updateSelectedSuggestion(items, selectedIndex);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (items[selectedIndex]) {
                const authorName = items[selectedIndex].dataset.author;
                selectAuthor(authorName);
            }
        } else if (e.key === 'Escape') {
            hideSuggestions();
        }
    });
    
    // 点击外部关闭建议列表
    document.addEventListener('click', function(e) {
        const searchBox = document.querySelector('.search-box');
        if (!searchBox.contains(e.target)) {
            hideSuggestions();
        }
    });
}

/**
 * 更新选中的建议项
 */
function updateSelectedSuggestion(items, index) {
    items.forEach((item, i) => {
        if (i === index) {
            item.classList.add('selected');
            item.scrollIntoView({ block: 'nearest' });
        } else {
            item.classList.remove('selected');
        }
    });
}

/**
 * 主函数：初始化页面
 */
async function initPage() {
    // 检查是否为管理员模式
    isAdminMode = checkAdminMode();
    
    // 检查是否有 explain 参数
    const urlParams = new URLSearchParams(window.location.search);
    const showExplain = urlParams.has('explain');
    
    // 如果有 explain 参数，只显示说明文字
    if (showExplain) {
        hideLoading();
        document.getElementById('gamemeExplanation').style.display = 'block';
        
        // 显示返回按钮并修改链接，跳转到不带参数的页面
        const backButton = document.getElementById('backButton');
        if (backButton) {
            backButton.style.display = 'inline-block';
            backButton.href = window.location.pathname;
        }
        
        // 隐藏问号按钮
        const helpIcon = document.querySelector('.help-icon-inline');
        if (helpIcon) {
            helpIcon.style.display = 'none';
        }
        return;
    }
    
    // 加载 NowBase 数据
    const papers = await loadJSONData(NOWBASE_FILE);
    
    if (!papers) {
        showError('无法加载论文数据');
        return;
    }
    
    // 保存全局数据
    nowbaseData = papers;
    allAuthors = extractAllAuthors(papers);
    
    // 隐藏加载状态
    hideLoading();
    
    // 计算统计数据（两种模式都需要）
    authorsData = calculateAuthorStats(papers);
    
    // 显示 Gameme Factor 分布图（两种模式都显示）
    showDistributionChart(authorsData);
    
    if (isAdminMode) {
        // 管理员模式：显示统计表格
        showStatsTable();
    } else {
        // 普通模式：显示搜索框
        showSearchUI();
    }
    
    // 初始化事件监听
    initEventListeners();
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', initPage);

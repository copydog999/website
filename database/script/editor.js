/**
 * 编辑部成员展示页面脚本
 * 从 URL 参数获取 id，加载并显示对应成员信息
 */

// 数据文件路径
const DATA_FILE = 'data/nowledge.json';

/**
 * 从 URL 获取查询参数
 */
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * 加载 JSON 数据
 */
async function loadEditorData() {
    try {
        const response = await fetch(DATA_FILE);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('加载数据失败:', error);
        showError(`数据加载失败: ${error.message}`);
        return null;
    }
}

/**
 * 加载 NowBase 论文数据
 */
async function loadNowBaseData() {
    try {
        const response = await fetch('data/nowbase.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('加载 NowBase 数据失败:', error);
        return [];
    }
}

/**
 * 查找指定 ID 的成员
 */
function findEditorById(editors, id) {
    return editors.find(editor => editor.id === id);
}

/**
 * 从 NowBase 中搜索作者的论文
 */
function findAuthorPapers(nowbaseData, authorName) {
    if (!nowbaseData || !authorName) return [];
    
    return nowbaseData.filter(paper => {
        if (!paper.authors || !Array.isArray(paper.authors)) return false;
        return paper.authors.some(author => author === authorName);
    });
}

/**
 * 渲染研究方向标签
 */
function renderResearchTags(tags) {
    if (!tags || tags.length === 0) {
        return '<p class="info-content">暂无信息</p>';
    }
    
    const tagsHtml = tags.map(tag => 
        `<a href="https://www.bing.com/search?q=${encodeURIComponent(tag)}" target="_blank" class="research-tag" title="点击在必应搜索: ${escapeHtml(tag)}">${escapeHtml(tag)}</a>`
    ).join('');
    
    return `<div class="research-tags">${tagsHtml}</div>`;
}

/**
 * 渲染论文列表
 */
function renderPapers(papers, nowbasePapers = [], isNowbaseSection = false) {
    // 合并成员自带的论文和从 NowBase 搜索到的论文
    const allPapers = [];
    
    // 添加成员自带的论文
    if (papers && papers.length > 0) {
        allPapers.push(...papers);
    }
    
    // 添加从 NowBase 搜索到的论文（去重）
    if (nowbasePapers && nowbasePapers.length > 0) {
        const existingDois = new Set(allPapers.map(p => p.doi).filter(Boolean));
        nowbasePapers.forEach(paper => {
            // 检查是否已存在
            if (!existingDois.has(paper.nowbasedoi)) {
                allPapers.push({
                    title: paper.title,
                    journal: paper.issue || '',
                    conference: '',
                    year: paper.year || new Date(paper.published).getFullYear(),
                    doi: paper.nowbasedoi
                });
            }
        });
    }
    
    if (allPapers.length === 0) {
        return { count: 0, html: '<p class="info-content">暂无发表论文</p>' };
    }
    
    const papersHtml = allPapers.map(paper => {
        const venue = paper.journal || paper.conference || '未知出版物';
        const venueType = paper.journal ? '期刊' : (paper.conference ? '会议' : '');
        const venueLabel = venueType ? `${venueType}：` : '';
        let doiDisplay;
        if (paper.doi && paper.doi !== '(Waiting for publishment)') {
            if (isNowbaseSection) {
                // 本刊发表论文：跳转到 nowbase.html
                doiDisplay = `<div class="paper-doi">NowBase DOI: <a href="../nowbase.html?doi=${encodeURIComponent(paper.doi)}" target="_blank">${escapeHtml(paper.doi)}</a></div>`;
            } else {
                // 其他学术论文：跳转到 doi.org
                doiDisplay = `<div class="paper-doi">DOI: <a href="https://doi.org/${paper.doi}" target="_blank">${escapeHtml(paper.doi)}</a></div>`;
            }
        } else {
            doiDisplay = isNowbaseSection 
                ? `<div class="paper-doi">NowBase DOI: ${escapeHtml(paper.doi || 'N/A')}</div>`
                : `<div class="paper-doi">DOI: ${escapeHtml(paper.doi || 'N/A')}</div>`;
        }
        
        return `
            <li class="paper-item">
                <div class="paper-title">${escapeHtml(paper.title)}</div>
                <div class="paper-meta">${venueLabel}${escapeHtml(venue)}, ${paper.year}</div>
                ${doiDisplay}
            </li>
        `;
    }).join('');
    
    return { count: allPapers.length, html: `<ul class="papers-list">${papersHtml}</ul>` };
}

/**
 * HTML 转义函数，防止 XSS 攻击
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 应用主题颜色
 */
function applyThemeColor(colorStyle) {
    // 定义不同主题的颜色方案
    const themes = {
        'blue': {
            primary: '#1A3A4A',      // 深沉蓝
            secondary: '#2C5060',    // 中深蓝
            accent: '#A05A20',       // 深橙色
            light: '#D8E4EC',        // 浅蓝背景
            gradient: 'linear-gradient(135deg, #1A3A4A 0%, #2C5060 100%)'
        },
        'purple': {
            primary: '#4A2C4A',      // 深沉紫
            secondary: '#5E4060',    // 中深紫
            accent: '#A05A20',       // 深橙色
            light: '#E4D8E4',        // 浅紫背景
            gradient: 'linear-gradient(135deg, #4A2C4A 0%, #5E4060 100%)'
        },
        'green': {
            primary: '#2C4A3A',      // 深沉绿
            secondary: '#406050',    // 中深绿
            accent: '#A05A20',       // 深橙色
            light: '#D8E4DE',        // 浅绿背景
            gradient: 'linear-gradient(135deg, #2C4A3A 0%, #406050 100%)'
        },
        'red': {
            primary: '#5A2C2C',      // 深沉红
            secondary: '#704040',    // 中深红
            accent: '#A05A20',       // 深橙色
            light: '#E4D8D8',        // 浅红背景
            gradient: 'linear-gradient(135deg, #5A2C2C 0%, #704040 100%)'
        },
        'teal': {
            primary: '#204A48',      // 深沉青
            secondary: '#306060',    // 中深青
            accent: '#A05A20',       // 深橙色
            light: '#D8E4E4',        // 浅青背景
            gradient: 'linear-gradient(135deg, #204A48 0%, #306060 100%)'
        },
        'indigo': {
            primary: '#2C3A5A',      // 深沉靛蓝
            secondary: '#405070',    // 中深靛蓝
            accent: '#A05A20',       // 深橙色
            light: '#D8DCE4',        // 浅靛蓝背景
            gradient: 'linear-gradient(135deg, #2C3A5A 0%, #405070 100%)'
        },
        'pink': {
            primary: '#5A2C40',      // 深沉粉
            secondary: '#704058',    // 中深粉
            accent: '#A05A20',       // 深橙色
            light: '#E4D8DE',        // 浅粉背景
            gradient: 'linear-gradient(135deg, #5A2C40 0%, #704058 100%)'
        },
        'brown': {
            primary: '#4A3A2C',      // 深沉棕
            secondary: '#605040',    // 中深棕
            accent: '#A05A20',       // 深橙色
            light: '#E4E0D8',        // 浅棕背景
            gradient: 'linear-gradient(135deg, #4A3A2C 0%, #605040 100%)'
        },
        'cyan': {
            primary: '#204A5A',      // 深沉青绿
            secondary: '#306070',    // 中深青绿
            accent: '#A05A20',       // 深橙色
            light: '#D8E4E8',        // 浅青绿背景
            gradient: 'linear-gradient(135deg, #204A5A 0%, #306070 100%)'
        },
        'orange': {
            primary: '#5A4020',      // 深沉橙
            secondary: '#705830',    // 中深橙
            accent: '#204060',       // 深蓝色
            light: '#E4DED8',        // 浅橙背景
            gradient: 'linear-gradient(135deg, #5A4020 0%, #705830 100%)'
        }
    };
    
    const theme = themes[colorStyle] || themes['blue'];
    
    // 创建或更新 style 标签
    let styleTag = document.getElementById('dynamic-theme');
    if (!styleTag) {
        styleTag = document.createElement('style');
        styleTag.id = 'dynamic-theme';
        document.head.appendChild(styleTag);
    }
    
    // 生成 CSS 变量和样式
    styleTag.textContent = `
        :root {
            --color-primary: ${theme.primary};
            --color-secondary: ${theme.secondary};
            --color-accent: ${theme.accent};
            --color-light: ${theme.light};
            --color-gradient: ${theme.gradient};
        }
        
        .back-button {
            color: var(--color-secondary);
            border-color: var(--color-secondary);
        }
        
        .back-button:hover {
            background-color: var(--color-secondary);
        }
        
        .section-title h2 {
            color: var(--color-primary);
            border-bottom-color: var(--color-accent);
        }
        
        .loading-state {
            color: var(--color-secondary);
        }
        
        .error-state {
            color: var(--color-accent);
            border-left-color: var(--color-accent);
        }
        
        .h-index-badge {
            color: var(--color-accent);
        }
        
        .author-header {
            background: var(--color-gradient);
        }
        
        .author-name,
        .author-position,
        .author-institution-title {
            color: white !important;
        }
        
        .info-label {
            color: var(--color-primary);
        }
        
        .bio-label {
            color: var(--color-accent);
        }
        
        .research-tag {
            background-color: var(--color-secondary);
        }
        
        .research-tag:hover {
            background-color: var(--color-accent);
            box-shadow: 0 4px 8px rgba(211, 106, 0, 0.3);
        }
        
        .paper-item {
            border-left-color: var(--color-accent);
        }
        
        .paper-title {
            color: var(--color-primary);
        }
        
        .paper-doi,
        .paper-doi a {
            color: var(--color-secondary);
        }
        
        .paper-doi a:hover {
            color: var(--color-accent);
        }
        
        .site-footer {
            background: linear-gradient(to bottom, var(--color-primary), #002147);
        }
    `;
}

/**
 * 渲染作者卡片
 */
function renderAuthorCard(author, nowbasePapers = []) {
    // 生成基于姓名的默认头像 URL
    const defaultAvatar = `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(author.name)}`;
    const avatarUrl = author.avatar_url || defaultAvatar;
    const hIndex = author['h-index'];
    const backgroundUrl = author.backgound_url || author.background_url;
    const colorStyle = author.colorstyle || 'blue'; // 默认蓝色
    
    // 应用主题色
    applyThemeColor(colorStyle);
    
    // 构建 h-index 显示 HTML（如果有该字段）
    const hIndexHtml = hIndex !== undefined && hIndex !== null ? `
        <div class="h-index-badge" title="h指数（h-index）：一名科研人员的h指数是指他（她）至多有h篇论文分别被引用了至少h次。">
            <div class="h-index-label">h-index</div>
            <div class="h-index-value">${hIndex}</div>
        </div>
    ` : '';
    
    // 构建所属机构·学术头衔的显示
    const institution = author.institution || '未知机构';
    const title = author.title || '未知头衔';
    const institutionTitle = `${institution} · ${title}`;
    
    // 构建背景样式
    const backgroundStyle = backgroundUrl ? `style="background-image: url('${escapeHtml(backgroundUrl)}'); background-size: cover; background-position: left top; background-repeat: no-repeat;"` : '';
    
    return `
        <div class="author-card">
            ${hIndexHtml}
            <div class="author-header" ${backgroundStyle}>
                <img src="${escapeHtml(avatarUrl)}" alt="${escapeHtml(author.name)}" class="author-avatar">
                <h2 class="author-name">${escapeHtml(author.name)}</h2>
                <p class="author-position">《电子游戏科学与技术》${escapeHtml(author.position)}</p>
                <p class="author-institution-title">${escapeHtml(institutionTitle)}</p>
            </div>
            
            <div class="author-body">
                <!-- 个人简介 -->
                <div class="info-section bio-section">
                    <div class="info-label bio-label">个人简介</div>
                    <div class="info-content bio-text">
                        ${escapeHtml(author.bio || '暂无简介')}
                    </div>
                </div>
                
                <!-- 研究方向 -->
                <div class="info-section">
                    <div class="info-label">研究方向</div>
                    ${renderResearchTags(author.resfield)}
                </div>
                
                <!-- 其他学术论文 -->
                ${(() => {
                    const otherPapersResult = renderPapers(author.papers, [], false);
                    if (otherPapersResult.count > 0) {
                        return `
                <div class="info-section">
                    <div class="info-label">学术论文 (${otherPapersResult.count})</div>
                    ${otherPapersResult.html}
                </div>`;
                    }
                    return '';
                })()}
                
                <!-- 本刊发表论文 -->
                ${(() => {
                    const nowbaseResult = renderPapers([], nowbasePapers, true);
                    if (nowbaseResult.count > 0) {
                        return `
                <div class="info-section">
                    <div class="info-label">本刊发表论文 (${nowbaseResult.count})</div>
                    ${nowbaseResult.html}
                </div>`;
                    }
                    return '';
                })()}
            </div>
        </div>
    `;
}

/**
 * 显示错误信息
 */
function showError(message) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const authorGrid = document.getElementById('authorGrid');
    
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
    
    if (authorGrid) {
        authorGrid.innerHTML = `
            <div class="error-state">
                <h3>⚠ 错误</h3>
                <p>${escapeHtml(message)}</p>
                <p><a href="editor.html" class="cta-button2-small">返回首页</a></p>
            </div>
        `;
    }
}

/**
 * 显示加载状态
 */
function showLoading() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
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
 * 主函数：初始化页面
 */
async function initPage() {
    showLoading();
    
    // 获取 URL 中的 id 参数
    const idParam = getUrlParameter('id');
    
    if (!idParam) {
        showError('未提供成员 ID。请使用 editor.html?id=x 格式访问。');
        hideLoading();
        return;
    }
    
    // 将 id 转换为数字类型（因为 JSON 中 id 是数字）
    const id = parseInt(idParam, 10);
    
    if (isNaN(id)) {
        showError(`无效的成员 ID: ${idParam}`);
        hideLoading();
        return;
    }
    
    // 加载数据
    const editors = await loadEditorData();
    
    if (!editors) {
        hideLoading();
        return;
    }
    
    // 查找指定成员
    const author = findEditorById(editors, id);
    
    if (!author) {
        showError(`未找到 ID 为 ${id} 的成员。`);
        hideLoading();
        return;
    }
    
    // 加载 NowBase 数据并搜索作者论文
    const nowbaseData = await loadNowBaseData();
    const authorPapers = findAuthorPapers(nowbaseData, author.name);
    
    // 渲染作者卡片
    const authorGrid = document.getElementById('authorGrid');
    if (authorGrid) {
        authorGrid.innerHTML = renderAuthorCard(author, authorPapers);
    }
    
    hideLoading();
    
    // 调试信息（可选）
    const debugInfo = document.getElementById('debugInfo');
    if (debugInfo) {
        debugInfo.innerHTML = `
            <strong>调试信息：</strong><br>
            成员 ID: ${author.id}<br>
            姓名: ${author.name}<br>
            职位: ${author.position}<br>
            论文数量: ${author.papers ? author.papers.length : 0}<br>
            NowBase 论文数量: ${authorPapers.length}
        `;
    }
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', initPage);

// 最佳论文数据
let bestPapersData = [];

// 加载最佳论文数据
async function loadBestPapers() {
    try {
        const response = await fetch('database/data/nowbase.json');
        const allPapers = await response.json();
        
        // 筛选出有 bestpaperaward 标记的论文
        bestPapersData = allPapers.filter(paper => paper.bestpaperaward === true);
        
        if (bestPapersData.length === 0) {
            document.getElementById('papersContainer').innerHTML = '<div class="no-results">暂无最佳论文奖</div>';
            return;
        }
        
        displayBestPapers(bestPapersData);
    } catch (error) {
        console.error('加载最佳论文数据失败:', error);
        document.getElementById('papersContainer').innerHTML = '<div class="no-results">加载失败</div>';
    }
}

// 按期号分组显示
function displayBestPapers(papers) {
    if (!papers || papers.length === 0) {
        document.getElementById('papersContainer').innerHTML = '<div class="no-results">未找到匹配的最佳论文</div>';
        return;
    }
    
    // 按 published 日期倒序排序（最新的在前）
    const sortedPapers = papers.sort((a, b) => {
        const dateA = a.published ? new Date(a.published) : new Date(0);
        const dateB = b.published ? new Date(b.published) : new Date(0);
        return dateB - dateA;
    });
    
    renderBestPapers(sortedPapers);
}

// 渲染最佳论文 - 直接展示卡片列表
function renderBestPapers(papers) {
    const container = document.getElementById('papersContainer');
    
    // 使用DocumentFragment优化DOM操作
    const fragment = document.createDocumentFragment();
    
    // 卡片列表容器
    const listContainer = document.createElement('div');
    listContainer.className = 'papers-list';
    listContainer.style.display = 'flex';
    listContainer.style.flexDirection = 'column';
    listContainer.style.gap = '20px';
    
    papers.forEach((paper) => {
        const card = createBestPaperCard(paper);
        listContainer.appendChild(card);
    });
    
    fragment.appendChild(listContainer);
    container.innerHTML = '';
    container.appendChild(fragment);
}

/**
 * 创建最佳论文卡片
 * @param {Object} paper - 论文数据对象
 * @returns {HTMLElement} 卡片元素
 */
function createBestPaperCard(paper) {
    const doi = paper.nowbasedoi || '';
    const posterPath = doi ? `database/data/poster/${doi}.jpeg` : '';
    
    // 获取自定义字体颜色(用于深色背景海报的论文)
    const customFontColor = utils.getFontColorForDOI(doi);
    const titleColor = customFontColor || '#002B4D';
    const authorColor = customFontColor || '#1a1a1a';
    const authorIconColor = customFontColor || '#004C7F';
    const textShadow = customFontColor ? '0 0 8px rgba(0,0,0,0.9), 0 0 4px rgba(0,0,0,0.9)' : '0 0 8px rgba(255,255,255,0.9), 0 0 4px rgba(255,255,255,0.9)';
    
    // 创建卡片容器
    const card = document.createElement('div');
    card.className = 'best-paper-card';
    card.style.position = 'relative';
    card.style.background = 'white';
    card.style.border = '2px solid #666';
    card.style.borderRadius = '8px';
    card.style.overflow = 'hidden';
    card.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
    card.style.transition = 'all 0.3s ease';
    card.style.cursor = 'pointer';
    card.style.minHeight = '200px';
    
    // 悬停效果
    card.addEventListener('mouseenter', () => {
        card.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        card.style.borderColor = '#D36A00';
    });
    card.addEventListener('mouseleave', () => {
        card.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
        card.style.borderColor = '#666';
    });
    
    // 点击跳转
    card.addEventListener('click', () => {
        window.location.href = `nowbase.html?doi=${doi}`;
    });
    
    // 背景海报(如果存在)
    if (posterPath && doi) {
        const bgLayer = document.createElement('div');
        bgLayer.style.position = 'absolute';
        bgLayer.style.top = '0';
        bgLayer.style.left = '0';
        bgLayer.style.width = '100%';
        bgLayer.style.height = '100%';
        bgLayer.style.backgroundImage = `url('${posterPath}')`;
        bgLayer.style.backgroundSize = 'cover';
        bgLayer.style.backgroundPosition = 'center';
        bgLayer.style.zIndex = '0';
        card.appendChild(bgLayer);
    }
    
    // 左上角 Best Paper Award 标志
    const badgeDiv = document.createElement('div');
    badgeDiv.style.position = 'absolute';
    badgeDiv.style.top = '-8px';
    badgeDiv.style.left = '-8px';
    badgeDiv.style.zIndex = '1';
    
    const badge = document.createElement('span');
    badge.className = 'best-paper-badge';
    badge.style.display = 'inline-block';
    badge.style.background = 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)';
    badge.style.color = '#8B4513';
    badge.style.padding = '0.7px 4.2px';
    badge.style.borderRadius = '8.4px';
    badge.style.fontSize = '0.49em';
    badge.style.fontWeight = 'bold';
    badge.style.verticalAlign = 'middle';
    badge.style.border = '1.4px solid #FFA500';
    badge.style.fontFamily = "'Times New Roman', Times, serif";
    badge.textContent = '🏆 Best Paper Award';
    
    badgeDiv.appendChild(badge);
    card.appendChild(badgeDiv);
    
    // 卡片内容容器
    const contentDiv = document.createElement('div');
    contentDiv.style.position = 'relative';
    contentDiv.style.zIndex = '1';
    contentDiv.style.padding = '30px';
    contentDiv.style.paddingLeft = '120px';
    
    // 标题
    const titleHeading = document.createElement('h3');
    titleHeading.style.margin = '0 0 15px 0';
    titleHeading.style.fontSize = '22px';
    titleHeading.style.lineHeight = '1.5';
    titleHeading.style.color = titleColor;
    titleHeading.style.fontWeight = '700';
    titleHeading.style.textShadow = textShadow;
    
    const titleLink = document.createElement('a');
    titleLink.href = `nowbase.html?doi=${doi}`;
    titleLink.style.color = titleColor;
    titleLink.style.textDecoration = 'none';
    titleLink.textContent = paper.title || '无标题'; // 自动转义
    titleLink.addEventListener('mouseenter', () => {
        titleLink.style.textDecoration = 'underline';
    });
    titleLink.addEventListener('mouseleave', () => {
        titleLink.style.textDecoration = 'none';
    });
    
    titleHeading.appendChild(titleLink);
    contentDiv.appendChild(titleHeading);
    
    // 作者
    if (paper.authors && paper.authors.length > 0) {
        const authorsText = Array.isArray(paper.authors) ? 
            (paper.authors.length <= 3 ? paper.authors.join(', ') : paper.authors.slice(0, 3).join(', ') + ' 等') :
            paper.authors;
        
        const authorDiv = document.createElement('div');
        authorDiv.style.fontSize = '18px';
        authorDiv.style.color = authorColor;
        authorDiv.style.marginBottom = '8px';
        authorDiv.style.fontWeight = '600';
        authorDiv.style.textShadow = textShadow;
        
        const authorSpan = document.createElement('span');
        authorSpan.style.color = authorIconColor;
        authorSpan.textContent = `👤 ${authorsText}`; // 自动转义
        
        authorDiv.appendChild(authorSpan);
        contentDiv.appendChild(authorDiv);
    }
    
    card.appendChild(contentDiv);
    return card;
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    utils.applySimpleMode();
    loadBestPapers();
});

document.addEventListener('DOMContentLoaded', function() {
    // 应用极简模式
    utils.applySimpleMode();
    
    // 研究方向标签页功能
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 移除所有按钮的 active 类
            tabButtons.forEach(btn => btn.classList.remove('active'));
            // 为当前按钮添加 active 类
            button.classList.add('active');
            
            // 隐藏所有内容区域
            tabContents.forEach(content => content.classList.remove('active'));
            
            // 显示对应的内容区域
            const tabId = button.getAttribute('data-tab');
            const activeContent = document.getElementById(`${tabId}-tab`);
            if (activeContent) {
                activeContent.classList.add('active');
            }
        });
    });
    
    // 默认显示第一个标签页
    if (tabButtons.length > 0 && tabContents.length > 0) {
        tabButtons[0].classList.add('active');
        tabContents[0].classList.add('active');
    }
    
    // 点击页面其他地方关闭下拉菜单
    document.addEventListener('click', function(e) {
        const dropdownContainers = document.querySelectorAll('.dropdown-container');
        dropdownContainers.forEach(container => {
            if (!container.contains(e.target)) {
                container.classList.remove('active');
            }
        });
    });
    
    // 投稿表单功能
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', function() {
            // 获取表单数据
            const paperTitle = document.getElementById('paperTitle').value.trim();
            const authorName = document.getElementById('authorName').value.trim();
            const affiliation = document.getElementById('affiliation').value.trim();
            const email = document.getElementById('email').value.trim();
            const researchField = document.getElementById('researchField').value;
            const paperType = document.getElementById('paperType').value;
            const keywords = document.getElementById('keywords').value.trim();
            const abstract = document.getElementById('abstract').value.trim();
            
            // 验证必填字段
            if (!paperTitle || !authorName || !email || !researchField) {
                alert('请填写所有必填字段（带*号的为必填项）');
                return;
            }
            
            // 验证邮箱格式
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert('请输入有效的邮箱地址');
                return;
            }
            
            // 生成邮件主题和内容
            const subject = encodeURIComponent(`【JOEST】论文投稿：${paperTitle}`);
            let body = `论文标题：${paperTitle}\n`;
            body += `作者姓名：${authorName}\n`;
            if (affiliation) body += `工作/学习单位：${affiliation}\n`;
            body += `邮箱地址：${email}\n`;
            
            // 将 researchField 值转换为中文名称
            const fieldNames = {
                'general': '公共科学版',
                'basic': '基础科学版',
                'engineering': '工程技术版',
                'social': '社会科学版',
                'humanities': '人文科学版',
                'education': '教育科学版',
                'health': '健康医学版',
                'youth': '少年科学志'
            };
            body += `投稿版块：${fieldNames[researchField]}\n`;
            
            body += `稿件类型：${paperType === 'regular' ? '常规投稿' : paperType === 'special' ? '特刊投稿' : '综述文章'}\n`;
            if (keywords) body += `关键词：${keywords}\n`;
            if (abstract) body += `\n摘要:\n${abstract}\n`;
            
            body += `\n\n请将稿件以附件形式发送至此邮件。`;
            
            // 生成邮件链接
            const mailtoLink = `mailto:dev.projectamadeus@outlook.com?subject=${subject}&body=${encodeURIComponent(body)}`;
            
            // 打开邮件客户端
            window.location.href = mailtoLink;
        });
    }
    
    // 加载侧边栏最佳论文奖（最新的 5 条）
    loadSidebarBestPapers();
});

// 加载侧边栏最佳论文奖
async function loadSidebarBestPapers() {
    try {
        const response = await fetch('database/data/nowbase.json');
        if (!response.ok) {
            console.error('加载 nowbase.json 失败');
            return;
        }
        
        const papersData = await response.json();
        
        if (!papersData || !Array.isArray(papersData) || papersData.length === 0) {
            return;
        }
        
        // 筛选出有 bestpaperaward 标记的论文
        const bestPapers = papersData.filter(paper => paper.bestpaperaward === true);
        
        if (bestPapers.length === 0) {
            document.getElementById('papersContainer').innerHTML = '<div class="no-results">暂无最佳论文奖</div>';
            return;
        }
        
        // 按 published 日期倒序排序（最新的在前）
        const sortedPapers = bestPapers.sort((a, b) => {
            const dateA = a.published ? new Date(a.published) : new Date(0);
            const dateB = b.published ? new Date(b.published) : new Date(0);
            return dateB - dateA;
        });
        
        // 取最新的 5 条
        const latestPapers = sortedPapers.slice(0, 5);
        
        displaySidebarBestPapers(latestPapers);
    } catch (error) {
        console.error('加载侧边栏最佳论文奖失败:', error);
        document.getElementById('papersContainer').innerHTML = '<div class="no-results">加载失败</div>';
    }
}

/**
 * HTML转义函数(防止XSS)
 * @param {string} text - 需要转义的文本
 * @returns {string} 转义后的文本
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 显示侧边栏最佳论文奖
 * @param {Array} papersList - 最佳论文列表(最多5条)
 */
function displaySidebarBestPapers(papersList) {
    const container = document.getElementById('papersContainer');
    if (!container) return;
    
    // 使用DocumentFragment优化DOM操作
    const fragment = document.createDocumentFragment();
    
    // 创建容器
    const listContainer = document.createElement('div');
    listContainer.className = 'sidebar-best-papers-list';
    listContainer.style.display = 'flex';
    listContainer.style.flexDirection = 'column';
    listContainer.style.gap = '8px';
    
    // 添加“查看全部最佳论文”链接
    const linkDiv = document.createElement('div');
    linkDiv.style.textAlign = 'left';
    linkDiv.style.marginBottom = '0';
    const link = document.createElement('a');
    link.href = 'bestpaper.html';
    link.style.color = '#00629B';
    link.style.textDecoration = 'none';
    link.style.fontSize = '14.7px';
    link.style.fontWeight = 'bold';
    link.textContent = '查看全部最佳论文 →';
    linkDiv.appendChild(link);
    listContainer.appendChild(linkDiv);
    
    // 生成卡片
    papersList.forEach((paper) => {
        const card = createSidebarPaperCard(paper);
        listContainer.appendChild(card);
    });
    
    fragment.appendChild(listContainer);
    container.innerHTML = '';
    container.appendChild(fragment);
}

/**
 * 创建侧边栏论文卡片
 * @param {Object} paper - 论文数据
 * @returns {HTMLElement} 卡片元素
 */
function createSidebarPaperCard(paper) {
    const doi = paper.nowbasedoi || '';
    const posterPath = doi ? `database/data/poster/${doi}.jpeg` : '';
    
    // 获取自定义字体颜色
    const customFontColor = utils.getFontColorForDOI(doi);
    const titleColor = customFontColor || '#002B4D';
    const authorColor = customFontColor || '#1a1a1a';
    const authorIconColor = customFontColor || '#004C7F';
    const textShadow = customFontColor ? '0 0 6px rgba(0,0,0,0.9), 0 0 3px rgba(0,0,0,0.9)' : '0 0 6px rgba(255,255,255,0.9), 0 0 3px rgba(255,255,255,0.9)';
    
    // 创建卡片容器
    const card = document.createElement('div');
    card.className = 'sidebar-best-paper-card';
    card.style.position = 'relative';
    card.style.background = 'white';
    card.style.border = '1.5px solid #666';
    card.style.borderRadius = '6px';
    card.style.overflow = 'hidden';
    card.style.boxShadow = '0 1px 4px rgba(0,0,0,0.08)';
    card.style.transition = 'all 0.3s ease';
    card.style.cursor = 'pointer';
    card.style.minHeight = '100px';
    card.dataset.doi = doi; // 存储DOI用于事件委托
    
    // 悬停效果
    card.addEventListener('mouseenter', () => {
        card.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
        card.style.borderColor = '#D36A00';
    });
    card.addEventListener('mouseleave', () => {
        card.style.boxShadow = '0 1px 4px rgba(0,0,0,0.08)';
        card.style.borderColor = '#666';
    });
    
    // 点击跳转
    card.addEventListener('click', () => {
        window.location.href = `nowbase.html?doi=${doi}`;
    });
    
    // 背景海报(如果存在)
    if (posterPath && doi) {
        const bgLayer1 = document.createElement('div');
        bgLayer1.style.position = 'absolute';
        bgLayer1.style.top = '0';
        bgLayer1.style.left = '0';
        bgLayer1.style.width = '100%';
        bgLayer1.style.height = '100%';
        bgLayer1.style.backgroundImage = `url('${posterPath}')`;
        bgLayer1.style.backgroundSize = 'cover';
        bgLayer1.style.backgroundPosition = 'center center';
        bgLayer1.style.filter = 'saturate(50%) blur(2px)';
        bgLayer1.style.zIndex = '0';
        card.appendChild(bgLayer1);
        
        const bgLayer2 = document.createElement('div');
        bgLayer2.style.position = 'absolute';
        bgLayer2.style.top = '0';
        bgLayer2.style.left = '0';
        bgLayer2.style.width = '100%';
        bgLayer2.style.height = '100%';
        bgLayer2.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
        bgLayer2.style.zIndex = '0';
        card.appendChild(bgLayer2);
    }
    
    // 卡片内容容器
    const contentDiv = document.createElement('div');
    contentDiv.style.position = 'relative';
    contentDiv.style.zIndex = '1';
    contentDiv.style.padding = '10px';
    
    // 标题
    const titleHeading = document.createElement('h4');
    titleHeading.style.margin = '0 0 4px 0';
    titleHeading.style.fontSize = '13px';
    titleHeading.style.lineHeight = '1.3';
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
            (paper.authors.length <= 2 ? paper.authors.join(', ') : paper.authors.slice(0, 2).join(', ') + ' 等') :
            paper.authors;
        
        const authorDiv = document.createElement('div');
        authorDiv.style.fontSize = '11px';
        authorDiv.style.color = authorColor;
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

// 切换下拉菜单显示状态
function toggleDropdown(event) {
    event.preventDefault();
    event.stopPropagation();
    
    const dropdownContainer = event.target.closest('.dropdown-container');
    if (dropdownContainer) {
        // 切换 active 类
        dropdownContainer.classList.toggle('active');
    }
}
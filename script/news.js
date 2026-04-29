// 新闻数据（可以从 JSON 文件加载或硬编码）
let newsData = [];

// 加载新闻数据
async function loadNews() {
    try {
        console.log('开始加载新闻数据...');
        // 尝试从 JSON 文件加载新闻
        const response = await fetch('database/data/news.json');
        console.log('响应状态:', response.status);
        
        if (response.ok) {
            newsData = await response.json();
            console.log('新闻数据加载成功:', newsData);
        } else {
            // 如果 JSON 文件不存在，使用默认空数组
            console.warn('JSON 文件不存在或返回错误');
            newsData = [];
        }
        displayNews(newsData);
    } catch (error) {
        console.error('加载新闻数据失败:', error);
        // 显示默认内容
        newsData = [];
        displayNews(newsData);
    }
}

// 获取URL参数中的新闻 ID
function getNewsIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const newsId = urlParams.get('id');
    return newsId ? parseInt(newsId) : null;
}

// 根据 ID 查找新闻
function findNewsById(id) {
    if (!newsData || !Array.isArray(newsData)) {
        return null;
    }
    return newsData.find(news => news.id === id);
}

// 显示单条新闻详情
async function displayNewsDetail(news) {
    const container = document.getElementById('newsContainer');
    
    let htmlContent = `<div class="news-item">`;
    
    // 新闻标题
    htmlContent += `<h3 class="news-title">${news.title || '无标题'}</h3>`;
    
    // 新闻元信息
    htmlContent += `<div class="news-meta">`;
    if (news.date) {
        htmlContent += `<span class="news-date">📅 ${news.date}</span>`;
    }
    htmlContent += `</div>`;
    
    // 加载并渲染 Markdown 内容
    htmlContent += `<div class="news-content" id="markdown-content">加载中...</div>`;
    
    // 返回链接
    htmlContent += `<div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">`;
    htmlContent += `<a href="news.html" class="read-more">← 返回新闻列表</a>`;
    htmlContent += `</div>`;
    
    htmlContent += `</div>`;
    
    container.innerHTML = htmlContent;
    
    // 异步加载 Markdown 文件
    try {
        const newsId = news.id;
        const mdPath = `database/news/${newsId}.md`;
        
        const response = await fetch(mdPath);
        if (!response.ok) {
            throw new Error(`无法加载 Markdown 文件：${mdPath}`);
        }
        
        const markdownText = await response.text();
        
        // 使用 marked 渲染 Markdown
        const renderedHtml = marked.parse(markdownText);
        
        // 更新内容区域
        const contentDiv = document.getElementById('markdown-content');
        if (contentDiv) {
            contentDiv.innerHTML = renderedHtml;
        }
    } catch (error) {
        console.error('加载 Markdown 失败:', error);
        const contentDiv = document.getElementById('markdown-content');
        if (contentDiv) {
            contentDiv.innerHTML = '<p style="color: red;">内容加载失败：' + error.message + '</p>';
        }
    }
}

// 显示新闻列表
function displayNewsList(newsList) {
    console.log('显示新闻列表，数量:', newsList.length);
    const container = document.getElementById('newsContainer');
    console.log('容器元素:', container);
    
    if (!newsList || newsList.length === 0) {
        // 没有新闻时显示空容器
        console.log('没有新闻数据');
        container.innerHTML = '';
        return;
    }
    
    // 有新闻时显示新闻列表
    let htmlContent = '';
    
    newsList.forEach((news, index) => {
        console.log(`渲染新闻 ${index}:`, news);
        const newsId = `news-${index}`;
        
        htmlContent += `<div class="news-item" id="${newsId}">`;
        
        // 新闻标题
        htmlContent += `<h3 class="news-title">${news.title || '无标题'}</h3>`;
        
        // 新闻元信息
        htmlContent += `<div class="news-meta">`;
        if (news.date) {
            htmlContent += `<span class="news-date">📅 ${news.date}</span>`;
        }
        htmlContent += `</div>`;
        
        // 查看详情链接（使用 id 参数）
        if (news.id) {
            htmlContent += `<a href="news.html?id=${news.id}" class="read-more">查看详情 →</a>`;
        }
        
        htmlContent += `</div>`;
    });
    
    console.log('生成的 HTML:', htmlContent);
    container.innerHTML = htmlContent;
    console.log('HTML 已插入容器');
}

// 显示新闻
function displayNews(newsList) {
    // 检查 URL 中是否有 id 参数
    const newsId = getNewsIdFromURL();
    
    if (newsId !== null) {
        // 有 id 参数，显示单条新闻详情
        const news = findNewsById(newsId);
        if (news) {
            displayNewsDetail(news);
        } else {
            // 未找到对应的新闻
            const container = document.getElementById('newsContainer');
            container.innerHTML = '<div class="no-news"><p>未找到该新闻</p></div>';
        }
    } else {
        // 没有 id 参数，显示新闻列表
        displayNewsList(newsList);
    }
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 应用极简模式
    utils.applySimpleMode();
    
    loadNews();
});

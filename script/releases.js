// 期刊数据将从 nowbase.json 加载
let papersData = [];
let totalCount = 0; // 总论文数
let currentCount = 0; // 当前显示的论文数
let expandedIssues = new Set(); // 记录已展开的期号

// 加载论文数据
async function loadPapers() {
    try {
        const response = await fetch('../database/data/nowbase.json');
        papersData = await response.json();
        totalCount = papersData.length; // 设置总论文数
        currentCount = totalCount; // 初始状态下显示全部论文
        updateResultCount(); // 更新显示
        displayPapers(papersData);
        
        // 检查 URL 中是否有搜索参数
        const urlParams = new URLSearchParams(window.location.search);
        const searchParam = urlParams.get('search');
        if (searchParam) {
            // 在搜索框中填入搜索参数并执行搜索
            const searchBox = document.getElementById('searchBox');
            if (searchBox) {
                searchBox.value = searchParam;
                searchPapers(searchParam);
            }
        }
    } catch (error) {
        console.error('加载论文数据失败:', error);
        document.getElementById('papersContainer').innerHTML = '<div class="no-results">加载期刊数据失败，请稍后重试</div>';
    }
}

// 按期号分组显示（懒加载模式）
function displayPapers(papers) {
    if (!papers || papers.length === 0) {
        currentCount = 0;
        updateResultCount();
        document.getElementById('papersContainer').innerHTML = '<div class="no-results">未找到匹配的论文</div>';
        return;
    }
    
    // 更新当前显示的论文数量
    currentCount = papers.length;
    updateResultCount();
    
    // 按期号分组
    const groupedPapers = {};
    papers.forEach(paper => {
        if (!groupedPapers[paper.issue]) {
            groupedPapers[paper.issue] = [];
        }
        groupedPapers[paper.issue].push(paper);
    });
    
    // 判断是否为搜索结果
    const searchBox = document.getElementById('searchBox');
    const isSearchMode = searchBox && searchBox.value.trim() !== '';
    
    // 搜索模式下直接展开全部，否则使用懒加载
    renderPapers(groupedPapers, false, false, isSearchMode);
}

// 渲染论文的辅助函数
function renderPapers(groupedPapers, isIndexPage, isSidebarMode, expandAll = false) {
    let htmlContent = '';
    
    // 非侧边栏模式：保持原有的分组显示，但按期号倒序排列（新的在前）
    const sortedIssues = Object.keys(groupedPapers).reverse();
    
    for (const issue of sortedIssues) {
        const issueId = `issue-${issue.replace(/\s+/g, '-')}`;
        const isExpanded = expandAll || expandedIssues.has(issue);
        
        // 期号标题（可点击展开/收起）
        htmlContent += `<div class="paper-section">`;
        htmlContent += `<div class="issue-header" onclick="toggleIssue('${issueId}')" style="cursor: pointer; padding: 15px; background-color: #f5f5f5; border-left: 4px solid #733eee; margin-bottom: ${isExpanded ? '0' : '15px'};">`;
        htmlContent += `<h2 style="margin: 0; display: inline-block;">${issue}</h2>`;
        htmlContent += `<span style="float: right; color: #666; font-size: 0.9em;">(${groupedPapers[issue].length} 篇)</span>`;
        htmlContent += `<span class="expand-icon" style="float: right; margin-right: 10px; display: inline-block; transform: ${isExpanded ? 'rotate(90deg)' : 'rotate(0deg)'};">▶</span>`;
        htmlContent += `</div>`;
        
        // 期号内容（默认隐藏，展开后显示）
        htmlContent += `<div id="${issueId}" class="issue-content-full" style="display: ${isExpanded ? 'block' : 'none'};">`;
        
        // 按期号内的论文也倒序排列（新的在前）
        groupedPapers[issue].slice().reverse().forEach((paper, index) => {
                const paperId = `paper-${issue.replace(/\s+/g, '-')}-${index}`;
                htmlContent += `<div class="paper-item" id="${paperId}" style="display: flex; gap: 20px; align-items: flex-start; cursor: pointer;" onclick="window.location.href='nowbase.html?doi=${paper.nowbasedoi}'">`;
                    
            // 左侧：论文信息
            htmlContent += `<div class="paper-info-left" style="flex: 1 1 40%; min-width: 40%;">`;
                    
            // 构建标题行
            let titleLine = '';
            if (paper.level) {
                titleLine += `<i>${paper.level}</i> `;
            }
                    
            // 处理作者字段
            let authorsDisplay = '';
            if (paper.authors) {  // 确保 authors 存在
              if (Array.isArray(paper.authors)) {  // 只检查是否为数组
                  // 如果 authors 是数组，每个作者都创建链接
                  if (paper.authors.length > 0) {
                      // 只取前 3 位作者，超过则加"等"
                      if (paper.authors.length <= 3) {
                          authorsDisplay = paper.authors.map(author => 
                              `<a href="releases.html?search=${encodeURIComponent(author || '')}" class="author-link">${author || ''}</a>`
                          ).join(', ');
                      } else {
                          authorsDisplay = paper.authors.slice(0, 3).map(author => 
                              `<a href="releases.html?search=${encodeURIComponent(author || '')}" class="author-link">${author || ''}</a>`
                          ).join(', ') + ', 等';
                      }
                  } else {
                      authorsDisplay = 'N/A'; // 空数组情况
                  }
              } else {
                  // 如果 authors 是字符串，按原逻辑处理
                  let mainAuthor = paper.authors;
                  if (typeof paper.authors === 'string' && paper.authors.includes(' et al.')) {
                      mainAuthor = paper.authors.split(' et al.')[0];
                  } else if (typeof paper.authors === 'string' && paper.authors.includes(' et al')) {
                      mainAuthor = paper.authors.split(' et al')[0];
                  } else if (typeof paper.authors === 'string' && paper.authors.includes(', ')) {
                      mainAuthor = paper.authors.split(',')[0];
                  }
                                      
                  authorsDisplay = `<a href="releases.html?search=${encodeURIComponent(mainAuthor || '')}">${paper.authors}</a>`;
              }
            } else {
              authorsDisplay = '未知作者'; // 如果没有作者信息
            }
                    
            // 作者单独一行
            htmlContent += `<div class="paper-authors"><i>${authorsDisplay}:</i></div>`;
                    
            // 标题单独一行，字号放大两个 pt
            titleLine += `<a href="nowbase.html?doi=${paper.nowbasedoi}" style="font-size: larger;">${paper.title}</a>`;
                    
            htmlContent += `<div class="paper-title">${titleLine}</div>`;
                    
            // 如果有 specialNote，单独显示一行
            if (paper.specialNote) {
                htmlContent += `<div class="paper-meta"><b>（${paper.specialNote}）</b></div>`;
            }
                    
            // 显示 DOI
            if (paper.nowbasedoi) {
                let doiHtml = `<div class="paper-doi"><b>Nowbase DOI:</b> <a href="nowbase.html?doi=${paper.nowbasedoi}">${paper.nowbasedoi}</a> <span class="open-access-badge" style="font-style: normal;">🔒Open Access</span>`;
                if (paper.bestpaperaward === true) {
                    doiHtml += ' <span class="best-paper-badge">🏆 Best Paper Award</span>';
                }
                doiHtml += '</div>';
                htmlContent += doiHtml;
            }
                    
            // 处理关键词数组并创建链接
            let keywordsHtml = 'Keywords: ';
            if (Array.isArray(paper.keywords)) {
                if (paper.keywords.length > 0) {
                    keywordsHtml += paper.keywords.map(keyword => 
                        `<a href="releases.html?search=${encodeURIComponent(keyword)}" class="keyword-link">${keyword}</a>`
                    ).join(', ');
                } else {
                    // 空数组情况，只显示 'Keywords: '
                }
            } else {
                keywordsHtml += paper.keywords;
            }
                htmlContent += `<div class="paper-keywords">${keywordsHtml}</div>`;
                        
                htmlContent += `</div>`; // end paper-info-left
            
            // 右侧：摘要（限制显示长度）- 只在非侧边栏模式显示
            if (paper.abstract && !isSidebarMode) {
                const abstractText = paper.abstract;
                let displayAbstract = abstractText;
                
                // 判断是否主要是英文（英文字符占比超过 50%）
                const englishChars = (abstractText.match(/[a-zA-Z]/g) || []).length;
                const totalChars = abstractText.length;
                const isEnglish = englishChars / totalChars > 0.5;
                
                if (isEnglish) {
                    // 英文摘要：显示前 50 个单词
                    const words = abstractText.split(/\s+/);
                    if (words.length > 50) {
                        displayAbstract = words.slice(0, 50).join(' ') + '...';
                    }
                } else {
                    // 中文摘要：显示前 200 个字符
                    if (abstractText.length > 200) {
                        displayAbstract = abstractText.substring(0, 200) + '...';
                    }
                }
                
                htmlContent += `<div class="paper-abstract-right" id="${paperId}-abstract" style="flex: 1 1 38%; max-width: calc(38% - 20px); overflow-y: auto; max-height: 100vh; padding: 10px; background-color: #f9f9f9; border-left: 3px solid #ddd; font-size: 15px; line-height: 1.5;">`;
                htmlContent += `<b>摘要:</b> ${displayAbstract}`;
                htmlContent += `</div>`;
            }
                    
                htmlContent += `</div>`; // end paper-item
            });
        
        htmlContent += `</div>`; // end issue-content or issue-content-full
        htmlContent += `</div>`; // end paper-section
    }
    
    document.getElementById('papersContainer').innerHTML = htmlContent;
}

// 切换期号展开/收起状态
function toggleIssue(issueId) {
    const contentDiv = document.getElementById(issueId);
    const headerDiv = contentDiv.previousElementSibling;
    const expandIcon = headerDiv.querySelector('.expand-icon');
    
    if (contentDiv.style.display === 'none') {
        // 展开
        contentDiv.style.display = 'block';
        expandIcon.style.transform = 'rotate(90deg)';
        headerDiv.style.marginBottom = '0';
        
        // 记录展开状态
        const issue = issueId.replace('issue-', '').replace(/-/g, ' ');
        expandedIssues.add(issue);
    } else {
        // 收起
        contentDiv.style.display = 'none';
        expandIcon.style.transform = 'rotate(0deg)';
        headerDiv.style.marginBottom = '15px';
        
        // 移除展开状态
        const issue = issueId.replace('issue-', '').replace(/-/g, ' ');
        expandedIssues.delete(issue);
    }
}

// 搜索功能
function searchPapers(query) {
    // 搜索时清空展开状态
    if (!query.trim()) {
        expandedIssues.clear();
        currentCount = totalCount; // 重置为总数量
        updateResultCount();
        displayPapers(papersData);
        return;
    }
    
    const filteredPapers = papersData.filter(paper => {
        const searchTerms = query.toLowerCase();
        return (
            paper.title.toLowerCase().includes(searchTerms) ||
            (paper.authors && Array.isArray(paper.authors) ? (paper.authors.length > 0 ? paper.authors.some(author => typeof author === 'string' && author.toLowerCase().includes(searchTerms)) : false) : paper.authors && typeof paper.authors === 'string' && paper.authors.toLowerCase().includes(searchTerms)) ||
            (paper.keywords && Array.isArray(paper.keywords) ? (paper.keywords.length > 0 ? paper.keywords.some(keyword => typeof keyword === 'string' && keyword.toLowerCase().includes(searchTerms)) : false) : paper.keywords && typeof paper.keywords === 'string' && paper.keywords.toLowerCase().includes(searchTerms)) ||
            (paper.level && paper.level.toLowerCase().includes(searchTerms)) ||
            (paper.specialNote && paper.specialNote.toLowerCase().includes(searchTerms)) ||
            paper.issue.toLowerCase().includes(searchTerms) ||
            (paper.abstract && paper.abstract.toLowerCase().includes(searchTerms)) ||  // 搜索摘要
            (paper.nowbasedoi && paper.nowbasedoi.toLowerCase().includes(searchTerms))  // 搜索DOI
        );
    });
    
    currentCount = filteredPapers.length; // 更新当前显示数量
    updateResultCount();
    displayPapers(filteredPapers);
}

// 更新结果计数显示
function updateResultCount() {
    const resultCountElement = document.getElementById('resultCount');
    if (resultCountElement) {
        resultCountElement.textContent = `(${currentCount}/${totalCount})`;
    }
}

// 页面加载完成后加载数据
document.addEventListener('DOMContentLoaded', function() {
    // 应用极简模式
    utils.applySimpleMode();
    
    loadPapers();
    
    // 绑定搜索事件（只在存在搜索框时）
    const searchBox = document.getElementById('searchBox');
    if (searchBox) {
        searchBox.addEventListener('input', function() {
            searchPapers(this.value);
        });
    }
});
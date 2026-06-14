// 全局变量存储所有论文数据
let allPapersData = [];
let filteredPapersData = [];

// 获取URL参数中的DOI - 使用 utils.getUrlParameter
function getParameterByName(name) {
  return utils.getUrlParameter(name);
}

// 检测是否为极简模式（sty=no 参数）- 使用 utils.isSimpleMode

// 使用 utils.js 中的公共函数
// generateGBCitation, extractAuthors, getPublishedInfo, getCurrentDate, wrapEnglish 已移至 utils.js

// 从nowbase.json加载数据并查找论文
async function loadPaperByDOI(doi) {
  try {
    const response = await fetch('database/data/nowbase.json');
    const papers = await response.json();

    // 查找匹配的论文
    const paper = papers.find(p => p.nowbasedoi === doi);

    if (paper) {
      displayPaper(paper);
    } else {
      showNotFoundError();
    }
  } catch (error) {
    console.error('加载数据失败:', error);
    showNotFoundError();
  }
}

// 显示论文信息
function displayPaper(paper) {
  document.getElementById('doi').innerHTML = `<a href="nowbase.html?doi=${paper.nowbasedoi}">${paper.nowbasedoi}</a>`;
  document.getElementById('title').innerHTML = `${paper.title}`;
  
  // 处理作者字段，提取主要作者名并创建链接
  let authorsHtml = '作者: ';
  if (paper.authors) {  // 确俚authors存在
    if (Array.isArray(paper.authors)) {  // 只检查是否为数组
      // 如果authors是数组，每个作者都创建链接
      if (paper.authors.length > 0) {
        authorsHtml += paper.authors.map(author => 
          `<a href="nowbase.html?author=${encodeURIComponent(author || '')}" class="author-link">${author || ''}</a>`
        ).join(', ');
      } else {
        authorsHtml += 'N/A'; // 空数组情况
      }
    } else {
      // 如果authors是字符串，按原逻辑处理
      let mainAuthor = paper.authors;
      if (typeof paper.authors === 'string' && paper.authors.includes(' et al.')) {
        mainAuthor = paper.authors.split(' et al.')[0];
      } else if (typeof paper.authors === 'string' && paper.authors.includes(' et al')) {
        mainAuthor = paper.authors.split(' et al')[0];
      } else if (typeof paper.authors === 'string' && paper.authors.includes(', ')) {
        mainAuthor = paper.authors.split(',')[0];
      }
        
      authorsHtml += `<a href="nowbase.html?author=${encodeURIComponent(mainAuthor || '')}">${paper.authors}</a>`;
    }
  } else {
    authorsHtml += '未知作者'; // 如果没有作者信息
  }
  
  document.getElementById('authors').innerHTML = authorsHtml;
  
  if (paper.level) {
    document.getElementById('level').textContent = paper.level;
    document.getElementById('level').style.display = 'inline-block';
  } else {
    document.getElementById('level').style.display = 'none';
  }
  
  document.getElementById('issue').textContent = paper.issue;
  
  // 创建引用按钮容器
  const citationContainer = document.createElement('div');
  citationContainer.className = 'citation-container';
  
  // 创建圆形引用按钮
  const citeButton = document.createElement('button');
  citeButton.className = 'cite-button';
  citeButton.innerHTML = '&#8221;'; // 右引号字符
  citeButton.title = '引用该文章';
  
  // 创建引用框
  const citationBox = document.createElement('div');
  citationBox.className = 'citation-box';
  
  // 引用文本区域
  const citationText = document.createElement('div');
  citationText.className = 'citation-text';
  
  // 复制提示
  const copyHint = document.createElement('div');
  copyHint.className = 'copy-hint';
  copyHint.textContent = '✓ 已复制';
  
  citationBox.appendChild(citationText);
  citationBox.appendChild(copyHint);
  citationContainer.appendChild(citeButton);
  citationContainer.appendChild(citationBox);
  
  // 鼠标悬停显示引用框
  citeButton.addEventListener('mouseenter', function() {
    const citation = utils.generateGBCitation(paper);
    citationText.innerHTML = citation;
    citationBox.style.display = 'block';
  });
  
  // 鼠标移入引用框时保持显示
  citationBox.addEventListener('mouseenter', function() {
    citationBox.style.display = 'block';
  });
  
  // 鼠标离开按钮和引用框时隐藏
  citeButton.addEventListener('mouseleave', function() {
    citationBox.style.display = 'none';
    copyHint.style.display = 'none';
  });
  
  citationBox.addEventListener('mouseleave', function() {
    citationBox.style.display = 'none';
    copyHint.style.display = 'none';
  });
  
  // 点击复制功能
  citeButton.addEventListener('click', function(e) {
    e.stopPropagation();
    const citation = utils.generateGBCitation(paper, true);
    
    navigator.clipboard.writeText(citation).then(function() {
      copyHint.style.display = 'block';
      setTimeout(function() {
        copyHint.style.display = 'none';
      }, 2000);
    }).catch(function(err) {
      // 降级方案：使用传统的 execCommand 方法
      const textArea = document.createElement('textarea');
      textArea.value = citation;
      textArea.style.position = 'fixed';
      textArea.style.left = '-9999px';
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        copyHint.style.display = 'block';
        setTimeout(function() {
          copyHint.style.display = 'none';
        }, 2000);
      } catch (err) {
        console.error('复制失败:', err);
      }
      document.body.removeChild(textArea);
    });
  });
  
  // 将引用按钮添加到右侧容器
  const buttonContainer = document.getElementById('citationButtonContainer');
  if (buttonContainer) {
    buttonContainer.appendChild(citeButton);
    buttonContainer.appendChild(citationBox);
  }
  
  // 显示DOI相关信息
  let doiInfoHtml = '';
  if (paper.doc_category || paper.edition || paper.volume || paper.year) {
    let infoItems = [];
    
    // 文献分类码显示
    if (paper.doc_category) {
      let categoryText = '';
      switch(paper.doc_category) {
        case 'R': categoryText = '学术论文（Research Paper）'; break;
        case 'N': categoryText = '新闻社论（News Editorial）'; break;
        case 'D': categoryText = '数据集（Dataset）'; break;
        case 'S': categoryText = '源代码（Source Code）'; break;
        case 'M': categoryText = '多媒体作品（Multimedia）'; break;
        case 'L': categoryText = '前沿快讯（Latest News）'; break;
        case 'I': categoryText = '产业报告（Industry Report）'; break;
        default: categoryText = `${paper.doc_category}`;
      }
      infoItems.push(`文献分类：${categoryText}`);
    }
    
    // 版号显示
    if (paper.edition) {
      let editionText = '';
      switch(paper.edition) {
        case 'ET': editionText = '工程技术版'; break;
        case 'PS': editionText = '公共科学版'; break;
        case 'BS': editionText = '基础科学版'; break;
        case 'SS': editionText = '社会科学版'; break;
        case 'HS': editionText = '人文科学版'; break;
        case 'EDU': editionText = '教育科学版'; break;
        case 'HM': editionText = '健康医学版'; break;
        case 'YSA': editionText = '少年科学志'; break;
        case 'TM': editionText = '论文模板'; break;
        case 'WP': editionText = '白皮书'; break;
        case 'BP': editionText = '蓝皮书'; break;
        default: editionText = `${paper.edition}`;
      }
      infoItems.push(`版号：${editionText}`);
    }
    
    // 卷号显示
    if (paper.volume) {
      // 直接显示卷号数字
      infoItems.push(`卷号：${paper.volume}`);
    }
    
    // 年份显示
    if (paper.year) {
      infoItems.push(`年份：${paper.year}`);
    }
    
    // 将所有信息项用竖线分隔显示在同一行
    doiInfoHtml = infoItems.join(' | ');
    document.getElementById('doiInfo').innerHTML = doiInfoHtml;
  } else {
    document.getElementById('doiInfo').style.display = 'none';
  }
  // 处理关键词数组并创建链接
  if (Array.isArray(paper.keywords)) {
    if (paper.keywords.length > 0) {
      const keywordsHtml = paper.keywords.map(keyword => 
        `<a href="nowbase.html?keyword1=${encodeURIComponent(keyword)}" class="keyword-link">${keyword}</a>`
      ).join(', ');
      document.getElementById('keywords').innerHTML = '关键词: ' + keywordsHtml;
    } else {
      document.getElementById('keywords').textContent = '关键词: '; // 空数组情况
    }
  } else {
    document.getElementById('keywords').textContent = '关键词: ' + paper.keywords;
  }
  document.getElementById('abstract').textContent = paper.abstract;
  
  // 显示特殊注释（如果存在）
  if (paper.specialNote) {
    document.getElementById('specialNote').textContent = paper.specialNote;
    document.getElementById('specialNote').style.display = 'block';
  } else {
    document.getElementById('specialNote').style.display = 'none';
  }
    
  // 设置 PDF 下载链接
  if (paper.filePath) {
    const downloadBtn = document.getElementById('downloadPdfBtn');
    downloadBtn.href = paper.filePath;
    downloadBtn.style.display = 'inline-block';
    
    // 如果存在size信息，更新按钮文本显示文件大小
    if (paper.size && Array.isArray(paper.size) && paper.size.length >= 1) {
      const fileSize = paper.size[0];
      const sizeText = formatFileSize(fileSize);
      downloadBtn.textContent = `📄 下载PDF（${sizeText}）`;
    }
    
    // 构建标签HTML
    let badgesHtml = ' <span class="open-access-badge" style="margin-left: 10px; font-style: normal;">🔒Open Access</span>';
    if (paper.bestpaperaward === true) {
      badgesHtml += ' <span class="best-paper-badge">🏆 Best Paper Award</span>';
    }
    
    // 在下载按钮后添加标识
    downloadBtn.insertAdjacentHTML('afterend', badgesHtml);
  }
  
  // 显示全文字数
  if (paper.size && Array.isArray(paper.size) && paper.size.length >= 2) {
    const wordCount = paper.size[1];
    const wordCountEl = document.getElementById('wordCount');
    if (wordCountEl) {
      wordCountEl.textContent = `${wordCount.toLocaleString()}字`;
      wordCountEl.style.display = 'inline-block';
    }
  } else {
    const wordCountEl = document.getElementById('wordCount');
    if (wordCountEl) {
      wordCountEl.style.display = 'none';
    }
  }
    
  // 处理 exfile 和 exfann 属性
  handleExfile(paper.exfile, paper.exfann);
  
  // 显示内容，隐藏加载提示和错误信息
  document.getElementById('loading').style.display = 'none';
  document.getElementById('error').style.display = 'none';
  document.getElementById('content').style.display = 'block';
  document.getElementById('listView').style.display = 'none'; // 隐藏数据库视图
}

// 显示 NowBase 服务介绍和数据库表格
function displayNowBaseIntroduction() {
  // 隐藏默认内容和错误信息
  document.getElementById('loading').style.display = 'none';
  document.getElementById('error').style.display = 'none';
  document.getElementById('content').style.display = 'none';
  
  // 显示数据库视图
  document.getElementById('listView').style.display = 'block';
  
  // 检查是否为极简模式
  if (utils.isSimpleMode()) {
    displaySimpleModeList();
  } else {
    // 设置 NowBase 服务介绍信息
    document.getElementById('introTitle').textContent = 'NowBase 论文检索服务';
    document.getElementById('introAuthors').textContent = '作者：EigenLife 机器视觉实验室';
    document.getElementById('introIssue').textContent = '期刊：电子游戏科学与技术';
    document.getElementById('introKeywords').textContent = '关键词：论文检索，DOI 服务，学术数据库，文档索引';
    document.getElementById('introAbstract').textContent = 'NowBase Document Indexing Service 是一个专业的学术论文检索与索引服务系统。该系统为《电子游戏科学与技术》期刊提供完整的论文管理、DOI 分配与检索功能。通过 NowBase，用户可以快速检索期刊中的论文，访问论文详细信息，以及获取 PDF 文档。系统支持通过 DOI 编号直接访问特定论文，并提供高级搜索功能，以满足学术研究和文献管理的需求。';
    
    // 加载所有论文并显示（搜索逻辑在loadAllPapers中处理）
    loadAllPapers();
  }
}

// 极简模式：显示所有论文的简化信息（无样式）
async function displaySimpleModeList() {
  try {
    const response = await fetch('database/data/nowbase.json');
    const papers = await response.json();
    
    // 生成纯文本格式的论文信息（用于复制）
    window.simpleModeTextContent = papers.map(paper => {
      let text = `Nowbase DOI: ${paper.nowbasedoi}\n`;
      text += `标题：${paper.title}\n`;
      
      // 作者
      if (Array.isArray(paper.authors) && paper.authors.length > 0) {
        text += `作者：${paper.authors.join(', ')}\n`;
      } else if (paper.authors) {
        text += `作者：${paper.authors}\n`;
      } else {
        text += `作者：未知作者\n`;
      }
      
      // 声明
      if (paper.specialNote) {
        text += `声明：${paper.specialNote}\n`;
      }
      
      // 关键词
      if (Array.isArray(paper.keywords) && paper.keywords.length > 0) {
        text += `关键词：${paper.keywords.join(', ')}\n`;
      }
      
      // 摘要
      if (paper.abstract) {
        text += `摘要：${paper.abstract}\n`;
      }
      
      return text;
    }).join('\n---\n\n');
    
    // 构建纯 HTML（无任何样式和内联 CSS）
    let htmlContent = '';
    
    // 添加复制按钮（使用 HTML 基础属性）
    htmlContent += '<button onclick="copyAllPapers()">📋 一键复制所有论文信息</button>';
    htmlContent += '<span id="copyHint" style="display:none; color:green;">已复制到剪贴板！</span>';
    htmlContent += '<br><br>';
    
    papers.forEach(paper => {
      htmlContent += '<div>';
      htmlContent += `<strong>Nowbase DOI:</strong> <a href="nowbase.html?doi=${paper.nowbasedoi}">${paper.nowbasedoi}</a><br>`;
      htmlContent += `<strong>标题:</strong> ${paper.title}<br>`;
      
      // 作者链接
      htmlContent += '<strong>作者:</strong> ';
      if (Array.isArray(paper.authors) && paper.authors.length > 0) {
        paper.authors.forEach((author, index) => {
          if (index > 0) htmlContent += ', ';
          htmlContent += `<a href="releases.html?search=${encodeURIComponent(author)}">${author}</a>`;
        });
      } else if (paper.authors) {
        htmlContent += `<a href="releases.html?search=${encodeURIComponent(paper.authors)}">${paper.authors}</a>`;
      } else {
        htmlContent += '未知作者';
      }
      htmlContent += '<br>';
      
      // 声明
      if (paper.specialNote) {
        htmlContent += `<strong>声明:</strong> ${paper.specialNote}<br>`;
      }
      
      // 关键词链接
      if (Array.isArray(paper.keywords) && paper.keywords.length > 0) {
        htmlContent += '<strong>关键词:</strong> ';
        paper.keywords.forEach((keyword, index) => {
          if (index > 0) htmlContent += ', ';
          htmlContent += `<a href="releases.html?search=${encodeURIComponent(keyword)}">${keyword}</a>`;
        });
        htmlContent += '<br>';
      }
      
      // 完整摘要
      if (paper.abstract) {
        htmlContent += `<strong>摘要:</strong> ${paper.abstract}<br>`;
      }
      
      htmlContent += '</div><hr>';
    });
    
    document.getElementById('papersContainer').innerHTML = htmlContent;
    document.getElementById('pagination').style.display = 'none'; // 极简模式不分页
    
    // 定义全局复制函数
    window.copyAllPapers = function() {
      const copyHint = document.getElementById('copyHint');
      
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(window.simpleModeTextContent).then(() => {
          copyHint.style.display = 'inline';
          setTimeout(() => {
            copyHint.style.display = 'none';
          }, 2000);
        });
      } else {
        const textArea = document.createElement('textarea');
        textArea.value = window.simpleModeTextContent;
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        document.body.appendChild(textArea);
        textArea.select();
        try {
          document.execCommand('copy');
          copyHint.style.display = 'inline';
          setTimeout(() => {
            copyHint.style.display = 'none';
          }, 2000);
        } catch (err) {
          console.error('复制失败:', err);
        }
        document.body.removeChild(textArea);
      }
    };
    
  } catch (error) {
    console.error('极简模式加载失败:', error);
    document.getElementById('papersContainer').innerHTML = '加载失败';
  }
}

// 加载所有论文
async function loadAllPapers() {
  try {
    const response = await fetch('database/data/nowbase.json');
    const papers = await response.json();
    
    // 存储到全局变量
    allPapersData = papers;
    filteredPapersData = papers;
    
    displayPapersTable(papers);
    
    // 数据加载完成后，检查是否有搜索参数需要执行
    checkAndExecuteSearchFromURL();
  } catch (error) {
    console.error('加载所有论文失败:', error);
    document.getElementById('loading').style.display = 'none';
    document.getElementById('error').style.display = 'block';
    document.getElementById('error').textContent = '加载数据库失败';
    document.getElementById('listView').style.display = 'none';
  }
}

// 显示数据库表格
function displayPapersTable(papers) {
  // 分页设置
  const papersPerPage = 8;
  let currentPage = 1;
  const totalPages = Math.ceil(papers.length / papersPerPage);
  
  // 如果没有数据，显示提示
  if (papers.length === 0) {
    document.getElementById('papersContainer').innerHTML = '<div style="text-align: center; padding: 40px; color: #666;">未找到匹配的论文</div>';
    document.getElementById('pagination').style.display = 'none';
    return;
  }
  
  // 渲染当前页的数据库表格
  function renderPage(page) {
    const startIndex = (page - 1) * papersPerPage;
    const endIndex = Math.min(startIndex + papersPerPage, papers.length);
    const papersToShow = papers.slice(startIndex, endIndex);
    
    // 先渲染分页控件到顶部
    let paginationHtml = '';
    if (totalPages > 1) {
      paginationHtml += '<div class="pagination">';
      // 上一页按钮 - 始终显示
      if (currentPage > 1) {
        paginationHtml += `<button onclick="changePage(${currentPage - 1})" class="pagination-btn">上一页</button>`;
      } else {
        paginationHtml += `<button class="pagination-btn" disabled style="opacity: 0.5; cursor: not-allowed;">上一页</button>`;
      }
      
      // 页码按钮
      for (let i = 1; i <= totalPages; i++) {
        if (i === currentPage) {
          paginationHtml += `<button class="pagination-btn active">${i}</button>`;
        } else {
          paginationHtml += `<button onclick="changePage(${i})" class="pagination-btn">${i}</button>`;
        }
      }
      
      // 下一页按钮 - 始终显示
      if (currentPage < totalPages) {
        paginationHtml += `<button onclick="changePage(${currentPage + 1})" class="pagination-btn">下一页</button>`;
      } else {
        paginationHtml += `<button class="pagination-btn" disabled style="opacity: 0.5; cursor: not-allowed;">下一页</button>`;
      }
      paginationHtml += '</div>';
    }
    
    // 构建表格HTML
    let tableHtml = paginationHtml;
    tableHtml += '<table class="papers-table">';
    tableHtml += '<thead><tr><th>DOI</th><th>论文题目</th><th>作者</th><th>引用</th><th>PDF</th></tr></thead>';
    tableHtml += '<tbody>';
    
    papersToShow.forEach(paper => {
      // 处理作者字段 - 只显示第一个作者 + et al.
      let authorsHtml = '';
      if (paper.authors) {
        if (Array.isArray(paper.authors) && paper.authors.length > 0) {
          const firstAuthor = paper.authors[0];
          authorsHtml = `<a href="releases.html?search=${encodeURIComponent(firstAuthor)}" class="author-link" style="color: #000000;">${firstAuthor}</a>`;
          if (paper.authors.length > 1) {
            authorsHtml += ' et al.';
          }
        } else if (typeof paper.authors === 'string') {
          let mainAuthor = paper.authors;
          if (paper.authors.includes(' et al.')) {
            mainAuthor = paper.authors.split(' et al.')[0];
          } else if (paper.authors.includes(' et al')) {
            mainAuthor = paper.authors.split(' et al')[0];
          } else if (paper.authors.includes(', ')) {
            mainAuthor = paper.authors.split(',')[0];
          }
          
          authorsHtml = `<a href="releases.html?search=${encodeURIComponent(mainAuthor)}" style="color: #000000;">${mainAuthor}</a>`;
          // 如果原字符串包含多个作者，添加 et al.
          if (paper.authors.includes(',') || paper.authors.includes(' et al')) {
            authorsHtml += ' et al.';
          }
        }
      } else {
        authorsHtml = '未知作者';
      }
      
      // 处理标题 - 中文最多30个字符，英文最多80个字符
      let displayTitle = paper.title;
      const isEnglish = /[a-zA-Z]/.test(paper.title) && paper.title.replace(/[a-zA-Z]/g, '').length / paper.title.length < 0.5;
      
      if (isEnglish) {
        // 英文标题：最多80个字符，在单词边界截断
        if (paper.title.length > 80) {
          // 找到第80个字符附近的最后一个空格
          let truncatePos = 80;
          const lastSpace = paper.title.lastIndexOf(' ', truncatePos);
          if (lastSpace > 60) { // 如果找到一个合理的截断点（至少60字符后）
            truncatePos = lastSpace;
          }
          displayTitle = paper.title.substring(0, truncatePos) + '...';
        }
      } else {
        // 中文标题：最多30个字符
        if (paper.title.length > 30) {
          displayTitle = paper.title.substring(0, 30) + '...';
        }
      }
      
      tableHtml += `<tr>
        <td><a href="nowbase.html?doi=${paper.nowbasedoi}" style="color: #ff8c00; font-weight: bold;">${paper.nowbasedoi}</a></td>
        <td><a href="nowbase.html?doi=${paper.nowbasedoi}" style="color: #003d82;">${displayTitle}</a>`;
      
      // 添加 Open Access 标签
      tableHtml += ' <span class="open-access-badge">🔒OA</span>';
      
      // 添加最佳论文奖标签
      if (paper.bestpaperaward === true) {
        tableHtml += ' <span class="best-paper-badge">BP</span>';
      }
      
      tableHtml += `</td>
        <td>${authorsHtml}</td>
        <td><button class="cite-button" data-doi="${paper.nowbasedoi}" title="引用该文章">&#8221;</button></td>
        <td>`;
      
      if (paper.filePath) {
        tableHtml += `<a href="${paper.filePath}" download target="_blank" style="color: #006400; text-decoration: none; font-weight: bold;">下载</a>`;
      } else {
        tableHtml += '<span style="color: #ff0000;">N/A</span>';
      }
      
      tableHtml += `</td>
      </tr>`;
    });
    
    tableHtml += '</tbody></table>';
    
    document.getElementById('papersContainer').innerHTML = tableHtml;
    
    // 为所有引用按钮添加事件监听
    setTimeout(() => {
      const citeButtons = document.querySelectorAll('.cite-button[data-doi]');
      citeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
          e.stopPropagation();
          e.preventDefault();
          const doi = this.getAttribute('data-doi');
          const paper = papers.find(p => p.nowbasedoi === doi);
          if (paper) {
            const citation = utils.generateGBCitation(paper, true);
            
            // 尝试复制
            const copySuccess = () => {
              // 显示成功提示
              const originalHTML = button.innerHTML;
              const originalColor = button.style.color;
              button.innerHTML = '✓';
              button.style.color = '#28a745';
              button.style.backgroundColor = '#d4edda';
              
              // 创建浮动提示
              const toast = document.createElement('div');
              toast.textContent = '已复制到剪贴板';
              toast.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #28a745; color: white; padding: 10px 20px; border-radius: 4px; z-index: 10000; font-size: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.2);';
              document.body.appendChild(toast);
              
              setTimeout(() => {
                button.innerHTML = originalHTML;
                button.style.color = originalColor;
                button.style.backgroundColor = '';
                document.body.removeChild(toast);
              }, 800);
            };
            
            // 使用 Clipboard API
            if (navigator.clipboard && navigator.clipboard.writeText) {
              navigator.clipboard.writeText(citation).then(copySuccess).catch(err => {
                console.error('复制失败:', err);
                fallbackCopy(citation, copySuccess);
              });
            } else {
              fallbackCopy(citation, copySuccess);
            }
          }
        });
      });
    }, 100);
  }
  
  // 降级复制方案
  function fallbackCopy(text, callback) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      callback();
    } catch (err) {
      console.error('复制失败:', err);
      alert('复制失败，请手动复制');
    }
    document.body.removeChild(textArea);
  }
  
  // 改变页面的函数
  window.changePage = function(page) {
    if (page < 1 || page > totalPages || page === currentPage) {
      return;
    }
    
    currentPage = page;
    renderPage(currentPage);
  };
  
  // 初始渲染第一页
  renderPage(currentPage);
}

// 处理 exfile 和 exfann 属性
function handleExfile(exfileUrl, exfannText) {
  const exfileContainer = document.getElementById('exfileContainer');
  const exfileDeclaration = document.getElementById('exfileDeclaration');
  const exfileTitle = document.getElementById('exfileTitle');
  const exfannElement = document.getElementById('exfann');
  
  // 隐藏 exfile 相关元素
  exfileContainer.style.display = 'none';
  exfileDeclaration.style.display = 'none';
  exfileTitle.style.display = 'none';
  exfannElement.style.display = 'none';
  
  if (!exfileUrl) return;
  
  // 显示附件标题
  exfileTitle.style.display = 'block';
  
  // 显示作者说明（如果存在）
  if (exfannText) {
    exfannElement.textContent = exfannText;
    exfannElement.style.display = 'block';
  }
  
  // 显示声明
  exfileDeclaration.style.display = 'block';
  
  let mediaHtml = '';
  
  // 检查是否为网易云音乐外链格式 (netease_<数字>)
  const neteaseMatch = exfileUrl.match(/^netease_(\d+)$/);
  if (neteaseMatch) {
    const musicId = neteaseMatch[1];
    mediaHtml = `
      <iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width="298" height="52" src="//music.163.com/outchain/player?type=2&id=${musicId}&auto=1&height=32"></iframe>
    `;
  } else {
    // 获取文件扩展名
    const fileExtension = getFileExtension(exfileUrl).toLowerCase();
    
    // 根据文件类型处理
    if (fileExtension === 'mp3') {
      // 音频文件
      mediaHtml = `
        <audio controls style="width: 100%; max-width: 500px;">
          <source src="${exfileUrl}" type="audio/mpeg">
          您的浏览器不支持音频播放。
        </audio>
      `;
    } else if (fileExtension === 'mp4') {
      // 视频文件
      mediaHtml = `
        <video controls style="width: 100%; max-width: 800px; height: auto;">
          <source src="${exfileUrl}" type="video/mp4">
          您的浏览器不支持视频播放。
        </video>
      `;
    } else if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(fileExtension)) {
      // 图片文件
      mediaHtml = `
        <img src="${exfileUrl}" alt="附加文件" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
      `;
    } else {
      // 其他文件类型 - 提供下载按钮
      const fileName = getFileNameFromUrl(exfileUrl);
      mediaHtml = `
        <a href="${exfileUrl}" download class="cta-button" style="display: inline-block; margin-top: 10px;">
          ${fileName}
        </a>
      `;
    }
  }
  
  exfileContainer.innerHTML = mediaHtml;
  exfileContainer.style.display = 'block';
}

// 获取文件扩展名
function getFileExtension(url) {
  const fileName = url.split('/').pop();
  const lastDotIndex = fileName.lastIndexOf('.');
  return lastDotIndex !== -1 ? fileName.substring(lastDotIndex + 1) : '';
}

// 从 URL 中获取友好的文件名
function getFileNameFromUrl(url) {
  // 先获取最后一段路径
  let fileName = url.split('/').pop() || '下载文件';
  
  // 如果文件名包含 URL 编码，尝试解码
  if (fileName.includes('%')) {
    try {
      fileName = decodeURIComponent(fileName);
    } catch (e) {
      // 解码失败则保持原样
    }
  }
  
  // 如果文件名过长（超过 50 字符），截取并添加省略号
  if (fileName.length > 50) {
    // 优先保留扩展名
    const dotIndex = fileName.lastIndexOf('.');
    if (dotIndex !== -1 && dotIndex < 50) {
      const extension = fileName.substring(dotIndex);
      const namePart = fileName.substring(0, 50 - extension.length - 3);
      fileName = namePart + '...' + extension;
    } else {
      fileName = fileName.substring(0, 50) + '...';
    }
  }
  
  return fileName;
}

/**
 * 格式化文件大小，自适应显示 B/KB/MB
 */
function formatFileSize(bytes) {
  if (bytes < 1024) {
    return `${bytes} B`;
  } else if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  } else {
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }
}

// 显示未找到错误
function showNotFoundError() {
  document.getElementById('loading').style.display = 'none';
  document.getElementById('error').style.display = 'block';
  document.getElementById('content').style.display = 'none';
  document.getElementById('listView').style.display = 'none';
}

// ========== 搜索功能 ==========

// 切换搜索模式
function toggleSearchMode() {
  const mode = document.getElementById('searchMode').value;
  const simpleSearch = document.getElementById('simpleSearch');
  const advancedSearch = document.getElementById('advancedSearch');
  
  if (mode === 'simple') {
    simpleSearch.style.display = 'flex';
    advancedSearch.style.display = 'none';
  } else {
    simpleSearch.style.display = 'none';
    advancedSearch.style.display = 'flex';
  }
}

// 普通检索 - 按回车键触发
function handleSimpleSearch(event) {
  if (event.key === 'Enter') {
    performSimpleSearch();
  }
}

// 高级检索 - 按回车键触发
function handleAdvancedSearchEnter(event) {
  if (event.key === 'Enter') {
    performAdvancedSearch();
  }
}

// 执行普通检索
function performSimpleSearch() {
  const searchTerm = document.getElementById('simpleSearchInput').value.trim();
  
  if (!searchTerm) {
    // 如果搜索词为空，显示所有论文
    filteredPapersData = allPapersData;
    displayPapersTable(filteredPapersData);
    // 清除URL参数
    window.history.pushState({}, '', 'nowbase.html');
  } else {
    // 按标题模糊匹配
    const searchLower = searchTerm.toLowerCase();
    filteredPapersData = allPapersData.filter(paper => {
      const title = paper.title ? paper.title.toLowerCase() : '';
      return title.includes(searchLower);
    });
    displayPapersTable(filteredPapersData);
    
    // 更新URL而不刷新页面
    window.history.pushState({}, '', 'nowbase.html?search=' + encodeURIComponent(searchTerm));
  }
}

// 清除普通检索
function clearSearch() {
  document.getElementById('simpleSearchInput').value = '';
  filteredPapersData = allPapersData;
  displayPapersTable(filteredPapersData);
  // 清除URL参数
  window.history.pushState({}, '', 'nowbase.html');
}

// 执行高级检索
function performAdvancedSearch() {
  const authorInput = document.getElementById('advAuthorInput').value.trim();
  const title = document.getElementById('advTitleInput').value.trim();
  const keywordInput = document.getElementById('advKeywordInput').value.trim();
  const abstract = document.getElementById('advAbstractInput').value.trim();
  
  // 解析关键词，支持中英文分号分隔
  let keywords = [];
  if (keywordInput) {
    keywords = keywordInput.split(/[;；]/).map(k => k.trim()).filter(k => k);
  }
  
  // 构建URL参数
  const params = new URLSearchParams();
  
  if (authorInput) params.append('author', authorInput);
  if (title) params.append('title', title);
  if (keywords.length > 0) params.append('keywords', keywordInput);
  if (abstract) params.append('abstract', abstract);
  
  // 如果没有任何参数，显示所有论文
  if (params.toString() === '') {
    filteredPapersData = allPapersData;
    displayPapersTable(filteredPapersData);
    window.history.pushState({}, '', 'nowbase.html');
  } else {
    // 执行搜索逻辑
    executeAdvancedSearchFromParams(authorInput, title, keywords, abstract);
    
    // 更新URL而不刷新页面
    window.history.pushState({}, '', 'nowbase.html?' + params.toString());
  }
}

// 清除高级检索
function clearAdvancedSearch() {
  document.getElementById('advAuthorInput').value = '';
  document.getElementById('advTitleInput').value = '';
  document.getElementById('advKeywordInput').value = '';
  document.getElementById('advAbstractInput').value = '';
  filteredPapersData = allPapersData;
  displayPapersTable(filteredPapersData);
  // 清除URL参数
  window.history.pushState({}, '', 'nowbase.html');
}

// 检查URL参数并执行搜索（在数据加载完成后调用）
function checkAndExecuteSearchFromURL() {
  const simpleSearch = getParameterByName('search');
  const advAuthor = getParameterByName('author');
  const advTitle = getParameterByName('title');
  const advAbstract = getParameterByName('abstract');
  
  // 获取关键词参数（支持keywords，用分号分隔）
  let advKeywords = [];
  const keywordsParam = getParameterByName('keywords');
  if (keywordsParam) {
    advKeywords = keywordsParam.split(/[;；]/).map(k => k.trim()).filter(k => k);
  }
  
  // 如果有搜索参数，自动填充并执行搜索
  if (simpleSearch || advAuthor || advTitle || advKeywords.length > 0 || advAbstract) {
    // 设置搜索模式
    if (advAuthor || advTitle || advKeywords.length > 0 || advAbstract) {
      document.getElementById('searchMode').value = 'advanced';
      toggleSearchMode();
      
      // 填充高级检索表单
      if (advAuthor) document.getElementById('advAuthorInput').value = advAuthor;
      if (advTitle) document.getElementById('advTitleInput').value = advTitle;
      if (advAbstract) document.getElementById('advAbstractInput').value = advAbstract;
      if (keywordsParam) document.getElementById('advKeywordInput').value = keywordsParam;
      
      // 直接执行搜索逻辑
      executeAdvancedSearchFromParams(advAuthor, advTitle, advKeywords, advAbstract);
    } else if (simpleSearch) {
      document.getElementById('searchMode').value = 'simple';
      toggleSearchMode();
      document.getElementById('simpleSearchInput').value = simpleSearch;
      
      // 直接执行搜索逻辑
      executeSimpleSearchFromParams(simpleSearch);
    }
  }
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
  const doi = getParameterByName('doi');
  
  if (doi) {
    loadPaperByDOI(doi);
  } else {
    // 没有DOI参数时，显示NowBase服务介绍和数据库表格
    displayNowBaseIntroduction();
  }
});

// 从URL参数执行普通检索（不跳转）
function executeSimpleSearchFromParams(searchTerm) {
  if (!searchTerm) {
    filteredPapersData = allPapersData;
  } else {
    const searchLower = searchTerm.toLowerCase();
    filteredPapersData = allPapersData.filter(paper => {
      const title = paper.title ? paper.title.toLowerCase() : '';
      return title.includes(searchLower);
    });
  }
  displayPapersTable(filteredPapersData);
}

// 从URL参数执行高级检索（不跳转）
function executeAdvancedSearchFromParams(authorInput, title, keywords, abstract) {
  // 解析作者输入，支持中英文分号和逗号分隔
  let authors = [];
  if (authorInput) {
    authors = authorInput.split(/[,;，；]/).map(a => a.trim()).filter(a => a);
  }
  
  // 转换为小写
  const titleLower = title ? title.toLowerCase() : '';
  const abstractLower = abstract ? abstract.toLowerCase() : '';
  const keywordsLower = keywords.map(k => k.toLowerCase());
  
  // 如果所有条件都为空，显示所有论文
  if (authors.length === 0 && !titleLower && keywordsLower.length === 0 && !abstractLower) {
    filteredPapersData = allPapersData;
  } else {
    // 多条件过滤
    filteredPapersData = allPapersData.filter(paper => {
      // 作者匹配（任意一个作者匹配即可）
      let authorMatch = true;
      if (authors.length > 0) {
        authorMatch = authors.some(searchAuthor => {
          const searchAuthorLower = searchAuthor.toLowerCase();
          if (Array.isArray(paper.authors)) {
            return paper.authors.some(a => a.toLowerCase().includes(searchAuthorLower));
          } else if (paper.authors) {
            return paper.authors.toLowerCase().includes(searchAuthorLower);
          }
          return false;
        });
      }
      
      // 标题匹配
      let titleMatch = true;
      if (titleLower) {
        const paperTitle = paper.title ? paper.title.toLowerCase() : '';
        titleMatch = paperTitle.includes(titleLower);
      }
      
      // 关键词匹配（所有输入的关键词都必须匹配）
      let keywordMatch = true;
      if (keywordsLower.length > 0) {
        if (Array.isArray(paper.keywords)) {
          keywordMatch = keywordsLower.every(inputKeyword => 
            paper.keywords.some(paperKeyword => paperKeyword.toLowerCase().includes(inputKeyword))
          );
        } else if (paper.keywords) {
          const paperKeywordsStr = paper.keywords.toLowerCase();
          keywordMatch = keywordsLower.every(inputKeyword => paperKeywordsStr.includes(inputKeyword));
        } else {
          keywordMatch = false;
        }
      }
      
      // 摘要匹配
      let abstractMatch = true;
      if (abstractLower) {
        const paperAbstract = paper.abstract ? paper.abstract.toLowerCase() : '';
        abstractMatch = paperAbstract.includes(abstractLower);
      }
      
      return authorMatch && titleMatch && keywordMatch && abstractMatch;
    });
  }
  
  displayPapersTable(filteredPapersData);
}

// NowGraph 作者知识图谱系统
// 主应用程序逻辑

class NowGraph {
    constructor() {
        // 系统配置
        this.config = {
            itemsPerPage: 50,
            maxAuthorsToShow: 1000,
            collaborationThreshold: 1,
            showLabels: true,
            showEditors: true,
            showCommittees: true,
            sortBy: 'name'
        };

        // 数据存储
        this.papers = [];
        this.authors = new Map(); // name -> author object
        this.filteredAuthors = [];
        this.currentAuthor = null;
        this.currentPage = 1;

        // ECharts实例
        this.chart = null;

        // 初始化
        this.init();
    }

    // 初始化应用
    async init() {
        console.log('NowGraph 系统初始化...');

        // 显示加载界面
        this.showLoading();

        try {
            // 1. 加载数据
            await this.loadData();

            // 2. 初始化UI组件
            this.initUI();

            // 3. 初始化图表
            this.initChart();

            // 4. 绑定事件
            this.bindEvents();

            // 5. 渲染初始视图
            this.renderAuthorList();
            this.updateStats();
            this.updateGraph();

            // 隐藏加载界面
            this.hideLoading();

            console.log('NowGraph 初始化完成！');
            console.log(`加载了 ${this.papers.length} 篇论文，${this.authors.size} 位作者`);

        } catch (error) {
            console.error('初始化失败:', error);
            this.hideLoading();
            alert('数据加载失败，请检查 nowbase.json 文件是否存在且格式正确。');
        }
    }

    // 加载JSON数据
    async loadData() {
        try {
            const response = await fetch('data/nowbase.json');
            if (!response.ok) {
                throw new Error(`HTTP错误: ${response.status}`);
            }

            const rawData = await response.json();

            // 确保数据是数组格式
            if (!Array.isArray(rawData)) {
                throw new Error('数据格式错误：应该是数组');
            }

            this.papers = rawData;

            // 处理进度更新
            const totalPapers = this.papers.length;
            let processed = 0;

            // 构建作者数据库
            this.authors.clear();

            for (const paper of this.papers) {
                // 更新进度
                processed++;
                const progress = (processed / totalPapers) * 100;
                document.getElementById('progressFill').style.width = `${progress}%`;

                // 处理每篇论文的作者
                if (paper.authors && Array.isArray(paper.authors)) {
                    for (const authorName of paper.authors) {
                        if (!authorName || authorName.trim() === '') continue;

                        const normalizedName = authorName.trim();

                        if (!this.authors.has(normalizedName)) {
                            // 新作者
                            this.authors.set(normalizedName, {
                                id: normalizedName,
                                name: normalizedName,
                                papers: [],
                                coAuthors: new Map(),
                                keywords: new Set(),
                                totalPapers: 0,
                                isEditor: normalizedName.includes('编辑') ||
                                         normalizedName.includes('Editor') ||
                                         normalizedName.includes('委员会') ||
                                         normalizedName.includes('Committee')||
                                         normalizedName.includes('copycat666') ||
                                         normalizedName.includes('doro') ||
                                         normalizedName.includes('mysteriousK'),
                                isCommittee: normalizedName.includes('委员会') ||
                                            normalizedName.includes('审查组') ||
                                            normalizedName.includes('伦理') ||
                                            normalizedName.includes('诚信')||
                                            normalizedName.includes('Char1es')||
                                            normalizedName.includes('Gina')
                            });
                        }

                        const author = this.authors.get(normalizedName);

                        // 添加论文引用
                        const paperRef = {
                            id: paper.id || paper.nowbasedoi || `paper_${processed}`,
                            title: paper.title || '无标题',
                            doi: paper.nowbasedoi,
                            keywords: paper.keywords || [],
                            abstract: paper.abstract || '',
                            year: paper.year || (paper.issue ? paper.issue.match(/\d{4}/)?.[0] : null)
                        };

                        author.papers.push(paperRef);
                        author.totalPapers = author.papers.length;

                        // 收集关键词
                        if (paper.keywords) {
                            paper.keywords.forEach(kw => author.keywords.add(kw));
                        }
                    }

                    // 构建合作者关系
                    const authorsInPaper = paper.authors.map(name => name.trim()).filter(name => name);

                    for (let i = 0; i < authorsInPaper.length; i++) {
                        for (let j = i + 1; j < authorsInPaper.length; j++) {
                            const authorA = authorsInPaper[i];
                            const authorB = authorsInPaper[j];

                            if (this.authors.has(authorA) && this.authors.has(authorB)) {
                                // 作者A的合作者记录
                                const coAuthorsA = this.authors.get(authorA).coAuthors;
                                coAuthorsA.set(authorB, (coAuthorsA.get(authorB) || 0) + 1);

                                // 作者B的合作者记录
                                const coAuthorsB = this.authors.get(authorB).coAuthors;
                                coAuthorsB.set(authorA, (coAuthorsB.get(authorA) || 0) + 1);
                            }
                        }
                    }
                }
            }

            console.log(`成功加载 ${this.authors.size} 位作者的数据`);

        } catch (error) {
            console.error('加载数据失败:', error);
            throw error;
        }
    }

    // 初始化UI组件
    initUI() {
        // 设置搜索输入框的初始值
        document.getElementById('searchInput').value = '';

        // 设置筛选器的初始状态
        document.getElementById('filterEditors').checked = this.config.showEditors;
        document.getElementById('filterCommittees').checked = this.config.showCommittees;

        const sortRadios = document.getElementsByName('sortBy');
        sortRadios.forEach(radio => {
            if (radio.value === this.config.sortBy) {
                radio.checked = true;
            }
        });
    }

    // 初始化ECharts图表
    initChart() {
        const chartDom = document.getElementById('knowledgeGraph');
        this.chart = echarts.init(chartDom);

        // 窗口大小变化时重绘
        window.addEventListener('resize', () => {
            if (this.chart) {
                this.chart.resize();
            }
        });

        // 绑定图表事件
        this.chart.on('click', params => {
            if (params.dataType === 'node') {
                this.selectAuthor(params.data.name);
            }
        });
    }

    // 绑定所有事件
    bindEvents() {
        // 搜索框事件
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {
            this.filterAuthors(e.target.value);
        });

        document.getElementById('clearSearch').addEventListener('click', () => {
            searchInput.value = '';
            this.filterAuthors('');
            searchInput.focus();
        });

        // 筛选器事件
        document.getElementById('filterEditors').addEventListener('change', (e) => {
            this.config.showEditors = e.target.checked;
            this.filterAuthors(searchInput.value);
        });

        document.getElementById('filterCommittees').addEventListener('change', (e) => {
            this.config.showCommittees = e.target.checked;
            this.filterAuthors(searchInput.value);
        });

        document.querySelectorAll('input[name="sortBy"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.config.sortBy = e.target.value;
                this.filterAuthors(searchInput.value);
            });
        });

        // 列表控制按钮
        document.getElementById('loadMore').addEventListener('click', () => {
            this.loadMoreAuthors();
        });

        document.getElementById('selectRandom').addEventListener('click', () => {
            this.selectRandomAuthor();
        });

        // 图谱控制按钮
        document.getElementById('resetView').addEventListener('click', () => {
            this.resetGraph();
        });

        document.getElementById('toggleLabels').addEventListener('click', () => {
            this.toggleLabels();
        });

        document.getElementById('exportGraph').addEventListener('click', () => {
            this.exportGraph();
        });

        document.getElementById('fullscreen').addEventListener('click', () => {
            this.toggleFullscreen();
        });

        document.getElementById('helpBtn').addEventListener('click', () => {
            this.showHelp();
        });

        // 详情面板关闭按钮
        document.getElementById('closeDetail').addEventListener('click', () => {
            this.closeDetail();
        });

        // 帮助模态框
        document.querySelector('.close-modal').addEventListener('click', () => {
            this.hideHelp();
        });

        document.getElementById('helpModal').addEventListener('click', (e) => {
            if (e.target.id === 'helpModal') {
                this.hideHelp();
            }
        });

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            // ESC键关闭详情或帮助
            if (e.key === 'Escape') {
                if (document.getElementById('helpModal').classList.contains('active')) {
                    this.hideHelp();
                } else if (this.currentAuthor) {
                    this.closeDetail();
                }
            }

            // Ctrl+F聚焦搜索框
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
        });
    }

    // 渲染作者列表
    renderAuthorList() {
        this.filterAuthors('');
    }

    // 筛选作者
    filterAuthors(searchTerm) {
        const searchLower = searchTerm.toLowerCase();

        // 获取所有作者并筛选
        let authorsArray = Array.from(this.authors.values());

        // 应用搜索筛选
        if (searchTerm) {
            authorsArray = authorsArray.filter(author => {
                // 中文名称匹配
                if (author.name.toLowerCase().includes(searchLower)) {
                    return true;
                }

                // 拼音匹配（简单实现）
                const pinyin = this.getPinyin(author.name);
                if (pinyin.toLowerCase().includes(searchLower)) {
                    return true;
                }

                // 关键词匹配
                for (const keyword of author.keywords) {
                    if (keyword.toLowerCase().includes(searchLower)) {
                        return true;
                    }
                }

                return false;
            });
        }

        // 应用类型筛选
        if (!this.config.showEditors) {
            authorsArray = authorsArray.filter(author => !author.isEditor);
        }

        if (!this.config.showCommittees) {
            authorsArray = authorsArray.filter(author => !author.isCommittee);
        }

        // 应用排序
        authorsArray.sort((a, b) => {
            if (this.config.sortBy === 'papers') {
                return b.totalPapers - a.totalPapers || a.name.localeCompare(b.name);
            } else {
                return a.name.localeCompare(b.name);
            }
        });

        this.filteredAuthors = authorsArray;
        this.currentPage = 1;

        this.updateAuthorListDisplay();
        this.updateStats();
    }

    // 更新作者列表显示
    updateAuthorListDisplay() {
        const container = document.getElementById('authorList');
        const startIndex = 0;
        const endIndex = Math.min(this.currentPage * this.config.itemsPerPage, this.filteredAuthors.length);
        const authorsToShow = this.filteredAuthors.slice(startIndex, endIndex);

        container.innerHTML = '';

        if (authorsToShow.length === 0) {
            container.innerHTML = `
                <div class="empty-list">
                    <i class="fas fa-search"></i>
                    <p>未找到匹配的作者</p>
                </div>
            `;
            return;
        }

        authorsToShow.forEach(author => {
            const isActive = this.currentAuthor && this.currentAuthor.name === author.name;
            const coAuthorCount = author.coAuthors.size;

            const badges = [];
            if (author.isEditor) badges.push('<span class="badge editor">编委</span>');
            if (author.isCommittee) badges.push('<span class="badge committee">委员会</span>');

            const item = document.createElement('div');
            item.className = `author-item ${isActive ? 'active' : ''}`;
            item.innerHTML = `
                <div class="author-header">
                    <div class="author-name">${author.name}</div>
                    <div class="author-badges">${badges.join('')}</div>
                </div>
                <div class="author-stats">
                    <div class="stat-papers">
                        <i class="fas fa-file-alt"></i>
                        <span>${author.totalPapers}篇</span>
                    </div>
                    <div class="stat-collabs">
                        <i class="fas fa-handshake"></i>
                        <span>${coAuthorCount}人</span>
                    </div>
                </div>
            `;

            item.addEventListener('click', () => {
                this.selectAuthor(author.name);
            });

            container.appendChild(item);
        });

        // 更新列表统计
        document.getElementById('visibleAuthors').textContent = endIndex;
        document.getElementById('allAuthors').textContent = this.filteredAuthors.length;

        // 显示/隐藏"加载更多"按钮
        const loadMoreBtn = document.getElementById('loadMore');
        if (endIndex < this.filteredAuthors.length) {
            loadMoreBtn.style.display = 'flex';
        } else {
            loadMoreBtn.style.display = 'none';
        }
    }

    // 加载更多作者
    loadMoreAuthors() {
        if (this.currentPage * this.config.itemsPerPage < this.filteredAuthors.length) {
            this.currentPage++;
            this.updateAuthorListDisplay();
        }
    }

    // 选择作者
    selectAuthor(authorName) {
        if (!this.authors.has(authorName)) return;

        const author = this.authors.get(authorName);
        this.currentAuthor = author;

        // 更新列表高亮
        document.querySelectorAll('.author-item').forEach(item => {
            item.classList.remove('active');
            if (item.querySelector('.author-name').textContent === authorName) {
                item.classList.add('active');
                // 滚动到可见区域
                item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });

        // 更新图谱
        this.updateGraph(authorName);

        // 更新详情面板
        this.showAuthorDetail(author);

        // 更新URL（支持分享）
        history.replaceState(null, '', `#${encodeURIComponent(authorName)}`);

        // 更新标题
        document.getElementById('graphTitle').textContent = `${authorName}的合作网络`;
    }

    // 随机选择作者
    selectRandomAuthor() {
        const authorsArray = Array.from(this.authors.values());
        if (authorsArray.length === 0) return;

        const randomIndex = Math.floor(Math.random() * authorsArray.length);
        const randomAuthor = authorsArray[randomIndex];

        this.selectAuthor(randomAuthor.name);
    }

    // 更新图谱
    updateGraph(focusAuthor = null) {
        if (!this.chart) return;

        // 获取要显示的作者
        let authorsToShow;
        if (focusAuthor && this.authors.has(focusAuthor)) {
            // 显示焦点作者及其合作网络
            const focusAuthorObj = this.authors.get(focusAuthor);
            const coAuthors = Array.from(focusAuthorObj.coAuthors.keys());
            authorsToShow = [focusAuthor, ...coAuthors];
        } else {
            // 显示所有作者（限制数量）
            const allAuthors = Array.from(this.authors.keys());
            authorsToShow = allAuthors.slice(0, this.config.maxAuthorsToShow);
        }

        // 构建节点数据
        const nodes = authorsToShow.map(authorName => {
            const author = this.authors.get(authorName);
            const isFocus = authorName === focusAuthor;
            const isCoAuthor = focusAuthor && author.coAuthors.has(focusAuthor);

            // 节点大小基于论文数量
            const baseSize = 20;
            const paperFactor = Math.min(author.totalPapers, 20);
            const size = baseSize + paperFactor * 1.5;

            // 节点颜色
            let color;
            if (isFocus) {
                color = '#ff4d4f'; // 红色：当前作者
            } else if (isCoAuthor) {
                color = '#1890ff'; // 蓝色：合作者
            } else {
                color = '#52c41a'; // 绿色：其他作者
            }

            return {
                id: authorName,
                name: authorName,
                symbolSize: size,
                value: author.totalPapers,
                category: isFocus ? 'focus' : (isCoAuthor ? 'coauthor' : 'normal'),
                itemStyle: {
                    color: color,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: this.config.showLabels,
                    position: 'right',
                    fontSize: 14,
                    fontWeight: isFocus ? 'bold' : 'normal',
                    color: isFocus ? '#ff4d4f' : '#333'
                },
                tooltip: {
                    formatter: this.getAuthorTooltip(author)
                }
            };
        });

        // 构建边数据（合作关系）
        const edges = [];
        const addedEdges = new Set();

        for (let i = 0; i < authorsToShow.length; i++) {
            for (let j = i + 1; j < authorsToShow.length; j++) {
                const authorA = authorsToShow[i];
                const authorB = authorsToShow[j];

                const authorObjA = this.authors.get(authorA);
                if (authorObjA && authorObjA.coAuthors.has(authorB)) {
                    const collaborationCount = authorObjA.coAuthors.get(authorB);

                    if (collaborationCount >= this.config.collaborationThreshold) {
                        const edgeKey = `${authorA}-${authorB}`;
                        const reverseKey = `${authorB}-${authorA}`;

                        if (!addedEdges.has(edgeKey) && !addedEdges.has(reverseKey)) {
                            // 根据合作次数确定连线粗细
                            let width = 2;
                            if (collaborationCount >= 4) width = 6;
                            else if (collaborationCount >= 2) width = 4;

                            edges.push({
                                source: authorA,
                                target: authorB,
                                value: collaborationCount,
                                lineStyle: {
                                    width: width,
                                    color: this.getEdgeColor(collaborationCount),
                                    curveness: 0.1,
                                    opacity: 0.8
                                },
                                label: {
                                    show: this.config.showLabels && collaborationCount > 1,
                                    formatter: `${collaborationCount}次`
                                }
                            });

                            addedEdges.add(edgeKey);
                        }
                    }
                }
            }
        }

        // 图表配置
        const option = {
            title: {
                text: focusAuthor ? `${focusAuthor}的合作网络` : 'JOEST作者合作网络',
                subtext: focusAuthor ?
                    `直接合作者: ${this.authors.get(focusAuthor).coAuthors.size}人 | 总论文: ${this.authors.get(focusAuthor).totalPapers}篇` :
                    `总作者: ${this.authors.size}人 | 总论文: ${this.papers.length}篇`,
                left: 'center',
                textStyle: {
                    fontSize: 18,
                    fontWeight: 'bold'
                },
                subtextStyle: {
                    fontSize: 13,
                    color: '#666'
                }
            },
            tooltip: {
                trigger: 'item',
                formatter: params => {
                    if (params.dataType === 'node') {
                        const author = this.authors.get(params.data.name);
                        return this.getAuthorTooltip(author);
                    } else if (params.dataType === 'edge') {
                        const authorA = this.authors.get(params.data.source);
                        const authorB = this.authors.get(params.data.target);
                        const count = params.data.value;

                        const commonPapers = this.getCommonPapers(params.data.source, params.data.target);
                        let papersHtml = '';
                        if (commonPapers.length > 0) {
                            papersHtml = '<div style="margin-top: 8px; border-top: 1px dashed #ddd; padding-top: 8px;">';
                            papersHtml += '<strong>合作论文:</strong><br>';
                            commonPapers.slice(0, 3).forEach(paper => {
                                papersHtml += `• ${paper.title}<br>`;
                            });
                            if (commonPapers.length > 3) {
                                papersHtml += `...等${commonPapers.length}篇`;
                            }
                            papersHtml += '</div>';
                        }

                        return `
                            <div style="padding: 12px; max-width: 350px;">
                                <div style="font-size: 16px; font-weight: bold; margin-bottom: 8px; color: #1890ff;">
                                    ${params.data.source} ↔ ${params.data.target}
                                </div>
                                <div style="margin-bottom: 6px;">
                                    <strong>合作次数:</strong> ${count}次
                                </div>
                                ${papersHtml}
                            </div>
                        `;
                    }
                }
            },
            legend: {
                show: false
            },
            animationDuration: 1000,
            animationEasingUpdate: 'quinticInOut',
            series: [{
                type: 'graph',
                layout: 'force',
                force: {
                    repulsion: 300,
                    edgeLength: focusAuthor ? 80 : 100,
                    gravity: 0.1
                },
                roam: true,
                draggable: true,
                focusNodeAdjacency: true,
                edgeSymbol: ['none', 'arrow'],
                edgeSymbolSize: [0, 10],
                categories: [
                    { name: 'focus', itemStyle: { color: '#ff4d4f' } },
                    { name: 'coauthor', itemStyle: { color: '#1890ff' } },
                    { name: 'normal', itemStyle: { color: '#52c41a' } }
                ],
                data: nodes,
                links: edges,
                lineStyle: {
                    opacity: 0.8,
                    curveness: 0.1
                },
                emphasis: {
                    focus: 'adjacency',
                    lineStyle: {
                        width: 4
                    }
                },
                label: {
                    show: this.config.showLabels,
                    position: 'right',
                    fontSize: 14
                }
            }]
        };

        this.chart.setOption(option, true);

        // 如果有焦点作者，将其置于中心
        if (focusAuthor) {
            setTimeout(() => {
                this.chart.dispatchAction({
                    type: 'focusNodeAdjacency',
                    seriesIndex: 0,
                    dataIndex: nodes.findIndex(node => node.id === focusAuthor)
                });
            }, 500);
        }
    }

    // 获取作者工具提示内容
    getAuthorTooltip(author) {
        const coAuthorCount = author.coAuthors.size;
        const topCoAuthors = Array.from(author.coAuthors.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3)
            .map(([name, count]) => `${name}(${count}次)`)
            .join('、');

        return `
            <div style="padding: 12px; max-width: 300px;">
                <div style="font-size: 16px; font-weight: bold; margin-bottom: 8px; color: #333;">
                    ${author.name}
                </div>
                <div style="margin-bottom: 6px;">
                    <strong>发表论文:</strong> ${author.totalPapers}篇
                </div>
                <div style="margin-bottom: 6px;">
                    <strong>合作者:</strong> ${coAuthorCount}人
                </div>
                ${topCoAuthors ? `
                    <div style="margin-bottom: 6px;">
                        <strong>主要合作者:</strong><br>
                        ${topCoAuthors}
                    </div>
                ` : ''}
                ${author.keywords.size > 0 ? `
                    <div style="margin-bottom: 6px;">
                        <strong>研究方向:</strong><br>
                        ${Array.from(author.keywords).slice(0, 5).join('、')}
                        ${author.keywords.size > 5 ? '...' : ''}
                    </div>
                ` : ''}
                <button onclick="nowGraph.selectAuthor('${author.name}')"
                        style="margin-top: 8px; padding: 6px 12px; background: #1890ff; color: white;
                               border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    查看详情
                </button>
            </div>
        `;
    }

    // 获取共同论文
    getCommonPapers(authorA, authorB) {
        const papersA = this.authors.get(authorA)?.papers || [];
        const papersB = this.authors.get(authorB)?.papers || [];

        // 简单实现：通过DOI或标题匹配
        const commonPapers = [];
        const paperIds = new Set(papersA.map(p => p.id));

        for (const paperB of papersB) {
            if (paperIds.has(paperB.id)) {
                commonPapers.push(paperB);
            }
        }

        return commonPapers;
    }

    // 获取边颜色
    getEdgeColor(collaborationCount) {
        if (collaborationCount >= 4) return '#096dd9';
        if (collaborationCount >= 2) return '#1890ff';
        return '#91d5ff';
    }

    // 显示作者详情
    showAuthorDetail(author) {
        const container = document.getElementById('authorDetail');
        const coAuthors = Array.from(author.coAuthors.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 30); // 限制显示数量

        // 统计合作强度
        let totalCollaborations = 0;
        let maxCollaborations = 0;
        coAuthors.forEach(([_, count]) => {
            totalCollaborations += count;
            if (count > maxCollaborations) maxCollaborations = count;
        });
        const avgCollaborations = coAuthors.length > 0 ? (totalCollaborations / coAuthors.length).toFixed(1) : 0;

        // 构建详情HTML
        let html = `
            <div class="author-detail-view">
                <div class="author-header-detail">
                    <div class="author-name-detail">${author.name}</div>
                    <div class="author-badges">
                        ${author.isEditor ? '<span class="badge editor">编委成员</span>' : ''}
                        ${author.isCommittee ? '<span class="badge committee">委员会成员</span>' : ''}
                    </div>
                </div>

                <div class="author-stats-detail">
                    <div class="stat-card">
                        <div class="value">${author.totalPapers}</div>
                        <div class="label">发表论文</div>
                    </div>
                    <div class="stat-card">
                        <div class="value">${coAuthors.length}</div>
                        <div class="label">合作者</div>
                    </div>
                    <div class="stat-card">
                        <div class="value">${totalCollaborations}</div>
                        <div class="label">总合作次数</div>
                    </div>
                    <div class="stat-card">
                        <div class="value">${avgCollaborations}</div>
                        <div class="label">平均合作强度</div>
                    </div>
                </div>

                <div class="detail-section">
                    <div class="detail-title">
                        <i class="fas fa-handshake"></i> 合作者网络
                    </div>
                    <div class="coauthor-grid">
        `;

        if (coAuthors.length === 0) {
            html += `<div class="empty-coauthors">暂无合作者记录</div>`;
        } else {
            coAuthors.forEach(([coAuthorName, count]) => {
                const strength = count / maxCollaborations; // 0到1之间
                const barWidth = 20 + (strength * 80); // 20到100px之间

                html += `
                    <div class="coauthor-item" onclick="nowGraph.selectAuthor('${coAuthorName}')">
                        <div class="coauthor-name">${coAuthorName}</div>
                        <div class="coauthor-count">合作${count}次</div>
                        <div style="margin-top: 4px; height: 4px; background: #e8e8e8; border-radius: 2px;">
                            <div style="width: ${barWidth}px; height: 100%; background: linear-gradient(90deg, #91d5ff, #1890ff); border-radius: 2px;"></div>
                        </div>
                    </div>
                `;
            });
        }

        html += `
                    </div>
                </div>

                <div class="detail-section">
                    <div class="detail-title">
                        <i class="fas fa-file-alt"></i> 发表论文 (${author.papers.length}篇)
                    </div>
                    <div class="paper-list">
        `;

        // 显示论文，按可能的时间排序（如果有年份信息）
        const sortedPapers = [...author.papers].sort((a, b) => {
            if (a.year && b.year) return b.year - a.year;
            return 0;
        }).slice(0, 10); // 最多显示10篇

        if (sortedPapers.length === 0) {
            html += `<div class="empty-papers">暂无论文信息</div>`;
        } else {
            sortedPapers.forEach(paper => {
                const doi = paper.doi || paper.nowbasedoi || '';
                html += `
                    <div class="paper-item" onclick="window.location.href='../nowbase.html?doi=${encodeURIComponent(doi)}'" style="cursor: pointer;">
                        <div class="paper-title">${paper.title || '无标题'}</div>
                        <div class="paper-meta">
                            ${doi ? `<span><i class="fas fa-fingerprint"></i> ${doi}</span>` : ''}
                            ${paper.year ? `<span><i class="fas fa-calendar"></i> ${paper.year}</span>` : ''}
                        </div>
                        ${paper.abstract ? `
                            <div class="paper-abstract">
                                ${paper.abstract.substring(0, 150)}${paper.abstract.length > 150 ? '...' : ''}
                            </div>
                        ` : ''}
                        ${paper.keywords && paper.keywords.length > 0 ? `
                            <div class="keywords">
                                ${paper.keywords.map(kw => `<span class="keyword-tag">${kw}</span>`).join('')}
                            </div>
                        ` : ''}
                    </div>
                `;
            });
        }

        if (author.papers.length > 10) {
            html += `<div style="text-align: center; margin-top: 10px; color: #666; font-size: 0.9em;">
                还有 ${author.papers.length - 10} 篇论文未显示...
            </div>`;
        }

        html += `
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;

        // 显示详情面板
        document.getElementById('detailContainer').style.display = 'flex';
    }

    // 关闭详情面板
    closeDetail() {
        this.currentAuthor = null;

        // 清除列表高亮
        document.querySelectorAll('.author-item').forEach(item => {
            item.classList.remove('active');
        });

        // 隐藏详情面板
        document.getElementById('detailContainer').style.display = 'none';

        // 恢复默认图谱视图
        this.updateGraph();
        document.getElementById('graphTitle').textContent = '作者合作网络图谱';

        // 清除URL中的hash
        history.replaceState(null, '', window.location.pathname);
    }

    // 更新统计信息
    updateStats() {
        document.getElementById('totalAuthors').textContent = this.authors.size;
        document.getElementById('totalPapers').textContent = this.papers.length;

        // 计算总合作次数
        let totalCollaborations = 0;
        this.authors.forEach(author => {
            author.coAuthors.forEach(count => {
                totalCollaborations += count;
            });
        });
        // 每次合作被计算两次（A->B和B->A），所以除以2
        document.getElementById('totalCollabs').textContent = Math.floor(totalCollaborations / 2);
    }

    // 重置图谱视图
    resetGraph() {
        this.updateGraph();
    }

    // 切换标签显示
    toggleLabels() {
        this.config.showLabels = !this.config.showLabels;
        this.updateGraph(this.currentAuthor?.name);

        const btn = document.getElementById('toggleLabels');
        btn.innerHTML = this.config.showLabels ?
            '<i class="fas fa-tag"></i>' :
            '<i class="fas fa-tag" style="opacity: 0.5;"></i>';
        btn.title = this.config.showLabels ? '隐藏标签' : '显示标签';
    }

    // 导出图表为图片
    exportGraph() {
        if (!this.chart) return;

        const timestamp = new Date().getTime();
        const authorName = this.currentAuthor ? `_${this.currentAuthor.name}` : '';
        const filename = `NowGraph${authorName}_${timestamp}.png`;

        const url = this.chart.getDataURL({
            type: 'png',
            pixelRatio: 2,
            backgroundColor: '#fff'
        });

        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();

        // 显示导出成功提示
        this.showToast('图表已导出为PNG图片', 'success');
    }

    // 切换全屏
    toggleFullscreen() {
        const elem = document.documentElement;

        if (!document.fullscreenElement) {
            if (elem.requestFullscreen) {
                elem.requestFullscreen();
            } else if (elem.webkitRequestFullscreen) {
                elem.webkitRequestFullscreen();
            } else if (elem.msRequestFullscreen) {
                elem.msRequestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
        }
    }

    // 显示帮助
    showHelp() {
        document.getElementById('helpModal').classList.add('active');
    }

    // 隐藏帮助
    hideHelp() {
        document.getElementById('helpModal').classList.remove('active');
    }

    // 显示加载界面
    showLoading() {
        document.getElementById('loadingMask').style.display = 'flex';
    }

    // 隐藏加载界面
    hideLoading() {
        setTimeout(() => {
            document.getElementById('loadingMask').style.display = 'none';
        }, 500);
    }

    // 显示提示信息
    showToast(message, type = 'info') {
        // 创建toast元素
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;

        // 添加到页面
        document.body.appendChild(toast);

        // 显示动画
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        // 3秒后移除
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    // 简单拼音转换（用于搜索）
    getPinyin(text) {
        // 这是一个简化的实现，实际应用中可能需要完整的拼音库
        const pinyinMap = {
            '和泉': 'hequan',
            '新川': 'xinchuan',
            '鶴岡': 'hegang',
            '誠一郎': 'chengyilang',
            'みさお': 'misao',
            '泰樹': 'taishu',
            // 可以添加更多映射
        };

        let result = text;
        for (const [chinese, pinyin] of Object.entries(pinyinMap)) {
            result = result.replace(new RegExp(chinese, 'g'), pinyin);
        }

        return result;
    }

    // 检查URL中的hash并加载对应的作者
    checkUrlHash() {
        const hash = window.location.hash;
        if (hash && hash.startsWith('#')) {
            const authorName = decodeURIComponent(hash.substring(1));
            if (this.authors.has(authorName)) {
                setTimeout(() => {
                    this.selectAuthor(authorName);
                }, 1000);
            }
        }
    }
}

// 全局NowGraph实例
let nowGraph;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    nowGraph = new NowGraph();

    // 添加toast样式
    const style = document.createElement('style');
    style.textContent = `
        .toast {
            position: fixed;
            top: 100px;
            right: 20px;
            background: white;
            border-radius: 8px;
            padding: 12px 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 9999;
            transform: translateX(120%);
            transition: transform 0.3s ease;
            border-left: 4px solid #1890ff;
        }
        .toast.show {
            transform: translateX(0);
        }
        .toast-success {
            border-left-color: #52c41a;
        }
        .toast i {
            font-size: 1.2rem;
        }
        .toast-success i {
            color: #52c41a;
        }
    `;
    document.head.appendChild(style);

    // 监听全屏变化
    document.addEventListener('fullscreenchange', updateFullscreenButton);
    document.addEventListener('webkitfullscreenchange', updateFullscreenButton);
    document.addEventListener('msfullscreenchange', updateFullscreenButton);

    function updateFullscreenButton() {
        const btn = document.getElementById('fullscreen');
        if (document.fullscreenElement) {
            btn.innerHTML = '<i class="fas fa-compress"></i>';
            btn.title = '退出全屏';
        } else {
            btn.innerHTML = '<i class="fas fa-expand"></i>';
            btn.title = '全屏';
        }
    }
});
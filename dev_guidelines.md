# JOEST 项目开发规范与元规则

## 目录
- [1. 核心设计哲学](#1-核心设计哲学)
- [2. 代码组织原则](#2-代码组织原则)
- [3. 功能开发规范](#3-功能开发规范)
- [4. 可复用性设计](#4-可复用性设计)
- [5. CSS 开发规范](#5-css-开发规范)
- [6. JavaScript 开发规范](#6-javascript-开发规范)
- [7. HTML 结构规范](#7-html-结构规范)
- [8. 数据管理规范](#8-数据管理规范)
- [9. 性能优化原则](#9-性能优化原则)
- [10. 维护与扩展指南](#10-维护与扩展指南)

---

## 1. 核心设计哲学

### 1.1 KISS 原则 (Keep It Simple, Stupid)
- **保持简单**: 用最直接的方式解决问题,避免过度设计
- **渐进增强**: 先实现核心功能,再考虑优化和扩展
- **最小惊讶**: 代码行为应符合直觉,降低认知负担

### 1.2 DRY 原则 (Don't Repeat Yourself)
- **消除重复**: 相同逻辑只写一次,通过抽象复用
- **单一真相源**: 每个知识点在系统中只有一个权威表示
- **工具函数化**: 通用逻辑提取到 `utils.js`

### 1.3 SOLID 原则的简化应用
- **单一职责**: 每个函数/模块只做一件事
- **开放封闭**: 对扩展开放,对修改封闭(通过配置而非改代码)
- **依赖倒置**: 高层模块不依赖低层模块,都依赖抽象

### 1.4 学术优先原则
- **内容第一**: 所有设计服务于学术内容的展示和检索
- **可访问性**: 确保极简模式(`?sty=no`)下内容完整可读
- **长期稳定**: 优先考虑向后兼容,避免破坏性变更

---

## 2. 代码组织原则

### 2.1 文件结构规范
```
JOEST-Server/
├── script/              # JavaScript 文件
│   ├── utils.js        # 通用工具函数库(必须)
│   ├── index.js        # 首页逻辑
│   ├── nowbase.js      # NowBase 检索系统
│   └── ...             # 其他页面脚本
├── style/              # CSS 样式文件
│   ├── main.css        # 全局样式(必须)
│   ├── index.css       # 首页专用样式
│   └── ...             # 其他页面样式
├── database/           # 数据文件(JSON)
│   ├── nowbase.json    # 论文数据库
│   ├── news.json       # 新闻数据
│   └── ...
├── *.html              # 页面文件
└── README.md           # 项目说明
```

### 2.2 模块化原则
- **按页面划分**: 每个页面对应一个 JS 文件和一个 CSS 文件
- **共享层分离**: 通用功能放在 `utils.js`,全局样式放在 `main.css`
- **数据与逻辑分离**: JSON 数据文件独立于业务逻辑

### 2.3 命名规范
```javascript
// 变量: camelCase
let papersData = [];
let currentPage = 1;

// 常量: UPPER_SNAKE_CASE
const MAX_PAPERS_PER_PAGE = 8;

// 函数: camelCase + 动词开头
function loadPapers() { }
function displayPaper(paper) { }

// 类名: PascalCase (如果使用)
class PaperManager { }

// CSS 类: kebab-case
.paper-item { }
.author-link { }
```

---

## 3. 功能开发规范

### 3.1 新增功能流程

#### Step 1: 需求分析
```
1. 这个功能解决什么问题?
2. 是否有现有功能可以复用?
3. 是否需要在多个页面使用?
4. 对性能有何影响?
```

#### Step 2: 设计方案
```javascript
// ❌ 错误: 直接在页面中写死逻辑
// index.html
<button onclick="alert('Hello')">点击</button>

// ✅ 正确: 分离关注点
// index.js
document.getElementById('myBtn').addEventListener('click', handleGreeting);

function handleGreeting() {
    utils.showToast('Hello'); // 使用工具函数
}
```

#### Step 3: 实现原则
1. **先写工具函数** (如果需要复用)
2. **再写业务逻辑** (页面特定功能)
3. **最后更新样式** (CSS)
4. **测试极简模式** (`?sty=no`)

#### Step 4: 文档更新
- 在相关代码中添加注释
- 更新本开发文档(如需要)

### 3.2 修改功能原则

#### 向后兼容性检查清单
- [ ] 旧的功能是否仍然可用?
- [ ] 旧的 URL 参数是否仍然有效?
- [ ] 旧的 CSS 类名是否保留(或提供迁移)?
- [ ] 数据格式是否兼容?

```javascript
// ✅ 示例: 保留旧 API
window.generateGBCitation = function(paper) {
    // 内部调用新实现
    return utils.generateGBCitation(paper);
};

// 新的推荐用法
utils.generateGBCitation(paper, true); // 纯文本
```

### 3.3 删除功能原则
1. **标记废弃** (至少保留一个版本)
```javascript
/**
 * @deprecated 请使用 utils.copyToClipboard() 代替
 */
function oldCopyFunction(text) {
    console.warn('此函数已废弃,请使用 utils.copyToClipboard()');
    utils.copyToClipboard(text);
}
```

2. **确认无依赖** (搜索整个代码库)
3. **更新文档** (记录删除原因和替代方案)

---

## 4. 可复用性设计

### 4.1 工具函数设计原则

#### 单一职责
```javascript
// ✅ 好: 每个函数只做一件事
function extractAuthors(paper) { /* ... */ }
function getPublishedInfo(paper) { /* ... */ }
function wrapEnglish(text) { /* ... */ }

// ❌ 坏: 一个函数做太多事
function processPaper(paper) {
    // 提取作者
    // 格式化日期
    // 生成引用
    // 复制文本
    // ...
}
```

#### 纯函数优先
```javascript
// ✅ 纯函数: 相同输入总是得到相同输出,无副作用
function generateCitation(paper, plainText = false) {
    const authors = extractAuthors(paper);
    const title = paper.title || '无标题';
    return `${authors}. ${title}[EB/OL]. ...`;
}

// ❌ 非纯函数: 依赖外部状态
let currentPaper = null;
function generateCitation() {
    return `${currentPaper.authors}. ${currentPaper.title}...`;
}
```

#### 参数设计
```javascript
// ✅ 好的参数设计: 有默认值,类型清晰
function showToast(message, duration = 2000) {
    // message: string - 提示信息
    // duration: number - 显示时长(毫秒),默认 2000
}

// ❌ 坏的参数设计: 魔法数字,含义不明
function showToast(msg, time) {
    // time 是什么单位?默认值是多少?
}
```

### 4.2 组件化思维

虽然本项目不使用框架,但应有组件化思维:

```javascript
// 可复用的"论文卡片"逻辑
function createPaperCard(paper) {
    return {
        render() {
            return `
                <div class="paper-item">
                    <h3>${paper.title}</h3>
                    <p>${paper.authors}</p>
                </div>
            `;
        },
        bindEvents(element) {
            element.addEventListener('click', () => {
                window.location.href = `nowbase.html?doi=${paper.nowbasedoi}`;
            });
        }
    };
}

// 使用
const card = createPaperCard(paperData);
container.innerHTML = card.render();
card.bindEvents(container.firstChild);
```

### 4.3 配置驱动设计

```javascript
// ❌ 硬编码
if (page === 1) { /* ... */ }
const itemsPerPage = 8;

// ✅ 配置化
const CONFIG = {
    pagination: {
        itemsPerPage: 8,
        maxVisiblePages: 5
    },
    search: {
        debounceDelay: 300,
        minSearchLength: 1
    }
};

// 使用时
if (currentPage === 1) { /* ... */ }
const items = papers.slice(0, CONFIG.pagination.itemsPerPage);
```

---

## 5. CSS 开发规范

### 5.1 样式优先级策略

```
1. 全局样式 (main.css) - 最低优先级
   ├─ 重置样式
   ├─ 布局系统
   └─ 通用组件(按钮、表格等)

2. 页面专用样式 (index.css, news.css 等) - 中等优先级
   ├─ 页面特有布局
   └─ 页面特有组件

3. 内联样式 - 最高优先级(尽量避免)
   └─ 仅在动态生成的内容中使用
```

### 5.2 BEM 命名规范 (简化版)

```css
/* Block: 独立组件 */
.paper-item { }

/* Element: 组件的一部分 */
.paper-item__title { }
.paper-item__author { }

/* Modifier: 变体 */
.paper-item--highlighted { }
.btn--primary { }
.btn--small { }
```

### 5.3 避免的选择器

```css
/* ❌ 避免: 过深的嵌套 */
div > ul > li > a span { }

/* ✅ 推荐: 扁平化选择器 */
.nav-link__text { }

/* ❌ 避免: ID 选择器(优先级过高) */
#mainContent .title { }

/* ✅ 推荐: 类选择器 */
.main-content__title { }

/* ❌ 避免: 通配符(性能差) */
* { margin: 0; }

/* ✅ 推荐: 明确指定 */
body, h1, h2, p { margin: 0; }
```

### 5.4 响应式设计原则

```css
/* 移动优先 */
.container {
    width: 100%;
    padding: 10px;
}

/* 平板 */
@media (min-width: 768px) {
    .container {
        max-width: 720px;
        margin: 0 auto;
    }
}

/* 桌面 */
@media (min-width: 1200px) {
    .container {
        max-width: 1140px;
    }
}
```

### 5.5 CSS 变量使用

```css
/* 定义全局变量 */
:root {
    --color-primary: #003C6B;
    --color-secondary: #00629B;
    --color-accent: #D36A00;
    --spacing-unit: 8px;
    --border-radius: 4px;
}

/* 使用变量 */
.btn-primary {
    background-color: var(--color-primary);
    padding: calc(var(--spacing-unit) * 2);
    border-radius: var(--border-radius);
}
```

---

## 6. JavaScript 开发规范

### 6.1 异步处理规范

```javascript
// ✅ 推荐: async/await + 错误处理
async function loadPapers() {
    try {
        const response = await fetch('database/nowbase.json');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const papers = await response.json();
        displayPapers(papers);
    } catch (error) {
        console.error('加载论文失败:', error);
        showError('数据加载失败,请刷新页面重试');
    }
}

// ❌ 避免: Promise 链过长
fetch('data.json')
    .then(response => response.json())
    .then(data => processData(data))
    .then(result => displayResult(result))
    .catch(error => handleError(error));
```

### 6.2 DOM 操作优化

```javascript
// ✅ 批量更新 DOM
function updatePaperList(papers) {
    const fragment = document.createDocumentFragment();
    
    papers.forEach(paper => {
        const element = createPaperElement(paper);
        fragment.appendChild(element);
    });
    
    container.innerHTML = '';
    container.appendChild(fragment); // 只触发一次重排
}

// ❌ 避免: 循环中频繁操作 DOM
papers.forEach(paper => {
    const element = createPaperElement(paper);
    container.appendChild(element); // 每次都触发重排
});
```

### 6.3 事件委托

```javascript
// ✅ 推荐: 事件委托
document.getElementById('paperList').addEventListener('click', (e) => {
    const paperItem = e.target.closest('.paper-item');
    if (paperItem) {
        const doi = paperItem.dataset.doi;
        navigateToPaper(doi);
    }
});

// ❌ 避免: 为每个元素绑定事件
papers.forEach(paper => {
    document.getElementById(`paper-${paper.id}`).addEventListener('click', () => {
        navigateToPaper(paper.doi);
    });
});
```

### 6.4 防抖与节流

```javascript
// 防抖: 适用于搜索输入
function debounce(func, delay) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
}

// 使用
searchInput.addEventListener('input', debounce((e) => {
    performSearch(e.target.value);
}, 300));

// 节流: 适用于滚动事件
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
```

### 6.5 错误处理

```javascript
// ✅ 完善的错误处理
async function loadData() {
    try {
        const response = await fetch('data.json');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (!Array.isArray(data)) {
            throw new TypeError('Expected array data');
        }
        
        return data;
    } catch (error) {
        if (error instanceof TypeError) {
            console.error('数据格式错误:', error);
            showUserError('数据格式异常,请联系管理员');
        } else if (error.message.includes('HTTP')) {
            console.error('网络错误:', error);
            showUserError('网络连接失败,请检查网络');
        } else {
            console.error('未知错误:', error);
            showUserError('发生未知错误');
        }
        
        return []; // 返回安全的默认值
    }
}
```

---

## 7. HTML 结构规范

### 7.1 语义化标签

```html
<!-- ✅ 推荐: 使用语义化标签 -->
<header>
    <h1>期刊名称</h1>
    <nav>
        <ul>
            <li><a href="index.html">首页</a></li>
        </ul>
    </nav>
</header>

<main>
    <section>
        <h2>论文明细</h2>
        <article class="paper-item">
            <!-- 内容 -->
        </article>
    </section>
</main>

<footer>
    <p>版权信息</p>
</footer>

<!-- ❌ 避免: 全部使用 div -->
<div class="header">
    <div class="nav">
        <div class="nav-item">...</div>
    </div>
</div>
```

### 7.2 无障碍访问 (a11y)

```html
<!-- ✅ 良好的无障碍性 -->
<button aria-label="关闭对话框" onclick="closeDialog()">
    <span aria-hidden="true">×</span>
</button>

<img src="cover.jpg" alt="《电子游戏科学与技术》封面">

<input type="text" id="search" aria-describedby="search-help">
<span id="search-help">输入关键词搜索论文</span>

<!-- ❌ 避免: 缺少无障碍属性 -->
<div onclick="closeDialog()">×</div>
<img src="cover.jpg">
<input type="text">
```

### 7.3 避免内联样式

```html
<!-- ❌ 避免: 大量内联样式 -->
<div style="display: flex; justify-content: space-between; margin: 20px;">
    <h2 style="color: #003C6B; font-size: 24px;">标题</h2>
</div>

<!-- ✅ 推荐: 使用 CSS 类 -->
<div class="section-header">
    <h2 class="section-title">标题</h2>
</div>

<style>
.section-header {
    display: flex;
    justify-content: space-between;
    margin: 20px;
}

.section-title {
    color: var(--color-primary);
    font-size: 24px;
}
</style>
```

### 7.4 动态内容生成

```javascript
// ✅ 推荐: 使用模板字符串 + 转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderPaper(paper) {
    return `
        <div class="paper-item" data-doi="${escapeHtml(paper.doi)}">
            <h3>${escapeHtml(paper.title)}</h3>
            <p>${escapeHtml(paper.authors)}</p>
        </div>
    `;
}

// ❌ 避免: 直接拼接用户输入
function renderPaper(paper) {
    return `<div onclick="showPaper('${paper.doi}')">${paper.title}</div>`;
    // XSS 风险!
}
```

---

## 8. 数据管理规范

### 8.1 JSON 数据结构

```json
{
    "nowbase.json": {
        "nowbasedoi": "ET-1-1-2025-R",
        "title": "论文标题",
        "authors": ["作者1", "作者2"],
        "keywords": ["关键词1", "关键词2"],
        "abstract": "摘要内容",
        "issue": "第一卷第一期",
        "published": "2025-01-01T00:00:00.000Z",
        "filePath": "articles/volume1/paper.pdf",
        "level": "主编推荐",
        "bestpaperaward": false,
        "specialNote": "",
        "doc_category": "R",
        "edition": "ET",
        "volume": 1,
        "year": 2025
    }
}
```

### 8.2 数据验证

```javascript
// 数据验证函数
function validatePaper(paper) {
    const required = ['nowbasedoi', 'title', 'authors', 'issue'];
    const missing = required.filter(field => !paper[field]);
    
    if (missing.length > 0) {
        throw new Error(`缺少必填字段: ${missing.join(', ')}`);
    }
    
    if (!Array.isArray(paper.authors) || paper.authors.length === 0) {
        throw new Error('authors 必须是非空数组');
    }
    
    return true;
}

// 使用时
try {
    validatePaper(paperData);
    processPaper(paperData);
} catch (error) {
    console.error('数据验证失败:', error);
}
```

### 8.3 数据缓存策略

```javascript
// 简单的内存缓存
const cache = {
    data: null,
    timestamp: null,
    ttl: 5 * 60 * 1000, // 5 分钟
    
    async get(key) {
        if (this.data && Date.now() - this.timestamp < this.ttl) {
            return this.data;
        }
        
        const response = await fetch(`database/${key}.json`);
        this.data = await response.json();
        this.timestamp = Date.now();
        
        return this.data;
    },
    
    invalidate() {
        this.data = null;
        this.timestamp = null;
    }
};

// 使用
const papers = await cache.get('nowbase');
```

---

## 9. 性能优化原则

### 9.1 加载优化

```html
<!-- ✅ 延迟加载非关键资源 -->
<script src="script/utils.js" defer></script>
<script src="script/index.js" defer></script>

<!-- ✅ 图片懒加载 -->
<img src="placeholder.jpg" data-src="actual-image.jpg" loading="lazy">

<!-- ❌ 避免: 阻塞渲染 -->
<script src="script/large-library.js"></script>
```

### 9.2 渲染优化

```javascript
// ✅ 使用 requestAnimationFrame
function animateScroll() {
    // 动画逻辑
    requestAnimationFrame(animateScroll);
}

// ✅ 虚拟化长列表 (只渲染可见部分)
function renderVisibleItems(items, scrollTop, viewportHeight) {
    const itemHeight = 50;
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
        startIndex + Math.ceil(viewportHeight / itemHeight) + 1,
        items.length
    );
    
    return items.slice(startIndex, endIndex);
}
```

### 9.3 网络优化

```javascript
// ✅ 合并请求
async function loadAllData() {
    const [papers, news, notifications] = await Promise.all([
        fetch('database/nowbase.json').then(r => r.json()),
        fetch('database/news.json').then(r => r.json()),
        fetch('database/notification.json').then(r => r.json())
    ]);
    
    return { papers, news, notifications };
}

// ✅ 使用 ETag/Last-Modified (浏览器自动处理)
// 服务器配置示例 (Nginx):
// etag on;
// last_modified on;
```

---

## 10. 维护与扩展指南

### 10.1 代码审查清单

#### 功能性
- [ ] 功能是否按预期工作?
- [ ] 边界情况是否处理?
- [ ] 错误处理是否完善?

#### 可维护性
- [ ] 代码是否清晰易读?
- [ ] 是否有充分的注释?
- [ ] 是否遵循命名规范?

#### 性能
- [ ] 是否有不必要的 DOM 操作?
- [ ] 是否有内存泄漏风险?
- [ ] 是否做了适当的缓存?

#### 兼容性
- [ ] 极简模式是否正常?
- [ ] 不同浏览器是否兼容?
- [ ] 移动端是否正常显示?

### 10.2 版本管理

```
版本号格式: MAJOR.MINOR.PATCH

MAJOR: 不兼容的 API 变更
MINOR: 向后兼容的功能新增
PATCH: 向后兼容的问题修正

示例:
1.0.0 -> 1.1.0  (新增搜索功能)
1.1.0 -> 1.1.1  (修复搜索 bug)
1.1.1 -> 2.0.0  (重构数据格式)
```

### 10.3 文档更新时机

**必须更新文档的情况:**
1. 新增公共 API
2. 修改数据格式
3. 改变配置方式
4. 废弃某个功能

**文档应包含:**
- 变更说明
- 迁移指南 (如有破坏性变更)
- 示例代码
- 常见问题

### 10.4 技术债务管理

```javascript
// 标记技术债务
// TODO: 重构此函数,当前复杂度过高
// FIXME: 此处存在竞态条件
// HACK: 临时解决方案,需要在 v2.0 中重写
// XXX: 警告: 这段代码很脆弱

// 定期回顾 (建议每月一次)
// 1. 搜索所有 TODO/FIXME
// 2. 评估优先级
// 3. 制定解决计划
```

### 10.5 扩展新功能的标准流程

```
1. 需求分析
   ├─ 明确功能目标
   ├─ 识别可复用部分
   └─ 评估影响范围

2. 设计阶段
   ├─ 确定技术方案
   ├─ 设计数据结构
   ├─ 规划 API (如需)
   └─ 编写设计文档

3. 实现阶段
   ├─ 编写工具函数 (如需要)
   ├─ 实现核心逻辑
   ├─ 添加样式
   └─ 编写测试

4. 测试阶段
   ├─ 功能测试
   ├─ 兼容性测试
   ├─ 性能测试
   └─ 极简模式测试

5. 部署阶段
   ├─ 代码审查
   ├─ 更新文档
   ├─ 备份数据
   └─ 灰度发布 (如需要)

6. 监控阶段
   ├─ 收集反馈
   ├─ 监控错误
   └─ 持续优化
```

---

## 附录 A: 常用工具函数速查

```javascript
// 极简模式
utils.isSimpleMode()
utils.applySimpleMode()

// 引用生成
utils.generateGBCitation(paper)              // 带格式
utils.generateGBCitation(paper, true)        // 纯文本

// 剪贴板
utils.copyToClipboard(text, onSuccess, onError)

// 提示
utils.showToast(message, duration)

// URL 参数
utils.getUrlParameter(name)

// 日期
utils.getCurrentDate()

// 作者处理
utils.extractAuthors(paper)
utils.getPublishedInfo(paper)

// 文本处理
utils.wrapEnglish(text)
```

## 附录 B: 常见问题 (FAQ)

### Q1: 为什么要有极简模式?
A: 确保在网络不佳、浏览器不支持 CSS 或用户需要快速访问时,内容仍然可读。这是学术网站的基本要求。

### Q2: 何时应该创建新的工具函数?
A: 当同一段逻辑出现 2 次以上,或者逻辑复杂度较高且可能被复用时。

### Q3: 如何处理跨页面共享的状态?
A: 优先使用 URL 参数,其次使用 localStorage,避免使用全局变量。

### Q4: CSS 和 JS 文件如何组织?
A: 按页面组织,每个页面对应一个 CSS 和一个 JS 文件。通用部分放在 `main.css` 和 `utils.js`。

### Q5: 如何保证数据安全?
A: 前端只做展示,敏感操作必须在后端进行。对用户输入进行转义,防止 XSS。

---

## 结语

本开发规范旨在建立一致的开发标准,提高代码质量和可维护性。规范不是束缚,而是指导。在实际开发中,应根据具体情况灵活应用,并持续改进规范本身。

**记住核心原则:**
1. 简单优于复杂
2. 复用优于重复
3. 清晰优于聪明
4. 稳定优于新颖

---

**文档版本**: 1.0.0  
**最后更新**: 2026-04-15  
**维护者**: JOEST 开发团队

# JOEST 期刊网站

## 目录

1. [项目概述](#项目概述)
2. [核心技术架构](#核心技术架构)
3. [零成本部署指南](#零成本部署指南)
4. [本地运行与开发](#本地运行与开发)
5. [nowbase.json 数据结构详解](#nowbasejson-数据结构详解)
6. [工具集使用说明](#工具集使用说明)
7. [常见问题](#常见问题)

---

## 项目概述

JOEST 是一个学术杂志网站。本仓库包含论文数据库管理、编辑部成员管理、通知公告发布、DOI生成、图片压缩、PDF处理等功能。

### 项目结构

```
JOEST/
├── index.html              # 网站首页
├── releases.html           # 期刊发布页面
├── notifications.html      # 通知公告页面
├── editorial.html          # 编辑部页面
├── nowbase.html            # 论文数据库页面
├── database/
│   └── data/
│       ├── nowbase.json    # 核心论文数据库
│       ├── nowledge.json   # 编辑部成员数据库
│       └── notification.json # 通知公告数据库
├── tools/                  # 管理工具集
│   ├── nowseek.py          # 统一图形界面（推荐使用）
│   ├── update_releases.py  # 论文发布更新工具
│   ├── manage_editors.py   # 编辑部成员管理
│   ├── update_notifications.py # 通知公告管理
│   ├── local_webserver.py  # 本地Web服务器
│   ├── deploy.py           # 部署打包工具
│   ├── compress_avatars.py # 头像压缩
│   ├── compress_posters.py # 海报压缩
│   └── gmmf_optimizr.py    # Gameme Factor优化器
├── script/                 # 前端脚本
│   └── stat.js             # 统计数据（Gameme Factor归一化参数）
└── articles/               # 论文PDF文件存放目录
```

---

## 核心技术架构

### 前端技术栈
- 纯原生 HTML/CSS/JavaScript，无框架依赖
- 通过 Fetch API 加载本地 JSON 文件
- 响应式设计，适配移动端

### 后端/存储
- **无需后端服务器**：所有数据存储在 JSON 文件中
- **静态托管**：可部署在任何静态网站托管服务（Netlify、GitHub Pages、Vercel等）
- **文件存储**：论文 PDF 存放在 Gitee/GitHub 仓库，通过原始链接访问

### 数据流转
```
用户操作 → 管理工具修改 JSON → 推送到 Git → 托管平台自动部署 → 网站更新
```

---

## 零成本部署指南

### 方案一：Netlify + Gitee（推荐）

#### 1. 准备代码仓库

**GitHub（代码托管）：**
```bash
# 1. 注册 GitHub 账号
# 2. 创建新仓库 joest
# 3. 推送代码
git remote add origin https://github.com/你的用户名/joest.git
git push -u origin main
```

**Gitee（PDF文件托管）：**
```bash
# 1. 注册 Gitee 账号
# 2. 创建仓库 articles（用于存PDF）
# 3. 上传论文PDF文件
# 4. 获取原始文件链接格式：
#    https://gitee.com/你的用户名/articles/raw/master/volume1/论文.pdf
```

#### 2. 部署到 Netlify

1. 访问 [netlify.com](https://netlify.com)，点击 "Sign up" 用 GitHub 登录
2. 点击 "Add new site" → "Import an existing project"
3. 选择 GitHub，授权并选择 `joest` 仓库
4. 构建设置：
   ```
   Build command: （留空）
   Publish directory: ./
   ```
5. 点击 "Deploy site"

**自动部署：** 以后每次 `git push`，Netlify 会自动重新部署。

#### 3. 修改配置文件

编辑 `generate_sitemap.py` 和前端 HTML 文件中的 URLs：

```python
# generate_sitemap.py
base_url = "https://你的站点名.netlify.app"
```

```html
<!-- index.html 等文件中的链接 -->
<a href="https://你的站点名.netlify.app/releases.html">
```

### 方案二：GitHub Pages（纯静态）

1. 仓库设置 → Pages → 分支选 `main`，目录选 `/（root）`
2. 访问 `https://你的用户名.github.io/joest/`
3. **注意**：GitHub Pages 不支持自定义 404 页面根路径，需要配置 `.nojekyll` 文件

### 方案三：Vercel

```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署
cd JOEST
vercel --prod
```

---

## 本地运行与开发

### 环境要求
- Python 3.8+
- pip（Python包管理器）

### 安装依赖

```bash
pip install pillow PyPDF2 requests
```

### 启动本地服务器

**方法一：使用内置工具（推荐）**
```bash
python tools/local_webserver.py
```
- 自动关闭占用 8000 端口的进程
- 自动打开浏览器访问 `http://localhost:8000`
- 支持 CORS，JSON 文件可正常加载

**方法二：Python 原生**
```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```

**方法三：使用其他工具**
```bash
# Node.js
npx serve

# PHP
php -S localhost:8000
```

### 启动管理工具

```bash
# 统一图形界面（包含所有工具）
python tools/nowseek.py

# 或单独运行各工具
python tools/update_releases.py    # 论文管理
python tools/manage_editors.py     # 成员管理
python tools/update_notifications.py # 通知管理
```

---

## nowbase.json 数据结构详解

这是项目的核心数据库，存储所有论文信息。

### 完整字段说明

```json
{
  "id": 171,                        // 论文唯一ID，自动递增
  "title": "论文标题",              // 论文完整标题
  "authors": ["作者1", "作者2"],   // 作者数组（注意：是数组不是字符串）
  "issue": "电子游戏科学与技术 第一卷", // 所属期数
  "keywords": ["关键词1", "关键词2"], // 关键词数组
  "filePath": "https://gitee.com/.../paper.pdf", // PDF文件URL
  "specialNote": "特邀稿件",        // 特殊说明（可为null）
  "abstract": "摘要内容...",        // 论文摘要
  "nowbasedoi": "PS-1-001-2026-R", // 自定义DOI格式
  "doc_category": "R",              // 文献分类码
  "edition": "PS",                  // 版号
  "volume": 1,                      // 卷号（整数）
  "year": "2026",                   // 出版年份
  "index": 1,                       // 卷内索引
  "published": "2026-04-30T10:30:00" // ISO格式发布时间
}
```

### 字段详细说明

| 字段           | 类型        | 必填 | 说明                                  |
| -------------- | ----------- | ---- | ------------------------------------- |
| `id`           | int         | 是   | 自增主键，用于前端定位和删除操作      |
| `title`        | string      | 是   | 论文标题，会检查重复                  |
| `authors`      | array       | 是   | **必须是数组**，如 `["张三","李四"]`  |
| `issue`        | string      | 是   | 期刊期数，用于分类显示                |
| `keywords`     | array       | 是   | 关键词数组，用于检索                  |
| `filePath`     | string      | 是   | PDF的完整URL（需支持外链）            |
| `specialNote`  | string/null | 否   | 特殊标注，如"封面文章"                |
| `abstract`     | string      | 否   | 摘要，会自动清理换行符                |
| `nowbasedoi`   | string      | 是   | 自定义DOI，需唯一                     |
| `doc_category` | string      | 是   | 文献分类：R/N/D/S/M/L/W               |
| `edition`      | string      | 是   | 版号：PS/BS/ET/SS/HS/EDU/HM/YSA/TM/WP |
| `volume`       | int         | 是   | 卷号，整数类型                        |
| `year`         | string      | 是   | 年份字符串                            |
| `index`        | int         | 是   | 该卷内的论文序号                      |
| `published`    | string      | 是   | ISO 8601 格式时间戳                   |

### 前端如何加载 these 数据

```javascript
// releases.html 中的加载逻辑
fetch('database/data/nowbase.json')
  .then(response => response.json())
  .then(data => {
    // 按 issue 分组显示
    const papersByIssue = {};
    data.forEach(paper => {
      if (!papersByIssue[paper.issue]) {
        papersByIssue[paper.issue] = [];
      }
      papersByIssue[paper.issue].push(paper);
    });
    // 渲染页面...
  });
```

---

## 工具集使用说明

### 1. nowseek.py - 统一管理界面（最常用）

```bash
python tools/nowseek.py
```

**界面功能：**
- 左侧工具列表，点击切换
- 右侧显示工具说明和参数配置
- 底部实时显示执行日志

**可用工具：**
- 通知公告管理
- 期刊发布更新
- 编辑人员管理
- Gameme因子优化器
- 本地Web服务器
- 部署工具

### 2. update_releases.py - 论文管理

```bash
python tools/update_releases.py
```

**功能：**
- **添加论文**：填写表单自动生成DOI
- **修改论文**：直接编辑JSON
- **删除论文**：从列表中移除
- **DOI生成**：基于版号+卷号+索引+年份+分类码生成
- **文件路径**：自动拼接Gitee链接

**DOI生成规则：**
```
格式：{edition}-{volume}-{index}-{year}-{category}
示例：PS-1-1-2026-R
```

### 3. manage_editors.py - 编辑部成员管理

```bash
python tools/manage_editors.py
```

**功能：**
- 增删改查编辑部成员
- **批量导入论文DOI**：输入多个DOI（分号分隔），自动从CrossRef API获取论文信息
- 管理成员的论文列表、研究方向、h-index等

### 4. update_notifications.py - 通知管理

```bash
python tools/update_notifications.py
```

**功能：**
- 发布/编辑/删除通知
- 自动处理换行符为 `<p></p>` 标签
- 按时间倒序排列

### 5. local_webserver.py - 本地服务器

```bash
python tools/local_webserver.py
```

**特点：**
- 添加 CORS 头，允许跨域访问
- 禁用缓存，开发时实时生效
- 自动清理占用端口的进程

### 6. deploy.py - 部署打包

```bash
python tools/deploy.py
```

**功能：**
- 自动排除 `.git`、`.idea`、`dev` 等目录
- 生成 `deploy.zip` 压缩包
- 自动打开 Netlify 网站

### 7. compress_avatars.py / compress_posters.py - 图片压缩

```bash
# 压缩头像（150px限制，30%质量）
python compress_avatars.py

# 压缩海报（1920px限制，85%质量）
python compress_posters.py
```

**安全机制：**
- 自动创建 `.backup` 备份文件
- 压缩失败自动恢复原图

### 8. gmmf_optimizr.py - Gameme Factor优化

```bash
python tools/gmmf_optimizr.py
```

**功能：**
- 计算每位作者的 Gameme Factor
- 三阶段搜索最优归一化参数
- 自动更新 `script/stat.js` 中的参数

---

## 常见问题

### Q1: 本地打开 HTML 文件无法加载 JSON？

**A:** 浏览器的 CORS 策略限制。必须通过 HTTP 服务器访问，不能用 `file://` 协议。
```bash
python tools/local_webserver.py
# 然后访问 http://localhost:8000
```

### Q2: Netlify 部署后 JSON 文件 404？

**A:** 检查文件路径是否正确：
```javascript
// 错误：相对路径可能失效
fetch('./database/data/nowbase.json')

// 正确：使用绝对路径
fetch('/database/data/nowbase.json')
```

### Q3: 如何修改网站标题和 logo？

**A:** 编辑每个 HTML 文件中的 `<title>` 标签和导航栏。

### Q4: 如何批量导入历史论文？

**A:** 
1. 使用 `update_releases.py` 逐个添加
2. 或直接编辑 `nowbase.json`，注意 JSON 格式正确
3. 确保 `id` 不重复，`authors` 和 `keywords` 为数组

### Q5: PDF 文件放哪里？

**A:** 
- **推荐**：Gitee/GitHub 仓库，获取原始文件链接
- **备选**：和网站同仓库（但会增加仓库体积）
- **不推荐**：本地服务器，公网无法访问

### Q6: 如何让搜索引擎收录？

**A:**
```bash
# 1. 生成 sitemap.xml
python generate_sitemap.py

# 2. 提交到搜索引擎
# Google: https://search.google.com/search-console
# Bing: https://www.bing.com/webmasters
```

### Q7: 修改数据后网站没更新？

**A:**
- 本地：清除浏览器缓存（Ctrl+Shift+R）
- Netlify：检查部署日志，确认自动部署成功
- Gitee：确认原始链接地址正确

---

## 维护建议

### 日常操作流程

```bash
# 1. 添加新论文
python tools/update_releases.py

# 2. 如有新成员，添加
python tools/manage_editors.py

# 3. 如有通知，发布
python tools/update_notifications.py

# 4. 压缩新上传的图片
python compress_avatars.py
python compress_posters.py

# 5. 重新生成 sitemap
python generate_sitemap.py

# 6. 提交到 Git
git add .
git commit -m "更新：新增论文XXX"
git push

# 7. Netlify 自动部署，约2分钟生效
```

### 备份策略

```bash
# 定期备份 JSON 文件
cp database/data/*.json ~/backup/joest/

# 或使用 Git 历史作为备份
git log --oneline  # 可随时回滚
```

---

## 许可证

MIT

# 📖 关于《电子游戏科学与技术》期刊

## 我们是做什么的

《电子游戏科学与技术》（Journal of Electronic Science and Technology，JOEST）是一本**开放获取、同行评议**的学术期刊，致力于将电子游戏作为严肃的学术研究对象。

我们不相信“游戏只是娱乐”这种说法。游戏是：

- **计算科学的试验场**——GPU、实时渲染、物理模拟，游戏产业推动着整个计算机科学的前沿
- **社会科学的实验室**——数百万玩家的行为数据，是研究人类协作、竞争、决策的天然样本
- **人文科学的文本**——叙事、美学、意识形态，游戏是一种需要被认真对待的媒介
- **教育学的工具**——从严肃游戏到游戏化学习，重新定义“教”与“学”
- **健康医学的干预手段**——从认知训练到数字疗法，游戏正在成为新的处方

## 我们的版块

期刊下设多个专业版块，每个版块有独立的创作指南：

| 版块       | 代码 | 定位                                     |
| ---------- | ---- | ---------------------------------------- |
| 基础科学版 | PS   | 游戏的形式化理论、数学模型、算法基础     |
| 工程技术版 | ET   | 渲染、引擎、网络、AI、性能优化           |
| 社会科学版 | SS   | 玩家行为、产业生态、政策法规、电竞社会学 |
| 人文科学版 | HS   | 游戏叙事、文化研究、美学批评、媒介考古   |
| 教育科学版 | EDU  | 游戏化学习、电竞教育、认知发展           |
| 健康医学版 | HM   | 电竞运动医学、数字疗法、认知训练         |
| 生物科学版 | BS   | 计算生物学、生物启发的游戏AI             |

此外，我们还设有：
- **公共科学版**：面向公众的深度评论、调查报告、思想实验
- **少年科学志**：面向青少年创作者的探索平台
- **白皮书**：行业报告、技术标准、产业倡议

## 我们的特色

### 1. 开放的学术生态

- **零 APC（文章处理费）**：作者无需支付任何费用
- **开放获取**：所有论文免费阅读、下载
- **开放同行评议**：审稿意见与论文一同发布（可选择匿名）
- **开放数据**：鼓励作者共享代码、数据集、实验材料

### 2. 独特的评价体系

我们开发了 **Gameme Factor（游戏迷因子）**，一种专门针对跨学科游戏研究者的贡献度评价模型。它综合考虑：

- 作者排序（指数衰减加权）
- 论文影响力（引用、下载、讨论）
- 跨学科贡献（连接不同领域的价值）
- 公共传播（科普写作、媒体曝光）

你可以访问 `/stat` 页面查看所有作者的实时排名。

### 3. 严肃的学术标准

我们不是“水刊”。每篇投稿都要经过：

1. **格式审查**（2天）：是否符合版块定位和创作指南
2. **伦理审查**（3天）：是否涉及敏感内容、利益冲突、人类受试者保护
3. **同行评议**（14天）：至少2位领域专家
4. **终审**（3天）：编委会决议

## 我们的承诺

- **不收取任何费用**：投稿、审稿、出版完全免费
- **快速响应**：初审≤5个工作日
- **永久存档**：所有论文在互联网档案馆长期保存
- **作者保留版权**：论文采用CC BY-NC 4.0协议

## 如何参与

### 作为作者

1. 阅读对应版块的**创作指南**（见 `database/data/nowbase.json` 中 DOI 以 `-G` 结尾的条目）
2. 下载论文模板（Word 版 DOI: `TM-2-1-2026-R`，LaTeX 版 DOI: `TM-3-1-2026-R`）
3. 将论文发送至：``dev.projectamadeus@outlook.com``
4. 等待审稿（通常2-4周）

### 作为审稿人

如果你在某个领域有专长，欢迎加入我们的审稿人库。联系：``dev.projectamadeus@outlook.com``

### 作为读者

所有内容免费访问：`https://journalofest.netlify.app`

## 联系我们

- 主编邮箱：`dev.projectamadeus@outlook.com`

---

*电子游戏不是逃避现实的出口，而是理解现实的入口。我们在这里，等你来投稿。*
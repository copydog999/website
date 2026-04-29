// 通用工具函数库

/**
 * 检测是否为极简模式
 * @returns {boolean}
 */
function isSimpleMode() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('sty') === 'no';
}

/**
 * 应用极简模式（移除所有 CSS）
 */
function applySimpleMode() {
    if (isSimpleMode()) {
        document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
            link.remove();
        });
    }
}

/**
 * 获取当前日期，格式为 YYYY-MM-DD
 * @returns {string}
 */
function getCurrentDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * 提取作者信息
 * @param {Object} paper - 论文对象
 * @returns {string} 格式化后的作者字符串
 */
function extractAuthors(paper) {
    if (!paper.authors) return '未知作者';
    
    if (Array.isArray(paper.authors)) {
        if (paper.authors.length === 0) return '未知作者';
        if (paper.authors.length <= 3) {
            return paper.authors.join(', ');
        }
        return paper.authors.slice(0, 3).join(', ') + ', 等';
    }
    
    // 字符串格式处理
    let mainAuthor = paper.authors;
    [' et al.', ' et al', ', '].forEach(separator => {
        if (mainAuthor.includes(separator)) {
            mainAuthor = mainAuthor.split(separator)[0];
        }
    });
    return mainAuthor + ', 等';
}

/**
 * 获取发表日期信息
 * @param {Object} paper - 论文对象
 * @returns {string} 格式化后的日期字符串
 */
function getPublishedInfo(paper) {
    if (!paper.published) return '';
    const pubDate = new Date(paper.published);
    const year = pubDate.getFullYear();
    const month = String(pubDate.getMonth() + 1).padStart(2, '0');
    const day = String(pubDate.getDate()).padStart(2, '0');
    return `(${year}-${month}-${day})`;
}

/**
 * 将英文、数字和半角符号用 span.en 包裹
 * @param {string} text - 输入文本
 * @returns {string} 处理后的文本
 */
function wrapEnglish(text) {
    return text.replace(/([a-zA-Z0-9\-\/\.\?\!\:\;\,\@\#\$\%\^\&\*\(\)\[\]\{\}\|\\\<\>\_\~\`\']+)/g, '<span class="en">$1</span>');
}

/**
 * 生成国标引用格式
 * @param {Object} paper - 论文对象
 * @param {boolean} plainText - 是否返回纯文本
 * @returns {string} 引用格式字符串
 */
function generateGBCitation(paper, plainText = false) {
    const authors = extractAuthors(paper);
    const title = paper.title || '无标题';
    const doi = paper.nowbasedoi || '';
    const currentDate = getCurrentDate();
    const publishedInfo = getPublishedInfo(paper);
    
    const citation = `${authors}. ${title}[EB/OL]. 电子游戏科学与技术，${publishedInfo}[${currentDate}]. https://journalofest.netlify.app/nowbase.html?doi=${doi}.`;
    
    return plainText ? citation : wrapEnglish(citation);
}

/**
 * 复制到剪贴板（带降级方案）
 * @param {string} text - 要复制的文本
 * @param {Function} onSuccess - 成功回调
 * @param {Function} onError - 失败回调
 */
function copyToClipboard(text, onSuccess, onError) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text)
            .then(onSuccess)
            .catch(err => {
                console.error('复制失败:', err);
                fallbackCopy(text, onSuccess, onError);
            });
    } else {
        fallbackCopy(text, onSuccess, onError);
    }
}

/**
 * 降级复制方案
 * @param {string} text - 要复制的文本
 * @param {Function} onSuccess - 成功回调
 * @param {Function} onError - 失败回调
 */
function fallbackCopy(text, onSuccess, onError) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    document.body.appendChild(textArea);
    textArea.select();
    try {
        document.execCommand('copy');
        if (onSuccess) onSuccess();
    } catch (err) {
        console.error('复制失败:', err);
        if (onError) onError(err);
    }
    document.body.removeChild(textArea);
}

/**
 * 显示浮动提示
 * @param {string} message - 提示信息
 * @param {number} duration - 显示时长（毫秒）
 */
function showToast(message, duration = 2000) {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #28a745; color: white; padding: 10px 20px; border-radius: 4px; z-index: 10000; font-size: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.2);';
    document.body.appendChild(toast);
    
    setTimeout(() => {
        document.body.removeChild(toast);
    }, duration);
}

/**
 * 从 URL 获取查询参数
 * @param {string} name - 参数名
 * @returns {string|null} 参数值
 */
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * DOI字体颜色例外库配置
 * 用于深色背景海报的论文,指定白色字体以确保可读性
 */
const DOI_FONT_COLOR_EXCEPTIONS = {

};

/**
 * 获取指定DOI的自定义字体颜色
 * @param {string} doi - 论文DOI
 * @returns {string|null} 字体颜色值或null(使用默认色)
 */
function getFontColorForDOI(doi) {
    return DOI_FONT_COLOR_EXCEPTIONS[doi] || null;
}

// 导出到全局
window.utils = {
    isSimpleMode,
    applySimpleMode,
    getCurrentDate,
    extractAuthors,
    getPublishedInfo,
    wrapEnglish,
    generateGBCitation,
    copyToClipboard,
    showToast,
    getUrlParameter,
    getFontColorForDOI
};

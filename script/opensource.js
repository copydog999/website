// 检测是否为极简模式
function isSimpleMode() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('sty') === 'no';
}

// 根据文件扩展名获取图标
function getFileIcon(filename) {
    // 检查是否有扩展名
    if (!filename.includes('.')) {
        return '📁'; // 文件夹图标
    }
    
    const ext = filename.split('.').pop().toLowerCase();
    const iconMap = {
        'zip': '📦',
        'rar': '📦',
        '7z': '📦',
        'tar': '📦',
        'gz': '📦',
        'json': '📄',
        'js': '📜',
        'py': '🐍',
        'java': '☕',
        'cpp': '⚙️',
        'c': '⚙️',
        'h': '⚙️',
        'html': '🌐',
        'css': '🎨',
        'md': '📝',
        'txt': '📄',
        'pdf': '📕',
        'doc': '📘',
        'docx': '📘',
        'xls': '📊',
        'xlsx': '📊',
        'png': '🖼️',
        'jpg': '🖼️',
        'jpeg': '🖼️',
        'gif': '🖼️',
        'svg': '🖼️',
        'mp4': '🎬',
        'avi': '🎬',
        'mkv': '🎬',
        'mp3': '🎵',
        'wav': '🎵',
        'exe': '⚡',
        'dll': '⚡',
        'so': '⚡'
    };
    return iconMap[ext] || '📄';
}

// 加载开源项目数据
async function loadOpensourceData() {
    try {
        const response = await fetch('database/data/opensource.json');
        const data = await response.json();
        displayOpensourceTable(data);
    } catch (error) {
        console.error('加载开源项目数据失败:', error);
        const tbody = document.querySelector('.mirror-table tbody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #D36A00;">加载数据失败，请稍后重试</td></tr>';
        }
    }
}

// 显示开源项目表格
function displayOpensourceTable(data) {
    if (!data || data.length === 0) {
        const tbody = document.querySelector('.mirror-table tbody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #666;">暂无开源项目</td></tr>';
        }
        return;
    }
    
    let htmlContent = '';
    
    // 按更新时间倒序排列（最新的在前）
    const sortedData = [...data].sort((a, b) => {
        return new Date(b.updated.replace(/\//g, '-')) - new Date(a.updated.replace(/\//g, '-'));
    });
    
    sortedData.forEach(item => {
        // DOI链接到nowbase
        const doiLink = item.doi ? `<a href="nowbase.html?doi=${item.doi}" class="mirror-link" target="_blank">${item.doi}</a>` : '-';
        // 发布者链接到nowbase搜索
        const publisherLink = item.publisher ? `<a href="nowbase.html?author=${encodeURIComponent(item.publisher)}" class="mirror-link" target="_blank">${item.publisher}</a>` : '-';
        // 根据文件类型获取图标
        const fileIcon = getFileIcon(item.name);
        
        htmlContent += `
        <tr>
            <td>
                <a href="${item.download}" class="mirror-link" target="_blank">
                    <span class="mirror-icon">${fileIcon}</span>
                    ${item.name}
                </a>
            </td>
            <td>${doiLink}</td>
            <td>${publisherLink}</td>
            <td title="${item.description || ''}">${item.description || '-'}</td>
            <td class="mirror-size">${item.size || '-'}</td>
            <td>${item.updated || '-'}</td>
        </tr>`;
    });
    
    const tbody = document.querySelector('.mirror-table tbody');
    if (tbody) {
        tbody.innerHTML = htmlContent;
    }
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 极简模式下移除所有 CSS
    if (isSimpleMode()) {
        document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
            link.remove();
        });
    }
    
    // 加载开源项目数据
    loadOpensourceData();
});

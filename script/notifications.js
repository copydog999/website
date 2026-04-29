function toggleNotice(id) {
  const content = document.getElementById(`notice-${id}`);
  const btn = content.previousElementSibling.querySelector('.expand-btn');
  if(content.style.display === 'none') {
    content.style.display = 'block';
    btn.textContent = '收起';
  } else {
    content.style.display = 'none';
    btn.textContent = '展开';
  }
}

// 通知数据将从 notification.json 加载
let notificationsData = [];
let isShowingAll = false; // 标记是否显示全部通知

// 加载通知数据
async function loadNotifications() {
    try {
        const response = await fetch('../database/data/notification.json');
        notificationsData = await response.json();
        displayNotifications(notificationsData);
        
        // 检查URL中是否有搜索参数
        const urlParams = new URLSearchParams(window.location.search);
        const searchParam = urlParams.get('search');
        if (searchParam) {
            // 在搜索框中填入搜索参数并执行搜索
            const searchBox = document.getElementById('notificationSearchBox');
            searchBox.value = searchParam;
            searchNotifications(searchParam);
        }
    } catch (error) {
        console.error('加载通知数据失败:', error);
        const container = document.getElementById('notificationsContainer');
        if (container) {
            container.innerHTML = '<div class="no-results">加载通知数据失败，请稍后重试</div>';
        }
    }
}

// 显示通知
function displayNotifications(notifications, showAll = false) {
    if (!notifications || notifications.length === 0) {
        const container = document.getElementById('notificationsContainer');
        if (container) {
            container.innerHTML = '<div class="no-results">暂无通知</div>';
        }
        return;
    }
    
    let htmlContent = '';
    
    // 按时间倒序排列（最新的在前）
    const sortedNotifications = [...notifications].sort((a, b) => b.id - a.id);
    
    // 如果不是显示全部且不是搜索状态，只显示前5个
    const displayList = (showAll || isShowingAll) ? sortedNotifications : sortedNotifications.slice(0, 5);
    
    displayList.forEach(notification => {
        htmlContent += `
        <div class="notice-item">
            <div class="notice-header" onclick="toggleNotice(${notification.id})">
                <span><h3>${notification.title}</h3><i>${notification.date} by: ${notification.author}</i></span>
                <button class="expand-btn">展开</button>
            </div>
            <div class="notice-content" id="notice-${notification.id}" style="display:none;">
                ${notification.content}
            </div>
        </div>`;
    });
    
    // 添加“查看全部”按钮（仅在非搜索状态且总数超过5个时显示）
    if (!isShowingAll && sortedNotifications.length > 5) {
        htmlContent += `
        <div class="load-more-container" style="text-align: center; margin-top: 20px;">
            <button onclick="showAllNotifications()" class="load-more-btn">查看全部 (${sortedNotifications.length} 条)</button>
        </div>`;
    }
    
    const container = document.getElementById('notificationsContainer');
    if (container) {
        container.innerHTML = htmlContent;
    }
}

// 搜索功能
function searchNotifications(query) {
    if (!query.trim()) {
        // 清空搜索时重置为懒加载模式
        isShowingAll = false;
        displayNotifications(notificationsData);
        return;
    }
    
    const filteredNotifications = notificationsData.filter(notification => {
        const searchTerms = query.toLowerCase();
        return (
            notification.title.toLowerCase().includes(searchTerms) ||
            notification.author.toLowerCase().includes(searchTerms) ||
            notification.content.toLowerCase().includes(searchTerms) ||
            notification.date.toLowerCase().includes(searchTerms)
        );
    });
    
    // 搜索结果全部显示，不限制数量
    displayNotifications(filteredNotifications, true);
}

// 显示所有通知
function showAllNotifications() {
    isShowingAll = true;
    displayNotifications(notificationsData, true);
}

// 页面加载完成后加载数据
document.addEventListener('DOMContentLoaded', function() {
    // 应用极简模式
    utils.applySimpleMode();
    
    loadNotifications();
    
    // 绑定搜索事件
    const searchBox = document.getElementById('notificationSearchBox');
    if (searchBox) {
        searchBox.addEventListener('input', function() {
            searchNotifications(this.value);
        });
    }
});
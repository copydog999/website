// 检测是否为极简模式
function isSimpleMode() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('sty') === 'no';
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 极简模式下移除所有 CSS
    if (isSimpleMode()) {
        document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
            link.remove();
        });
    }
});

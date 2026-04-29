function submitReport() {
    // 获取选中的举报类型
    const checkboxes = document.querySelectorAll('input[name="issueType"]:checked');
    const issueTypes = Array.from(checkboxes).map(cb => cb.value);
    
    // 获取详细描述
    const details = document.getElementById('details').value.trim();
    
    if (!details) {
        alert('请填写具体情况说明！');
        return;
    }
    
    if (issueTypes.length === 0) {
        alert('请至少选择一项举报类型！');
        return;
    }
    
    // 构建邮件内容
    const subject = `举报：${issueTypes.join('、')}`;
    const body = `举报类型：${issueTypes.join('，')}%0D%0A%0D%0A具体情况：%0D%0A${encodeURIComponent(details)}`;
    
    // 发送邮件
    window.location.href = `mailto:report.joest.cn@outlook.com?subject=${subject}&body=${body}`;
    
    // 重置表单（可选）
    document.getElementById('reportForm').reset();
    alert('举报信息已准备发送，请检查邮件内容后点击发送！');
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 应用极简模式
    utils.applySimpleMode();
});
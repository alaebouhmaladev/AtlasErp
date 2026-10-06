// Portal navigation only; native document lists retain their server-side scope.
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.web-sidebar');
    if (!sidebar || sidebar.querySelector('.atlas-portal-return')) return;
    const link = document.createElement('a');
    link.className = 'atlas-portal-return';
    link.href = '/atlas-portal';
    link.textContent = typeof __ === 'function' ? __('Customer workspace') : 'Customer workspace';
    sidebar.prepend(link);
});

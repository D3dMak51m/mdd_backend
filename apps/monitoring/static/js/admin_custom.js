// apps/monitoring/static/js/admin_custom.js

document.addEventListener("DOMContentLoaded", function() {
    // 1. Принудительно убираем класс dark у html тега
    document.documentElement.classList.remove('dark');

    // 2. Записываем в localStorage, что тема светлая (чтобы Unfold запомнил)
    localStorage.setItem('theme', 'light');

    // 3. Скрываем кнопку переключения темы (обычно это иконка луны/солнца)
    const themeToggle = document.querySelector('button[data-action="theme-toggle"]');
    if (themeToggle) {
        themeToggle.style.display = 'none';
    }

    // Дополнительная страховка: ищем любые элементы с классом dark и чистим их
    document.querySelectorAll('.dark').forEach(el => {
        el.classList.remove('dark');
    });
});
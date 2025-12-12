// apps/monitoring/static/js/admin_custom.js

// Принудительная светлая тема - запускается немедленно
(function() {
    'use strict';

    // 1. Удаляем класс dark
    const forceLight = () => {
        document.documentElement.classList.remove('dark');
        document.documentElement.removeAttribute('data-theme');
        document.body.classList.remove('dark');
    };

    // Запускаем немедленно
    forceLight();

    // 2. Устанавливаем localStorage
    try {
        localStorage.setItem('theme', 'light');
        localStorage.removeItem('darkMode');
    } catch(e) {}

    // 3. Мониторим изменения DOM
    const observer = new MutationObserver(forceLight);

    document.addEventListener('DOMContentLoaded', function() {
        forceLight();

        // Наблюдаем за изменениями
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['class', 'data-theme']
        });

        // Скрываем кнопку переключения темы
        const hideThemeToggle = () => {
            const selectors = [
                'button[data-action="theme-toggle"]',
                '[data-theme-toggle]',
                '.theme-toggle',
                'button[aria-label*="theme"]',
                'button[aria-label*="Theme"]'
            ];

            selectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                    el.style.opacity = '0';
                    el.style.pointerEvents = 'none';
                });
            });
        };

        hideThemeToggle();

        // Повторяем каждые 500мс первые 3 секунды
        let count = 0;
        const interval = setInterval(() => {
            forceLight();
            hideThemeToggle();
            count++;
            if (count > 6) clearInterval(interval);
        }, 500);
    });

    // Блокируем события изменения темы
    window.addEventListener('storage', function(e) {
        if (e.key === 'theme' && e.newValue !== 'light') {
            localStorage.setItem('theme', 'light');
            forceLight();
        }
    });
})();
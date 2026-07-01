/**
 * Thème clair/sombre ONIP — remplace le bundle Mazer app.js (sidebar PerfectScrollbar
 * incompatible avec notre layout onip-sidebar).
 */
(function () {
    var STORAGE_KEY = 'theme';
    var THEME_CLASS = /\btheme-[a-z0-9]+\b/g;
    var toggle = document.getElementById('toggle-dark');

    function setTheme(theme, skipPersist) {
        document.body.className = document.body.className.replace(THEME_CLASS, '');
        document.body.classList.add(theme);
        if (toggle) {
            toggle.checked = theme === 'theme-dark';
        }
        if (!skipPersist) {
            localStorage.setItem(STORAGE_KEY, theme);
        }
    }

    function toggleDarkTheme() {
        setTheme(document.body.classList.contains('theme-dark') ? 'theme-light' : 'theme-dark');
    }

    if (toggle) {
        toggle.addEventListener('input', function (event) {
            setTheme(event.target.checked ? 'theme-dark' : 'theme-light');
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        var saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
            setTheme(saved, true);
            return;
        }
        if (window.matchMedia) {
            var mq = window.matchMedia('(prefers-color-scheme: dark)');
            mq.addEventListener('change', function (event) {
                setTheme(event.matches ? 'theme-dark' : 'theme-light', true);
            });
            setTheme(mq.matches ? 'theme-dark' : 'theme-light', true);
            return;
        }
        setTheme('theme-light', true);
    });

    window.setTheme = setTheme;
    window.toggleDarkTheme = toggleDarkTheme;
})();

document.addEventListener('DOMContentLoaded', function () {
    const weeklyBtn = document.getElementById('attendance-view-weekly');
    const monthlyBtn = document.getElementById('attendance-view-monthly');
    const weeklyPanel = document.getElementById('attendance-weekly-panel');
    const monthlyPanel = document.getElementById('attendance-monthly-panel');
    const weekNav = document.getElementById('attendance-week-nav');
    const monthNav = document.getElementById('attendance-month-nav');
    const storageKey = 'payday-employee-attendance-view';

    function setView(mode) {
        const isWeekly = mode === 'weekly';
        if (weeklyBtn) weeklyBtn.classList.toggle('active', isWeekly);
        if (monthlyBtn) monthlyBtn.classList.toggle('active', !isWeekly);
        if (weeklyPanel) weeklyPanel.hidden = !isWeekly;
        if (monthlyPanel) monthlyPanel.hidden = isWeekly;
        if (weekNav) weekNav.hidden = !isWeekly;
        if (monthNav) monthNav.hidden = isWeekly;
        localStorage.setItem(storageKey, mode);
    }

    if (weeklyBtn && monthlyBtn) {
        const saved = localStorage.getItem(storageKey) || 'weekly';
        setView(saved);

        weeklyBtn.addEventListener('click', function () {
            setView('weekly');
        });
        monthlyBtn.addEventListener('click', function () {
            setView('monthly');
        });
    }

    initEmployeeGeographySection();

    document.querySelectorAll('a[data-bs-toggle="tab"]').forEach(function (tab) {
        tab.addEventListener('show.bs.tab', function (event) {
            localStorage.setItem('payday-employee-last-tab', event.target.getAttribute('href'));
        });
    });

    const activeTab = localStorage.getItem('payday-employee-last-tab');
    if (activeTab) {
        const tabEl = document.querySelector('.employee-tabs a[href="' + activeTab + '"]');
        if (tabEl) {
            bootstrap.Tab.getOrCreateInstance(tabEl).show();
        }
    }
});

function initEmployeeGeographySection() {
    const homeCountry = document.getElementById('id_home_country');
    const section = document.getElementById('employee-geography-section');
    if (!homeCountry || !section) {
        return;
    }

    const drcValues = new Set([
        'République démocratique du Congo',
        'RDC',
        'Congolaise',
        'Congo',
    ]);

    function isDrc(value) {
        const text = (value || '').trim();
        if (!text) {
            return true;
        }
        return drcValues.has(text);
    }

    function toggleGeography() {
        const show = isDrc(homeCountry.value);
        section.hidden = !show;
        section.querySelectorAll('select').forEach(function (select) {
            select.disabled = !show;
        });
    }

    homeCountry.addEventListener('change', toggleGeography);
    if (window.jQuery) {
        window.jQuery(homeCountry).on('select2:select select2:clear', toggleGeography);
    }
    toggleGeography();
}

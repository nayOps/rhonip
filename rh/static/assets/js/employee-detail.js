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
    initEducationReferenceFields();
    initEmployeeFormStepper();

    document.querySelectorAll('a[data-bs-toggle="tab"]').forEach(function (tab) {
        tab.addEventListener('show.bs.tab', function (event) {
            const target = event.target.getAttribute('href') || event.target.getAttribute('data-bs-target');
            if (target && target.startsWith('#epd-tab-')) {
                localStorage.setItem('payday-employee-last-tab', target);
            }
        });
    });

    const hashTab = window.location.hash;
    const savedTab = localStorage.getItem('payday-employee-last-tab');
    const targetTab = hashTab || savedTab;
    if (targetTab && targetTab.startsWith('#epd-tab-')) {
        const tabEl = document.querySelector('.epd-tabs a[href="' + targetTab + '"], .epd-tabs button[data-bs-target="' + targetTab + '"]');
        if (tabEl) {
            bootstrap.Tab.getOrCreateInstance(tabEl).show();
        }
    }
});

function initEducationReferenceFields() {
    function otherInputForSelect(select) {
        const form = select.closest('form') || document;
        const refField = select.getAttribute('data-ref-field');
        if (refField) {
            const wrap = select.closest('.education-ref-field');
            if (wrap) {
                const byWrap = wrap.querySelector('input[data-other-for="' + refField + '"]');
                if (byWrap) {
                    return byWrap;
                }
            }
            if (select.name) {
                const otherName = select.name.replace(
                    new RegExp('-' + refField + '$'),
                    '-' + refField + '_other',
                );
                const byName = form.querySelector('[name="' + otherName + '"]');
                if (byName) {
                    return byName;
                }
            }
        }
        return null;
    }

    function toggleOtherInput(select) {
        const autresPk = (select.getAttribute('data-autres-pk') || '').trim();
        const otherInput = otherInputForSelect(select);
        if (!otherInput) {
            return;
        }
        const show = autresPk && String(select.value) === autresPk;
        otherInput.style.display = show ? '' : 'none';
        otherInput.required = show;
        if (!show) {
            otherInput.value = '';
        }
    }

    function bindSelect(select) {
        if (select.dataset.onipEducationBound !== '1') {
            select.dataset.onipEducationBound = '1';
            select.addEventListener('change', function () {
                toggleOtherInput(select);
            });
        }
        if (window.jQuery) {
            window.jQuery(select)
                .off('select2:select.onipEducation select2:clear.onipEducation')
                .on('select2:select.onipEducation select2:clear.onipEducation', function () {
                    toggleOtherInput(select);
                });
        }
        toggleOtherInput(select);
    }

    function apply() {
        document.querySelectorAll('.onip-education-ref-select').forEach(bindSelect);
    }

    apply();
    document.addEventListener('click', function () {
        setTimeout(apply, 80);
    });
    document.addEventListener('onip:employee-step-shown', function () {
        window.setTimeout(function () {
            apply();
            if (typeof window.onipSyncEmployeeFormSelect2 === 'function') {
                window.onipSyncEmployeeFormSelect2();
            }
        }, 120);
    });
}

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

    function setSelectDisabled(select, disabled) {
        if (window.jQuery) {
            var $select = window.jQuery(select);
            if ($select.hasClass('select2-hidden-accessible')) {
                $select.prop('disabled', disabled);
                return;
            }
        }
        select.disabled = disabled;
    }

    function toggleGeography() {
        const show = isDrc(homeCountry.value);
        const wasHidden = section.hidden;
        section.hidden = !show;
        section.querySelectorAll('select').forEach(function (select) {
            setSelectDisabled(select, !show);
        });
        if (show && wasHidden && typeof window.onipSyncEmployeeFormSelect2 === 'function') {
            window.onipSyncEmployeeFormSelect2();
        }
    }

    homeCountry.addEventListener('change', toggleGeography);
    if (window.jQuery) {
        window.jQuery(homeCountry).on('select2:select select2:clear', toggleGeography);
    }
    toggleGeography();
}

function initEmployeeFormStepper() {
    const panels = document.getElementById('employee-form-step-panels');
    const stepItems = document.querySelectorAll('.employee-form-stepper__item');
    const panes = panels ? panels.querySelectorAll('.employee-step-pane') : [];
    const prevBtn = document.getElementById('employee-step-prev');
    const nextBtn = document.getElementById('employee-step-next');
    const saveBtn = document.getElementById('employee-step-save');
    const storageKey = 'payday-employee-form-step';

    if (!panels || !stepItems.length || !panes.length) {
        return;
    }

    let currentIndex = 0;

    function setStep(index, persist) {
        const safeIndex = Math.max(0, Math.min(index, panes.length - 1));
        currentIndex = safeIndex;

        panes.forEach(function (pane, paneIndex) {
            pane.classList.toggle('show', paneIndex === safeIndex);
            pane.classList.toggle('active', paneIndex === safeIndex);
        });

        stepItems.forEach(function (item, itemIndex) {
            item.classList.remove('is-active', 'is-complete');
            if (itemIndex < safeIndex) {
                item.classList.add('is-complete');
            } else if (itemIndex === safeIndex) {
                item.classList.add('is-active');
            }
        });

        if (prevBtn) {
            prevBtn.disabled = safeIndex === 0;
        }
        if (nextBtn) {
            const isLast = safeIndex === panes.length - 1;
            nextBtn.hidden = isLast;
            nextBtn.innerHTML = isLast
                ? 'Terminer <i class="bi bi-check-lg"></i>'
                : 'Suivant <i class="bi bi-arrow-right"></i>';
        }
        if (saveBtn) {
            saveBtn.hidden = safeIndex !== panes.length - 1;
        }

        if (persist) {
            localStorage.setItem(storageKey, String(safeIndex));
        }

        document.dispatchEvent(new CustomEvent('onip:employee-step-shown', {
            detail: { index: safeIndex, pane: panes[safeIndex] },
        }));

        styleNativeSelects(panes[safeIndex]);
        scheduleSelect2Sync();
        if (typeof initEducationReferenceFields === 'function') {
            window.setTimeout(initEducationReferenceFields, 100);
        }
    }

    function scheduleSelect2Sync() {
        if (typeof window.onipSyncEmployeeFormSelect2 !== 'function') {
            return;
        }
        window.setTimeout(window.onipSyncEmployeeFormSelect2, 80);
        window.setTimeout(window.onipSyncEmployeeFormSelect2, 260);
    }

    function styleNativeSelects(root) {
        if (!root) {
            return;
        }
        root.querySelectorAll('select:not(.select2-hidden-accessible):not([data-autocomplete-light-function])').forEach(function (el) {
            el.classList.add('form-select', 'onip-step-field');
        });
        root.querySelectorAll(
            'input:not([type="checkbox"]):not([type="radio"]):not([type="hidden"]):not([type="file"]).onip-step-field, ' +
            'input:not([type="checkbox"]):not([type="radio"]):not([type="hidden"]):not([type="file"])',
        ).forEach(function (el) {
            if (el.closest('.select2-container') || el.classList.contains('onip-education-other-input')) {
                return;
            }
            if (!el.classList.contains('form-control')) {
                el.classList.add('form-control', 'onip-step-field');
            }
        });
    }

    stepItems.forEach(function (item) {
        const btn = item.querySelector('.employee-form-stepper__btn');
        if (!btn) {
            return;
        }
        btn.addEventListener('click', function () {
            const index = Number(item.getAttribute('data-step-index') || 0);
            setStep(index, true);
        });
    });

    if (prevBtn) {
        prevBtn.addEventListener('click', function () {
            setStep(currentIndex - 1, true);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function () {
            if (currentIndex >= panes.length - 1) {
                return;
            }
            setStep(currentIndex + 1, true);
        });
    }

    document.querySelectorAll('.employee-step-add-btn').forEach(function (button) {
        button.addEventListener('click', function () {
            const pane = button.closest('.employee-step-pane');
            if (!pane) {
                return;
            }
            const target = pane.querySelector('.add-row a, a.add-row, .add-row button');
            if (target) {
                target.click();
            }
        });
    });

    const saved = Number(localStorage.getItem(storageKey) || 0);
    setStep(Number.isFinite(saved) ? saved : 0, false);
    scheduleSelect2Sync();
}

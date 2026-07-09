/**
 * Select2 / DAL — init différée pour onglets masqués + stepper employé.
 */
(function () {
    function jquery() {
        if (window.django && django.jQuery) {
            return django.jQuery;
        }
        return window.jQuery;
    }

    function dalFunctionName($el) {
        return $el.attr('data-autocomplete-light-function') || 'select2';
    }

    function runDalInit($el) {
        var $ = jquery();
        var fnName = dalFunctionName($el);
        if (window.yl && yl.functions && typeof yl.functions[fnName] === 'function') {
            yl.functions[fnName]($, $el[0]);
            return true;
        }
        if (window.__dal__initialize) {
            window.__dal__initialize.call($el[0]);
            return true;
        }
        return false;
    }

    function isInActivePane(element) {
        if (!element) {
            return true;
        }
        var pane = element.closest('.employee-step-pane, .tab-pane');
        if (!pane) {
            return true;
        }
        return pane.classList.contains('active') && pane.classList.contains('show');
    }

    function destroySelect2Element($el) {
        if (!$el || !$el.length) {
            return;
        }
        if ($el.hasClass('select2-hidden-accessible')) {
            try {
                $el.select2('destroy');
            } catch (e) {
                /* noop */
            }
        }
        $el.next('.select2-container').remove();
        $el.removeClass('select2-hidden-accessible');
        $el.removeAttr('data-select2-id');
        $el.removeAttr('aria-hidden');
        $el.removeAttr('tabindex');
    }

    function initElement($el, forceReinit) {
        if (forceReinit) {
            destroySelect2Element($el);
        } else if ($el.hasClass('select2-hidden-accessible')) {
            return;
        }
        runDalInit($el);
    }

    function initAutocompleteIn($root, forceReinit) {
        var $ = jquery();
        if (!$ || !$root || !$root.length) {
            return;
        }
        $root.find('[data-autocomplete-light-function]').each(function () {
            initElement($(this), forceReinit);
        });
        $root.find('select.onip-education-ref-select').each(function () {
            var $el = $(this);
            if (!$el.attr('data-autocomplete-light-function')) {
                $el.attr('data-autocomplete-light-function', 'select2');
            }
            initElement($el, forceReinit);
        });
    }

    function getActivePane($) {
        var $step = $('.employee-step-pane.active.show').first();
        if ($step.length) {
            return $step;
        }
        return $('.tab-pane.active.show').first();
    }

    function stripHiddenPaneSelect2() {
        var $ = jquery();
        if (!$) {
            return;
        }
        $('.employee-step-pane:not(.active), .tab-pane:not(.active)')
            .find('[data-autocomplete-light-function]')
            .each(function () {
                destroySelect2Element($(this));
            });
    }

    function syncActivePaneSelect2() {
        var $ = jquery();
        if (!$) {
            return;
        }
        var $pane = getActivePane($);
        if (!$pane.length) {
            return;
        }
        // Ne détruire que les panneaux réellement masqués (évite de casser l'étape active).
        $('.employee-step-pane:not(.active):not(.show), .tab-pane:not(.active):not(.show)')
            .find('[data-autocomplete-light-function].select2-hidden-accessible')
            .each(function () {
                destroySelect2Element($(this));
            });
        initAutocompleteIn($pane, true);
    }

    function onTabShown(event) {
        var $ = jquery();
        if (!$) {
            return;
        }
        var target = $(event.target).attr('data-bs-target') || $(event.target).attr('href');
        if (!target) {
            return;
        }
        var $pane = $(target);
        if ($pane.length) {
            window.setTimeout(function () {
                stripHiddenPaneSelect2();
                initAutocompleteIn($pane, true);
            }, 80);
        }
    }

    function onDalElementInitialized(event) {
        var element = event.detail && event.detail.element;
        if (!element || isInActivePane(element)) {
            return;
        }
        window.setTimeout(function () {
            destroySelect2Element(jquery()(element));
        }, 0);
    }

    function onDalReady() {
        window.setTimeout(syncActivePaneSelect2, 120);
    }

    function boot() {
        var $ = jquery();
        if (!$) {
            return;
        }
        $('a[data-bs-toggle="tab"], button[data-bs-toggle="tab"]').on('shown.bs.tab', onTabShown);
        document.addEventListener('onip:employee-step-shown', function () {
            window.setTimeout(syncActivePaneSelect2, 60);
        });
        document.addEventListener('dal-element-initialized', onDalElementInitialized);
        window.onipReinitSelect2In = initAutocompleteIn;
        window.onipSyncEmployeeFormSelect2 = syncActivePaneSelect2;
        window.onipDestroySelect2Element = destroySelect2Element;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }

    window.addEventListener('load', onDalReady);
})();

/**
 * Select2 / DAL — init différée pour onglets masqués + ré-init fiable.
 *
 * DAL mémorise les champs déjà initialisés : un destroy + __dal__initialize
 * ne suffit pas. On appelle directement yl.functions.select2 après destroy.
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

    function initElement($el, forceReinit) {
        if (forceReinit && $el.hasClass('select2-hidden-accessible')) {
            try {
                $el.select2('destroy');
            } catch (e) {
                /* noop */
            }
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
    }

    function stripHiddenTabSelect2() {
        var $ = jquery();
        if (!$) return;
        $('.tab-pane:not(.active) [data-autocomplete-light-function].select2-hidden-accessible').each(function () {
            try {
                $(this).select2('destroy');
            } catch (e) {
                /* noop */
            }
        });
    }

    function syncActiveTabSelect2() {
        var $ = jquery();
        if (!$) return;
        var $pane = $('.tab-pane.active').first();
        if ($pane.length) {
            initAutocompleteIn($pane, true);
        }
    }

    function onTabShown(event) {
        var $ = jquery();
        if (!$) return;
        var target = $(event.target).attr('data-bs-target') || $(event.target).attr('href');
        if (!target) return;
        var $pane = $(target);
        if ($pane.length) {
            window.setTimeout(function () {
                initAutocompleteIn($pane, true);
            }, 80);
        }
    }

    function onDalReady() {
        window.setTimeout(function () {
            stripHiddenTabSelect2();
            syncActiveTabSelect2();
        }, 120);
    }

    function boot() {
        var $ = jquery();
        if (!$) return;
        $('a[data-bs-toggle="tab"]').on('shown.bs.tab', onTabShown);
        window.onipReinitSelect2In = initAutocompleteIn;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }

    window.addEventListener('load', onDalReady);
})();

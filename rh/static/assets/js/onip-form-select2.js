/**
 * Select2 / DAL dans onglets Bootstrap (fiche employé).
 * N'initialise que les champs pas encore transformés — pas de destroy (évite les conflits DAL).
 */
(function ($) {
    if (!$) return;

    function initAutocompleteIn($root) {
        if (!$root || !$root.length) return;
        $root.find('[data-autocomplete-light-function]').each(function () {
            var $el = $(this);
            if ($el.hasClass('select2-hidden-accessible')) {
                return;
            }
            $(document).trigger('autocompleteLightInitialize', [this]);
        });
    }

    function onTabShown(event) {
        var target = $(event.target).attr('data-bs-target') || $(event.target).attr('href');
        if (!target) return;
        var $pane = $(target);
        if ($pane.length) {
            window.setTimeout(function () {
                initAutocompleteIn($pane);
            }, 80);
        }
    }

    $(function () {
        $('a[data-bs-toggle="tab"]').on('shown.bs.tab', onTabShown);

        var hash = window.location.hash;
        if (hash && $(hash).length) {
            window.setTimeout(function () {
                initAutocompleteIn($(hash));
            }, 200);
        }
    });
})(window.jQuery);

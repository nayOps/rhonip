/**
 * Cascade géographique employé : province → territoire → secteur → groupement → village.
 */
(function ($) {
    function clearSelect($el) {
        if (!$el.length) return;
        $el.val(null).trigger('change');
    }

    $(function () {
        var $province = $('#id_home_province');
        var $territory = $('#id_home_territory');
        var $sector = $('#id_home_sector');
        var $groupement = $('#id_home_groupement');
        var $village = $('#id_home_village');

        if (!$province.length) return;

        $province.on('change select2:select select2:clear', function () {
            clearSelect($territory);
            clearSelect($sector);
            clearSelect($groupement);
            clearSelect($village);
        });

        $territory.on('change select2:select select2:clear', function () {
            clearSelect($sector);
            clearSelect($groupement);
            clearSelect($village);
        });

        $sector.on('change select2:select select2:clear', function () {
            clearSelect($groupement);
            clearSelect($village);
        });

        $groupement.on('change select2:select select2:clear', function () {
            clearSelect($village);
        });
    });
})(jQuery);

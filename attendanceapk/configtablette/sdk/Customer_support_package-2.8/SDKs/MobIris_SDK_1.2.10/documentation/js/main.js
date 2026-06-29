$(function() {
    $('pre').addClass('prettyprint');
    prettyPrint();
    $('.section > *').unwrap();
    $('li.active').after('<div id="toc"></div>');
    document.title = $('li.active').text();
    $("#toc").tocify({
        selectors: 'h1,h2,h3',
        extendPage: false,
        smoothScroll: false
    });
    $('h1,h2,h3').prev().addClass('clear').each(function() {
        this.id = $(this).attr('name');
    });
    if(window.location.pathname.match(/\Wapi(?=\W)[^\/]*$/i)) {
        $('body').addClass('api open');
        $('#bodyColumn').addClass('api-body');
    }
    $('#banner, .breadcrumb').addClass('clearfix');
    $('#rightColumnToggler').click(function() {
        $('body').toggleClass('closed open');
    });
});

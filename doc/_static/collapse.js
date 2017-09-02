$(document).ready(function() {
    // Default to collapsed
    $('dl.staticmethod, dl.method').addClass('collapsed')

    $('dl.staticmethod > dd > p:first-child, dl.method > dd > p:first-child').click(function(e) {
        $(this).parents().eq(1).toggleClass('collapsed');
    });

    // Attaching the hashchange event listener
    $(window).on('hashchange', function() {
        base = window.location.hash.replace(/\./g, '\\.');
        base = $(base);
        base.parent().removeClass('collapsed');
    });

    // Manually triggering it if we have hash part in URL
    if (window.location.hash) {
        $(window).trigger('hashchange')
    }
});

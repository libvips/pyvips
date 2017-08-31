function collapse_dd() {
    if ($(this).hasClass('collapsed')) {
        $(this).removeClass('collapsed');
        $(this).children('dd').show('fast');
    } else {
        $(this).addClass('collapsed');
        $(this).children('dd').hide('fast');
    }
    return false;
}
$(document).ready(function() {
    $('dl.staticmethod > dd').hide();
    $('dl.staticmethod').addClass('collapsed').click(collapse_dd);
    $('dl.method > dd').hide();
    $('dl.method').addClass('collapsed').click(collapse_dd);

    $('a').click(function(e) {
        e.stopPropagation();
    });
	
    // Attaching the hashchange event listener
    $(window).on('hashchange', function () {
        base = window.location.hash.replace(/\./g, '\\.');
        base = $(base);
        base.removeClass('collapsed');
        base.parents('dd').show();
        base.parents('dl').removeClass('collapsed');
        base.siblings('dd').show();
    });

    // Manually tiggering it if we have hash part in URL
    if (window.location.hash) {
        $(window).trigger('hashchange')
    }
}); 

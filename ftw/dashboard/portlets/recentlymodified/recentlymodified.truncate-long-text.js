jQuery(function($){
    $(window).bind("load", function() {
        $('dl.portlet.portletRecent span.title a').smartTruncation();
        $('dl.portlet.portletRecent dd.portletItem span.title').css('visibility','visible');
    });
});
